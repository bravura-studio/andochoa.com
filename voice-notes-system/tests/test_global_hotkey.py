"""
Tests for global hotkey functionality.
"""

import unittest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from src.global_hotkey import GlobalHotkeyManager
    from src.config_manager import ConfigManager
    from src.audio_recorder import AudioRecorder
except ImportError:
    from global_hotkey import GlobalHotkeyManager
    from config_manager import ConfigManager
    from audio_recorder import AudioRecorder


class TestGlobalHotkeyManager(unittest.TestCase):
    """Test cases for GlobalHotkeyManager."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock config manager
        self.mock_config = Mock(spec=ConfigManager)
        self.mock_config.get_hotkeys_config.return_value = {
            'record_toggle': 'cmd+shift+r',
            'cancel': 'escape',
            'audio_feedback': True
        }

        # Mock audio recorder
        self.mock_audio_recorder = Mock(spec=AudioRecorder)
        self.mock_audio_recorder.start_recording.return_value = True
        self.mock_audio_recorder.stop_recording.return_value = "/tmp/test_audio.wav"

        # Create manager with mocks
        with patch('src.global_hotkey.keyboard') as mock_keyboard:
            mock_keyboard.Key = Mock()
            mock_keyboard.Key.cmd = 'cmd'
            mock_keyboard.Key.shift = 'shift'
            mock_keyboard.Key.esc = 'esc'
            mock_keyboard.KeyCode = Mock()
            mock_keyboard.KeyCode.from_char = Mock(return_value='r')
            mock_keyboard.Listener = Mock()

            self.manager = GlobalHotkeyManager(
                config_manager=self.mock_config,
                audio_recorder=self.mock_audio_recorder
            )

    def test_initialization(self):
        """Test manager initialization."""
        self.assertEqual(self.manager.primary_key, 'cmd+shift+r')
        self.assertEqual(self.manager.stop_key, 'escape')
        self.assertTrue(self.manager.audio_feedback)
        self.assertFalse(self.manager.is_active)
        self.assertFalse(self.manager.is_recording)

    def test_parse_key_combination_simple(self):
        """Test parsing simple key combinations."""
        # Test single key
        keys = self.manager._parse_key_combination('escape')
        self.assertTrue(len(keys) > 0)

        # Test multiple keys
        keys = self.manager._parse_key_combination('cmd+shift+r')
        self.assertTrue(len(keys) >= 3)

    def test_parse_key_combination_empty(self):
        """Test parsing empty key combination."""
        keys = self.manager._parse_key_combination('')
        self.assertEqual(len(keys), 0)

        keys = self.manager._parse_key_combination(None)
        self.assertEqual(len(keys), 0)

    @patch('src.global_hotkey.notification')
    def test_show_notification(self, mock_notification):
        """Test notification display."""
        # Test with notification available
        mock_notification.notify = Mock()
        self.manager._show_notification("Test Title", "Test Message")
        mock_notification.notify.assert_called_once()

        # Test with notification unavailable
        mock_notification.notify.side_effect = Exception("Test exception")
        self.manager._show_notification("Test Title", "Test Message")
        # Should not raise exception

    @patch('src.global_hotkey.os.system')
    def test_play_audio_feedback_macos(self, mock_system):
        """Test audio feedback on macOS."""
        with patch('src.global_hotkey.sys.platform', 'darwin'):
            self.manager._play_audio_feedback('start')
            mock_system.assert_called()

            self.manager._play_audio_feedback('stop')
            mock_system.assert_called()

    def test_play_audio_feedback_disabled(self):
        """Test audio feedback when disabled."""
        self.manager.audio_feedback = False
        with patch('src.global_hotkey.os.system') as mock_system:
            self.manager._play_audio_feedback('start')
            mock_system.assert_not_called()

    def test_start_recording_success(self):
        """Test successful recording start."""
        # Mock time and callbacks
        with patch('src.global_hotkey.time.time', return_value=1234567890):
            with patch('src.global_hotkey.time.strftime', return_value='20240919_143022'):
                # Set up callback
                callback_called = False
                session_id = None

                def on_start(sid):
                    nonlocal callback_called, session_id
                    callback_called = True
                    session_id = sid

                self.manager.set_callbacks(on_recording_start=on_start)

                # Start recording
                self.manager._start_recording()

                # Verify state changes
                self.assertTrue(self.manager.is_recording)
                self.assertIsNotNone(self.manager.current_session_id)
                self.assertIsNotNone(self.manager.recording_start_time)

                # Verify audio recorder called
                self.mock_audio_recorder.start_recording.assert_called_once()

                # Verify callback called
                self.assertTrue(callback_called)
                self.assertEqual(session_id, self.manager.current_session_id)

    def test_start_recording_already_recording(self):
        """Test starting recording when already recording."""
        self.manager.is_recording = True

        with patch.object(self.manager, 'logger') as mock_logger:
            self.manager._start_recording()
            mock_logger.warning.assert_called_with("Recording already in progress")

    def test_start_recording_failure(self):
        """Test recording start failure."""
        self.mock_audio_recorder.start_recording.return_value = False

        with patch.object(self.manager, 'logger') as mock_logger:
            self.manager._start_recording()
            mock_logger.error.assert_called()
            self.assertFalse(self.manager.is_recording)

    def test_stop_recording_success(self):
        """Test successful recording stop."""
        # Set up recording state
        self.manager.is_recording = True
        self.manager.current_session_id = "test_session"
        self.manager.recording_start_time = time.time() - 10  # 10 seconds ago

        # Set up callback
        callback_called = False
        result_session_id = None
        result_file = None
        result_duration = None

        def on_stop(sid, file_path, duration):
            nonlocal callback_called, result_session_id, result_file, result_duration
            callback_called = True
            result_session_id = sid
            result_file = file_path
            result_duration = duration

        self.manager.set_callbacks(on_recording_stop=on_stop)

        # Mock file existence
        with patch('src.global_hotkey.os.path.exists', return_value=True):
            self.manager._stop_recording()

        # Verify state changes
        self.assertFalse(self.manager.is_recording)
        self.assertIsNone(self.manager.current_session_id)
        self.assertIsNone(self.manager.recording_start_time)

        # Verify audio recorder called
        self.mock_audio_recorder.stop_recording.assert_called_once()

        # Verify callback called
        self.assertTrue(callback_called)
        self.assertEqual(result_session_id, "test_session")
        self.assertEqual(result_file, "/tmp/test_audio.wav")
        self.assertGreater(result_duration, 0)

    def test_stop_recording_not_recording(self):
        """Test stopping recording when not recording."""
        self.manager.is_recording = False

        with patch.object(self.manager, 'logger') as mock_logger:
            self.manager._stop_recording()
            mock_logger.warning.assert_called_with("No recording in progress")

    def test_stop_recording_no_file(self):
        """Test stopping recording with no file saved."""
        self.manager.is_recording = True
        self.manager.current_session_id = "test_session"
        self.manager.recording_start_time = time.time()

        # Mock no file returned
        self.mock_audio_recorder.stop_recording.return_value = None

        with patch.object(self.manager, 'logger') as mock_logger:
            self.manager._stop_recording()
            mock_logger.warning.assert_called()
            self.assertFalse(self.manager.is_recording)

    def test_handle_primary_hotkey_start(self):
        """Test primary hotkey starting recording."""
        self.manager.is_recording = False

        with patch.object(self.manager, '_start_recording') as mock_start:
            self.manager._handle_primary_hotkey()
            mock_start.assert_called_once()

    def test_handle_primary_hotkey_stop(self):
        """Test primary hotkey stopping recording."""
        self.manager.is_recording = True

        with patch.object(self.manager, '_stop_recording') as mock_stop:
            self.manager._handle_primary_hotkey()
            mock_stop.assert_called_once()

    def test_handle_stop_hotkey(self):
        """Test stop hotkey functionality."""
        self.manager.is_recording = True

        with patch.object(self.manager, '_stop_recording') as mock_stop:
            self.manager._handle_stop_hotkey()
            mock_stop.assert_called_once()

    def test_handle_stop_hotkey_not_recording(self):
        """Test stop hotkey when not recording."""
        self.manager.is_recording = False

        with patch.object(self.manager, '_stop_recording') as mock_stop:
            self.manager._handle_stop_hotkey()
            mock_stop.assert_called_once()  # Should still call (handles the check internally)

    def test_get_status(self):
        """Test status information retrieval."""
        status = self.manager.get_status()

        expected_keys = [
            'is_active', 'is_recording', 'current_session_id',
            'primary_hotkey', 'stop_hotkey', 'audio_feedback',
            'recording_duration'
        ]

        for key in expected_keys:
            self.assertIn(key, status)

        self.assertEqual(status['primary_hotkey'], 'cmd+shift+r')
        self.assertEqual(status['stop_hotkey'], 'escape')
        self.assertTrue(status['audio_feedback'])

    def test_set_callbacks(self):
        """Test callback setting."""
        start_callback = Mock()
        stop_callback = Mock()
        error_callback = Mock()

        self.manager.set_callbacks(
            on_recording_start=start_callback,
            on_recording_stop=stop_callback,
            on_error=error_callback
        )

        self.assertEqual(self.manager.on_recording_start, start_callback)
        self.assertEqual(self.manager.on_recording_stop, stop_callback)
        self.assertEqual(self.manager.on_error, error_callback)

    @patch('src.global_hotkey.keyboard')
    def test_start_listener_success(self, mock_keyboard):
        """Test successful listener start."""
        mock_listener = Mock()
        mock_keyboard.Listener.return_value = mock_listener

        result = self.manager.start()

        self.assertTrue(result)
        self.assertTrue(self.manager.is_active)
        mock_listener.start.assert_called_once()

    @patch('src.global_hotkey.keyboard', None)
    def test_start_listener_no_pynput(self):
        """Test listener start without pynput."""
        result = self.manager.start()

        self.assertFalse(result)
        self.assertFalse(self.manager.is_active)

    @patch('src.global_hotkey.keyboard')
    def test_start_listener_exception(self, mock_keyboard):
        """Test listener start with exception."""
        mock_keyboard.Listener.side_effect = Exception("Test exception")

        with patch.object(self.manager, 'logger') as mock_logger:
            result = self.manager.start()

            self.assertFalse(result)
            self.assertFalse(self.manager.is_active)
            mock_logger.error.assert_called()

    def test_stop_listener(self):
        """Test stopping the listener."""
        # Set up active state
        self.manager.is_active = True
        self.manager.is_recording = True
        mock_listener = Mock()
        self.manager.listener = mock_listener

        with patch.object(self.manager, '_stop_recording') as mock_stop:
            self.manager.stop()

            mock_stop.assert_called_once()
            mock_listener.stop.assert_called_once()
            self.assertFalse(self.manager.is_active)
            self.assertIsNone(self.manager.listener)

    def test_stop_listener_not_active(self):
        """Test stopping inactive listener."""
        self.manager.is_active = False

        # Should not raise exception
        self.manager.stop()

    def test_is_running(self):
        """Test running status check."""
        # Not active
        self.manager.is_active = False
        self.assertFalse(self.manager.is_running())

        # Active but no listener
        self.manager.is_active = True
        self.manager.listener = None
        self.assertFalse(self.manager.is_running())

        # Active with listener
        mock_listener = Mock()
        mock_listener.running = True
        self.manager.listener = mock_listener
        self.assertTrue(self.manager.is_running())

    def test_context_manager(self):
        """Test context manager functionality."""
        with patch.object(self.manager, 'start') as mock_start:
            with patch.object(self.manager, 'stop') as mock_stop:
                with self.manager:
                    pass

                mock_start.assert_called_once()
                mock_stop.assert_called_once()


class TestGlobalHotkeyIntegration(unittest.TestCase):
    """Integration tests for global hotkey functionality."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.config_dir = Path(__file__).parent.parent / "config"
        self.config = ConfigManager()

    @patch('src.global_hotkey.keyboard')
    def test_full_integration_mock(self, mock_keyboard):
        """Test full integration with mocked dependencies."""
        # Set up mocks
        mock_listener = Mock()
        mock_keyboard.Listener.return_value = mock_listener
        mock_keyboard.Key = Mock()
        mock_keyboard.KeyCode = Mock()

        # Create manager
        manager = GlobalHotkeyManager(config_manager=self.config)

        # Test start
        result = manager.start()
        self.assertTrue(result)

        # Test status
        status = manager.get_status()
        self.assertTrue(status['is_active'])

        # Test stop
        manager.stop()
        self.assertFalse(manager.is_active)

    def test_config_integration(self):
        """Test integration with configuration system."""
        # Test with custom config
        mock_config = Mock(spec=ConfigManager)
        mock_config.get_hotkeys_config.return_value = {
            'record_toggle': 'ctrl+shift+v',
            'cancel': 'ctrl+c',
            'audio_feedback': False
        }

        with patch('src.global_hotkey.keyboard'):
            manager = GlobalHotkeyManager(config_manager=mock_config)

            self.assertEqual(manager.primary_key, 'ctrl+shift+v')
            self.assertEqual(manager.stop_key, 'ctrl+c')
            self.assertFalse(manager.audio_feedback)


if __name__ == '__main__':
    unittest.main()