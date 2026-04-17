"""Tests for the system tray application."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from PIL import Image

from src.system_tray import VoiceNotesSystemTray


class TestVoiceNotesSystemTray:
    """Test cases for VoiceNotesSystemTray."""

    @pytest.fixture
    def config(self):
        """Sample configuration for testing."""
        return {
            'ui': {
                'ready_color': 'green',
                'recording_color': 'red',
                'processing_color': 'yellow',
                'error_color': 'gray'
            },
            'files': {
                'output_directory': '/tmp/voice_notes_test'
            },
            'processing': {
                'default_mode': 'standard'
            }
        }

    @pytest.fixture
    def system_tray(self, config):
        """Create a system tray instance for testing."""
        return VoiceNotesSystemTray(config)

    def test_initialization(self, system_tray, config):
        """Test system tray initialization."""
        assert system_tray.config == config
        assert system_tray.current_status == 'ready'
        assert system_tray.recording_start_time is None
        assert system_tray.is_running is False
        assert system_tray.recent_notes == []

    def test_set_callbacks(self, system_tray):
        """Test setting callback functions."""
        start_cb = Mock()
        stop_cb = Mock()
        open_cb = Mock()
        quit_cb = Mock()

        system_tray.set_callbacks(
            start_recording=start_cb,
            stop_recording=stop_cb,
            open_notes=open_cb,
            quit_app=quit_cb
        )

        assert system_tray.start_recording_callback == start_cb
        assert system_tray.stop_recording_callback == stop_cb
        assert system_tray.open_notes_callback == open_cb
        assert system_tray.quit_callback == quit_cb

    def test_create_icon_image_ready(self, system_tray):
        """Test creating icon image for ready status."""
        image = system_tray.create_icon_image('ready')
        assert isinstance(image, Image.Image)
        assert image.size == (64, 64)

    def test_create_icon_image_recording(self, system_tray):
        """Test creating icon image for recording status."""
        image = system_tray.create_icon_image('recording', show_timer=True, timer_text="01:30")
        assert isinstance(image, Image.Image)
        assert image.size == (64, 64)

    def test_create_icon_image_processing(self, system_tray):
        """Test creating icon image for processing status."""
        image = system_tray.create_icon_image('processing')
        assert isinstance(image, Image.Image)
        assert image.size == (64, 64)

    def test_create_icon_image_error(self, system_tray):
        """Test creating icon image for error status."""
        image = system_tray.create_icon_image('error')
        assert isinstance(image, Image.Image)
        assert image.size == (64, 64)

    @patch('src.system_tray.PYSTRAY_AVAILABLE', True)
    def test_update_status_without_icon(self, system_tray):
        """Test updating status when icon is not running."""
        system_tray.update_status('recording', datetime.now())
        assert system_tray.current_status == 'recording'
        assert system_tray.recording_start_time is not None

    @patch('src.system_tray.PYSTRAY_AVAILABLE', True)
    def test_update_status_with_icon(self, system_tray):
        """Test updating status when icon is running."""
        # Mock the icon
        mock_icon = Mock()
        system_tray.icon = mock_icon
        system_tray.is_running = True

        start_time = datetime.now()
        system_tray.update_status('recording', start_time)

        assert system_tray.current_status == 'recording'
        assert system_tray.recording_start_time == start_time
        # Icon should be updated
        assert mock_icon.icon is not None
        assert "Recording" in mock_icon.title

    def test_create_menu_ready_status(self, system_tray):
        """Test creating menu when in ready status."""
        with patch('src.system_tray.PYSTRAY_AVAILABLE', True):
            menu = system_tray.create_menu()
            assert menu is not None

    def test_create_menu_recording_status(self, system_tray):
        """Test creating menu when in recording status."""
        system_tray.current_status = 'recording'
        system_tray.recording_start_time = datetime.now()

        with patch('src.system_tray.PYSTRAY_AVAILABLE', True):
            menu = system_tray.create_menu()
            assert menu is not None

    def test_create_menu_with_recent_notes(self, system_tray):
        """Test creating menu with recent notes."""
        system_tray.recent_notes = ['Note 1', 'Note 2', 'Note 3']

        with patch('src.system_tray.PYSTRAY_AVAILABLE', True):
            menu = system_tray.create_menu()
            assert menu is not None

    def test_start_recording_callback(self, system_tray):
        """Test start recording callback."""
        mock_callback = Mock()
        system_tray.start_recording_callback = mock_callback

        system_tray._start_recording()
        mock_callback.assert_called_once()

    def test_start_recording_callback_error(self, system_tray):
        """Test start recording callback with error."""
        mock_callback = Mock(side_effect=Exception("Test error"))
        system_tray.start_recording_callback = mock_callback

        system_tray._start_recording()
        assert system_tray.current_status == 'error'

    def test_stop_recording_callback(self, system_tray):
        """Test stop recording callback."""
        mock_callback = Mock()
        system_tray.stop_recording_callback = mock_callback

        system_tray._stop_recording()
        mock_callback.assert_called_once()

    def test_cancel_recording(self, system_tray):
        """Test cancel recording functionality."""
        mock_callback = Mock()
        system_tray.stop_recording_callback = mock_callback

        with patch.object(system_tray, 'show_notification') as mock_notify:
            system_tray._cancel_recording()

        mock_callback.assert_called_once()
        mock_notify.assert_called_once()
        assert system_tray.current_status == 'ready'

    def test_change_processing_mode(self, system_tray):
        """Test changing processing mode."""
        with patch.object(system_tray, 'show_notification') as mock_notify:
            system_tray._change_processing_mode('deep')

        assert system_tray.config['processing']['default_mode'] == 'deep'
        mock_notify.assert_called_once()

    @patch('src.system_tray.os.system')
    def test_open_notes_with_callback(self, mock_os, system_tray):
        """Test opening notes with callback."""
        mock_callback = Mock()
        system_tray.open_notes_callback = mock_callback

        system_tray._open_notes()
        mock_callback.assert_called_once()
        mock_os.assert_not_called()

    @patch('src.system_tray.os.system')
    @patch('src.system_tray.Path')
    def test_open_notes_fallback(self, mock_path, mock_os, system_tray):
        """Test opening notes fallback."""
        # Mock path exists
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value.expanduser.return_value = mock_path_instance

        system_tray._open_notes()
        mock_os.assert_called_once()

    @patch('src.system_tray.os.system')
    @patch('src.system_tray.Path')
    def test_open_specific_note(self, mock_path, mock_os, system_tray):
        """Test opening a specific note."""
        # Mock note file exists
        mock_note_path = Mock()
        mock_note_path.exists.return_value = True
        mock_path.return_value.expanduser.return_value.__truediv__.return_value = mock_note_path

        system_tray._open_note("test_note")
        mock_os.assert_called_once()

    def test_update_recent_notes(self, system_tray):
        """Test updating recent notes list."""
        notes = ['Note 1', 'Note 2', 'Note 3']
        system_tray.update_recent_notes(notes)

        assert system_tray.recent_notes == notes

    def test_update_recent_notes_limit(self, system_tray):
        """Test recent notes list respects limit."""
        notes = [f'Note {i}' for i in range(15)]  # 15 notes
        system_tray.update_recent_notes(notes)

        assert len(system_tray.recent_notes) == 10  # Should be limited to 10

    @patch('src.system_tray.PYSTRAY_AVAILABLE', True)
    def test_show_notification_with_icon(self, system_tray):
        """Test showing notification when icon is running."""
        mock_icon = Mock()
        system_tray.icon = mock_icon
        system_tray.is_running = True

        system_tray.show_notification("Test Title", "Test Message")
        mock_icon.notify.assert_called_once_with("Test Message", "Test Title")

    def test_show_notification_without_icon(self, system_tray):
        """Test showing notification when icon is not running."""
        # Should not raise error
        system_tray.show_notification("Test Title", "Test Message")

    @patch('src.system_tray.PYSTRAY_AVAILABLE', True)
    def test_is_available_true(self, system_tray):
        """Test is_available when pystray is available."""
        assert system_tray.is_available() is True

    @patch('src.system_tray.PYSTRAY_AVAILABLE', False)
    def test_is_available_false(self, system_tray):
        """Test is_available when pystray is not available."""
        assert system_tray.is_available() is False

    def test_get_status(self, system_tray):
        """Test getting system tray status."""
        status = system_tray.get_status()

        assert 'available' in status
        assert 'running' in status
        assert 'current_status' in status
        assert 'recording_start_time' in status
        assert status['current_status'] == 'ready'

    @patch('src.system_tray.PYSTRAY_AVAILABLE', False)
    def test_start_without_pystray(self, system_tray):
        """Test starting system tray without pystray available."""
        result = system_tray.start()
        assert result is False

    @patch('src.system_tray.PYSTRAY_AVAILABLE', True)
    @patch('src.system_tray.pystray')
    @patch('src.system_tray.threading')
    def test_start_success(self, mock_threading, mock_pystray, system_tray):
        """Test successful system tray start."""
        mock_icon = Mock()
        mock_pystray.Icon.return_value = mock_icon
        mock_thread = Mock()
        mock_threading.Thread.return_value = mock_thread

        result = system_tray.start()

        assert result is True
        assert system_tray.is_running is True
        mock_pystray.Icon.assert_called_once()
        mock_thread.start.assert_called_once()

    def test_stop_when_not_running(self, system_tray):
        """Test stopping system tray when not running."""
        # Should not raise error
        system_tray.stop()

    def test_stop_when_running(self, system_tray):
        """Test stopping system tray when running."""
        mock_icon = Mock()
        mock_thread = Mock()
        mock_thread.is_alive.return_value = True

        system_tray.icon = mock_icon
        system_tray.icon_thread = mock_thread
        system_tray.is_running = True

        system_tray.stop()

        assert system_tray.is_running is False
        mock_icon.stop.assert_called_once()
        mock_thread.join.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])