#!/usr/bin/env python3
"""
Claude Integration Module
Handles API communication with Claude for agent execution
"""

import json
import logging
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from config import get_config


class ClaudeAPI:
    """Claude API client for agent communication"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        # Set up headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'x-api-key': self.config.claude_api_key,
            'anthropic-version': '2023-06-01'
        })
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1  # seconds between requests
        
    def execute_agent(self, agent_name: str, context: Dict, max_retries: int = 3) -> Optional[Dict]:
        """Execute an agent with given context"""
        
        try:
            # Load agent prompt template
            agent_prompt = self._load_agent_prompt(agent_name)
            if not agent_prompt:
                self.logger.error(f"Could not load agent prompt: {agent_name}")
                return None
            
            # Prepare the message
            message = self._prepare_message(agent_prompt, context)
            
            # Execute with retries
            for attempt in range(max_retries):
                try:
                    response = self._make_api_call(message)
                    
                    if response:
                        self.logger.info(f"Successfully executed {agent_name} agent")
                        return {
                            'agent': agent_name,
                            'success': True,
                            'response': response,
                            'context': context,
                            'timestamp': datetime.now().isoformat(),
                            'attempt': attempt + 1
                        }
                        
                except Exception as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed for {agent_name}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(self.config.retry_delay * (attempt + 1))  # Exponential backoff
                    
            self.logger.error(f"All attempts failed for {agent_name} agent")
            return {
                'agent': agent_name,
                'success': False,
                'error': 'Max retries exceeded',
                'context': context,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error executing {agent_name} agent: {e}")
            return None
    
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
    
    def _prepare_message(self, agent_prompt: str, context: Dict) -> str:
        """Prepare message with agent prompt and context"""
        
        # Format the prompt with context variables
        try:
            formatted_prompt = agent_prompt.format(**context)
        except KeyError as e:
            self.logger.warning(f"Missing context variable {e}, using original prompt")
            formatted_prompt = agent_prompt
        
        # Add context information
        context_info = f"""
## Execution Context
- Timestamp: {datetime.now().isoformat()}
- Vault Path: {self.config.vault_path}
- Trigger: {context.get('trigger_event', 'unknown')}
- File: {context.get('file_path', 'none')}

## Agent Instructions
{formatted_prompt}

## Current Context Data
{json.dumps(context, indent=2)}
"""
        
        return context_info
    
    def _make_api_call(self, message: str) -> Optional[str]:
        """Make API call to Claude"""
        
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        try:
            # Prepare request payload
            payload = {
                'model': self.config.claude_model,
                'max_tokens': 4000,
                'messages': [
                    {
                        'role': 'user',
                        'content': message
                    }
                ]
            }
            
            # Make the request
            self.logger.debug(f"Making API call to Claude...")
            response = self.session.post(
                self.config.claude_api_url,
                json=payload,
                timeout=self.config.workflow_timeout
            )
            
            self.last_request_time = time.time()
            
            # Check response
            if response.status_code == 200:
                response_data = response.json()
                return response_data['content'][0]['text']
            else:
                self.logger.error(f"API call failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            self.logger.error("API request timed out")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in API call: {e}")
            return None


class AgentCoordinator:
    """Coordinates execution of multiple agents in workflows"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.claude_api = ClaudeAPI()
        
        # Agent execution cache
        self.execution_cache = {}
        self.cache_timeout = 300  # 5 minutes
    
    def execute_workflow(self, workflow_type: str, context: Dict) -> Dict:
        """Execute a complete workflow with multiple agents"""
        
        self.logger.info(f"Executing workflow: {workflow_type}")
        
        workflow_result = {
            'workflow_type': workflow_type,
            'started': datetime.now().isoformat(),
            'context': context,
            'agents_executed': [],
            'success': False,
            'errors': []
        }
        
        try:
            # Determine agent sequence for workflow
            agent_sequence = self._get_agent_sequence(workflow_type)
            
            if not agent_sequence:
                error_msg = f"Unknown workflow type: {workflow_type}"
                self.logger.error(error_msg)
                workflow_result['errors'].append(error_msg)
                return workflow_result
            
            # Execute agents in sequence
            for agent_config in agent_sequence:
                agent_name = agent_config['agent']
                agent_context = self._prepare_agent_context(agent_config, context, workflow_result)
                
                self.logger.info(f"Executing agent: {agent_name}")
                
                # Execute agent
                result = self.claude_api.execute_agent(agent_name, agent_context)
                
                if result and result.get('success'):
                    workflow_result['agents_executed'].append(result)
                    
                    # Process agent output
                    self._process_agent_output(agent_name, result, context)
                    
                else:
                    error_msg = f"Agent {agent_name} failed"
                    self.logger.error(error_msg)
                    workflow_result['errors'].append(error_msg)
                    
                    # Check if this agent is required
                    if agent_config.get('required', True):
                        workflow_result['completed'] = datetime.now().isoformat()
                        return workflow_result
            
            # Mark workflow as successful if we got here
            workflow_result['success'] = True
            workflow_result['completed'] = datetime.now().isoformat()
            
            self.logger.info(f"Workflow {workflow_type} completed successfully")
            
        except Exception as e:
            error_msg = f"Workflow execution error: {e}"
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
                {'agent': 'analyzer', 'required': False},  # Check recent content
                {'agent': 'connector', 'required': False},  # Update connections
                {'agent': 'style-learner', 'required': False},  # Update style if needed
                {'agent': 'draftsmith', 'required': True}  # Generate the draft
            ],
            'system_health_check': [
                {'agent': 'orchestrator', 'required': True}
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
        elif agent_name == 'orchestrator':
            agent_context.update(self._get_orchestrator_context(base_context))
        
        return agent_context
    
    def _get_analyzer_context(self, context: Dict) -> Dict:
        """Get analyzer-specific context"""
        return {
            'file_content': self._read_file_content(context.get('file_path')),
            'training_data_themes': self._get_training_data_themes(),
            'analysis_mode': 'automated'
        }
    
    def _get_connector_context(self, context: Dict) -> Dict:
        """Get connector-specific context"""
        return {
            'recent_files': self._get_recent_files(),
            'existing_connections': self._get_existing_connections(),
            'worldview_content': self._get_worldview_content()
        }
    
    def _get_style_learner_context(self, context: Dict) -> Dict:
        """Get style learner-specific context"""
        return {
            'great_writing_content': self._read_file_content(context.get('file_path')),
            'current_style_profile': self._get_current_style_profile()
        }
    
    def _get_draftsmith_context(self, context: Dict) -> Dict:
        """Get draftsmith-specific context"""
        return {
            'recent_files': self._get_recent_files(days=7),
            'style_profile': self._get_current_style_profile(),
            'connected_insights': self._get_connected_insights(),
            'worldview_matches': self._get_worldview_content()
        }
    
    def _get_orchestrator_context(self, context: Dict) -> Dict:
        """Get orchestrator-specific context"""
        return {
            'system_status': self._get_system_status(),
            'recent_workflows': self._get_recent_workflows(),
            'performance_metrics': self._get_performance_metrics()
        }
    
    def _read_file_content(self, file_path: Optional[str]) -> Optional[str]:
        """Read file content safely"""
        if not file_path:
            return None
            
        try:
            return Path(file_path).read_text(encoding='utf-8')
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def _get_training_data_themes(self) -> List[str]:
        """Get themes from training data"""
        # Implementation would scan training data directory
        return ['placeholder_theme']
    
    def _get_recent_files(self, days: int = 7) -> List[str]:
        """Get list of recently modified files"""
        # Implementation would scan for recent files
        return ['placeholder_file.md']
    
    def _get_existing_connections(self) -> List[str]:
        """Get existing wikilink connections"""
        # Implementation would scan for existing links
        return []
    
    def _get_worldview_content(self) -> List[str]:
        """Get worldview content references"""
        # Implementation would scan world-view directory
        return []
    
    def _get_current_style_profile(self) -> Optional[str]:
        """Get current style profile"""
        style_profile_path = self.config.get_workflow_path('style-profile')
        return self._read_file_content(str(style_profile_path))
    
    def _get_connected_insights(self) -> List[str]:
        """Get connected insights from content graph"""
        # Implementation would analyze content connections
        return []
    
    def _get_system_status(self) -> Dict:
        """Get current system status"""
        return {'status': 'operational'}
    
    def _get_recent_workflows(self) -> List[Dict]:
        """Get recent workflow executions"""
        return []
    
    def _get_performance_metrics(self) -> Dict:
        """Get system performance metrics"""
        return {}
    
    def _process_agent_output(self, agent_name: str, result: Dict, context: Dict):
        """Process the output from an agent execution"""
        
        self.logger.debug(f"Processing output from {agent_name}")
        
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
        # Implementation would parse YAML and update file
        pass
    
    def _process_connector_output(self, response: str, context: Dict):
        """Process connector agent output (apply wikilinks)"""
        # Implementation would parse link recommendations and apply them
        pass
    
    def _process_style_learner_output(self, response: str, context: Dict):
        """Process style learner output (update style profile)"""
        # Implementation would update style profile file
        pass
    
    def _process_draftsmith_output(self, response: str, context: Dict):
        """Process draftsmith output (save generated draft)"""
        # Implementation would save draft to appropriate location
        pass