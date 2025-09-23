import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigManager:
    """Manages configuration loading and API key security."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager.

        Args:
            config_dir: Path to configuration directory. Defaults to ./config/
        """
        self.config_dir = config_dir or Path(__file__).parent.parent / "config"
        self.config_file = self.config_dir / "config.yaml"
        self.prompts_file = self.config_dir / "prompts.yaml"
        self.env_file = Path(__file__).parent.parent / ".env"

        # Load environment variables
        load_dotenv(self.env_file)

        # Load configurations
        self._config = self._load_yaml_config(self.config_file)
        self._prompts = self._load_yaml_config(self.prompts_file)

    @property
    def config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary."""
        return self._config

    @property
    def prompts(self) -> Dict[str, Any]:
        """Get the prompts configuration dictionary."""
        return self._prompts

    def _load_yaml_config(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML configuration file.

        Args:
            file_path: Path to YAML file

        Returns:
            Configuration dictionary
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            print(f"Warning: Configuration file {file_path} not found")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file {file_path}: {e}")
            return {}

    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI API configuration with secure key handling.

        Returns:
            OpenAI configuration dictionary
        """
        openai_config = self._config.get('api', {}).get('openai', {}).copy()

        # Get API key from environment variable first, then config file
        api_key = os.getenv('OPENAI_API_KEY') or openai_config.get('api_key', '')

        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Please set OPENAI_API_KEY environment "
                "variable or add it to config/config.yaml"
            )

        openai_config['api_key'] = api_key
        return openai_config

    def get_mcp_config(self) -> Dict[str, Any]:
        """Get MCP server configuration.

        Returns:
            MCP configuration dictionary
        """
        mcp_config = self._config.get('mcp', {}).copy()

        # Get MCP settings from environment variables or config
        mcp_config['server_url'] = (
            os.getenv('MCP_SERVER_URL') or
            mcp_config.get('server_url', '')
        )
        mcp_config['api_key'] = (
            os.getenv('MCP_API_KEY') or
            mcp_config.get('api_key', '')
        )

        return mcp_config

    def get_audio_config(self) -> Dict[str, Any]:
        """Get audio recording configuration.

        Returns:
            Audio configuration dictionary
        """
        return self._config.get('audio', {})

    def get_hotkeys_config(self) -> Dict[str, Any]:
        """Get global hotkeys configuration.

        Returns:
            Hotkeys configuration dictionary
        """
        return self._config.get('hotkeys', {})

    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing options configuration.

        Returns:
            Processing configuration dictionary
        """
        return self._config.get('processing', {})

    def get_files_config(self) -> Dict[str, Any]:
        """Get file management configuration.

        Returns:
            Files configuration dictionary
        """
        files_config = self._config.get('files', {}).copy()

        # Expand user directory if needed
        output_dir = files_config.get('output_directory', '~/Documents/Voice Notes')
        if output_dir.startswith('~/'):
            files_config['output_directory'] = str(Path(output_dir).expanduser())

        # Override with environment variable if set
        env_output_dir = os.getenv('VOICE_NOTES_OUTPUT_DIR')
        if env_output_dir:
            files_config['output_directory'] = env_output_dir

        return files_config

    def get_ui_config(self) -> Dict[str, Any]:
        """Get UI settings configuration.

        Returns:
            UI configuration dictionary
        """
        return self._config.get('ui', {})

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration.

        Returns:
            Logging configuration dictionary
        """
        logging_config = self._config.get('logging', {}).copy()

        # Override log level with environment variable if set
        env_log_level = os.getenv('LOG_LEVEL')
        if env_log_level:
            logging_config['level'] = env_log_level

        return logging_config

    def get_privacy_config(self) -> Dict[str, Any]:
        """Get privacy and security configuration.

        Returns:
            Privacy configuration dictionary
        """
        return self._config.get('privacy', {})

    def get_cost_management_config(self) -> Dict[str, Any]:
        """Get cost management configuration.

        Returns:
            Cost management configuration dictionary
        """
        return self._config.get('cost_management', {})

    def get_prompt(self, prompt_name: str) -> str:
        """Get a conversation prompt template.

        Args:
            prompt_name: Name of the prompt to retrieve

        Returns:
            Prompt template string
        """
        return self._prompts.get(prompt_name, '')

    def get_conversation_style(self, topic_type: str) -> Dict[str, Any]:
        """Get conversation style for a specific topic type.

        Args:
            topic_type: Type of topic (struggle, win, reflection, etc.)

        Returns:
            Conversation style configuration
        """
        styles = self._prompts.get('conversation_styles', {})
        return styles.get(topic_type, styles.get('other', {}))

    def get_all_prompts(self) -> Dict[str, Any]:
        """Get all prompt templates.

        Returns:
            All prompts configuration
        """
        return self._prompts

    def validate_configuration(self) -> Dict[str, bool]:
        """Validate that all required configuration is present.

        Returns:
            Dictionary of validation results
        """
        results = {}

        # Check OpenAI API key
        try:
            self.get_openai_config()
            results['openai_api_key'] = True
        except ValueError:
            results['openai_api_key'] = False

        # Check MCP configuration
        mcp_config = self.get_mcp_config()
        results['mcp_server_url'] = bool(mcp_config.get('server_url'))

        # Check output directory exists or can be created
        files_config = self.get_files_config()
        output_dir = Path(files_config.get('output_directory', ''))
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            results['output_directory'] = True
        except (OSError, PermissionError):
            results['output_directory'] = False

        # Check configuration files exist
        results['config_file'] = self.config_file.exists()
        results['prompts_file'] = self.prompts_file.exists()

        return results

    def create_sample_env_file(self) -> bool:
        """Create a sample .env file if it doesn't exist.

        Returns:
            True if file was created, False if it already exists
        """
        if self.env_file.exists():
            return False

        template_file = self.env_file.parent / ".env.template"
        if template_file.exists():
            # Copy template to .env
            with open(template_file, 'r') as src, open(self.env_file, 'w') as dst:
                dst.write(src.read())
            return True

        return False