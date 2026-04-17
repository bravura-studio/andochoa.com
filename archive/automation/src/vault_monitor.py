#!/usr/bin/env python3
"""
Vault Monitor - File System Watcher for Obsidian Vault
Monitors specified directories for changes and triggers appropriate workflows
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from config import Config
from workflow_engine import WorkflowEngine
from utils import setup_logging, load_state, save_state


class VaultEventHandler(FileSystemEventHandler):
    """Handles file system events in the Obsidian vault"""
    
    def __init__(self, workflow_engine):
        super().__init__()
        self.workflow_engine = workflow_engine
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # Debouncing - prevent duplicate events
        self.recent_events = {}
        self.debounce_time = 2  # seconds
        
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
        """Process the actual file event"""
        self.logger.info(f"Processing {event_type} event for: {file_path}")
        
        try:
            # Determine workflow based on file location
            relative_path = os.path.relpath(file_path, self.config.vault_path)
            workflow_type = self._determine_workflow(relative_path)
            
            if workflow_type:
                # Queue workflow for execution
                self.workflow_engine.queue_workflow(
                    workflow_type=workflow_type,
                    trigger_event=event_type,
                    file_path=file_path,
                    timestamp=datetime.now().isoformat()
                )
                
                self.logger.info(f"Queued {workflow_type} workflow for {file_path}")
            else:
                self.logger.debug(f"No workflow determined for {file_path}")
                
        except Exception as e:
            self.logger.error(f"Error processing file event: {e}")
    
    def _determine_workflow(self, relative_path):
        """Determine appropriate workflow based on file location"""
        
        if relative_path.startswith('1-raw-ideas/'):
            return 'analyze_new_content'
            
        elif relative_path.startswith('training-data/great-writing/'):
            return 'update_style_profile'
            
        elif relative_path.startswith('training-data/world-view/'):
            return 'update_worldview_index'
            
        elif relative_path.startswith('4-published-content/'):
            return 'integrate_published_content'
            
        else:
            return None
    
    def _cleanup_recent_events(self, current_time):
        """Remove old events from recent_events cache"""
        cutoff_time = current_time - (self.debounce_time * 2)
        self.recent_events = {
            key: timestamp for key, timestamp in self.recent_events.items()
            if timestamp > cutoff_time
        }


class VaultMonitor:
    """Main vault monitoring class"""
    
    def __init__(self):
        self.config = Config()
        self.logger = setup_logging(self.config.log_level, self.config.log_file)
        self.workflow_engine = WorkflowEngine()
        self.observer = Observer()
        
        # Event handler
        self.event_handler = VaultEventHandler(self.workflow_engine)
        
        # State management
        self.state_file = Path(self.config.automation_dir) / 'state' / 'monitor_state.json'
        self.state = self._load_state()
        
    def start_monitoring(self):
        """Start the file system monitoring"""
        self.logger.info("Starting vault monitoring...")
        
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
            
            self.logger.info("Vault monitoring started successfully")
            
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
        self.logger.info("Stopping vault monitoring...")
        
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            
        self.state['monitor_stopped'] = datetime.now().isoformat()
        self.state['status'] = 'stopped'
        self._save_state()
        
        self.logger.info("Vault monitoring stopped")
        
    def _periodic_maintenance(self):
        """Perform periodic maintenance tasks"""
        # Update state
        self.state['last_heartbeat'] = datetime.now().isoformat()
        self._save_state()
        
        # Check workflow engine health
        if not self.workflow_engine.is_healthy():
            self.logger.warning("Workflow engine health check failed")
            
    def _load_state(self):
        """Load monitor state from disk"""
        return load_state(self.state_file, default={
            'status': 'stopped',
            'monitor_started': None,
            'monitor_stopped': None,
            'last_heartbeat': None,
            'total_events_processed': 0
        })
        
    def _save_state(self):
        """Save monitor state to disk"""
        save_state(self.state_file, self.state)
        
    def get_status(self):
        """Get current monitor status"""
        return {
            'status': self.state.get('status', 'unknown'),
            'uptime': self._calculate_uptime(),
            'observer_alive': self.observer.is_alive() if self.observer else False,
            'monitored_paths': self.config.monitor_paths,
            'last_heartbeat': self.state.get('last_heartbeat')
        }
        
    def _calculate_uptime(self):
        """Calculate monitor uptime"""
        if self.state.get('monitor_started') and self.state.get('status') == 'running':
            start_time = datetime.fromisoformat(self.state['monitor_started'])
            uptime = datetime.now() - start_time
            return str(uptime).split('.')[0]  # Remove microseconds
        return None


def main():
    """Main entry point"""
    monitor = VaultMonitor()
    
    try:
        monitor.start_monitoring()
    except Exception as e:
        logging.error(f"Failed to start vault monitor: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())