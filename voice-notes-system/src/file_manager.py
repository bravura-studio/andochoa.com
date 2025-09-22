"""
File Manager for Voice Notes System.
Handles saving formatted notes to Obsidian vault with proper naming and directory structure.
"""

import os
import re
import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass

try:
    from .markdown_formatter import MarkdownFormatter, ConversationMetadata
except ImportError:
    # Handle case when module is run directly (not as package)
    from markdown_formatter import MarkdownFormatter, ConversationMetadata

logger = logging.getLogger(__name__)


@dataclass
class SaveResult:
    """Result of saving a voice note file."""
    success: bool
    file_path: Optional[str] = None
    error: Optional[str] = None
    conflict_resolved: bool = False
    cleanup_performed: bool = False


class FileManager:
    """
    Manages file system operations for voice notes.
    Handles saving to Obsidian vault with proper naming and directory structure.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the file manager with configuration.

        Args:
            config: Configuration dictionary containing file settings
        """
        self.config = config
        self.file_config = config.get('files', {})
        self.markdown_formatter = MarkdownFormatter()

        # Get output directory and expand user path
        output_dir = self.file_config.get('output_directory', '~/Documents/Voice Notes')
        self.output_directory = Path(output_dir).expanduser()

        # Ensure output directory exists
        self.output_directory.mkdir(parents=True, exist_ok=True)

        # Get configuration settings
        self.naming_pattern = self.file_config.get('naming_pattern', 'hybrid')
        self.daily_folders = self.file_config.get('daily_folders', True)
        self.cleanup_temp_files = self.file_config.get('cleanup_temp_files', True)

        logger.info(f"FileManager initialized with output directory: {self.output_directory}")

    def create_hybrid_filename(self, title: str, metadata: ConversationMetadata) -> str:
        """
        Create hybrid filename combining date and topic.

        Args:
            title: Generated title for the conversation
            metadata: Conversation metadata with creation time

        Returns:
            Formatted filename with .md extension
        """
        # Format date part
        date_str = metadata.created_at.strftime("%Y-%m-%d")

        # Clean title for filename
        clean_title = self._clean_title_for_filename(title)

        # Determine naming pattern
        if self.naming_pattern == "date":
            filename = f"{date_str}.md"
        elif self.naming_pattern == "topic":
            filename = f"{clean_title}.md"
        else:  # hybrid (default)
            filename = f"{date_str}_{clean_title}.md"

        logger.debug(f"Generated filename: {filename}")
        return filename

    def _clean_title_for_filename(self, title: str) -> str:
        """Clean title text for use in filename."""
        # Remove topic type prefix if present (e.g., "Struggle: " -> "")
        title = re.sub(r'^[^:]+:\s*', '', title)

        # Replace invalid filename characters with spaces first
        clean_title = re.sub(r'[<>:"/\\|?*]', ' ', title)

        # Replace spaces and multiple dashes with single dashes
        clean_title = re.sub(r'[\s\-]+', '-', clean_title)

        # Remove leading/trailing dashes
        clean_title = clean_title.strip('-')

        # Limit length to avoid filesystem issues
        if len(clean_title) > 50:
            clean_title = clean_title[:50].rstrip('-')

        # Ensure we have something if title was completely cleaned away
        if not clean_title:
            clean_title = "voice-note"

        return clean_title

    def get_save_directory(self, metadata: ConversationMetadata) -> Path:
        """
        Determine the correct directory for saving the file.

        Args:
            metadata: Conversation metadata with creation time

        Returns:
            Path to the directory where file should be saved
        """
        base_dir = self.output_directory

        if self.daily_folders:
            # Create daily subfolder: YYYY/MM/DD or YYYY-MM-DD format
            date_folder = metadata.created_at.strftime("%Y-%m-%d")
            save_dir = base_dir / date_folder
        else:
            save_dir = base_dir

        # Ensure directory exists
        save_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Save directory: {save_dir}")
        return save_dir

    def handle_file_conflicts(self, file_path: Path) -> Tuple[Path, bool]:
        """
        Handle file conflicts by generating unique filename.

        Args:
            file_path: Original file path that may conflict

        Returns:
            Tuple of (final_file_path, conflict_was_resolved)
        """
        if not file_path.exists():
            return file_path, False

        # File exists, need to resolve conflict
        logger.info(f"File conflict detected: {file_path}")

        stem = file_path.stem
        suffix = file_path.suffix
        parent = file_path.parent

        counter = 1
        while True:
            new_name = f"{stem}_{counter:02d}{suffix}"
            new_path = parent / new_name

            if not new_path.exists():
                logger.info(f"Conflict resolved with filename: {new_name}")
                return new_path, True

            counter += 1

            # Safety valve to prevent infinite loop
            if counter > 999:
                # Use timestamp as last resort
                timestamp = datetime.now().strftime("%H%M%S")
                final_name = f"{stem}_{timestamp}{suffix}"
                final_path = parent / final_name
                logger.warning(f"Using timestamp fallback: {final_name}")
                return final_path, True

    def cleanup_temporary_files(self, temp_files: List[str]) -> bool:
        """
        Clean up temporary audio files.

        Args:
            temp_files: List of temporary file paths to clean up

        Returns:
            True if cleanup was successful, False otherwise
        """
        if not self.cleanup_temp_files:
            logger.debug("Temporary file cleanup disabled in config")
            return False

        cleanup_count = 0
        failed_cleanup = []

        for temp_file_path in temp_files:
            try:
                temp_path = Path(temp_file_path)
                if temp_path.exists() and temp_path.is_file():
                    temp_path.unlink()
                    cleanup_count += 1
                    logger.debug(f"Cleaned up temporary file: {temp_file_path}")
                else:
                    logger.debug(f"Temporary file not found: {temp_file_path}")
            except Exception as e:
                logger.error(f"Failed to cleanup temporary file {temp_file_path}: {e}")
                failed_cleanup.append(temp_file_path)

        if failed_cleanup:
            logger.warning(f"Failed to cleanup {len(failed_cleanup)} temporary files")
            return False

        if cleanup_count > 0:
            logger.info(f"Successfully cleaned up {cleanup_count} temporary files")

        return True

    def save_voice_note(self, conversation_data: Dict[str, Any],
                       metadata: ConversationMetadata,
                       temp_files: List[str] = None) -> SaveResult:
        """
        Save formatted voice note to the Obsidian vault.

        Args:
            conversation_data: Dictionary containing conversation history and context
            metadata: Conversation metadata
            temp_files: List of temporary files to clean up after saving

        Returns:
            SaveResult with details about the save operation
        """
        if temp_files is None:
            temp_files = []

        try:
            # Create complete markdown document
            existing_notes = self._scan_existing_notes()
            markdown_content = self.markdown_formatter.create_complete_document(
                conversation_data, metadata, include_timestamps=False, existing_notes=existing_notes
            )

            # Extract title from the frontmatter for filename generation
            title = self._extract_title_from_markdown(markdown_content)

            # Generate filename
            filename = self.create_hybrid_filename(title, metadata)

            # Determine save directory
            save_directory = self.get_save_directory(metadata)

            # Create full file path
            file_path = save_directory / filename

            # Handle potential conflicts
            final_file_path, conflict_resolved = self.handle_file_conflicts(file_path)

            # Save the file
            with open(final_file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            # Clean up temporary files
            cleanup_performed = self.cleanup_temporary_files(temp_files)

            logger.info(f"Voice note saved successfully: {final_file_path}")

            return SaveResult(
                success=True,
                file_path=str(final_file_path),
                conflict_resolved=conflict_resolved,
                cleanup_performed=cleanup_performed
            )

        except Exception as e:
            logger.error(f"Failed to save voice note: {e}")
            return SaveResult(
                success=False,
                error=str(e)
            )

    def _extract_title_from_markdown(self, markdown_content: str) -> str:
        """Extract title from markdown frontmatter."""
        try:
            # Split frontmatter from content
            parts = markdown_content.split('---', 2)
            if len(parts) >= 2:
                frontmatter_text = parts[1].strip()
                frontmatter_data = yaml.safe_load(frontmatter_text)
                return frontmatter_data.get('title', 'Voice Note')
        except Exception as e:
            logger.debug(f"Could not extract title from frontmatter: {e}")

        return 'Voice Note'

    def _scan_existing_notes(self) -> List[str]:
        """
        Scan the output directory for existing note titles.

        Returns:
            List of existing note titles (without .md extension)
        """
        existing_notes = []

        try:
            # Walk through all subdirectories
            for md_file in self.output_directory.rglob("*.md"):
                # Extract title from filename (remove date prefix if hybrid naming)
                stem = md_file.stem

                # Try to extract title from frontmatter first
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    title = self._extract_title_from_markdown(content)
                    if title and title != 'Voice Note':
                        existing_notes.append(title)
                        continue
                except Exception:
                    pass

                # Fallback to filename-based title extraction
                if self.naming_pattern == "hybrid":
                    # Remove date prefix: YYYY-MM-DD_title -> title
                    title_match = re.match(r'\d{4}-\d{2}-\d{2}_(.+)', stem)
                    if title_match:
                        title = title_match.group(1).replace('-', ' ').title()
                        existing_notes.append(title)
                elif self.naming_pattern == "topic":
                    title = stem.replace('-', ' ').title()
                    existing_notes.append(title)
                # For date-only naming, we can't extract meaningful titles

        except Exception as e:
            logger.error(f"Error scanning existing notes: {e}")

        logger.debug(f"Found {len(existing_notes)} existing notes")
        return existing_notes

    def get_vault_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the voice notes vault.

        Returns:
            Dictionary with vault statistics
        """
        stats = {
            'total_notes': 0,
            'total_size_mb': 0.0,
            'oldest_note': None,
            'newest_note': None,
            'notes_by_month': {},
            'average_note_size_kb': 0.0
        }

        try:
            md_files = list(self.output_directory.rglob("*.md"))
            stats['total_notes'] = len(md_files)

            if not md_files:
                return stats

            total_size_bytes = 0
            oldest_time = None
            newest_time = None

            for md_file in md_files:
                # File size
                file_size = md_file.stat().st_size
                total_size_bytes += file_size

                # File timestamps
                modified_time = datetime.fromtimestamp(md_file.stat().st_mtime)

                if oldest_time is None or modified_time < oldest_time:
                    oldest_time = modified_time
                    stats['oldest_note'] = str(md_file.name)

                if newest_time is None or modified_time > newest_time:
                    newest_time = modified_time
                    stats['newest_note'] = str(md_file.name)

                # Monthly counts
                month_key = modified_time.strftime("%Y-%m")
                stats['notes_by_month'][month_key] = stats['notes_by_month'].get(month_key, 0) + 1

            # Calculate sizes
            stats['total_size_mb'] = round(total_size_bytes / (1024 * 1024), 2)
            stats['average_note_size_kb'] = round((total_size_bytes / len(md_files)) / 1024, 2)

        except Exception as e:
            logger.error(f"Error calculating vault statistics: {e}")

        return stats