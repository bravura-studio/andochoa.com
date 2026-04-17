#!/usr/bin/env python3
"""
Demo script for desktop notification system.

Run this script to test the notification system with sample notifications.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from desktop_notifications import DesktopNotificationSystem, DesktopNotification, NotificationType, NotificationPriority


def main():
    """Demonstrate desktop notification system."""
    print("🔔 Desktop Notification System Demo")
    print("=" * 40)

    # Create notification system with demo config
    config = {
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

    try:
        notification_system = DesktopNotificationSystem(config)

        print(f"✅ Notification system initialized")
        print(f"📱 Platform: {notification_system.platform}")
        print(f"🔔 System notifications available: {notification_system.system_notifications_available}")
        print()

        # Test various notification types
        print("🧪 Testing notification types...")
        print()

        # 1. Recording started notification
        print("1️⃣ Testing recording started notification...")
        result1 = notification_system.notify_recording_started()
        print(f"   Result: {'✅ Success' if result1 else '❌ Failed'}")
        time.sleep(2)

        # 2. Recording stopped notification
        print("2️⃣ Testing recording stopped notification...")
        result2 = notification_system.notify_recording_stopped(duration_seconds=45)
        print(f"   Result: {'✅ Success' if result2 else '❌ Failed'}")
        time.sleep(2)

        # 3. Processing started notification
        print("3️⃣ Testing processing started notification...")
        result3 = notification_system.notify_processing_started()
        print(f"   Result: {'✅ Success' if result3 else '❌ Failed'}")
        time.sleep(2)

        # 4. Processing complete notification
        print("4️⃣ Testing processing complete notification...")
        result4 = notification_system.notify_processing_complete(
            note_title="Demo Voice Note",
            file_path="/Users/demo/Documents/Voice Notes/2023-12-01_demo_note.md"
        )
        print(f"   Result: {'✅ Success' if result4 else '❌ Failed'}")
        time.sleep(2)

        # 5. Error notification
        print("5️⃣ Testing error notification...")
        result5 = notification_system.notify_error_with_recovery(
            error_title="Demo Error",
            error_message="This is a demonstration error message"
        )
        print(f"   Result: {'✅ Success' if result5 else '❌ Failed'}")
        time.sleep(2)

        # 6. Fallback mode notification
        print("6️⃣ Testing fallback mode notification...")
        result6 = notification_system.notify_fallback_mode(
            service_name="Transcription Service",
            fallback_description="local speech recognition"
        )
        print(f"   Result: {'✅ Success' if result6 else '❌ Failed'}")
        time.sleep(2)

        # 7. Daily summary notification
        print("7️⃣ Testing daily summary notification...")
        result7 = notification_system.notify_daily_summary(
            notes_count=8,
            total_duration=1800  # 30 minutes
        )
        print(f"   Result: {'✅ Success' if result7 else '❌ Failed'}")
        time.sleep(2)

        # 8. Custom notification
        print("8️⃣ Testing custom notification...")
        custom_notification = DesktopNotification(
            title="Custom Demo Notification",
            message="This is a custom notification with actions",
            notification_type=NotificationType.INFO,
            priority=NotificationPriority.NORMAL,
            duration=5,
            category="demo",
            actions=[
                {'label': 'View Details', 'action': 'view_details'},
                {'label': 'Dismiss', 'action': 'dismiss'}
            ]
        )
        result8 = notification_system.show_notification(custom_notification)
        print(f"   Result: {'✅ Success' if result8 else '❌ Failed'}")
        time.sleep(2)

        print()
        print("📊 Final Statistics:")
        stats = notification_system.get_stats()
        print(f"   Notifications sent: {stats['sent']}")
        print(f"   Errors: {stats['errors']}")
        print(f"   By type: {stats['by_type']}")
        print(f"   By priority: {stats['by_priority']}")

        # Test system notification functionality
        print()
        print("🧪 Testing system notification methods...")
        test_results = notification_system.test_notifications()
        print("Test results:")
        for result in test_results:
            status = "✅" if result['success'] else "❌"
            print(f"   {result['type']}: {status}")

        print()
        print("🎉 Demo completed successfully!")

    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()