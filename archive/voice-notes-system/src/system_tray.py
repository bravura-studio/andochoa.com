"""
System Tray Application for Voice Notes.
Provides visual status indicators and quick access to voice notes functionality.
"""

import os
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import logging

try:
    import pystray
    from pystray import MenuItem, Menu
    from PIL import Image, ImageDraw
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    pystray = None
    MenuItem = None
    Menu = None

logger = logging.getLogger(__name__)


class VoiceNotesSystemTray:
    """
    System tray application for voice notes with status indicators.
    Provides visual feedback and quick access to functionality.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the system tray application.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.ui_config = config.get('ui', {})

        # Status colors from config
        self.status_colors = {
            'ready': self.ui_config.get('ready_color', 'green'),
            'recording': self.ui_config.get('recording_color', 'red'),
            'processing': self.ui_config.get('processing_color', 'yellow'),
            'error': self.ui_config.get('error_color', 'gray')
        }

        # Current state
        self.current_status = 'ready'
        self.recording_start_time = None
        self.is_running = False

        # Callbacks for actions
        self.start_recording_callback = None
        self.stop_recording_callback = None
        self.open_notes_callback = None
        self.quit_callback = None

        # System tray icon
        self.icon = None
        self.icon_thread = None

        # Recent notes cache
        self.recent_notes = []

        if not PYSTRAY_AVAILABLE:
            logger.warning("pystray not available - system tray will not work")

    def set_callbacks(self, start_recording: Callable = None,
                     stop_recording: Callable = None,
                     open_notes: Callable = None,
                     quit_app: Callable = None):
        """Set callback functions for tray actions."""
        self.start_recording_callback = start_recording
        self.stop_recording_callback = stop_recording
        self.open_notes_callback = open_notes
        self.quit_callback = quit_app

    def create_icon_image(self, status: str = 'ready', show_timer: bool = False,
                         timer_text: str = '') -> Image:
        """
        Create system tray icon image based on current status.

        Args:
            status: Current status ('ready', 'recording', 'processing', 'error')
            show_timer: Whether to show timer overlay
            timer_text: Timer text to display

        Returns:
            PIL Image for the system tray icon
        """
        # Create a 64x64 pixel image
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Color mapping
        color_map = {
            'ready': '#00FF00',      # Green
            'recording': '#FF0000',   # Red
            'processing': '#FFFF00',  # Yellow
            'error': '#808080'        # Gray
        }

        # Get color for current status
        color = color_map.get(status, '#808080')

        # Draw main circle
        margin = 8
        circle_bbox = [margin, margin, size - margin, size - margin]
        draw.ellipse(circle_bbox, fill=color, outline='#FFFFFF', width=2)

        # Add status indicator in center
        center_size = 16
        center_margin = (size - center_size) // 2
        center_bbox = [center_margin, center_margin,
                      center_margin + center_size, center_margin + center_size]

        if status == 'recording':
            # Recording: solid circle
            draw.ellipse(center_bbox, fill='#FFFFFF')
        elif status == 'processing':
            # Processing: spinning indicator (simplified as triangle)
            points = [
                (size // 2, center_margin),
                (center_margin, center_margin + center_size),
                (center_margin + center_size, center_margin + center_size)
            ]
            draw.polygon(points, fill='#FFFFFF')
        elif status == 'ready':
            # Ready: play button triangle
            triangle_points = [
                (center_margin + 4, center_margin),
                (center_margin + 4, center_margin + center_size),
                (center_margin + center_size - 4, center_margin + center_size // 2)
            ]
            draw.polygon(triangle_points, fill='#FFFFFF')
        else:  # error
            # Error: X mark
            draw.line([center_margin + 2, center_margin + 2,
                      center_margin + center_size - 2, center_margin + center_size - 2],
                     fill='#FFFFFF', width=3)
            draw.line([center_margin + 2, center_margin + center_size - 2,
                      center_margin + center_size - 2, center_margin + 2],
                     fill='#FFFFFF', width=3)

        # Add timer text if recording
        if show_timer and timer_text:
            # Simple timer display (would need font for proper text)
            # For now, add a small indicator
            timer_size = 12
            timer_x = size - timer_size - 4
            timer_y = 4
            draw.ellipse([timer_x, timer_y, timer_x + timer_size, timer_y + timer_size],
                        fill='#FFFFFF', outline=color, width=1)

        return image

    def update_status(self, status: str, recording_start_time: Optional[datetime] = None):
        """
        Update the system tray status.

        Args:
            status: New status ('ready', 'recording', 'processing', 'error')
            recording_start_time: When recording started (for timer)
        """
        self.current_status = status
        self.recording_start_time = recording_start_time

        if self.icon and self.is_running:
            # Update icon
            show_timer = (status == 'recording' and recording_start_time is not None)
            timer_text = ''

            if show_timer:
                elapsed = datetime.now() - recording_start_time
                minutes = int(elapsed.total_seconds() // 60)
                seconds = int(elapsed.total_seconds() % 60)
                timer_text = f"{minutes:02d}:{seconds:02d}"

            new_image = self.create_icon_image(status, show_timer, timer_text)
            self.icon.icon = new_image

            # Update title with status
            status_display = status.title()
            if timer_text:
                status_display += f" ({timer_text})"

            self.icon.title = f"Voice Notes - {status_display}"

        logger.debug(f"System tray status updated to: {status}")

    def create_menu(self) -> Menu:
        """Create the right-click context menu."""
        menu_items = []

        # Status display (non-clickable)
        status_text = f"Status: {self.current_status.title()}"
        if self.current_status == 'recording' and self.recording_start_time:
            elapsed = datetime.now() - self.recording_start_time
            minutes = int(elapsed.total_seconds() // 60)
            seconds = int(elapsed.total_seconds() % 60)
            status_text = f"🔴 Recording ({minutes:02d}:{seconds:02d})"
        elif self.current_status == 'processing':
            status_text = "🔄 Processing..."
        elif self.current_status == 'ready':
            status_text = "✅ Ready"
        elif self.current_status == 'error':
            status_text = "❌ Error"

        menu_items.append(MenuItem(status_text, None))  # Non-clickable status
        menu_items.append(MenuItem('', None))  # Separator

        # Recording controls
        if self.current_status == 'recording':
            menu_items.append(MenuItem('🛑 Stop Recording', self._stop_recording))
        elif self.current_status == 'processing':
            menu_items.append(MenuItem('🎤 Start Recording', None))  # Disabled during processing
        else:
            menu_items.append(MenuItem('🎤 Start Recording', self._start_recording))

        # Cancel recording if in progress
        if self.current_status == 'recording':
            menu_items.append(MenuItem('🚫 Cancel Recording', self._cancel_recording))

        menu_items.append(MenuItem('', None))  # Separator

        # Quick actions
        menu_items.append(MenuItem('📁 Open Notes Folder', self._open_notes))
        menu_items.append(MenuItem('📊 View Statistics', self._view_statistics))

        # Recent notes submenu
        if self.recent_notes:
            recent_menu_items = []
            for note in self.recent_notes[:5]:  # Show last 5
                # Create closure to capture note value correctly
                note_action = self._create_note_action(note)
                recent_menu_items.append(MenuItem(f"📝 {note}", note_action))

            # Add "View All" option
            recent_menu_items.append(MenuItem('', None))  # Separator
            recent_menu_items.append(MenuItem('📋 View All Notes', self._view_all_notes))

            menu_items.append(MenuItem('📋 Recent Notes', Menu(*recent_menu_items)))
        else:
            menu_items.append(MenuItem('📋 Recent Notes', None))  # Disabled if no notes

        menu_items.append(MenuItem('', None))  # Separator

        # Processing mode submenu
        processing_modes = ['quick', 'standard', 'deep']
        current_mode = self.config.get('processing', {}).get('default_mode', 'standard')

        mode_menu_items = []
        for mode in processing_modes:
            mode_display = mode.title()
            if mode == current_mode:
                mode_display = f"✓ {mode_display}"
            mode_action = self._create_mode_action(mode)
            mode_menu_items.append(MenuItem(mode_display, mode_action))

        menu_items.append(MenuItem('⚙️ Processing Mode', Menu(*mode_menu_items)))

        # Tools submenu
        tools_menu_items = [
            MenuItem('🔍 Analyze with Agent', self._trigger_analysis),
            MenuItem('🔗 Generate Wikilinks', self._generate_wikilinks),
            MenuItem('📈 Usage Statistics', self._show_usage_stats),
        ]
        menu_items.append(MenuItem('🛠️ Tools', Menu(*tools_menu_items)))

        menu_items.append(MenuItem('', None))  # Separator

        # Settings and help
        menu_items.append(MenuItem('⚙️ Preferences', self._open_preferences))
        menu_items.append(MenuItem('❓ Help', self._show_help))
        menu_items.append(MenuItem('ℹ️ About', self._show_about))

        menu_items.append(MenuItem('', None))  # Separator
        menu_items.append(MenuItem('❌ Quit Voice Notes', self._quit))

        return Menu(*menu_items)

    def _create_note_action(self, note_name: str):
        """Create a closure for note action to capture the note name correctly."""
        def action(icon=None, item=None):
            self._open_note(note_name)
        return action

    def _create_mode_action(self, mode: str):
        """Create a closure for mode change action."""
        def action(icon=None, item=None):
            self._change_processing_mode(mode)
        return action

    def _start_recording(self, icon=None, item=None):
        """Handle start recording menu item."""
        if self.start_recording_callback:
            try:
                self.start_recording_callback()
            except Exception as e:
                logger.error(f"Error starting recording: {e}")
                self.update_status('error')

    def _stop_recording(self, icon=None, item=None):
        """Handle stop recording menu item."""
        if self.stop_recording_callback:
            try:
                self.stop_recording_callback()
            except Exception as e:
                logger.error(f"Error stopping recording: {e}")
                self.update_status('error')

    def _open_notes(self, icon=None, item=None):
        """Handle open notes folder menu item."""
        if self.open_notes_callback:
            try:
                self.open_notes_callback()
            except Exception as e:
                logger.error(f"Error opening notes: {e}")
        else:
            # Fallback: open default notes directory
            notes_dir = Path(self.config.get('files', {}).get('output_directory',
                                                            '~/Documents/Voice Notes')).expanduser()
            if notes_dir.exists():
                os.system(f'open "{notes_dir}"')  # macOS

    def _cancel_recording(self, icon=None, item=None):
        """Handle cancel recording menu item."""
        if self.stop_recording_callback:
            try:
                self.stop_recording_callback()
                self.update_status('ready')
                self.show_notification("Recording Cancelled", "Voice recording was cancelled")
            except Exception as e:
                logger.error(f"Error cancelling recording: {e}")
                self.update_status('error')

    def _view_statistics(self, icon=None, item=None):
        """View recording and processing statistics."""
        logger.info("Showing statistics")
        # Would integrate with activity logging when implemented
        self.show_notification("Statistics", "Statistics feature coming soon")

    def _view_all_notes(self, icon=None, item=None):
        """Open the notes directory to view all notes."""
        self._open_notes()

    def _change_processing_mode(self, mode: str):
        """Change the processing mode."""
        logger.info(f"Changing processing mode to: {mode}")
        # Update config and notify
        if 'processing' not in self.config:
            self.config['processing'] = {}
        self.config['processing']['default_mode'] = mode
        self.show_notification("Processing Mode", f"Changed to {mode.title()} mode")

        # Update menu to reflect new selection
        if self.icon and self.is_running:
            self.icon.menu = self.create_menu()

    def _trigger_analysis(self, icon=None, item=None):
        """Trigger analysis of recent notes with Analyzer agent."""
        logger.info("Triggering analysis with Analyzer agent")
        self.show_notification("Analysis", "Manual analysis feature coming soon")

    def _generate_wikilinks(self, icon=None, item=None):
        """Generate wikilinks for recent notes."""
        logger.info("Generating wikilinks")
        self.show_notification("Wikilinks", "Auto-wikilink generation coming soon")

    def _show_usage_stats(self, icon=None, item=None):
        """Show detailed usage statistics."""
        logger.info("Showing usage statistics")
        self.show_notification("Usage Stats", "Detailed usage statistics coming soon")

    def _open_preferences(self, icon=None, item=None):
        """Open preferences window."""
        logger.info("Opening preferences")
        self.show_notification("Preferences", "Preferences window coming soon")

    def _show_help(self, icon=None, item=None):
        """Show help information."""
        logger.info("Showing help")
        help_text = """Voice Notes System

Hotkeys:
• Cmd+Shift+R: Start/Stop recording

Menu Options:
• Right-click tray icon for options
• Change processing modes
• View recent notes
• Access tools and settings

Status Colors:
• Green: Ready
• Red: Recording
• Yellow: Processing
• Gray: Error/Offline"""
        self.show_notification("Help", "Check system tray menu for full options")

    def _show_about(self, icon=None, item=None):
        """Show about information."""
        logger.info("Showing about")
        about_text = "Voice Notes System v1.0\nAI-powered voice note capture and processing"
        self.show_notification("About", about_text)

    def _open_note(self, note_name: str):
        """Open a specific note."""
        logger.info(f"Opening note: {note_name}")
        # Find and open the note file
        notes_dir = Path(self.config.get('files', {}).get('output_directory',
                                                        '~/Documents/Voice Notes')).expanduser()
        # Look for the note file (could be .md file)
        possible_paths = [
            notes_dir / f"{note_name}.md",
            notes_dir / note_name,
        ]

        for note_path in possible_paths:
            if note_path.exists():
                os.system(f'open "{note_path}"')  # macOS
                return

        logger.warning(f"Could not find note file: {note_name}")
        self.show_notification("Note Not Found", f"Could not find: {note_name}")

    def _open_settings(self, icon=None, item=None):
        """Handle settings menu item."""
        logger.info("Settings requested - redirecting to preferences")
        self._open_preferences(icon, item)

    def _quit(self, icon=None, item=None):
        """Handle quit menu item."""
        self.stop()
        if self.quit_callback:
            self.quit_callback()

    def start(self):
        """Start the system tray application."""
        if not PYSTRAY_AVAILABLE:
            logger.error("Cannot start system tray - pystray not available")
            return False

        if self.is_running:
            logger.warning("System tray already running")
            return True

        try:
            # Create initial icon
            initial_image = self.create_icon_image('ready')

            # Create system tray icon
            self.icon = pystray.Icon(
                "voice_notes",
                initial_image,
                "Voice Notes - Ready",
                menu=self.create_menu()
            )

            # Start icon in separate thread
            self.is_running = True
            self.icon_thread = threading.Thread(target=self._run_icon, daemon=True)
            self.icon_thread.start()

            logger.info("System tray started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start system tray: {e}")
            self.is_running = False
            return False

    def _run_icon(self):
        """Run the system tray icon (in separate thread)."""
        try:
            self.icon.run()
        except Exception as e:
            logger.error(f"System tray icon error: {e}")
        finally:
            self.is_running = False

    def stop(self):
        """Stop the system tray application."""
        if not self.is_running:
            return

        self.is_running = False

        if self.icon:
            self.icon.stop()
            self.icon = None

        if self.icon_thread and self.icon_thread.is_alive():
            self.icon_thread.join(timeout=2.0)

        logger.info("System tray stopped")

    def update_recent_notes(self, notes: List[str]):
        """Update the list of recent notes."""
        self.recent_notes = notes[:10]  # Keep last 10

        # Update menu if running
        if self.icon and self.is_running:
            self.icon.menu = self.create_menu()

    def show_notification(self, title: str, message: str, duration: int = 3):
        """
        Show a system notification.

        Args:
            title: Notification title
            message: Notification message
            duration: Duration in seconds
        """
        if self.icon and self.is_running:
            try:
                self.icon.notify(message, title)
                logger.debug(f"Notification shown: {title} - {message}")
            except Exception as e:
                logger.error(f"Failed to show notification: {e}")

    def is_available(self) -> bool:
        """Check if system tray functionality is available."""
        return PYSTRAY_AVAILABLE

    def get_status(self) -> Dict[str, Any]:
        """Get current system tray status."""
        return {
            'available': PYSTRAY_AVAILABLE,
            'running': self.is_running,
            'current_status': self.current_status,
            'recording_start_time': self.recording_start_time.isoformat() if self.recording_start_time else None
        }