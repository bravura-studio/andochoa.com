"""
Desktop Notification System for Voice Notes.

Provides comprehensive system notifications for all status updates including
recording start/stop, processing complete, error notifications, and user preferences.
"""

import logging
import platform
import subprocess
import sys
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

try:
    from .error_notifications import ErrorNotificationSystem, UserNotification, NotificationType
except ImportError:
    # Fallback for when running as standalone script or in tests
    from error_notifications import ErrorNotificationSystem, UserNotification, NotificationType

logger = logging.getLogger(__name__)


class NotificationPriority(Enum):
    """Priority levels for notifications."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DesktopNotification:
    """Desktop notification with enhanced features."""
    title: str
    message: str
    notification_type: NotificationType = NotificationType.INFO
    priority: NotificationPriority = NotificationPriority.NORMAL
    duration: int = 4  # seconds
    sound: bool = True
    actions: List[Dict[str, str]] = field(default_factory=list)
    icon_path: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    persistent: bool = False
    category: str = "voice_notes"


class DesktopNotificationSystem:
    """
    Comprehensive desktop notification system for Voice Notes application.

    Handles all types of notifications including:
    - Recording status (start/stop)
    - Processing status updates
    - Error notifications with actions
    - Success notifications
    - Configurable user preferences
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize desktop notification system.

        Args:
            config: Application configuration dictionary
        """
        self.config = config or {}
        self.notification_config = self.config.get('notifications', {})

        # Notification preferences
        self.enabled = self.notification_config.get('enabled', True)
        self.sound_enabled = self.notification_config.get('sound_enabled', True)
        self.show_recording_notifications = self.notification_config.get('show_recording', True)
        self.show_processing_notifications = self.notification_config.get('show_processing', True)
        self.show_error_notifications = self.notification_config.get('show_errors', True)
        self.show_success_notifications = self.notification_config.get('show_success', True)
        self.notification_duration = self.notification_config.get('default_duration', 4)
        self.non_intrusive_mode = self.notification_config.get('non_intrusive', False)

        # System capability detection
        self.system_notifications_available = self._detect_system_notification_support()
        self.platform = platform.system().lower()

        # Error notification system integration
        self.error_system = ErrorNotificationSystem(config)
        self.error_system.add_notification_callback(self._handle_error_notification)

        # Notification callbacks
        self.notification_callbacks: List[Callable[[DesktopNotification], None]] = []

        # Statistics tracking
        self.notification_stats = {
            'sent': 0,
            'errors': 0,
            'by_type': {t.value: 0 for t in NotificationType},
            'by_priority': {p.value: 0 for p in NotificationPriority}
        }

        logger.info(f"Desktop notification system initialized. Available: {self.system_notifications_available}")

    def _detect_system_notification_support(self) -> bool:
        """Detect if system notifications are supported on this platform."""
        system = platform.system().lower()

        try:
            if system == "darwin":  # macOS
                # Check for osascript (AppleScript) support
                result = subprocess.run(
                    ['osascript', '-e', 'return'],
                    capture_output=True,
                    timeout=2,
                    check=True
                )
                return True
            elif system == "linux":
                # Check for notify-send
                result = subprocess.run(
                    ['which', 'notify-send'],
                    capture_output=True,
                    timeout=2,
                    check=True
                )
                return True
            elif system == "windows":
                # Windows 10+ has built-in notification support
                return True

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning(f"System notifications not available on {system}")

        return False

    def add_notification_callback(self, callback: Callable[[DesktopNotification], None]):
        """
        Add callback for notification events.

        Args:
            callback: Function to call when notifications are shown
        """
        self.notification_callbacks.append(callback)

    def show_notification(self, notification: DesktopNotification) -> bool:
        """
        Display a desktop notification.

        Args:
            notification: Notification to display

        Returns:
            True if notification was shown successfully
        """
        if not self.enabled:
            return False

        # Check type-specific preferences
        if not self._should_show_notification(notification):
            return False

        try:
            # Apply non-intrusive mode adjustments
            if self.non_intrusive_mode:
                notification = self._make_non_intrusive(notification)

            # Call registered callbacks first
            for callback in self.notification_callbacks:
                try:
                    callback(notification)
                except Exception as e:
                    logger.error(f"Error in notification callback: {e}")

            # Show system notification
            success = self._show_system_notification(notification)

            # Update statistics
            self._update_stats(notification, success)

            if success:
                logger.debug(f"Notification shown: {notification.title}")

            return success

        except Exception as e:
            logger.error(f"Error showing notification: {e}")
            self._update_stats(notification, False)
            return False

    def _should_show_notification(self, notification: DesktopNotification) -> bool:
        """Check if notification should be shown based on user preferences."""
        if notification.notification_type == NotificationType.ERROR and not self.show_error_notifications:
            return False
        elif notification.notification_type == NotificationType.SUCCESS and not self.show_success_notifications:
            return False
        elif notification.category == "recording" and not self.show_recording_notifications:
            return False
        elif notification.category == "processing" and not self.show_processing_notifications:
            return False

        return True

    def _make_non_intrusive(self, notification: DesktopNotification) -> DesktopNotification:
        """Adjust notification to be less intrusive."""
        # Reduce duration
        notification.duration = min(notification.duration, 2)
        # Disable sound for non-critical notifications
        if notification.priority != NotificationPriority.CRITICAL:
            notification.sound = False
        # Remove actions for quick notifications
        if notification.priority == NotificationPriority.LOW:
            notification.actions = []

        return notification

    def _show_system_notification(self, notification: DesktopNotification) -> bool:
        """Show system notification using platform-specific method."""
        if not self.system_notifications_available:
            logger.debug("System notifications not available, skipping")
            return False

        try:
            if self.platform == "darwin":
                return self._show_macos_notification(notification)
            elif self.platform == "linux":
                return self._show_linux_notification(notification)
            elif self.platform == "windows":
                return self._show_windows_notification(notification)
            else:
                logger.warning(f"Unsupported platform: {self.platform}")
                return False

        except Exception as e:
            logger.error(f"Failed to show system notification: {e}")
            return False

    def _show_macos_notification(self, notification: DesktopNotification) -> bool:
        """Show macOS notification using osascript."""
        sound_clause = ""
        if notification.sound and self.sound_enabled:
            # Different sounds for different notification types
            sound_map = {
                NotificationType.ERROR: "Basso",
                NotificationType.WARNING: "Sosumi",
                NotificationType.SUCCESS: "Glass",
                NotificationType.INFO: "Blow"
            }
            sound = sound_map.get(notification.notification_type, "Glass")
            sound_clause = f'sound name "{sound}"'

        # Create AppleScript
        script = f'''
        display notification "{notification.message}" ¬
        with title "{notification.title}" ¬
        {sound_clause}
        '''

        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            timeout=5,
            text=True
        )

        return result.returncode == 0

    def _show_linux_notification(self, notification: DesktopNotification) -> bool:
        """Show Linux notification using notify-send."""
        # Map priority to urgency
        urgency_map = {
            NotificationPriority.LOW: "low",
            NotificationPriority.NORMAL: "normal",
            NotificationPriority.HIGH: "normal",
            NotificationPriority.CRITICAL: "critical"
        }
        urgency = urgency_map.get(notification.priority, "normal")

        # Map type to icon
        icon_map = {
            NotificationType.ERROR: "dialog-error",
            NotificationType.WARNING: "dialog-warning",
            NotificationType.SUCCESS: "dialog-information",
            NotificationType.INFO: "dialog-information"
        }
        icon = icon_map.get(notification.notification_type, "dialog-information")

        cmd = [
            'notify-send',
            '--urgency', urgency,
            '--expire-time', str(notification.duration * 1000),
            '--icon', icon,
            '--category', notification.category,
            notification.title,
            notification.message
        ]

        result = subprocess.run(cmd, capture_output=True, timeout=5)
        return result.returncode == 0

    def _show_windows_notification(self, notification: DesktopNotification) -> bool:
        """Show Windows notification using PowerShell."""
        # Map type to Windows icon
        icon_map = {
            NotificationType.ERROR: "Error",
            NotificationType.WARNING: "Warning",
            NotificationType.SUCCESS: "Info",
            NotificationType.INFO: "Info"
        }
        icon = icon_map.get(notification.notification_type, "Info")

        script = f'''
        Add-Type -AssemblyName System.Windows.Forms
        $notify = New-Object System.Windows.Forms.NotifyIcon
        $notify.Icon = [System.Drawing.SystemIcons]::{icon}
        $notify.Visible = $true
        $notify.ShowBalloonTip(
            {notification.duration * 1000},
            "{notification.title}",
            "{notification.message}",
            [System.Windows.Forms.ToolTipIcon]::{icon}
        )
        Start-Sleep -Seconds {notification.duration}
        $notify.Dispose()
        '''

        result = subprocess.run(
            ['powershell', '-Command', script],
            capture_output=True,
            timeout=notification.duration + 2
        )

        return result.returncode == 0

    def _handle_error_notification(self, user_notification: UserNotification):
        """Handle error notifications from the error system."""
        # Convert to desktop notification
        desktop_notification = DesktopNotification(
            title=user_notification.title,
            message=user_notification.message,
            notification_type=user_notification.notification_type,
            duration=user_notification.duration,
            actions=user_notification.actions,
            persistent=user_notification.persistent,
            priority=NotificationPriority.HIGH if user_notification.notification_type == NotificationType.ERROR else NotificationPriority.NORMAL,
            category="error"
        )

        self.show_notification(desktop_notification)

    def _update_stats(self, notification: DesktopNotification, success: bool):
        """Update notification statistics."""
        if success:
            self.notification_stats['sent'] += 1
            self.notification_stats['by_type'][notification.notification_type.value] += 1
            self.notification_stats['by_priority'][notification.priority.value] += 1
        else:
            self.notification_stats['errors'] += 1

    # Convenience methods for common notification types

    def notify_recording_started(self):
        """Show notification when recording starts."""
        notification = DesktopNotification(
            title="Voice Notes",
            message="🎤 Recording started. Press hotkey again or ESC to stop.",
            notification_type=NotificationType.INFO,
            priority=NotificationPriority.NORMAL,
            duration=3,
            category="recording",
            actions=[
                {'label': 'Stop Recording', 'action': 'stop_recording'}
            ]
        )
        return self.show_notification(notification)

    def notify_recording_stopped(self, duration_seconds: int = None):
        """Show notification when recording stops."""
        message = "🛑 Recording stopped. Processing your voice note..."
        if duration_seconds:
            mins = duration_seconds // 60
            secs = duration_seconds % 60
            if mins > 0:
                message = f"🛑 Recording stopped ({mins}m {secs}s). Processing your voice note..."
            else:
                message = f"🛑 Recording stopped ({secs}s). Processing your voice note..."

        notification = DesktopNotification(
            title="Voice Notes",
            message=message,
            notification_type=NotificationType.INFO,
            priority=NotificationPriority.LOW,
            duration=2,
            category="recording",
            sound=False  # Less intrusive for stop
        )
        return self.show_notification(notification)

    def notify_processing_started(self):
        """Show notification when processing begins."""
        notification = DesktopNotification(
            title="Voice Notes",
            message="🔄 Processing your voice note...",
            notification_type=NotificationType.INFO,
            priority=NotificationPriority.LOW,
            duration=2,
            category="processing",
            sound=False
        )
        return self.show_notification(notification)

    def notify_processing_complete(self, note_title: str = None, file_path: str = None):
        """Show notification when processing completes successfully."""
        message = "✅ Voice note saved successfully!"
        if note_title:
            message = f"✅ '{note_title}' saved successfully!"

        actions = []
        if file_path:
            actions = [
                {'label': 'Open Note', 'action': f'open_file:{file_path}'},
                {'label': 'Open Folder', 'action': f'open_folder:{Path(file_path).parent}'}
            ]

        notification = DesktopNotification(
            title="Voice Notes",
            message=message,
            notification_type=NotificationType.SUCCESS,
            priority=NotificationPriority.NORMAL,
            duration=4,
            category="processing",
            actions=actions
        )
        return self.show_notification(notification)

    def notify_error_with_recovery(self, error_title: str, error_message: str):
        """Show error notification with recovery options."""
        notification = DesktopNotification(
            title=error_title,
            message=f"❌ {error_message}",
            notification_type=NotificationType.ERROR,
            priority=NotificationPriority.HIGH,
            duration=8,
            category="error",
            persistent=True,
            actions=[
                {'label': 'View Details', 'action': 'view_error_details'},
                {'label': 'Retry', 'action': 'retry_operation'}
            ]
        )
        return self.show_notification(notification)

    def notify_fallback_mode(self, service_name: str, fallback_description: str):
        """Show notification when entering fallback mode."""
        notification = DesktopNotification(
            title="Voice Notes - Fallback Mode",
            message=f"⚠️ {service_name} unavailable. Using {fallback_description}.",
            notification_type=NotificationType.WARNING,
            priority=NotificationPriority.NORMAL,
            duration=6,
            category="system",
            actions=[
                {'label': 'View Details', 'action': 'view_service_status'}
            ]
        )
        return self.show_notification(notification)

    def notify_daily_summary(self, notes_count: int, total_duration: int):
        """Show daily activity summary notification."""
        hours = total_duration // 3600
        minutes = (total_duration % 3600) // 60

        if hours > 0:
            time_str = f"{hours}h {minutes}m"
        else:
            time_str = f"{minutes}m"

        message = f"📊 Today: {notes_count} notes, {time_str} recorded"

        notification = DesktopNotification(
            title="Voice Notes Daily Summary",
            message=message,
            notification_type=NotificationType.INFO,
            priority=NotificationPriority.LOW,
            duration=5,
            category="summary",
            actions=[
                {'label': 'View All Notes', 'action': 'view_daily_notes'}
            ]
        )
        return self.show_notification(notification)

    def update_preferences(self, preferences: Dict[str, Any]):
        """Update notification preferences."""
        self.enabled = preferences.get('enabled', self.enabled)
        self.sound_enabled = preferences.get('sound_enabled', self.sound_enabled)
        self.show_recording_notifications = preferences.get('show_recording', self.show_recording_notifications)
        self.show_processing_notifications = preferences.get('show_processing', self.show_processing_notifications)
        self.show_error_notifications = preferences.get('show_errors', self.show_error_notifications)
        self.show_success_notifications = preferences.get('show_success', self.show_success_notifications)
        self.notification_duration = preferences.get('default_duration', self.notification_duration)
        self.non_intrusive_mode = preferences.get('non_intrusive', self.non_intrusive_mode)

        logger.info("Notification preferences updated")

    def get_stats(self) -> Dict[str, Any]:
        """Get notification statistics."""
        return {
            **self.notification_stats,
            'system_available': self.system_notifications_available,
            'enabled': self.enabled,
            'platform': self.platform
        }

    def test_notifications(self):
        """Test notification system with sample notifications."""
        test_notifications = [
            DesktopNotification(
                title="Test - Info",
                message="This is an info notification test",
                notification_type=NotificationType.INFO,
                duration=2
            ),
            DesktopNotification(
                title="Test - Success",
                message="This is a success notification test",
                notification_type=NotificationType.SUCCESS,
                duration=2
            ),
            DesktopNotification(
                title="Test - Warning",
                message="This is a warning notification test",
                notification_type=NotificationType.WARNING,
                duration=3
            ),
            DesktopNotification(
                title="Test - Error",
                message="This is an error notification test",
                notification_type=NotificationType.ERROR,
                priority=NotificationPriority.HIGH,
                duration=3
            )
        ]

        results = []
        for notification in test_notifications:
            success = self.show_notification(notification)
            results.append({
                'type': notification.notification_type.value,
                'success': success
            })

        return results