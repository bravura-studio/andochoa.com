"""
User-friendly error notification system.

Provides clear, actionable error messages and system notifications for users.
"""

import logging
import platform
import subprocess
import sys
from typing import Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

try:
    from .error_recovery import ErrorType, ErrorSeverity, ErrorInfo
except ImportError:
    # Fallback for when running as standalone script or in tests
    from error_recovery import ErrorType, ErrorSeverity, ErrorInfo

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of notifications."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class UserNotification:
    """User-friendly notification."""
    title: str
    message: str
    notification_type: NotificationType
    timestamp: datetime
    actions: List[Dict[str, str]] = None  # List of action buttons/links
    duration: int = 5  # seconds
    persistent: bool = False  # Whether notification persists until dismissed

    def __post_init__(self):
        if self.actions is None:
            self.actions = []


class ErrorNotificationSystem:
    """System for generating and displaying user-friendly error notifications."""

    def __init__(self, config: Dict = None):
        """Initialize notification system.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.notification_config = self.config.get('error_recovery', {}).get('notifications', {})

        # Notification settings
        self.show_user_messages = self.notification_config.get('show_user_messages', True)
        self.system_notifications = self.notification_config.get('system_notifications', True)
        self.notify_levels = self.notification_config.get('notify_levels', ['medium', 'high', 'critical'])

        # Callbacks for different notification methods
        self.notification_callbacks: List[Callable[[UserNotification], None]] = []
        self.system_notification_available = self._check_system_notification_support()

        logger.info(f"Error notification system initialized. System notifications: {self.system_notification_available}")

    def _check_system_notification_support(self) -> bool:
        """Check if system notifications are supported on this platform."""
        system = platform.system().lower()

        try:
            if system == "darwin":  # macOS
                # Check if osascript is available
                subprocess.run(['osascript', '-e', 'return'],
                             capture_output=True, check=True, timeout=2)
                return True
            elif system == "linux":
                # Check if notify-send is available
                subprocess.run(['which', 'notify-send'],
                             capture_output=True, check=True, timeout=2)
                return True
            elif system == "windows":
                # Windows 10/11 has built-in toast notifications
                return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return False

    def add_notification_callback(self, callback: Callable[[UserNotification], None]):
        """Add a callback for handling notifications.

        Args:
            callback: Function to call with UserNotification objects
        """
        self.notification_callbacks.append(callback)

    def create_error_notification(self, error_info: ErrorInfo) -> Optional[UserNotification]:
        """Create a user-friendly notification from error info.

        Args:
            error_info: Error information

        Returns:
            UserNotification or None if notification not needed
        """
        if not self.show_user_messages:
            return None

        if error_info.severity.value not in self.notify_levels:
            return None

        # Generate appropriate notification based on error type and context
        notification = self._generate_notification(error_info)

        return notification

    def _generate_notification(self, error_info: ErrorInfo) -> UserNotification:
        """Generate notification content based on error information."""
        title, message, actions, persistent = self._get_error_content(error_info)

        notification_type = self._map_severity_to_type(error_info.severity)
        duration = self._get_duration_for_severity(error_info.severity)

        return UserNotification(
            title=title,
            message=message,
            notification_type=notification_type,
            timestamp=error_info.timestamp,
            actions=actions,
            duration=duration,
            persistent=persistent
        )

    def _get_error_content(self, error_info: ErrorInfo) -> tuple:
        """Get title, message, actions, and persistence for error notification."""
        error_templates = {
            ErrorType.AUDIO_RECORDING: {
                'title': 'Recording Error',
                'messages': {
                    'device': {
                        'message': 'Microphone not detected. Please check your audio device connections.',
                        'actions': [
                            {'label': 'Check Settings', 'action': 'open_audio_settings'},
                            {'label': 'Test Microphone', 'action': 'test_microphone'}
                        ]
                    },
                    'permission': {
                        'message': 'Microphone access denied. Please enable microphone permissions.',
                        'actions': [
                            {'label': 'Open Privacy Settings', 'action': 'open_privacy_settings'},
                            {'label': 'Retry', 'action': 'retry_recording'}
                        ]
                    },
                    'default': {
                        'message': 'Failed to record audio. Please check your microphone.',
                        'actions': [
                            {'label': 'Retry Recording', 'action': 'retry_recording'},
                            {'label': 'Check Settings', 'action': 'open_settings'}
                        ]
                    }
                }
            },
            ErrorType.TRANSCRIPTION: {
                'title': 'Transcription Error',
                'messages': {
                    'api': {
                        'message': 'Transcription service unavailable. Using backup method.',
                        'actions': [
                            {'label': 'View Details', 'action': 'view_error_details'}
                        ]
                    },
                    'cost': {
                        'message': 'Daily transcription limit reached. Try again tomorrow or check your usage.',
                        'actions': [
                            {'label': 'View Usage', 'action': 'view_usage'},
                            {'label': 'Adjust Limits', 'action': 'adjust_cost_limits'}
                        ],
                        'persistent': True
                    },
                    'network': {
                        'message': 'Network connection issue. Retrying transcription...',
                        'actions': [
                            {'label': 'Check Connection', 'action': 'check_network'},
                            {'label': 'Use Offline Mode', 'action': 'enable_offline_mode'}
                        ]
                    },
                    'default': {
                        'message': 'Failed to transcribe audio. The recording was saved and will be retried.',
                        'actions': [
                            {'label': 'Retry Now', 'action': 'retry_transcription'},
                            {'label': 'View Queue', 'action': 'view_recovery_queue'}
                        ]
                    }
                }
            },
            ErrorType.MCP_CONNECTION: {
                'title': 'Conversation Service Error',
                'messages': {
                    'timeout': {
                        'message': 'Conversation service timed out. Your note was saved with the transcript.',
                        'actions': [
                            {'label': 'View Note', 'action': 'view_last_note'},
                            {'label': 'Retry Later', 'action': 'retry_conversation'}
                        ]
                    },
                    'auth': {
                        'message': 'Authentication failed. Please check your MCP server configuration.',
                        'actions': [
                            {'label': 'Check Settings', 'action': 'open_mcp_settings'},
                            {'label': 'Use Offline Mode', 'action': 'enable_offline_mode'}
                        ]
                    },
                    'default': {
                        'message': 'Could not connect to conversation service. Using basic note format.',
                        'actions': [
                            {'label': 'View Note', 'action': 'view_last_note'},
                            {'label': 'Check Connection', 'action': 'test_mcp_connection'}
                        ]
                    }
                }
            },
            ErrorType.FILE_SAVE: {
                'title': 'Save Error',
                'messages': {
                    'disk': {
                        'message': 'Not enough disk space. Please free up space and try again.',
                        'actions': [
                            {'label': 'Open Disk Utility', 'action': 'open_disk_utility'},
                            {'label': 'Change Location', 'action': 'change_save_location'}
                        ],
                        'persistent': True
                    },
                    'permission': {
                        'message': 'Permission denied. Please check folder permissions.',
                        'actions': [
                            {'label': 'Choose New Location', 'action': 'choose_save_location'},
                            {'label': 'Fix Permissions', 'action': 'fix_permissions'}
                        ]
                    },
                    'default': {
                        'message': 'Failed to save voice note. Your recording is queued for retry.',
                        'actions': [
                            {'label': 'Retry Save', 'action': 'retry_save'},
                            {'label': 'Change Location', 'action': 'change_save_location'}
                        ]
                    }
                }
            },
            ErrorType.NETWORK: {
                'title': 'Network Error',
                'messages': {
                    'timeout': {
                        'message': 'Request timed out. Your recording is saved and will be processed when connection improves.',
                        'actions': [
                            {'label': 'Check Connection', 'action': 'check_network'},
                            {'label': 'Use Offline Mode', 'action': 'enable_offline_mode'}
                        ]
                    },
                    'dns': {
                        'message': 'DNS resolution failed. Please check your network settings.',
                        'actions': [
                            {'label': 'Network Settings', 'action': 'open_network_settings'},
                            {'label': 'Use Offline Mode', 'action': 'enable_offline_mode'}
                        ]
                    },
                    'default': {
                        'message': 'Network connection issue. Operating in offline mode.',
                        'actions': [
                            {'label': 'Retry Connection', 'action': 'retry_connection'},
                            {'label': 'View Offline Notes', 'action': 'view_offline_notes'}
                        ]
                    }
                }
            },
            ErrorType.SYSTEM: {
                'title': 'System Error',
                'messages': {
                    'default': {
                        'message': 'A system error occurred. The application will attempt to recover automatically.',
                        'actions': [
                            {'label': 'View Error Log', 'action': 'view_error_log'},
                            {'label': 'Restart Application', 'action': 'restart_app'}
                        ]
                    }
                }
            },
            ErrorType.CONFIGURATION: {
                'title': 'Configuration Error',
                'messages': {
                    'default': {
                        'message': 'Configuration issue detected. Please check your settings.',
                        'actions': [
                            {'label': 'Open Settings', 'action': 'open_settings'},
                            {'label': 'Reset to Defaults', 'action': 'reset_config'}
                        ]
                    }
                }
            }
        }

        # Get template for error type
        template = error_templates.get(error_info.error_type, error_templates[ErrorType.SYSTEM])
        title = template['title']

        # Find best matching message template
        error_str = error_info.message.lower()
        message_templates = template['messages']

        # Try to match specific error patterns
        for pattern, content in message_templates.items():
            if pattern != 'default' and pattern in error_str:
                return (
                    title,
                    content['message'],
                    content.get('actions', []),
                    content.get('persistent', False)
                )

        # Use default template
        default_content = message_templates['default']
        return (
            title,
            default_content['message'],
            default_content.get('actions', []),
            default_content.get('persistent', False)
        )

    def _map_severity_to_type(self, severity: ErrorSeverity) -> NotificationType:
        """Map error severity to notification type."""
        mapping = {
            ErrorSeverity.LOW: NotificationType.INFO,
            ErrorSeverity.MEDIUM: NotificationType.WARNING,
            ErrorSeverity.HIGH: NotificationType.ERROR,
            ErrorSeverity.CRITICAL: NotificationType.ERROR
        }
        return mapping.get(severity, NotificationType.WARNING)

    def _get_duration_for_severity(self, severity: ErrorSeverity) -> int:
        """Get notification duration based on severity."""
        durations = {
            ErrorSeverity.LOW: 3,
            ErrorSeverity.MEDIUM: 5,
            ErrorSeverity.HIGH: 8,
            ErrorSeverity.CRITICAL: 10
        }
        return durations.get(severity, 5)

    def show_notification(self, notification: UserNotification):
        """Display notification to user using available methods."""
        # Call registered callbacks
        for callback in self.notification_callbacks:
            try:
                callback(notification)
            except Exception as e:
                logger.error(f"Error in notification callback: {e}")

        # Show system notification if enabled and available
        if self.system_notifications and self.system_notification_available:
            self._show_system_notification(notification)

    def _show_system_notification(self, notification: UserNotification):
        """Show system notification using platform-specific method."""
        if not self.system_notification_available:
            return

        try:
            system = platform.system().lower()

            if system == "darwin":  # macOS
                self._show_macos_notification(notification)
            elif system == "linux":
                self._show_linux_notification(notification)
            elif system == "windows":
                self._show_windows_notification(notification)

        except Exception as e:
            logger.warning(f"Failed to show system notification: {e}")

    def _show_macos_notification(self, notification: UserNotification):
        """Show macOS notification using osascript."""
        script = f'''
        display notification "{notification.message}" ¬
        with title "{notification.title}" ¬
        sound name "Glass"
        '''

        subprocess.run(['osascript', '-e', script],
                      capture_output=True, timeout=5)

    def _show_linux_notification(self, notification: UserNotification):
        """Show Linux notification using notify-send."""
        urgency = "normal"
        if notification.notification_type == NotificationType.ERROR:
            urgency = "critical"
        elif notification.notification_type == NotificationType.WARNING:
            urgency = "normal"

        subprocess.run([
            'notify-send',
            '--urgency', urgency,
            '--expire-time', str(notification.duration * 1000),
            notification.title,
            notification.message
        ], capture_output=True, timeout=5)

    def _show_windows_notification(self, notification: UserNotification):
        """Show Windows notification using PowerShell."""
        # Create Windows toast notification
        script = f'''
        Add-Type -AssemblyName System.Windows.Forms
        $notify = New-Object System.Windows.Forms.NotifyIcon
        $notify.Icon = [System.Drawing.SystemIcons]::Information
        $notify.Visible = $true
        $notify.ShowBalloonTip(
            {notification.duration * 1000},
            "{notification.title}",
            "{notification.message}",
            [System.Windows.Forms.ToolTipIcon]::Info
        )
        Start-Sleep -Seconds {notification.duration}
        $notify.Dispose()
        '''

        subprocess.run([
            'powershell', '-Command', script
        ], capture_output=True, timeout=notification.duration + 2)

    def create_success_notification(self, title: str, message: str, actions: List[Dict[str, str]] = None) -> UserNotification:
        """Create a success notification.

        Args:
            title: Notification title
            message: Notification message
            actions: Optional list of action buttons

        Returns:
            UserNotification object
        """
        return UserNotification(
            title=title,
            message=message,
            notification_type=NotificationType.SUCCESS,
            timestamp=datetime.now(),
            actions=actions or [],
            duration=3,
            persistent=False
        )

    def create_info_notification(self, title: str, message: str, actions: List[Dict[str, str]] = None) -> UserNotification:
        """Create an info notification.

        Args:
            title: Notification title
            message: Notification message
            actions: Optional list of action buttons

        Returns:
            UserNotification object
        """
        return UserNotification(
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            timestamp=datetime.now(),
            actions=actions or [],
            duration=4,
            persistent=False
        )

    def notify_recording_started(self):
        """Show notification when recording starts."""
        notification = self.create_info_notification(
            title="Voice Notes",
            message="Recording started. Press the hotkey again or ESC to stop.",
            actions=[
                {'label': 'Stop Recording', 'action': 'stop_recording'}
            ]
        )
        self.show_notification(notification)

    def notify_recording_stopped(self):
        """Show notification when recording stops."""
        notification = self.create_info_notification(
            title="Voice Notes",
            message="Recording stopped. Processing your voice note...",
            actions=[]
        )
        self.show_notification(notification)

    def notify_processing_complete(self, file_path: str):
        """Show notification when processing completes successfully."""
        notification = self.create_success_notification(
            title="Voice Notes",
            message="Voice note saved successfully!",
            actions=[
                {'label': 'Open Note', 'action': f'open_file:{file_path}'},
                {'label': 'Open Folder', 'action': f'open_folder:{file_path}'}
            ]
        )
        self.show_notification(notification)

    def notify_degraded_mode(self, unavailable_services: List[str]):
        """Show notification when app enters degraded mode."""
        services_str = ", ".join(unavailable_services)
        notification = UserNotification(
            title="Voice Notes - Limited Mode",
            message=f"Some services are unavailable: {services_str}. Basic functionality is still available.",
            notification_type=NotificationType.WARNING,
            timestamp=datetime.now(),
            actions=[
                {'label': 'View Details', 'action': 'view_service_status'},
                {'label': 'Try Full Restart', 'action': 'restart_app'}
            ],
            duration=8,
            persistent=True
        )
        self.show_notification(notification)

    def get_recovery_summary_notification(self, recovery_summary: Dict) -> UserNotification:
        """Create notification summarizing recovery queue processing."""
        if recovery_summary['succeeded'] > 0:
            title = "Recovery Complete"
            message = f"Successfully recovered {recovery_summary['succeeded']} failed operations."
            notification_type = NotificationType.SUCCESS
        elif recovery_summary['failed'] > 0:
            title = "Recovery Issues"
            message = f"{recovery_summary['failed']} operations could not be recovered."
            notification_type = NotificationType.WARNING
        else:
            # No operations to report
            return None

        return UserNotification(
            title=title,
            message=message,
            notification_type=notification_type,
            timestamp=datetime.now(),
            actions=[
                {'label': 'View Details', 'action': 'view_recovery_status'}
            ],
            duration=5,
            persistent=False
        )