"""
Global hotkey integration for voice notes capture.

This module provides global hotkey functionality that works in the background
without requiring the application to have focus.
"""

import os
import sys
import time
import threading
import logging
from typing import Optional, Callable, Dict, Any
from pathlib import Path

try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode, Listener
except ImportError:
    print("Warning: pynput not available. Install with: pip install pynput")
    keyboard = None
    Key = None
    KeyCode = None
    Listener = None

try:
    from plyer import notification
except ImportError:
    print("Warning: plyer not available. Install with: pip install plyer")
    notification = None

try:
    from .config_manager import ConfigManager
    from .audio_recorder import AudioRecorder
except ImportError:
    from config_manager import ConfigManager
    from audio_recorder import AudioRecorder


class GlobalHotkeyManager:
    """Manages global hotkeys for voice recording functionality."""

    def __init__(self, config_manager: Optional[ConfigManager] = None,
                 audio_recorder: Optional[AudioRecorder] = None):
        """Initialize the global hotkey manager.

        Args:
            config_manager: Configuration manager instance
            audio_recorder: Audio recorder instance
        """
        self.config = config_manager or ConfigManager()
        self.audio_recorder = audio_recorder or AudioRecorder(self.config)

        # Get hotkey configuration
        hotkey_config = self.config.get_hotkeys_config()
        self.primary_key = hotkey_config.get('record_toggle', 'cmd+shift+r')
        self.stop_key = hotkey_config.get('cancel', 'escape')
        self.audio_feedback = hotkey_config.get('audio_feedback', True)

        # State management
        self.is_active = False
        self.is_recording = False
        self.listener: Optional[Listener] = None
        self.pressed_keys = set()

        # Recording session tracking
        self.current_session_id: Optional[str] = None
        self.recording_start_time: Optional[float] = None

        # Callbacks
        self.on_recording_start: Optional[Callable] = None
        self.on_recording_stop: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Parse hotkey combinations
        self._parse_hotkey_combinations()

    def _parse_hotkey_combinations(self):
        """Parse hotkey combination strings into key sets."""
        self.primary_combination = self._parse_key_combination(self.primary_key)
        self.stop_combination = self._parse_key_combination(self.stop_key)

        self.logger.info(f"Primary hotkey: {self.primary_key}")
        self.logger.info(f"Stop hotkey: {self.stop_key}")

    def _parse_key_combination(self, key_string: str) -> set:
        """Parse a key combination string into a set of keys.

        Args:
            key_string: String like 'cmd+shift+r' or 'escape'

        Returns:
            Set of keys for the combination
        """
        if not key_string:
            return set()

        keys = set()
        parts = key_string.lower().split('+')

        for part in parts:
            part = part.strip()
            if part == 'cmd' or part == 'command':
                keys.add(Key.cmd)
            elif part == 'ctrl' or part == 'control':
                keys.add(Key.ctrl)
            elif part == 'shift':
                keys.add(Key.shift)
            elif part == 'alt' or part == 'option':
                keys.add(Key.alt)
            elif part == 'escape' or part == 'esc':
                keys.add(Key.esc)
            elif part == 'space':
                keys.add(Key.space)
            elif part == 'enter' or part == 'return':
                keys.add(Key.enter)
            elif len(part) == 1:
                # Single character key
                keys.add(KeyCode.from_char(part))
            else:
                self.logger.warning(f"Unknown key: {part}")

        return keys

    def _show_notification(self, title: str, message: str):
        """Show system notification if available."""
        if notification:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Voice Notes",
                    timeout=2
                )
                return
            except Exception as e:
                self.logger.warning(f"Failed to show notification: {e}")
        
        # Fallback: macOS AppleScript via osascript
        try:
            if sys.platform == "darwin":
                # Escape quotes and newlines for AppleScript
                safe_title = title.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ")
                safe_message = message.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", " ")
                sound_clause = "sound name \"Glass\""
                script = f'display notification "{safe_message}" with title "{safe_title}" {sound_clause}'
                os.system(f"osascript -e \"{script}\" >/dev/null 2>&1")
        except Exception as e:
            self.logger.debug(f"Notification fallback failed: {e}")

    def _play_audio_feedback(self, sound_type: str):
        """Play audio feedback for recording events."""
        if not self.audio_feedback:
            return

        # Simple beep feedback - could be enhanced with actual sound files
        if sys.platform == "darwin":  # macOS
            if sound_type == "start":
                os.system("afplay /System/Library/Sounds/Glass.aiff 2>/dev/null &")
            elif sound_type == "stop":
                os.system("afplay /System/Library/Sounds/Tink.aiff 2>/dev/null &")
        else:
            # Cross-platform fallback - could be enhanced
            print(f"\a")  # Terminal bell

    def _on_key_press(self, key):
        """Handle key press events."""
        try:
            self.pressed_keys.add(key)

            # Check for hotkey combinations
            if self._is_combination_pressed(self.primary_combination):
                self._handle_primary_hotkey()
            elif self._is_combination_pressed(self.stop_combination):
                self._handle_stop_hotkey()

        except Exception as e:
            self.logger.error(f"Error in key press handler: {e}")
            if self.on_error:
                self.on_error(e)

    def _on_key_release(self, key):
        """Handle key release events."""
        try:
            self.pressed_keys.discard(key)
        except Exception as e:
            self.logger.error(f"Error in key release handler: {e}")

    def _is_combination_pressed(self, combination: set) -> bool:
        """Check if a key combination is currently pressed."""
        if not combination:
            return False
        return combination.issubset(self.pressed_keys)

    def _handle_primary_hotkey(self):
        """Handle the primary hotkey (Cmd+Shift+R by default)."""
        if self.is_recording:
            # Stop recording if already recording
            self._stop_recording()
        else:
            # Start recording
            self._start_recording()

    def _handle_stop_hotkey(self):
        """Handle the stop hotkey (ESC by default)."""
        if self.is_recording:
            self._stop_recording()

    def _start_recording(self):
        """Start voice recording."""
        if self.is_recording:
            self.logger.warning("Recording already in progress")
            return

        try:
            self.logger.info("Starting voice recording via hotkey")

            # Generate session ID
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            self.current_session_id = f"hotkey_{timestamp}"
            self.recording_start_time = time.time()

            # Start audio recording
            success = self.audio_recorder.start_recording()

            if success:
                self.is_recording = True

                # Provide feedback
                self._play_audio_feedback("start")
                self._show_notification(
                    "Voice Recording Started",
                    f"Session: {self.current_session_id}\nPress {self.primary_key} or {self.stop_key} to stop"
                )

                # Call callback
                if self.on_recording_start:
                    self.on_recording_start(self.current_session_id)

                self.logger.info(f"Recording started with session ID: {self.current_session_id}")
            else:
                self.logger.error("Failed to start audio recording")
                self._show_notification("Recording Failed", "Could not start audio recording")

        except Exception as e:
            self.logger.error(f"Error starting recording: {e}")
            self._show_notification("Recording Error", str(e))
            if self.on_error:
                self.on_error(e)

    def _stop_recording(self):
        """Stop voice recording."""
        if not self.is_recording:
            self.logger.warning("No recording in progress")
            return

        try:
            self.logger.info("Stopping voice recording via hotkey")

            # Stop audio recording and save file
            recording_stopped = self.audio_recorder.stop_recording()
            if recording_stopped:
                audio_file = self.audio_recorder.save_audio()
            else:
                audio_file = None

            self.is_recording = False
            duration = time.time() - self.recording_start_time if self.recording_start_time else 0

            # Provide feedback
            self._play_audio_feedback("stop")

            if audio_file and os.path.exists(audio_file):
                self._show_notification(
                    "Recording Completed",
                    f"Duration: {duration:.1f}s\nFile: {Path(audio_file).name}"
                )

                # Call callback
                if self.on_recording_stop:
                    self.on_recording_stop(self.current_session_id, audio_file, duration)

                self.logger.info(f"Recording completed: {audio_file} ({duration:.1f}s)")
            else:
                self._show_notification("Recording Warning", "Recording stopped but no file saved")
                self.logger.warning("Recording stopped but no file was saved")

            # Reset session
            self.current_session_id = None
            self.recording_start_time = None

        except Exception as e:
            self.logger.error(f"Error stopping recording: {e}")
            self._show_notification("Stop Recording Error", str(e))
            self.is_recording = False
            if self.on_error:
                self.on_error(e)

    def start(self) -> bool:
        """Start the global hotkey listener.

        Returns:
            True if started successfully, False otherwise
        """
        if self.is_active:
            self.logger.warning("Hotkey manager already active")
            return True

        if not keyboard:
            self.logger.error("pynput not available - cannot start hotkey listener")
            return False

        try:
            self.listener = Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )

            self.listener.start()
            self.is_active = True

            self.logger.info("Global hotkey listener started")
            self._show_notification(
                "Voice Notes Ready",
                f"Press {self.primary_key} to start recording"
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to start hotkey listener: {e}")
            if self.on_error:
                self.on_error(e)
            return False

    def stop(self):
        """Stop the global hotkey listener."""
        if not self.is_active:
            return

        try:
            # Stop any ongoing recording
            if self.is_recording:
                self._stop_recording()

            # Stop the listener
            if self.listener:
                self.listener.stop()
                self.listener = None

            self.is_active = False
            self.logger.info("Global hotkey listener stopped")

        except Exception as e:
            self.logger.error(f"Error stopping hotkey listener: {e}")

    def is_running(self) -> bool:
        """Check if the hotkey listener is running."""
        return self.is_active and self.listener and self.listener.running

    def get_status(self) -> Dict[str, Any]:
        """Get current status information."""
        return {
            "is_active": self.is_active,
            "is_recording": self.is_recording,
            "current_session_id": self.current_session_id,
            "primary_hotkey": self.primary_key,
            "stop_hotkey": self.stop_key,
            "audio_feedback": self.audio_feedback,
            "recording_duration": (
                time.time() - self.recording_start_time
                if self.recording_start_time else 0
            )
        }

    def set_callbacks(self,
                     on_recording_start: Optional[Callable] = None,
                     on_recording_stop: Optional[Callable] = None,
                     on_error: Optional[Callable] = None):
        """Set callback functions for events.

        Args:
            on_recording_start: Called when recording starts (session_id)
            on_recording_stop: Called when recording stops (session_id, file_path, duration)
            on_error: Called when an error occurs (exception)
        """
        self.on_recording_start = on_recording_start
        self.on_recording_stop = on_recording_stop
        self.on_error = on_error

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()