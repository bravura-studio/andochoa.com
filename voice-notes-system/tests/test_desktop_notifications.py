"""
Tests for desktop notification system.

Comprehensive test suite covering all notification types, preferences,
and platform-specific functionality.
"""

import pytest
import platform
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from desktop_notifications import (
    DesktopNotificationSystem,
    DesktopNotification,
    NotificationPriority,
    NotificationType
)


class TestDesktopNotificationSystem:
    """Test suite for DesktopNotificationSystem."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        return {
            'notifications': {
                'enabled': True,
                'sound_enabled': True,
                'show_recording': True,
                'show_processing': True,
                'show_errors': True,
                'show_success': True,
                'default_duration': 4,
                'non_intrusive': False
            }
        }

    @pytest.fixture
    def notification_system(self, mock_config):
        """Create notification system instance for testing."""
        with patch('desktop_notifications.ErrorNotificationSystem'):
            return DesktopNotificationSystem(mock_config)

    @pytest.fixture
    def sample_notification(self):
        """Sample notification for testing."""
        return DesktopNotification(
            title="Test Notification",
            message="This is a test message",
            notification_type=NotificationType.INFO,
            priority=NotificationPriority.NORMAL,
            duration=3,
            category="test"
        )

    def test_initialization(self, mock_config):
        """Test notification system initialization."""
        with patch('desktop_notifications.ErrorNotificationSystem'):
            system = DesktopNotificationSystem(mock_config)

            assert system.enabled is True
            assert system.sound_enabled is True
            assert system.show_recording_notifications is True
            assert system.show_processing_notifications is True
            assert system.show_error_notifications is True
            assert system.show_success_notifications is True
            assert system.notification_duration == 4
            assert system.non_intrusive_mode is False

    def test_initialization_with_defaults(self):
        """Test initialization with default configuration."""
        with patch('desktop_notifications.ErrorNotificationSystem'):
            system = DesktopNotificationSystem()

            assert system.enabled is True
            assert system.sound_enabled is True
            assert system.notification_duration == 4
            assert system.non_intrusive_mode is False

    @patch('desktop_notifications.subprocess.run')
    def test_system_detection_macos(self, mock_subprocess):
        """Test macOS system notification detection."""
        mock_subprocess.return_value = Mock(returncode=0)

        with patch('platform.system', return_value='Darwin'):
            with patch('desktop_notifications.ErrorNotificationSystem'):
                system = DesktopNotificationSystem()
                assert system.system_notifications_available is True

    @patch('desktop_notifications.subprocess.run')
    def test_system_detection_linux(self, mock_subprocess):
        """Test Linux system notification detection."""
        mock_subprocess.return_value = Mock(returncode=0)

        with patch('platform.system', return_value='Linux'):
            with patch('desktop_notifications.ErrorNotificationSystem'):
                system = DesktopNotificationSystem()
                assert system.system_notifications_available is True

    @patch('platform.system')
    def test_system_detection_windows(self, mock_platform):
        """Test Windows system notification detection."""
        mock_platform.return_value = 'Windows'

        with patch('desktop_notifications.ErrorNotificationSystem'):
            system = DesktopNotificationSystem()
            assert system.system_notifications_available is True

    @patch('desktop_notifications.subprocess.run')
    def test_system_detection_failure(self, mock_subprocess):
        """Test system detection when commands fail."""
        mock_subprocess.side_effect = FileNotFoundError()

        with patch('desktop_notifications.ErrorNotificationSystem'):
            system = DesktopNotificationSystem()
            assert system.system_notifications_available is False

    def test_add_notification_callback(self, notification_system):
        """Test adding notification callbacks."""
        callback = Mock()
        notification_system.add_notification_callback(callback)

        assert callback in notification_system.notification_callbacks

    def test_show_notification_disabled(self, notification_system, sample_notification):
        """Test that notifications don't show when disabled."""
        notification_system.enabled = False

        result = notification_system.show_notification(sample_notification)

        assert result is False

    def test_show_notification_callback_execution(self, notification_system, sample_notification):
        """Test that callbacks are executed when showing notifications."""
        callback = Mock()
        notification_system.add_notification_callback(callback)
        notification_system.system_notifications_available = False  # Skip system notification

        notification_system.show_notification(sample_notification)

        callback.assert_called_once_with(sample_notification)

    def test_show_notification_callback_exception_handling(self, notification_system, sample_notification):
        """Test that callback exceptions don't break notification flow."""
        failing_callback = Mock(side_effect=Exception("Test error"))
        working_callback = Mock()

        notification_system.add_notification_callback(failing_callback)
        notification_system.add_notification_callback(working_callback)
        notification_system.system_notifications_available = False

        notification_system.show_notification(sample_notification)

        failing_callback.assert_called_once_with(sample_notification)
        working_callback.assert_called_once_with(sample_notification)

    def test_should_show_notification_preferences(self, notification_system):
        """Test notification filtering based on preferences."""
        # Test recording notification preference
        notification_system.show_recording_notifications = False
        recording_notification = DesktopNotification(
            title="Recording", message="Test", category="recording"
        )
        assert not notification_system._should_show_notification(recording_notification)

        # Test processing notification preference
        notification_system.show_processing_notifications = False
        processing_notification = DesktopNotification(
            title="Processing", message="Test", category="processing"
        )
        assert not notification_system._should_show_notification(processing_notification)

        # Test error notification preference
        notification_system.show_error_notifications = False
        error_notification = DesktopNotification(
            title="Error", message="Test", notification_type=NotificationType.ERROR
        )
        assert not notification_system._should_show_notification(error_notification)

        # Test success notification preference
        notification_system.show_success_notifications = False
        success_notification = DesktopNotification(
            title="Success", message="Test", notification_type=NotificationType.SUCCESS
        )
        assert not notification_system._should_show_notification(success_notification)

    def test_make_non_intrusive(self, notification_system):
        """Test non-intrusive mode adjustments."""
        notification = DesktopNotification(
            title="Test",
            message="Test message",
            duration=10,
            sound=True,
            priority=NotificationPriority.LOW,
            actions=[{'label': 'Test', 'action': 'test'}]
        )

        adjusted = notification_system._make_non_intrusive(notification)

        assert adjusted.duration <= 2
        assert adjusted.actions == []  # Actions removed for low priority

        # Test critical notifications keep sound
        critical_notification = DesktopNotification(
            title="Critical",
            message="Critical message",
            priority=NotificationPriority.CRITICAL,
            sound=True
        )

        adjusted_critical = notification_system._make_non_intrusive(critical_notification)
        assert adjusted_critical.sound is True  # Critical keeps sound

    @patch('desktop_notifications.subprocess.run')
    def test_show_macos_notification_success(self, mock_subprocess):
        """Test successful macOS notification."""
        mock_subprocess.return_value = Mock(returncode=0)

        with patch('desktop_notifications.ErrorNotificationSystem'):
            system = DesktopNotificationSystem()
            system.platform = "darwin"
            system.system_notifications_available = True

            notification = DesktopNotification(
                title="Test",
                message="Test message",
                notification_type=NotificationType.SUCCESS,
                sound=True
            )

            result = system._show_macos_notification(notification)

            assert result is True
            mock_subprocess.assert_called_once()

            # Check the AppleScript contains expected elements
            call_args = mock_subprocess.call_args[0][0]
            assert 'osascript' in call_args
            assert '-e' in call_args

    @patch('desktop_notifications.subprocess.run')
    def test_show_macos_notification_no_sound(self, mock_subprocess):
        """Test macOS notification without sound."""
        mock_subprocess.return_value = Mock(returncode=0)

        with patch('desktop_notifications.ErrorNotificationSystem'):
            system = DesktopNotificationSystem()
            system.platform = "darwin"
            system.system_notifications_available = True
            system.sound_enabled = False

            notification = DesktopNotification(
                title="Test",
                message="Test message",
                sound=True
            )

            result = system._show_macos_notification(notification)

            assert result is True

    @patch('desktop_notifications.subprocess.run')
    def test_show_linux_notification(self, mock_subprocess):
        """Test Linux notification with notify-send."""
        mock_subprocess.return_value = Mock(returncode=0)

        with patch('desktop_notifications.ErrorNotificationSystem'):
            system = DesktopNotificationSystem()
            system.platform = "linux"
            system.system_notifications_available = True

            notification = DesktopNotification(
                title="Test",
                message="Test message",
                notification_type=NotificationType.WARNING,
                priority=NotificationPriority.HIGH,
                duration=5
            )

            result = system._show_linux_notification(notification)

            assert result is True
            mock_subprocess.assert_called_once()

            # Check notify-send parameters
            call_args = mock_subprocess.call_args[0][0]
            assert 'notify-send' in call_args
            assert '--urgency' in call_args
            assert '--expire-time' in call_args
            assert '5000' in call_args  # 5 seconds * 1000

    @patch('desktop_notifications.subprocess.run')
    def test_show_windows_notification(self, mock_subprocess):
        """Test Windows PowerShell notification."""
        mock_subprocess.return_value = Mock(returncode=0)

        with patch('desktop_notifications.ErrorNotificationSystem'):
            system = DesktopNotificationSystem()
            system.platform = "windows"
            system.system_notifications_available = True

            notification = DesktopNotification(
                title="Test",
                message="Test message",
                notification_type=NotificationType.ERROR,
                duration=4
            )

            result = system._show_windows_notification(notification)

            assert result is True
            mock_subprocess.assert_called_once()

            # Check PowerShell command
            call_args = mock_subprocess.call_args[0][0]
            assert 'powershell' in call_args
            assert '-Command' in call_args

    def test_stats_update_success(self, notification_system, sample_notification):
        """Test statistics update on successful notification."""
        initial_sent = notification_system.notification_stats['sent']
        initial_info = notification_system.notification_stats['by_type']['info']
        initial_normal = notification_system.notification_stats['by_priority']['normal']

        notification_system._update_stats(sample_notification, True)

        assert notification_system.notification_stats['sent'] == initial_sent + 1
        assert notification_system.notification_stats['by_type']['info'] == initial_info + 1
        assert notification_system.notification_stats['by_priority']['normal'] == initial_normal + 1

    def test_stats_update_failure(self, notification_system, sample_notification):
        """Test statistics update on failed notification."""
        initial_errors = notification_system.notification_stats['errors']

        notification_system._update_stats(sample_notification, False)

        assert notification_system.notification_stats['errors'] == initial_errors + 1

    def test_notify_recording_started(self, notification_system):
        """Test recording started notification."""
        with patch.object(notification_system, 'show_notification') as mock_show:
            mock_show.return_value = True

            result = notification_system.notify_recording_started()

            assert result is True
            mock_show.assert_called_once()

            # Check the notification properties
            notification = mock_show.call_args[0][0]
            assert "Recording started" in notification.message
            assert notification.category == "recording"
            assert len(notification.actions) > 0

    def test_notify_recording_stopped(self, notification_system):
        """Test recording stopped notification with duration."""
        with patch.object(notification_system, 'show_notification') as mock_show:
            mock_show.return_value = True

            result = notification_system.notify_recording_stopped(duration_seconds=90)

            assert result is True
            mock_show.assert_called_once()

            notification = mock_show.call_args[0][0]
            assert "1m 30s" in notification.message
            assert notification.category == "recording"
            assert notification.sound is False  # Should be non-intrusive

    def test_notify_processing_complete(self, notification_system):
        """Test processing complete notification."""
        test_title = "My Voice Note"
        test_path = "/path/to/note.md"

        with patch.object(notification_system, 'show_notification') as mock_show:
            mock_show.return_value = True

            result = notification_system.notify_processing_complete(
                note_title=test_title,
                file_path=test_path
            )

            assert result is True
            mock_show.assert_called_once()

            notification = mock_show.call_args[0][0]
            assert test_title in notification.message
            assert notification.notification_type == NotificationType.SUCCESS
            assert len(notification.actions) == 2  # Open Note and Open Folder

    def test_notify_error_with_recovery(self, notification_system):
        """Test error notification with recovery options."""
        error_title = "Recording Failed"
        error_message = "Microphone not available"

        with patch.object(notification_system, 'show_notification') as mock_show:
            mock_show.return_value = True

            result = notification_system.notify_error_with_recovery(error_title, error_message)

            assert result is True
            mock_show.assert_called_once()

            notification = mock_show.call_args[0][0]
            assert notification.title == error_title
            assert error_message in notification.message
            assert notification.notification_type == NotificationType.ERROR
            assert notification.priority == NotificationPriority.HIGH
            assert notification.persistent is True
            assert len(notification.actions) > 0

    def test_notify_fallback_mode(self, notification_system):
        """Test fallback mode notification."""
        service_name = "Transcription Service"
        fallback_description = "local speech recognition"

        with patch.object(notification_system, 'show_notification') as mock_show:
            mock_show.return_value = True

            result = notification_system.notify_fallback_mode(service_name, fallback_description)

            assert result is True
            mock_show.assert_called_once()

            notification = mock_show.call_args[0][0]
            assert service_name in notification.message
            assert fallback_description in notification.message
            assert notification.notification_type == NotificationType.WARNING

    def test_notify_daily_summary(self, notification_system):
        """Test daily summary notification."""
        notes_count = 5
        total_duration = 3750  # 1h 2m 30s

        with patch.object(notification_system, 'show_notification') as mock_show:
            mock_show.return_value = True

            result = notification_system.notify_daily_summary(notes_count, total_duration)

            assert result is True
            mock_show.assert_called_once()

            notification = mock_show.call_args[0][0]
            assert "5 notes" in notification.message
            assert "1h 2m" in notification.message
            assert notification.category == "summary"

    def test_update_preferences(self, notification_system):
        """Test updating notification preferences."""
        new_preferences = {
            'enabled': False,
            'sound_enabled': False,
            'show_recording': False,
            'default_duration': 10,
            'non_intrusive': True
        }

        notification_system.update_preferences(new_preferences)

        assert notification_system.enabled is False
        assert notification_system.sound_enabled is False
        assert notification_system.show_recording_notifications is False
        assert notification_system.notification_duration == 10
        assert notification_system.non_intrusive_mode is True

    def test_get_stats(self, notification_system):
        """Test getting notification statistics."""
        stats = notification_system.get_stats()

        assert 'sent' in stats
        assert 'errors' in stats
        assert 'by_type' in stats
        assert 'by_priority' in stats
        assert 'system_available' in stats
        assert 'enabled' in stats
        assert 'platform' in stats

    def test_test_notifications(self, notification_system):
        """Test the notification testing functionality."""
        with patch.object(notification_system, 'show_notification') as mock_show:
            mock_show.return_value = True

            results = notification_system.test_notifications()

            assert len(results) == 4  # Info, Success, Warning, Error
            assert all(result['success'] for result in results)
            assert mock_show.call_count == 4

            # Check that all notification types were tested
            tested_types = [result['type'] for result in results]
            assert 'info' in tested_types
            assert 'success' in tested_types
            assert 'warning' in tested_types
            assert 'error' in tested_types

    def test_notification_type_filtering(self, notification_system):
        """Test filtering different notification types based on preferences."""
        # Disable error notifications
        notification_system.show_error_notifications = False

        error_notification = DesktopNotification(
            title="Error",
            message="Error message",
            notification_type=NotificationType.ERROR
        )

        result = notification_system.show_notification(error_notification)
        assert result is False

        # Enable error notifications, should show
        notification_system.show_error_notifications = True
        notification_system.system_notifications_available = False  # Skip system notification

        result = notification_system.show_notification(error_notification)
        assert result is False  # Still false because system notifications unavailable

        # Test with system notifications available
        with patch.object(notification_system, '_show_system_notification', return_value=True):
            notification_system.system_notifications_available = True
            result = notification_system.show_notification(error_notification)
            assert result is True


class TestDesktopNotificationDataClass:
    """Test DesktopNotification data class."""

    def test_desktop_notification_creation(self):
        """Test creating DesktopNotification with defaults."""
        notification = DesktopNotification(
            title="Test",
            message="Test message"
        )

        assert notification.title == "Test"
        assert notification.message == "Test message"
        assert notification.notification_type == NotificationType.INFO
        assert notification.priority == NotificationPriority.NORMAL
        assert notification.duration == 4
        assert notification.sound is True
        assert notification.actions == []
        assert notification.icon_path is None
        assert isinstance(notification.timestamp, datetime)
        assert notification.persistent is False
        assert notification.category == "voice_notes"

    def test_desktop_notification_custom_values(self):
        """Test creating DesktopNotification with custom values."""
        custom_timestamp = datetime(2023, 1, 1, 12, 0, 0)
        custom_actions = [{'label': 'Test', 'action': 'test'}]

        notification = DesktopNotification(
            title="Custom Test",
            message="Custom message",
            notification_type=NotificationType.WARNING,
            priority=NotificationPriority.HIGH,
            duration=10,
            sound=False,
            actions=custom_actions,
            icon_path="/path/to/icon.png",
            timestamp=custom_timestamp,
            persistent=True,
            category="custom"
        )

        assert notification.title == "Custom Test"
        assert notification.message == "Custom message"
        assert notification.notification_type == NotificationType.WARNING
        assert notification.priority == NotificationPriority.HIGH
        assert notification.duration == 10
        assert notification.sound is False
        assert notification.actions == custom_actions
        assert notification.icon_path == "/path/to/icon.png"
        assert notification.timestamp == custom_timestamp
        assert notification.persistent is True
        assert notification.category == "custom"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])