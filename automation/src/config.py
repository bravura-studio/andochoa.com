#!/usr/bin/env python3
"""
Configuration Management for Vault Automation System
Handles environment variables, settings, and system configuration
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv


class Config:
    """Configuration management class"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration"""
        
        # Load environment variables
        if config_file:
            load_dotenv(config_file)
        else:
            # Look for .env in automation directory
            automation_dir = Path(__file__).parent.parent
            env_file = automation_dir / '.env'
            if env_file.exists():
                load_dotenv(env_file)
        
        # Set up paths
        self.automation_dir = Path(__file__).parent.parent
        self.vault_path = self._get_vault_path()
        
        # Claude API Configuration
        self.claude_api_key = os.getenv('CLAUDE_API_KEY')
        self.claude_model = os.getenv('CLAUDE_MODEL', 'claude-3-sonnet-20241022')
        self.claude_api_url = os.getenv('CLAUDE_API_URL', 'https://api.anthropic.com/v1/messages')
        
        # Monitoring Configuration
        self.monitor_paths = self._parse_monitor_paths()
        self.auto_analysis = os.getenv('AUTO_ANALYSIS', 'true').lower() == 'true'
        self.background_processing = os.getenv('BACKGROUND_PROCESSING', 'true').lower() == 'true'
        
        # Workflow Configuration
        self.weekly_draft_day = os.getenv('WEEKLY_DRAFT_DAY', 'friday').lower()
        self.weekly_draft_time = os.getenv('WEEKLY_DRAFT_TIME', '14:00')
        self.max_concurrent_workflows = int(os.getenv('MAX_CONCURRENT_WORKFLOWS', '1'))
        self.workflow_timeout = int(os.getenv('WORKFLOW_TIMEOUT', '600'))  # seconds
        
        # Performance Configuration
        self.debounce_time = int(os.getenv('DEBOUNCE_TIME', '2'))  # seconds
        self.retry_attempts = int(os.getenv('RETRY_ATTEMPTS', '3'))
        self.retry_delay = int(os.getenv('RETRY_DELAY', '5'))  # seconds
        
        # Logging Configuration
        self.log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
        self.log_file = os.getenv('LOG_FILE', 'automation.log')
        self.log_max_size = int(os.getenv('LOG_MAX_SIZE', '10485760'))  # 10MB
        self.log_backup_count = int(os.getenv('LOG_BACKUP_COUNT', '5'))
        
        # Agent Paths (relative to vault)
        self.agents_dir = 'agents'
        self.workflows_dir = 'workflows'
        self.training_data_dir = 'training-data'
        
        # State Management
        self.state_dir = self.automation_dir / 'state'
        self.logs_dir = self.automation_dir / 'logs'
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Validate configuration
        self._validate_config()
    
    def _get_vault_path(self) -> str:
        """Get and validate vault path"""
        vault_path = os.getenv('VAULT_PATH')
        
        if not vault_path:
            # Try to auto-detect based on common locations
            possible_paths = [
                Path.home() / 'Documents' / 'Obsidian' / 'Content Bank',
                Path.home() / 'Obsidian' / 'Content Bank',  
                Path(__file__).parent.parent.parent  # Assume automation is in vault
            ]
            
            for path in possible_paths:
                if path.exists() and (path / 'agents').exists():
                    vault_path = str(path)
                    break
        
        if not vault_path or not Path(vault_path).exists():
            raise ValueError(f"Vault path not found or invalid: {vault_path}")
            
        return vault_path
    
    def _parse_monitor_paths(self) -> List[str]:
        """Parse comma-separated monitor paths"""
        paths_str = os.getenv('MONITOR_PATHS', '1-raw-ideas,training-data,4-published-content')
        return [path.strip() for path in paths_str.split(',') if path.strip()]
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            self.state_dir,
            self.logs_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _validate_config(self):
        """Validate configuration values"""
        errors = []
        
        # Check Claude API key
        if not self.claude_api_key:
            errors.append("CLAUDE_API_KEY not set in environment")
        
        # Check vault path and structure
        vault = Path(self.vault_path)
        if not vault.exists():
            errors.append(f"Vault path does not exist: {self.vault_path}")
        else:
            # Check for required directories
            required_dirs = ['agents', 'workflows']
            for req_dir in required_dirs:
                if not (vault / req_dir).exists():
                    errors.append(f"Required vault directory missing: {req_dir}")
        
        # Check monitor paths
        for monitor_path in self.monitor_paths:
            full_path = Path(self.vault_path) / monitor_path
            if not full_path.exists():
                errors.append(f"Monitor path does not exist: {full_path}")
        
        # Check workflow timing
        if self.weekly_draft_day not in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            errors.append(f"Invalid weekly draft day: {self.weekly_draft_day}")
        
        # Time format validation
        try:
            hour, minute = map(int, self.weekly_draft_time.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError()
        except ValueError:
            errors.append(f"Invalid weekly draft time format: {self.weekly_draft_time}")
        
        # Report errors
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            raise ValueError(error_msg)
    
    def get_agent_path(self, agent_name: str) -> Path:
        """Get full path to agent template"""
        return Path(self.vault_path) / self.agents_dir / f"{agent_name}-agent.md"
    
    def get_workflow_path(self, workflow_name: str) -> Path:
        """Get full path to workflow file"""
        return Path(self.vault_path) / self.workflows_dir / f"{workflow_name}.md"
    
    def get_state_file(self, state_name: str) -> Path:
        """Get full path to state file"""
        return self.state_dir / f"{state_name}.json"
    
    def get_log_file(self) -> Path:
        """Get full path to log file"""
        return self.logs_dir / self.log_file
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return {
            'vault_path': self.vault_path,
            'monitor_paths': self.monitor_paths,
            'auto_analysis': self.auto_analysis,
            'background_processing': self.background_processing,
            'weekly_draft_day': self.weekly_draft_day,
            'weekly_draft_time': self.weekly_draft_time,
            'claude_model': self.claude_model,
            'max_concurrent_workflows': self.max_concurrent_workflows,
            'workflow_timeout': self.workflow_timeout,
            'log_level': logging.getLevelName(self.log_level),
            'log_file': self.log_file
        }
    
    def __str__(self) -> str:
        """String representation of configuration"""
        config_dict = self.to_dict()
        # Hide sensitive information
        config_dict['claude_api_key'] = '*' * 8 if self.claude_api_key else 'NOT_SET'
        
        return f"VaultAutomationConfig(\n" + \
               "\n".join(f"  {key}: {value}" for key, value in config_dict.items()) + \
               "\n)"


# Global configuration instance
_config = None

def get_config(config_file: Optional[str] = None) -> Config:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = Config(config_file)
    return _config


# Configuration validation function
def validate_environment() -> bool:
    """Validate that the environment is properly configured"""
    try:
        config = get_config()
        print("✅ Configuration validation passed")
        print(f"📁 Vault path: {config.vault_path}")
        print(f"👁️ Monitor paths: {', '.join(config.monitor_paths)}")
        print(f"🤖 Claude model: {config.claude_model}")
        print(f"📅 Weekly draft: {config.weekly_draft_day} at {config.weekly_draft_time}")
        return True
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


if __name__ == "__main__":
    # Run configuration validation
    if validate_environment():
        config = get_config()
        print("\n" + str(config))
    else:
        exit(1)