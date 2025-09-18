#!/usr/bin/env python3
"""
Modified Vault Monitor for Claude Desktop Integration
Monitors file changes but uses desktop workflows instead of API calls
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from config import Config
from desktop_workflow_engine import DesktopWorkflowEngine
from utils import setup_logging, load_state, save_state


class DesktopVaultEventHandler(FileSystemEventHandler):
    """Handles file system events for desktop-based workflows"""
    
    def __init__(self, workflow_engine):
        super().__init__()
        self.workflow_engine = workflow_engine
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # Debouncing - prevent duplicate events
        self.recent_events = {}
        self.debounce_time = 2  # seconds
        
        # Desktop-specific settings
        self.auto_process_training_data = True  # Auto-process training data updates
        self.notify_new_content = True  # Notify about new content but don't auto-process
        
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        if self._should_process_file(file_path):
            self._debounced_process('created', file_path)
            
    def on_modified(self, event):
        """Handle file modification events"""  
        if event.is_directory:
            return
            
        file_path = event.src_path
        if self._should_process_file(file_path):
            self._debounced_process('modified', file_path)
    
    def _should_process_file(self, file_path):
        """Determine if file should trigger workflow"""
        # Skip hidden files, temp files, and system files
        if any(part.startswith('.') for part in Path(file_path).parts):
            return False
            
        # Skip non-markdown files in content directories
        if not file_path.endswith('.md'):
            return False
            
        # Skip auto-generated files from our system
        if 'automation' in file_path:
            return False
            
        # Check if file is in monitored directories
        relative_path = os.path.relpath(file_path, self.config.vault_path)
        
        for monitor_path in self.config.monitor_paths:
            if relative_path.startswith(monitor_path):
                return True
                
        return False
    
    def _debounced_process(self, event_type, file_path):
        """Process file event with debouncing to prevent duplicates"""
        current_time = time.time()
        event_key = f"{event_type}:{file_path}"
        
        # Check if we've seen this event recently
        if event_key in self.recent_events:
            if current_time - self.recent_events[event_key] < self.debounce_time:
                return  # Skip duplicate event
                
        # Update recent events and process
        self.recent_events[event_key] = current_time
        self._process_file_event(event_type, file_path)
        
        # Clean up old events  
        self._cleanup_recent_events(current_time)
    
    def _process_file_event(self, event_type, file_path):
        """Process the actual file event for desktop workflows"""
        self.logger.info(f"Processing {event_type} event for: {file_path}")
        
        try:
            # Determine workflow based on file location
            relative_path = os.path.relpath(file_path, self.config.vault_path)
            workflow_action = self._determine_workflow_action(relative_path, file_path)
            
            if workflow_action:
                self._handle_workflow_action(workflow_action, file_path, event_type)
                
        except Exception as e:
            self.logger.error(f"Error processing file event: {e}")
    
    def _determine_workflow_action(self, relative_path, file_path):
        """Determine what action to take for desktop workflows"""
        
        if relative_path.startswith('1-raw-ideas/'):
            return {
                'type': 'notify_new_content',
                'workflow': 'analyze_new_content',
                'auto_process': False,  # User decides when to process
                'priority': 'medium'
            }
            
        elif relative_path.startswith('training-data/great-writing/'):
            return {
                'type': 'auto_process_training',
                'workflow': 'update_style_profile',
                'auto_process': self.auto_process_training_data,
                'priority': 'low'
            }
            
        elif relative_path.startswith('training-data/world-view/'):
            return {
                'type': 'auto_process_training',
                'workflow': 'update_worldview_index', 
                'auto_process': self.auto_process_training_data,
                'priority': 'low'
            }
            
        elif relative_path.startswith('4-published-content/'):
            return {
                'type': 'notify_new_content',
                'workflow': 'integrate_published_content',
                'auto_process': False,
                'priority': 'medium'
            }
            
        else:
            return None
    
    def _handle_workflow_action(self, action, file_path, event_type):
        """Handle the determined workflow action"""
        
        action_type = action['type']
        workflow_type = action['workflow']
        
        if action_type == 'notify_new_content':
            self._notify_new_content(file_path, workflow_type, event_type)
            
        elif action_type == 'auto_process_training' and action['auto_process']:
            self._auto_process_training_data(file_path, workflow_type, event_type)
            
        else:
            self.logger.info(f"File detected but no action taken: {file_path}")
    
    def _notify_new_content(self, file_path, workflow_type, event_type):
        """Send notification about new content that can be processed"""
        
        self.logger.info(f"New content detected: {file_path}")
        
        # Send desktop notification
        try:
            import platform
            system = platform.system()
            
            file_name = Path(file_path).name
            
            if system == "Darwin":  # macOS
                os.system(f'''
                osascript -e 'display notification "New content ready for processing: {file_name}" with title "Vault Monitor"'
                ''')
            elif system == "Windows":  # Windows
                try:
                    import win10toast
                    toaster = win10toast.ToastNotifier()
                    toaster.show_toast(
                        "Vault Monitor", 
                        f"New content ready: {file_name}",
                        duration=5
                    )
                except ImportError:
                    pass
            elif system == "Linux":  # Linux
                os.system(f'notify-send "Vault Monitor" "New content ready: {file_name}"')
                
        except Exception as e:
            self.logger.warning(f"Could not send notification: {e}")
        
        # Create a pending workflow notification file
        self._create_workflow_notification(file_path, workflow_type)
    
    def _auto_process_training_data(self, file_path, workflow_type, event_type):
        """Auto-process training data updates"""
        
        self.logger.info(f"Auto-processing training data: {file_path}")
        
        # Queue workflow for automatic processing
        workflow_id = self.workflow_engine.queue_workflow(
            workflow_type=workflow_type,
            trigger_event=event_type,
            file_path=file_path,
            priority='low'
        )
        
        # Send notification that processing will begin
        try:
            import platform
            system = platform.system()
            
            file_name = Path(file_path).name
            
            if system == "Darwin":  # macOS
                os.system(f'''
                osascript -e 'display notification "Training data update detected. Workflow queued for processing." with title "Auto-Processing"'
                ''')
        except Exception:
            pass
    
    def _create_workflow_notification(self, file_path, workflow_type):
        """Create a file to notify user about available workflows"""
        
        notifications_dir = Path(self.config.automation_dir) / 'notifications'
        notifications_dir.mkdir(exist_ok=True)
        
        notification_file = notifications_dir / f"workflow_available_{int(time.time())}.md"
        
        content = f"""# Workflow Available

**File**: {file_path}
**Workflow Type**: {workflow_type}
**Detected At**: {datetime.now().isoformat()}

## To Process This Content:

Run the following command:

```bash
python -m src.desktop_workflow_engine --workflow {workflow_type} --file "{file_path}"
```

Or process all pending content with:

```bash
python -m src.desktop_workflow_engine --workflow analyze_new_content
```

## What This Will Do:

- Analyze the content and extract semantic metadata
- Create connections to related content
- Update your knowledge graph automatically
- Prepare prompts for Claude Desktop interaction

The system will guide you through the copy/paste process with Claude Desktop.
"""
        
        notification_file.write_text(content, encoding='utf-8')
        self.logger.info(f"Created workflow notification: {notification_file}")
    
    def _cleanup_recent_events(self, current_time):
        """Remove old events from recent_events cache"""
        cutoff_time = current_time - (self.debounce_time * 2)
        self.recent_events = {
            key: timestamp for key, timestamp in self.recent_events.items()
            if timestamp > cutoff_time
        }


class DesktopVaultMonitor:
    """Desktop-optimized vault monitoring class"""
    
    def __init__(self):
        self.config = Config()
        self.logger = setup_logging(self.config.log_level, self.config.get_log_file())
        self.workflow_engine = DesktopWorkflowEngine()
        self.observer = Observer()
        
        # Event handler
        self.event_handler = DesktopVaultEventHandler(self.workflow_engine)
        
        # State management
        self.state_file = Path(self.config.automation_dir) / 'state' / 'desktop_monitor_state.json'
        self.state = self._load_state()
        
        # Create welcome message
        self._create_welcome_message()
        
    def start_monitoring(self):
        """Start the file system monitoring for desktop workflows"""
        self.logger.info("Starting desktop vault monitoring...")
        
        try:
            # Set up directory monitoring
            for monitor_path in self.config.monitor_paths:
                full_path = os.path.join(self.config.vault_path, monitor_path)
                
                if os.path.exists(full_path):
                    self.observer.schedule(
                        self.event_handler, 
                        full_path, 
                        recursive=True
                    )
                    self.logger.info(f"Monitoring: {full_path}")
                else:
                    self.logger.warning(f"Monitor path does not exist: {full_path}")
            
            # Start observer
            self.observer.start()
            self.state['monitor_started'] = datetime.now().isoformat()
            self.state['status'] = 'running'
            self._save_state()
            
            self.logger.info("Desktop vault monitoring started successfully")
            print("\n✅ Desktop Vault Monitor is running!")
            print("📁 Monitoring your vault for changes...")
            print("🔔 You'll get notifications when new content is ready to process")
            print("\n💡 Commands available while monitoring:")
            print("   Ctrl+C: Stop monitoring")
            print("   Open new terminal for manual workflows:")
            print("   python -m src.desktop_workflow_engine --list")
            print("\n🎯 Ready for automated content detection!")
            
            # Keep the monitor running
            try:
                while True:
                    time.sleep(10)  # Check every 10 seconds
                    self._periodic_maintenance()
                    
            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal, stopping monitor...")
                self.stop_monitoring()
                
        except Exception as e:
            self.logger.error(f"Error starting monitor: {e}")
            self.stop_monitoring()
            
    def stop_monitoring(self):
        """Stop the file system monitoring"""
        self.logger.info("Stopping desktop vault monitoring...")
        
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            
        self.state['monitor_stopped'] = datetime.now().isoformat()
        self.state['status'] = 'stopped'
        self._save_state()
        
        self.logger.info("Desktop vault monitoring stopped")
        print("👋 Desktop vault monitoring stopped")
        
    def _create_welcome_message(self):
        """Create welcome message for first-time users"""
        
        welcome_file = Path(self.config.automation_dir) / 'WELCOME_DESKTOP.md'
        
        if not welcome_file.exists():
            content = """# 🎉 Welcome to Desktop Vault Automation!

Your automation system is now running with Claude Desktop integration.

## How It Works:

### 1. **Automatic Detection** 🔍
- System monitors your vault for new files
- Detects changes in real-time
- Sends desktop notifications when content is ready

### 2. **Smart Workflows** 🧠
- Prepares complete prompts for Claude Desktop
- Guides you through copy/paste process
- Processes results automatically

### 3. **Minimal User Effort** ⚡
- 90% automation, 10% copy/paste
- Uses your existing Claude Pro subscription
- No API costs or setup required

## Quick Start:

### Test the System:
1. **Create a test file**: Add any content to `1-raw-ideas/test.md`
2. **Get notification**: System will notify you content is ready
3. **Run workflow**: `python -m src.desktop_workflow_engine --workflow analyze_new_content`
4. **Follow prompts**: Copy/paste to Claude Desktop as instructed

### Generate Weekly Draft:
1. **Run command**: `python -m src.desktop_workflow_engine --workflow generate_weekly_draft`  
2. **Copy prompt**: System prepares complete context automatically
3. **Paste to Claude**: One interaction with Claude Desktop
4. **Get result**: Automatic draft saved to your vault

## Available Commands:

```bash
# List all workflows
python -m src.desktop_workflow_engine --list

# Generate weekly draft  
python -m src.desktop_workflow_engine --workflow generate_weekly_draft

# Process new content
python -m src.desktop_workflow_engine --workflow analyze_new_content

# Check system status
python -m src.desktop_workflow_engine --status
```

## File Structure:

- `prompts/` - Ready-to-use prompts for Claude Desktop
- `responses/` - Save Claude Desktop responses here  
- `notifications/` - Workflow availability notifications
- `logs/` - System logs and activity

## Tips:

- Keep Claude Desktop app open for faster workflows
- System notifications guide you to ready workflows
- Copy ENTIRE responses from Claude Desktop
- File names matter - use exact names from prompts

**You now have a true AI-powered content creation partner! 🚀**
"""
            welcome_file.write_text(content, encoding='utf-8')
    
    def _periodic_maintenance(self):
        """Perform periodic maintenance tasks"""
        # Update state
        self.state['last_heartbeat'] = datetime.now().isoformat()
        self._save_state()
        
        # Clean up old notification files (older than 7 days)
        try:
            notifications_dir = Path(self.config.automation_dir) / 'notifications'
            if notifications_dir.exists():
                cutoff_time = time.time() - (7 * 24 * 3600)
                for notification_file in notifications_dir.glob('workflow_available_*.md'):
                    if notification_file.stat().st_mtime < cutoff_time:
                        notification_file.unlink()
        except Exception:
            pass
        
    def _load_state(self) -> dict:
        """Load monitor state from disk"""
        return load_state(self.state_file, default={
            'status': 'stopped',
            'monitor_started': None,
            'monitor_stopped': None,
            'last_heartbeat': None,
            'total_events_processed': 0,
            'version': '1.0-desktop'
        })
        
    def _save_state(self):
        """Save monitor state to disk"""
        save_state(self.state_file, self.state)


def main():
    """Main entry point for desktop monitor"""
    monitor = DesktopVaultMonitor()
    
    try:
        monitor.start_monitoring()
    except Exception as e:
        logging.error(f"Failed to start desktop vault monitor: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())