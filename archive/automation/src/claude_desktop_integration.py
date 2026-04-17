#!/usr/bin/env python3
"""
Claude Desktop Integration Module
Handles workflow preparation and response processing for Claude Desktop app
instead of direct API calls, using existing Claude Pro subscription
Creates markdown files for seamless Obsidian integration
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from config import get_config


class ClaudeDesktopIntegration:
    """Claude Desktop integration for agent communication without API"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Set up directories
        self.prompts_dir = Path(self.config.automation_dir) / 'prompts'
        self.responses_dir = Path(self.config.automation_dir) / 'responses'
        self.contexts_dir = Path(self.config.automation_dir) / 'contexts'
        
        # Ensure directories exist
        for directory in [self.prompts_dir, self.responses_dir, self.contexts_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create instruction files if they don't exist
        self._create_instruction_files()
        
    def prepare_agent_workflow(self, agent_name: str, context: Dict, workflow_id: str) -> Optional[Dict]:
        """Prepare an agent workflow for Claude Desktop execution"""
        
        try:
            # Load agent prompt template
            agent_prompt = self._load_agent_prompt(agent_name)
            if not agent_prompt:
                self.logger.error(f"Could not load agent prompt: {agent_name}")
                return None
            
            # Prepare complete prompt with context
            complete_prompt = self._prepare_complete_prompt(agent_prompt, context, workflow_id)
            
            # Save prompt file for user (now in markdown format)
            prompt_file = self.prompts_dir / f"{workflow_id}_{agent_name}_prompt.md"
            context_file = self.contexts_dir / f"{workflow_id}_{agent_name}_context.json"
            
            # Save prompt in markdown format
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(complete_prompt)
            
            # Save context for response processing
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(context, f, indent=2)
            
            # Create workflow tracking
            workflow_info = {
                'workflow_id': workflow_id,
                'agent': agent_name,
                'status': 'prompt_ready',
                'prompt_file': str(prompt_file),
                'context_file': str(context_file),
                'response_file': str(self.responses_dir / f"{workflow_id}_{agent_name}_response.md"),
                'created_at': datetime.now().isoformat(),
                'context': context
            }
            
            # Send desktop notification
            self._send_desktop_notification(
                title=f"Claude Prompt Ready: {agent_name.title()} Agent",
                message=f"Prompt prepared for {agent_name} agent. Click to open prompt file.",
                prompt_file=prompt_file
            )
            
            self.logger.info(f"Prepared {agent_name} prompt for workflow {workflow_id}")
            return workflow_info
            
        except Exception as e:
            self.logger.error(f"Error preparing {agent_name} workflow: {e}")
            return None
    
    def check_for_response(self, workflow_id: str, agent_name: str, timeout: int = 300) -> Optional[Dict]:
        """Check for user-provided response from Claude Desktop"""
        
        response_file = self.responses_dir / f"{workflow_id}_{agent_name}_response.md"
        context_file = self.contexts_dir / f"{workflow_id}_{agent_name}_context.json"
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if response_file.exists():
                try:
                    # Read response
                    response_text = response_file.read_text(encoding='utf-8')
                    
                    # Load context
                    context = {}
                    if context_file.exists():
                        with open(context_file, 'r', encoding='utf-8') as f:
                            context = json.load(f)
                    
                    # Mark as processed by renaming
                    processed_file = self.responses_dir / f"{workflow_id}_{agent_name}_processed.md"
                    response_file.rename(processed_file)
                    
                    result = {
                        'agent': agent_name,
                        'workflow_id': workflow_id,
                        'success': True,
                        'response': response_text,
                        'context': context,
                        'timestamp': datetime.now().isoformat(),
                        'response_file': str(processed_file)
                    }
                    
                    self.logger.info(f"Received response for {agent_name} workflow {workflow_id}")
                    return result
                    
                except Exception as e:
                    self.logger.error(f"Error processing response for {workflow_id}: {e}")
                    return None
            
            # Check every 5 seconds
            time.sleep(5)
        
        # Timeout reached
        self.logger.warning(f"Timeout waiting for response: {workflow_id}_{agent_name}")
        return {
            'agent': agent_name,
            'workflow_id': workflow_id,
            'success': False,
            'error': 'Response timeout',
            'timestamp': datetime.now().isoformat()
        }
    
    def wait_for_user_interaction(self, workflow_info: Dict, max_wait_time: int = 1800) -> Dict:
        """Wait for user to complete Claude Desktop interaction"""
        
        workflow_id = workflow_info['workflow_id']
        agent_name = workflow_info['agent']
        
        self.logger.info(f"Waiting for user interaction: {agent_name} agent (workflow {workflow_id})")
        
        # Send reminder notification after 5 minutes
        reminder_sent = False
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            # Check for response
            response_result = self.check_for_response(workflow_id, agent_name, timeout=60)
            
            if response_result and response_result.get('success'):
                return response_result
            
            # Send reminder notification after 5 minutes
            if not reminder_sent and time.time() - start_time > 300:
                self._send_reminder_notification(workflow_info)
                reminder_sent = True
            
            time.sleep(10)  # Check every 10 seconds
        
        # Max wait time exceeded
        return {
            'agent': agent_name,
            'workflow_id': workflow_id,
            'success': False,
            'error': 'Max wait time exceeded',
            'timestamp': datetime.now().isoformat()
        }
    
    def _load_agent_prompt(self, agent_name: str) -> Optional[str]:
        """Load agent prompt template from file"""
        agent_path = self.config.get_agent_path(agent_name)
        
        try:
            if agent_path.exists():
                return agent_path.read_text(encoding='utf-8')
            else:
                self.logger.error(f"Agent file not found: {agent_path}")
                return None
        except Exception as e:
            self.logger.error(f"Error loading agent prompt {agent_name}: {e}")
            return None
    
    def _prepare_complete_prompt(self, agent_prompt: str, context: Dict, workflow_id: str) -> str:
        """Prepare complete prompt with context and instructions for Claude Desktop"""
        
        # Format the prompt with context variables
        try:
            formatted_prompt = agent_prompt.format(**context)
        except KeyError as e:
            self.logger.warning(f"Missing context variable {e}, using original prompt")
            formatted_prompt = agent_prompt
        
        # Get response filename for instructions
        response_filename = f"{workflow_id}_{context.get('agent', 'unknown')}_response.md"
        
        # Create complete prompt in proper markdown format for Obsidian
        complete_prompt = f"""# 🤖 Claude Desktop Workflow
> **Workflow ID**: `{workflow_id}`  
> **Agent**: {context.get('agent', 'unknown').title()}  
> **Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> **Status**: Ready for Claude Desktop

## 📋 Instructions for You

1. **Copy Agent Prompt**: Copy everything in the "Agent Prompt" section below
2. **Paste to Claude Desktop**: Open Claude Desktop app and paste the copied content  
3. **Get Response**: Wait for Claude to provide complete response
4. **Copy Full Response**: Select and copy Claude's ENTIRE response (including formatting)
5. **Save Response**: Create file `{response_filename}` in the `responses/` folder with Claude's response
6. **System Processes**: The automation system will detect and process the response automatically

## 📊 Workflow Context

- **🗂 Vault Path**: `{self.config.vault_path}`
- **🔄 Trigger**: {context.get('trigger_event', 'manual')}
- **📄 File**: {context.get('file_path', 'none')}  
- **⚙️ Workflow Type**: {context.get('workflow_type', 'unknown')}

---

## 🤖 Agent Prompt
> Copy everything below this line to Claude Desktop

{formatted_prompt}

---

## 🗃 Context Data
> This context is provided to the agent for processing

```json
{json.dumps(context, indent=2)}
```

---

## ✅ Next Steps

1. Copy the Agent Prompt section above
2. Paste into Claude Desktop
3. After Claude responds, save the response to:
   **`{self.responses_dir}/{response_filename}`**

> **💡 Tip**: Keep this file open in Obsidian for reference while working with Claude Desktop!
"""
        
        return complete_prompt
    
    def _send_desktop_notification(self, title: str, message: str, prompt_file: Path):
        """Send desktop notification to user"""
        
        try:
            # Try different notification systems based on OS
            import platform
            system = platform.system()
            
            if system == "Darwin":  # macOS
                os.system(f'''
                osascript -e 'display notification "{message}" with title "{title}"'
                ''')
                # Auto-open the prompt file in Obsidian if possible, otherwise default app
                os.system(f'open "{prompt_file}"')
                
            elif system == "Windows":  # Windows
                try:
                    import win10toast
                    toaster = win10toast.ToastNotifier()
                    toaster.show_toast(title, message, duration=10)
                    # Auto-open the prompt file
                    os.startfile(str(prompt_file))
                except ImportError:
                    # Fallback: just open the file
                    os.startfile(str(prompt_file))
                    
            elif system == "Linux":  # Linux
                os.system(f'notify-send "{title}" "{message}"')
                # Auto-open with default text editor
                os.system(f'xdg-open "{prompt_file}"')
                
            else:
                # Fallback: just log
                self.logger.info(f"Notification: {title} - {message}")
                
        except Exception as e:
            self.logger.warning(f"Could not send desktop notification: {e}")
            # Fallback: create a notification file
            notification_file = self.prompts_dir / "NOTIFICATION.md"
            with open(notification_file, 'w') as f:
                f.write(f"# 🔔 {title}\n\n{message}\n\n**Prompt file**: `{prompt_file}`\n")
    
    def _send_reminder_notification(self, workflow_info: Dict):
        """Send reminder notification after waiting"""
        
        title = f"Reminder: Claude Workflow Waiting"
        message = f"Still waiting for {workflow_info['agent']} agent response"
        
        try:
            import platform
            system = platform.system()
            
            if system == "Darwin":  # macOS
                os.system(f'osascript -e \'display notification "{message}" with title "{title}"\'')
            elif system == "Windows":  # Windows  
                try:
                    import win10toast
                    toaster = win10toast.ToastNotifier()
                    toaster.show_toast(title, message, duration=5)
                except ImportError:
                    pass
            elif system == "Linux":  # Linux
                os.system(f'notify-send "{title}" "{message}"')
                
        except Exception as e:
            self.logger.warning(f"Could not send reminder notification: {e}")
    
    def _create_instruction_files(self):
        """Create instruction files for user reference"""
        
        # Main instructions file
        instructions_file = self.prompts_dir / "HOW_TO_USE.md"
        if not instructions_file.exists():
            instructions_content = """# 🚀 How to Use Claude Desktop Integration

## Quick Start Workflow

### 1. 🔔 **Get Notification**
- System detects new content or workflow trigger
- Desktop notification appears: *"Claude Prompt Ready: [Agent] Agent"*
- Prompt file auto-opens in your default markdown editor

### 2. 📋 **Copy Agent Prompt** 
- Open the auto-opened `.md` file in the `prompts/` folder
- Find the **"Agent Prompt"** section
- Copy everything under that section (the actual prompt for Claude)

### 3. 🤖 **Paste to Claude Desktop**
- Open Claude Desktop app
- Paste the copied prompt
- Wait for Claude to provide complete response

### 4. 📄 **Save Response**
- Select and copy Claude's ENTIRE response
- Create new file in `responses/` folder with exact name specified in prompt
- Paste Claude's response and save
- **Important**: Copy everything including formatting, code blocks, etc.

### 5. ⚙️ **System Processes**
- System automatically detects your saved response
- Processes the response and updates your vault
- Moves to next agent if needed, or completes workflow

---

## 📁 File Structure

```
automation/
├── prompts/          # 📋 Ready-to-use prompts (auto-opened)
├── responses/        # 💾 Save Claude Desktop responses here  
├── contexts/         # 🗃 System context (don't modify)
└── logs/            # 📊 System activity logs
```

---

## 🎯 Workflow Examples

### **New Content Analysis**
1. Add file to `1-raw-ideas/`
2. 🔔 "Analyzer Agent prompt ready" 
3. Copy prompt → Claude Desktop → Save response
4. 🔔 "Connector Agent prompt ready"
5. Copy prompt → Claude Desktop → Save response
6. ✅ Content analyzed and connected automatically

### **Weekly Draft Generation**  
1. Run: `python run_desktop_workflow.py --workflow generate_weekly_draft`
2. 🔔 "Draftsmith Agent prompt ready"
3. Copy prompt → Claude Desktop → Save response
4. ✅ Complete draft saved to `3-article-drafts/`

---

## 💡 Pro Tips

- **Keep both apps open**: Obsidian and Claude Desktop for fastest workflow
- **Use exact filenames**: Response files must match names in prompts exactly
- **Copy everything**: Include all markdown formatting from Claude's responses
- **Files auto-open**: Prompt files should open automatically when ready
- **Watch notifications**: System guides you through each step
- **Check logs**: `logs/` folder has detailed activity if troubleshooting needed

---

## 🆘 Troubleshooting

**Prompt doesn't open automatically?**
- Check `prompts/` folder manually
- Look for newest `.md` file

**Response not detected?**  
- Verify exact filename matches prompt instructions
- Make sure file is in `responses/` folder
- Check that you saved as `.md` format

**Workflow stuck?**
- Check `logs/desktop_automation.log` for errors
- Restart with: `python run_desktop_workflow.py --status`

---

That's it! The system handles all the coordination - you just copy/paste between the files and Claude Desktop! 🎉
"""
            
            with open(instructions_file, 'w', encoding='utf-8') as f:
                f.write(instructions_content)
        
        # Create response folder README
        response_readme = self.responses_dir / "README.md"
        if not response_readme.exists():
            response_content = """# 📁 Response Folder

Save Claude Desktop responses here using the **exact filenames** specified in the prompt files.

## 📝 File Naming Pattern
```
{workflow_id}_{agent_name}_response.md
```

## 📋 Example Process
1. Prompt says: *"Save response to: `abc123_analyzer_response.md`"*
2. Copy Claude's entire response from Claude Desktop
3. Create file `abc123_analyzer_response.md` in this folder
4. Paste Claude's response and save
5. System automatically processes and renames to `*_processed.md`

## ✅ Important Notes

- **Copy EVERYTHING**: Include all formatting, markdown, code blocks, etc.
- **Exact filenames**: Must match exactly what prompt specifies
- **Full responses**: Don't edit or truncate Claude's responses
- **Save as .md**: Always use markdown format for Obsidian compatibility

## 🔄 Processing Flow

```
response.md → system detects → processes content → *_processed.md
```

After processing, your original response file gets renamed to `*_processed.md` to show it's been handled by the system.

---

💡 **Tip**: You can keep processed response files as reference, or delete them to keep the folder clean!
"""
            with open(response_readme, 'w', encoding='utf-8') as f:
                f.write(response_content)


class DesktopWorkflowCoordinator:
    """Coordinates desktop-based workflows with user interaction"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.desktop_integration = ClaudeDesktopIntegration()
        
    def execute_workflow(self, workflow_type: str, context: Dict) -> Dict:
        """Execute a workflow using Claude Desktop integration"""
        
        self.logger.info(f"Executing desktop workflow: {workflow_type}")
        
        workflow_result = {
            'workflow_type': workflow_type,
            'started': datetime.now().isoformat(),
            'context': context,
            'agents_executed': [],
            'success': False,
            'errors': [],
            'method': 'claude_desktop'
        }
        
        try:
            # Determine agent sequence for workflow
            agent_sequence = self._get_agent_sequence(workflow_type)
            
            if not agent_sequence:
                error_msg = f"Unknown workflow type: {workflow_type}"
                self.logger.error(error_msg)
                workflow_result['errors'].append(error_msg)
                return workflow_result
            
            # Execute agents in sequence with user interaction
            for agent_config in agent_sequence:
                agent_name = agent_config['agent']
                workflow_id = f"{workflow_type}_{int(time.time())}"
                
                self.logger.info(f"Preparing desktop workflow for {agent_name}")
                
                # Prepare agent context
                agent_context = self._prepare_agent_context(agent_config, context, workflow_result)
                agent_context['workflow_id'] = workflow_id
                agent_context['agent'] = agent_name
                
                # Prepare workflow for desktop
                workflow_info = self.desktop_integration.prepare_agent_workflow(
                    agent_name, agent_context, workflow_id
                )
                
                if not workflow_info:
                    error_msg = f"Failed to prepare {agent_name} workflow"
                    self.logger.error(error_msg)
                    workflow_result['errors'].append(error_msg)
                    
                    if agent_config.get('required', True):
                        workflow_result['completed'] = datetime.now().isoformat()
                        return workflow_result
                    continue
                
                # Wait for user interaction
                response_result = self.desktop_integration.wait_for_user_interaction(
                    workflow_info, max_wait_time=1800  # 30 minutes
                )
                
                if response_result and response_result.get('success'):
                    workflow_result['agents_executed'].append(response_result)
                    
                    # Process agent output
                    self._process_agent_output(agent_name, response_result, context)
                    
                    self.logger.info(f"Successfully completed {agent_name} agent")
                    
                else:
                    error_msg = f"Agent {agent_name} failed or timed out"
                    self.logger.error(error_msg)
                    workflow_result['errors'].append(error_msg)
                    
                    if agent_config.get('required', True):
                        workflow_result['completed'] = datetime.now().isoformat()
                        return workflow_result
            
            # Mark workflow as successful if we got here
            workflow_result['success'] = True
            workflow_result['completed'] = datetime.now().isoformat()
            
            self.logger.info(f"Desktop workflow {workflow_type} completed successfully")
            
        except Exception as e:
            error_msg = f"Desktop workflow execution error: {e}"
            self.logger.error(error_msg)
            workflow_result['errors'].append(error_msg)
            workflow_result['completed'] = datetime.now().isoformat()
        
        return workflow_result
    
    def _get_agent_sequence(self, workflow_type: str) -> Optional[List[Dict]]:
        """Get the sequence of agents for a workflow type"""
        
        workflows = {
            'analyze_new_content': [
                {'agent': 'analyzer', 'required': True},
                {'agent': 'connector', 'required': False}
            ],
            'update_style_profile': [
                {'agent': 'style-learner', 'required': True}
            ],
            'update_worldview_index': [
                {'agent': 'connector', 'required': True}
            ],
            'integrate_published_content': [
                {'agent': 'analyzer', 'required': True},
                {'agent': 'connector', 'required': False}
            ],
            'generate_weekly_draft': [
                {'agent': 'draftsmith', 'required': True}  # Simplified for desktop workflow
            ]
        }
        
        return workflows.get(workflow_type)
    
    def _prepare_agent_context(self, agent_config: Dict, base_context: Dict, workflow_result: Dict) -> Dict:
        """Prepare context specific to an agent"""
        
        # Start with base context
        agent_context = base_context.copy()
        
        # Add workflow information
        agent_context.update({
            'workflow_type': workflow_result['workflow_type'],
            'workflow_started': workflow_result['started'],
            'previous_agents': workflow_result['agents_executed']
        })
        
        # Add agent-specific context
        agent_name = agent_config['agent']
        
        if agent_name == 'analyzer':
            agent_context.update(self._get_analyzer_context(base_context))
        elif agent_name == 'connector':
            agent_context.update(self._get_connector_context(base_context))
        elif agent_name == 'style-learner':
            agent_context.update(self._get_style_learner_context(base_context))
        elif agent_name == 'draftsmith':
            agent_context.update(self._get_draftsmith_context(base_context))
        
        return agent_context
    
    def _get_analyzer_context(self, context: Dict) -> Dict:
        """Get analyzer-specific context"""
        file_content = ""
        if context.get('file_path'):
            try:
                file_content = Path(context['file_path']).read_text(encoding='utf-8')
            except Exception:
                file_content = "[Error reading file]"
        
        return {
            'file_content': file_content,
            'analysis_mode': 'automated'
        }
    
    def _get_connector_context(self, context: Dict) -> Dict:
        """Get connector-specific context"""
        return {
            'connection_mode': 'automated'
        }
    
    def _get_style_learner_context(self, context: Dict) -> Dict:
        """Get style learner-specific context"""
        file_content = ""
        if context.get('file_path'):
            try:
                file_content = Path(context['file_path']).read_text(encoding='utf-8')
            except Exception:
                file_content = "[Error reading file]"
        
        return {
            'great_writing_content': file_content
        }
    
    def _get_draftsmith_context(self, context: Dict) -> Dict:
        """Get draftsmith-specific context"""
        
        # Get recent files from raw ideas
        recent_files_content = []
        try:
            raw_ideas_path = Path(self.config.vault_path) / "1-raw-ideas"
            for file_path in raw_ideas_path.glob("*.md"):
                if file_path.stat().st_mtime > (time.time() - 7 * 24 * 3600):  # Last 7 days
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        recent_files_content.append(f"## {file_path.name}\n\n{content}\n\n---\n")
                    except Exception:
                        continue
        except Exception:
            pass
        
        # Get style profile
        style_profile = ""
        try:
            style_profile_path = self.config.get_workflow_path('style-profile')
            if style_profile_path.exists():
                style_profile = style_profile_path.read_text(encoding='utf-8')
        except Exception:
            pass
        
        return {
            'recent_files_content': '\n'.join(recent_files_content[:5]),  # Limit to prevent prompt overflow
            'style_profile': style_profile,
            'draft_generation_mode': 'automated'
        }
    
    def _process_agent_output(self, agent_name: str, result: Dict, context: Dict):
        """Process the output from an agent execution"""
        
        self.logger.info(f"Processing output from {agent_name}")
        
        try:
            response_text = result.get('response', '')
            
            if agent_name == 'analyzer':
                self._process_analyzer_output(response_text, context)
            elif agent_name == 'connector':
                self._process_connector_output(response_text, context)
            elif agent_name == 'style-learner':
                self._process_style_learner_output(response_text, context)
            elif agent_name == 'draftsmith':
                self._process_draftsmith_output(response_text, context)
                
        except Exception as e:
            self.logger.error(f"Error processing {agent_name} output: {e}")
    
    def _process_analyzer_output(self, response: str, context: Dict):
        """Process analyzer agent output (extract YAML frontmatter)"""
        
        if not context.get('file_path'):
            return
        
        try:
            import re
            
            # Extract YAML frontmatter from response
            yaml_match = re.search(r'```yaml\n(---\n.*?\n---)\n```', response, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                
                # Read original file
                file_path = Path(context['file_path'])
                original_content = file_path.read_text(encoding='utf-8')
                
                # Add YAML frontmatter if it doesn't exist
                if not original_content.startswith('---\n'):
                    new_content = f"{yaml_content}\n\n{original_content}"
                    file_path.write_text(new_content, encoding='utf-8')
                    self.logger.info(f"Added YAML frontmatter to {file_path.name}")
                
        except Exception as e:
            self.logger.error(f"Error processing analyzer output: {e}")
    
    def _process_connector_output(self, response: str, context: Dict):
        """Process connector agent output (apply wikilinks)"""
        # For now, just log - could implement link insertion logic
        self.logger.info("Connector output processed (manual implementation needed)")
    
    def _process_style_learner_output(self, response: str, context: Dict):
        """Process style learner output (update style profile)"""
        
        try:
            # Look for style profile updates in response
            style_profile_path = self.config.get_workflow_path('style-profile')
            
            # For now, append the analysis to the style profile
            if style_profile_path.exists():
                current_content = style_profile_path.read_text(encoding='utf-8')
                updated_content = f"{current_content}\n\n## Analysis Update - {datetime.now().isoformat()}\n\n{response}\n\n---\n"
                style_profile_path.write_text(updated_content, encoding='utf-8')
                self.logger.info("Updated style profile")
            
        except Exception as e:
            self.logger.error(f"Error processing style learner output: {e}")
    
    def _process_draftsmith_output(self, response: str, context: Dict):
        """Process draftsmith output (save generated draft)"""
        
        try:
            # Save draft to article drafts folder
            drafts_dir = Path(self.config.vault_path) / "3-article-drafts"
            drafts_dir.mkdir(exist_ok=True)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d")
            draft_file = drafts_dir / f"weekly-insights-{timestamp}.md"
            
            draft_file.write_text(response, encoding='utf-8')
            self.logger.info(f"Saved weekly draft to {draft_file}")
            
            # Send completion notification
            try:
                import platform
                system = platform.system()
                
                if system == "Darwin":  # macOS
                    os.system(f'''osascript -e 'display notification "Weekly draft generated and saved to {draft_file.name}!" with title "🎉 Workflow Complete"' ''')
                    os.system(f'open "{draft_file}"')
            except Exception:
                pass
            
        except Exception as e:
            self.logger.error(f"Error processing draftsmith output: {e}")


def main():
    """Test desktop integration"""
    integration = ClaudeDesktopIntegration()
    coordinator = DesktopWorkflowCoordinator()
    
    print("Claude Desktop Integration Test")
    print("Available workflows:", ['analyze_new_content', 'generate_weekly_draft'])
    
    return 0


if __name__ == "__main__":
    exit(main())
