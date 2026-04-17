"""
Prompt Templates System for Voice Notes.
Manages loading, categorizing, and templating conversation prompts.
"""

import yaml
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from string import Template

logger = logging.getLogger(__name__)


class PromptTemplateManager:
    """
    Manages prompt templates with categorization, variables, and easy modification.
    Extends the basic YAML loading with advanced templating features.
    """

    def __init__(self, config_path: str = "config/prompts.yaml"):
        """Initialize with prompt configuration path."""
        self.config_path = Path(config_path)
        self.prompts = {}
        self.templates = {}
        self.load_prompts()

    def load_prompts(self) -> None:
        """Load and process prompts from YAML configuration."""
        try:
            with open(self.config_path, 'r') as file:
                raw_data = yaml.safe_load(file)
                self.prompts = raw_data or {}
                self._process_templates()
                logger.info(f"Loaded prompts from {self.config_path}")
        except FileNotFoundError:
            logger.error(f"Prompts configuration file not found: {self.config_path}")
            self.prompts = {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing prompts YAML: {e}")
            self.prompts = {}

    def _process_templates(self) -> None:
        """Process loaded prompts to create template objects."""
        self.templates = {}

        # Process conversation styles
        conversation_styles = self.prompts.get("conversation_styles", {})
        for topic_type, style_data in conversation_styles.items():
            self.templates[f"conversation_{topic_type}"] = {
                "initial_prompt": Template(style_data.get("initial_prompt", "")),
                "follow_up_prompts": [
                    Template(prompt) for prompt in style_data.get("follow_up_prompts", [])
                ]
            }

        # Process output generation templates
        output_generation = self.prompts.get("output_generation", {})
        for template_name, template_text in output_generation.items():
            self.templates[f"output_{template_name}"] = Template(template_text)

        # Process other template sections
        for section_name in ["topic_analysis", "closing_prompts"]:
            section_data = self.prompts.get(section_name)
            if isinstance(section_data, str):
                self.templates[section_name] = Template(section_data)
            elif isinstance(section_data, dict):
                self.templates[section_name] = {
                    key: Template(value) for key, value in section_data.items()
                }

        logger.debug(f"Processed {len(self.templates)} template groups")

    def get_prompts_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get prompts categorized by topic type or functional category.

        Args:
            category: Category name (e.g., 'struggles', 'wins', 'reflection', 'conversation', 'output')

        Returns:
            Dictionary of prompts for the specified category
        """
        # Map common categories to our topic types
        category_mapping = {
            "struggles": "struggle",
            "wins": "win",
            "metrics": "update",  # Metrics often relate to progress updates
            "reflection": "reflection",
            "planning": "planning",
            "ideas": "idea",
            "updates": "update"
        }

        # If it's a direct topic type, use it; otherwise check mapping
        topic_type = category_mapping.get(category.lower(), category.lower())

        # Return conversation style prompts for topic types
        if topic_type in ["struggle", "win", "reflection", "planning", "idea", "update", "other"]:
            conversation_styles = self.prompts.get("conversation_styles", {})
            return conversation_styles.get(topic_type, {})

        # Handle functional categories
        if category.lower() == "conversation":
            return self.prompts.get("conversation_styles", {})
        elif category.lower() == "output":
            return self.prompts.get("output_generation", {})
        elif category.lower() == "analysis":
            return {"topic_analysis": self.prompts.get("topic_analysis", "")}
        elif category.lower() == "closing":
            return self.prompts.get("closing_prompts", {})
        elif category.lower() == "flow":
            return self.prompts.get("conversation_flow", {})
        else:
            logger.warning(f"Unknown category: {category}")
            return {}

    def list_available_categories(self) -> List[str]:
        """
        List all available prompt categories.

        Returns:
            List of category names
        """
        categories = []

        # Add topic-based categories
        conversation_styles = self.prompts.get("conversation_styles", {})
        categories.extend(conversation_styles.keys())

        # Add functional categories
        functional_categories = ["conversation", "output", "analysis", "closing", "flow"]
        categories.extend(functional_categories)

        # Add mapped categories
        mapped_categories = ["struggles", "wins", "metrics", "updates", "ideas"]
        categories.extend(mapped_categories)

        return sorted(list(set(categories)))

    def get_topic_specific_prompts(self, topic_type: str) -> Dict[str, Any]:
        """
        Get all prompts specific to a topic type.

        Args:
            topic_type: The topic type (struggle, win, reflection, etc.)

        Returns:
            Dictionary containing initial_prompt and follow_up_prompts
        """
        return self.get_prompts_by_category(topic_type)

    def render_template(self, template_name: str, variables: Dict[str, Any] = None) -> str:
        """
        Render a template with provided variables.

        Args:
            template_name: Name of the template to render
            variables: Dictionary of variables to substitute

        Returns:
            Rendered template string
        """
        if variables is None:
            variables = {}

        template = self.templates.get(template_name)
        if not template:
            logger.warning(f"Template not found: {template_name}")
            return ""

        try:
            if isinstance(template, Template):
                return template.safe_substitute(**variables)
            elif isinstance(template, dict):
                rendered = {}
                for key, tmpl in template.items():
                    if isinstance(tmpl, Template):
                        rendered[key] = tmpl.safe_substitute(**variables)
                    else:
                        rendered[key] = str(tmpl)
                return rendered
            else:
                return str(template)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            return str(template) if isinstance(template, str) else ""

    def render_conversation_prompt(self, topic_type: str, variables: Dict[str, Any] = None,
                                 prompt_type: str = "initial") -> str:
        """
        Render a conversation prompt for a specific topic type.

        Args:
            topic_type: The topic type (struggle, win, etc.)
            variables: Variables to substitute in the template
            prompt_type: Type of prompt ("initial" or "follow_up")

        Returns:
            Rendered prompt string
        """
        template_name = f"conversation_{topic_type}"
        templates = self.templates.get(template_name, {})

        if prompt_type == "initial":
            template = templates.get("initial_prompt")
            if isinstance(template, Template):
                return template.safe_substitute(**(variables or {}))
            return str(template) if template else ""

        elif prompt_type == "follow_up":
            follow_up_templates = templates.get("follow_up_prompts", [])
            if not follow_up_templates:
                return ""

            # Return all follow-up prompts rendered
            rendered_prompts = []
            for template in follow_up_templates:
                if isinstance(template, Template):
                    rendered_prompts.append(template.safe_substitute(**(variables or {})))
                else:
                    rendered_prompts.append(str(template))
            return rendered_prompts

        else:
            logger.warning(f"Unknown prompt type: {prompt_type}")
            return ""

    def get_template_variables(self, template_name: str) -> List[str]:
        """
        Extract variable names from a template.

        Args:
            template_name: Name of the template to analyze

        Returns:
            List of variable names found in the template
        """
        template = self.templates.get(template_name)
        if not template:
            return []

        variables = set()

        def extract_vars(tmpl):
            if isinstance(tmpl, Template):
                # Extract variables from template pattern
                pattern = r'\$\{?(\w+)\}?'
                matches = re.findall(pattern, tmpl.template)
                variables.update(matches)
            elif isinstance(tmpl, dict):
                for value in tmpl.values():
                    extract_vars(value)
            elif isinstance(tmpl, list):
                for item in tmpl:
                    extract_vars(item)

        extract_vars(template)
        return sorted(list(variables))

    def validate_template_variables(self, template_name: str, variables: Dict[str, Any]) -> List[str]:
        """
        Validate that all required template variables are provided.

        Args:
            template_name: Name of the template to validate
            variables: Variables dictionary to check

        Returns:
            List of missing variable names
        """
        required_vars = self.get_template_variables(template_name)
        provided_vars = set(variables.keys()) if variables else set()
        missing_vars = set(required_vars) - provided_vars
        return sorted(list(missing_vars))

    def include_template_file(self, template_file_path: str) -> bool:
        """
        Include prompts from an additional template file.

        Args:
            template_file_path: Path to additional YAML template file

        Returns:
            True if successfully included, False otherwise
        """
        try:
            template_path = Path(template_file_path)
            if not template_path.exists():
                logger.error(f"Template file not found: {template_file_path}")
                return False

            with open(template_path, 'r') as file:
                additional_prompts = yaml.safe_load(file)

            if not additional_prompts:
                logger.warning(f"No prompts found in: {template_file_path}")
                return False

            # Merge with existing prompts
            self._merge_prompts(additional_prompts)
            self._process_templates()  # Reprocess to include new templates

            logger.info(f"Successfully included templates from: {template_file_path}")
            return True

        except Exception as e:
            logger.error(f"Error including template file {template_file_path}: {e}")
            return False

    def _merge_prompts(self, additional_prompts: Dict[str, Any]) -> None:
        """
        Merge additional prompts with existing ones.

        Args:
            additional_prompts: Dictionary of additional prompts to merge
        """
        for section, content in additional_prompts.items():
            if section in self.prompts:
                if isinstance(self.prompts[section], dict) and isinstance(content, dict):
                    # Merge dictionaries (e.g., conversation_styles)
                    self.prompts[section].update(content)
                elif isinstance(self.prompts[section], list) and isinstance(content, list):
                    # Extend lists
                    self.prompts[section].extend(content)
                else:
                    # Replace with new content
                    self.prompts[section] = content
            else:
                # Add new section
                self.prompts[section] = content

    def get_existing_templates(self) -> Dict[str, Any]:
        """
        Get all currently loaded templates and their structure.

        Returns:
            Dictionary containing all template information
        """
        template_info = {}

        for template_name, template in self.templates.items():
            info = {
                "type": type(template).__name__,
                "variables": self.get_template_variables(template_name)
            }

            if isinstance(template, dict):
                info["keys"] = list(template.keys())
            elif isinstance(template, list):
                info["count"] = len(template)

            template_info[template_name] = info

        return template_info

    def export_templates(self, output_path: str) -> bool:
        """
        Export current templates to a YAML file.

        Args:
            output_path: Path where to save the exported templates

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert templates back to exportable format
            exportable = {}

            # Export conversation styles
            conversation_styles = {}
            for template_name, template in self.templates.items():
                if template_name.startswith("conversation_"):
                    topic_type = template_name.replace("conversation_", "")
                    if isinstance(template, dict):
                        style_data = {}
                        if "initial_prompt" in template:
                            style_data["initial_prompt"] = template["initial_prompt"].template
                        if "follow_up_prompts" in template:
                            style_data["follow_up_prompts"] = [
                                t.template for t in template["follow_up_prompts"]
                            ]
                        conversation_styles[topic_type] = style_data

            if conversation_styles:
                exportable["conversation_styles"] = conversation_styles

            # Export other templates
            for template_name, template in self.templates.items():
                if not template_name.startswith("conversation_"):
                    if isinstance(template, Template):
                        exportable[template_name] = template.template
                    elif isinstance(template, dict):
                        exportable[template_name] = {
                            k: (v.template if isinstance(v, Template) else v)
                            for k, v in template.items()
                        }

            # Add non-template sections from original prompts
            for section in ["conversation_flow", "depth_triggers"]:
                if section in self.prompts:
                    exportable[section] = self.prompts[section]

            with open(output_path, 'w') as file:
                yaml.dump(exportable, file, default_flow_style=False, sort_keys=True)

            logger.info(f"Templates exported to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting templates: {e}")
            return False

    def add_conversation_style(self, topic_type: str, initial_prompt: str,
                             follow_up_prompts: List[str]) -> bool:
        """
        Add or update a conversation style for a topic type.

        Args:
            topic_type: The topic type name
            initial_prompt: Initial conversation prompt
            follow_up_prompts: List of follow-up prompts

        Returns:
            True if successful, False otherwise
        """
        try:
            # Add to prompts structure
            if "conversation_styles" not in self.prompts:
                self.prompts["conversation_styles"] = {}

            self.prompts["conversation_styles"][topic_type] = {
                "initial_prompt": initial_prompt,
                "follow_up_prompts": follow_up_prompts
            }

            # Reprocess templates to include the new style
            self._process_templates()

            logger.info(f"Added conversation style for topic: {topic_type}")
            return True

        except Exception as e:
            logger.error(f"Error adding conversation style for {topic_type}: {e}")
            return False

    def update_prompt(self, section: str, key: str, value: Any) -> bool:
        """
        Update a specific prompt in a section.

        Args:
            section: Section name (e.g., 'conversation_styles', 'output_generation')
            key: Key within the section
            value: New value for the prompt

        Returns:
            True if successful, False otherwise
        """
        try:
            if section not in self.prompts:
                self.prompts[section] = {}

            if isinstance(self.prompts[section], dict):
                self.prompts[section][key] = value
            else:
                logger.error(f"Cannot update key in non-dict section: {section}")
                return False

            # Reprocess templates
            self._process_templates()

            logger.info(f"Updated prompt: {section}.{key}")
            return True

        except Exception as e:
            logger.error(f"Error updating prompt {section}.{key}: {e}")
            return False

    def add_follow_up_prompt(self, topic_type: str, new_prompt: str) -> bool:
        """
        Add a new follow-up prompt to an existing topic type.

        Args:
            topic_type: The topic type to add to
            new_prompt: The new follow-up prompt to add

        Returns:
            True if successful, False otherwise
        """
        try:
            conversation_styles = self.prompts.get("conversation_styles", {})

            if topic_type not in conversation_styles:
                logger.error(f"Topic type not found: {topic_type}")
                return False

            if "follow_up_prompts" not in conversation_styles[topic_type]:
                conversation_styles[topic_type]["follow_up_prompts"] = []

            conversation_styles[topic_type]["follow_up_prompts"].append(new_prompt)

            # Reprocess templates
            self._process_templates()

            logger.info(f"Added follow-up prompt to {topic_type}")
            return True

        except Exception as e:
            logger.error(f"Error adding follow-up prompt to {topic_type}: {e}")
            return False

    def remove_prompt(self, section: str, key: str) -> bool:
        """
        Remove a prompt from a section.

        Args:
            section: Section name
            key: Key to remove

        Returns:
            True if successful, False otherwise
        """
        try:
            if section not in self.prompts:
                logger.error(f"Section not found: {section}")
                return False

            if isinstance(self.prompts[section], dict) and key in self.prompts[section]:
                del self.prompts[section][key]

                # Reprocess templates
                self._process_templates()

                logger.info(f"Removed prompt: {section}.{key}")
                return True
            else:
                logger.error(f"Key not found: {section}.{key}")
                return False

        except Exception as e:
            logger.error(f"Error removing prompt {section}.{key}: {e}")
            return False

    def save_changes(self, backup: bool = True) -> bool:
        """
        Save current prompts back to the configuration file.

        Args:
            backup: Whether to create a backup of the original file

        Returns:
            True if successful, False otherwise
        """
        try:
            if backup:
                backup_path = self.config_path.with_suffix('.yaml.backup')
                if self.config_path.exists():
                    import shutil
                    shutil.copy2(self.config_path, backup_path)
                    logger.info(f"Created backup: {backup_path}")

            with open(self.config_path, 'w') as file:
                yaml.dump(self.prompts, file, default_flow_style=False, sort_keys=True)

            logger.info(f"Saved changes to: {self.config_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving changes: {e}")
            return False

    def create_prompt_template(self, name: str, template_text: str,
                             section: str = "custom_templates") -> bool:
        """
        Create a new custom prompt template.

        Args:
            name: Name for the new template
            template_text: Template text with variable placeholders
            section: Section to add the template to

        Returns:
            True if successful, False otherwise
        """
        try:
            if section not in self.prompts:
                self.prompts[section] = {}

            self.prompts[section][name] = template_text

            # Reprocess templates
            self._process_templates()

            logger.info(f"Created template: {section}.{name}")
            return True

        except Exception as e:
            logger.error(f"Error creating template {name}: {e}")
            return False

    def reload_prompts(self) -> bool:
        """
        Reload prompts from the configuration file.

        Returns:
            True if successful, False otherwise
        """
        try:
            self.load_prompts()
            logger.info("Prompts reloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error reloading prompts: {e}")
            return False