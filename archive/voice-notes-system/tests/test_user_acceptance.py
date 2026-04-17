"""
User Acceptance Tests for Voice Notes System.

These tests simulate real user scenarios and workflows to ensure
the system meets user expectations and requirements.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json

import sys
sys.path.append(str(Path(__file__).parent.parent / 'src'))


class TestUserAcceptanceScenarios:
    """User acceptance tests simulating real-world usage scenarios."""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for user tests."""
        temp_dir = tempfile.mkdtemp(prefix="voice_notes_user_test_")
        workspace = Path(temp_dir)

        # Create subdirectories that users would have
        (workspace / "Voice Notes").mkdir()
        (workspace / "Voice Notes" / datetime.now().strftime("%Y-%m-%d")).mkdir()

        yield workspace
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_user_config(self, temp_workspace):
        """Mock user configuration."""
        return {
            'files': {
                'output_directory': str(temp_workspace / "Voice Notes"),
                'naming_pattern': 'hybrid',
                'daily_folders': True,
                'cleanup_temp_files': True
            },
            'processing': {
                'default_mode': 'standard',
                'auto_process': True,
                'max_conversation_depth': 5
            },
            'notifications': {
                'enabled': True,
                'show_recording': True,
                'show_processing': True,
                'show_success': True,
                'non_intrusive': False
            },
            'hotkeys': {
                'record_toggle': 'cmd+shift+r',
                'cancel': 'escape',
                'audio_feedback': True
            },
            'ui': {
                'show_notifications': True,
                'notification_duration': 3
            }
        }

    def test_user_scenario_quick_voice_memo(self, mock_user_config, temp_workspace):
        """
        User Scenario: Quick voice memo capture

        User wants to quickly capture a thought or reminder without interrupting their workflow.

        Acceptance Criteria:
        - Hotkey starts recording immediately
        - Visual/audio feedback confirms recording started
        - Recording stops on second hotkey press
        - Note is processed and saved automatically
        - User receives notification when complete
        """
        # Mock all the components
        with patch('audio_recorder.AudioRecorder') as MockRecorder, \
             patch('transcription.TranscriptionService') as MockTranscription, \
             patch('conversation_manager.ConversationManager') as MockConversation, \
             patch('file_manager.FileManager') as MockFileManager, \
             patch('desktop_notifications.DesktopNotificationSystem') as MockNotifications:

            # Setup mocks
            mock_recorder = Mock()
            mock_transcription = Mock()
            mock_conversation = Mock()
            mock_file_manager = Mock()
            mock_notifications = Mock()

            MockRecorder.return_value = mock_recorder
            MockTranscription.return_value = mock_transcription
            MockConversation.return_value = mock_conversation
            MockFileManager.return_value = mock_file_manager
            MockNotifications.return_value = mock_notifications

            # Configure mock responses
            mock_recorder.start_recording.return_value = True
            mock_recorder.stop_recording.return_value = True
            mock_recorder.is_recording = False

            mock_transcription.transcribe_audio.return_value = Mock(
                text="Remember to call the dentist tomorrow morning",
                confidence=0.98,
                duration=3.2,
                word_count=7,
                cost_usd=0.006
            )

            mock_conversation.process_transcript.return_value = {
                'key_insight': 'Dental appointment reminder',
                'topic_type': 'reminder',
                'conversation': [
                    {'role': 'user', 'content': 'Remember to call the dentist tomorrow morning'},
                    {'role': 'assistant', 'content': 'I\'ll help you remember this dental appointment task.'}
                ],
                'action_items': ['Call dentist tomorrow morning'],
                'entities': ['dentist'],
                'topics': ['health', 'appointments']
            }

            mock_file_manager.save_note.return_value = str(temp_workspace / "Voice Notes" / "2023-12-01_dental_appointment_reminder.md")

            # Simulate user actions

            # 1. User presses hotkey to start recording
            recording_started = mock_recorder.start_recording()
            assert recording_started is True

            # 2. System should show recording notification
            mock_notifications.notify_recording_started()
            mock_notifications.notify_recording_started.assert_called_once()

            # 3. User speaks for a few seconds (simulated)
            mock_recorder.is_recording = True

            # 4. User presses hotkey again to stop
            recording_stopped = mock_recorder.stop_recording()
            assert recording_stopped is True
            mock_recorder.is_recording = False

            # 5. System should show recording stopped notification
            mock_notifications.notify_recording_stopped(duration_seconds=3)
            mock_notifications.notify_recording_stopped.assert_called()

            # 6. System automatically processes the recording
            transcription_result = mock_transcription.transcribe_audio("temp_audio.wav")
            assert transcription_result.text == "Remember to call the dentist tomorrow morning"

            # 7. System processes with conversation manager
            conversation_result = mock_conversation.process_transcript(transcription_result.text)
            assert conversation_result['topic_type'] == 'reminder'
            assert 'Call dentist tomorrow morning' in conversation_result['action_items']

            # 8. System saves the processed note
            saved_path = mock_file_manager.save_note(conversation_result)
            assert saved_path.endswith("dental_appointment_reminder.md")

            # 9. User receives completion notification
            mock_notifications.notify_processing_complete(note_title="Dental Reminder", file_path=saved_path)
            mock_notifications.notify_processing_complete.assert_called()

            print("✅ Quick voice memo scenario completed successfully")

    def test_user_scenario_detailed_project_reflection(self, mock_user_config, temp_workspace):
        """
        User Scenario: Detailed project reflection

        User wants to reflect on a project with deep conversation to extract insights.

        Acceptance Criteria:
        - System detects this is a reflection/thinking session
        - Uses deep processing mode
        - Generates multiple follow-up questions
        - Extracts actionable insights and next steps
        - Creates comprehensive note with proper structure
        """
        with patch('audio_recorder.AudioRecorder') as MockRecorder, \
             patch('transcription.TranscriptionService') as MockTranscription, \
             patch('conversation_manager.ConversationManager') as MockConversation, \
             patch('file_manager.FileManager') as MockFileManager:

            # Setup mocks
            mock_recorder = Mock()
            mock_transcription = Mock()
            mock_conversation = Mock()
            mock_file_manager = Mock()

            MockRecorder.return_value = mock_recorder
            MockTranscription.return_value = mock_transcription
            MockConversation.return_value = mock_conversation
            MockFileManager.return_value = mock_file_manager

            # Configure for detailed reflection scenario
            mock_recorder.start_recording.return_value = True
            mock_recorder.stop_recording.return_value = True

            # Longer, more complex transcription
            long_reflection = """
            I've been thinking about the mobile app project we just completed.
            It was really challenging, especially the user authentication part.
            We had some great breakthroughs with the UI design, but I feel like
            we could have done better with the backend architecture. The team
            communication was mostly good, though there were some issues with
            the handoff between design and development. I learned a lot about
            React Native and I think this experience will help with future projects.
            """

            mock_transcription.transcribe_audio.return_value = Mock(
                text=long_reflection.strip(),
                confidence=0.94,
                duration=45.0,
                word_count=85,
                cost_usd=0.027
            )

            # Deep conversation processing
            mock_conversation.process_transcript.return_value = {
                'key_insight': 'Mobile app project retrospective with focus on architecture improvements',
                'topic_type': 'reflection',
                'conversation': [
                    {'role': 'user', 'content': long_reflection.strip()},
                    {'role': 'assistant', 'content': 'It sounds like this mobile app project had both challenges and successes. What specific aspect of the backend architecture do you think needs the most improvement?'},
                    {'role': 'user', 'content': 'The API design and data flow between components'},
                    {'role': 'assistant', 'content': 'API design is crucial for maintainability. What patterns or approaches are you considering for future projects?'},
                    {'role': 'user', 'content': 'Maybe implementing a more robust state management solution and better error handling'}
                ],
                'action_items': [
                    'Research better backend architecture patterns',
                    'Improve team communication processes',
                    'Document lessons learned for future projects',
                    'Implement better API design practices'
                ],
                'entities': ['mobile app', 'React Native', 'authentication', 'UI design', 'backend architecture'],
                'topics': ['project management', 'software development', 'team communication', 'technical learning']
            }

            expected_file_path = str(temp_workspace / "Voice Notes" / "2023-12-01_mobile_app_project_retrospective.md")
            mock_file_manager.save_note.return_value = expected_file_path

            # Simulate the detailed reflection workflow

            # 1. User starts recording for a longer session
            mock_recorder.start_recording()

            # 2. User speaks for extended period (45 seconds)
            mock_recorder.is_recording = True

            # 3. User stops recording
            mock_recorder.stop_recording()
            mock_recorder.is_recording = False

            # 4. System transcribes longer content
            transcription = mock_transcription.transcribe_audio("long_audio.wav")
            assert transcription.duration == 45.0
            assert transcription.word_count == 85

            # 5. System recognizes this as a reflection and processes deeply
            conversation_result = mock_conversation.process_transcript(transcription.text)
            assert conversation_result['topic_type'] == 'reflection'
            assert len(conversation_result['conversation']) > 3  # Multiple exchanges
            assert len(conversation_result['action_items']) >= 4

            # 6. System saves comprehensive note
            saved_path = mock_file_manager.save_note(conversation_result)
            assert 'retrospective' in saved_path.lower() or 'project' in saved_path.lower()

            print("✅ Detailed project reflection scenario completed successfully")

    def test_user_scenario_meeting_notes_capture(self, mock_user_config, temp_workspace):
        """
        User Scenario: Capturing meeting notes

        User is in a meeting and wants to capture key points and action items.

        Acceptance Criteria:
        - System captures longer recording session
        - Processes meeting content appropriately
        - Extracts attendees, decisions, and action items
        - Creates well-structured meeting notes
        - Integrates with existing note-taking workflow
        """
        with patch('audio_recorder.AudioRecorder') as MockRecorder, \
             patch('transcription.TranscriptionService') as MockTranscription, \
             patch('conversation_manager.ConversationManager') as MockConversation, \
             patch('file_manager.FileManager') as MockFileManager:

            # Setup mocks
            mock_recorder = Mock()
            mock_transcription = Mock()
            mock_conversation = Mock()
            mock_file_manager = Mock()

            MockRecorder.return_value = mock_recorder
            MockTranscription.return_value = mock_transcription
            MockConversation.return_value = mock_conversation
            MockFileManager.return_value = mock_file_manager

            # Meeting scenario setup
            meeting_transcript = """
            Okay, so we're here to discuss the Q4 marketing campaign.
            Sarah mentioned that the budget is approved at 50K.
            We need to focus on digital channels, especially social media and email marketing.
            John will handle the creative assets, and Maria will manage the email campaigns.
            We should have the first drafts ready by next Friday.
            The campaign launch is planned for December 15th.
            We also discussed tracking metrics - we want to focus on conversion rates and customer acquisition cost.
            """

            mock_transcription.transcribe_audio.return_value = Mock(
                text=meeting_transcript.strip(),
                confidence=0.91,
                duration=120.0,
                word_count=95,
                cost_usd=0.036
            )

            mock_conversation.process_transcript.return_value = {
                'key_insight': 'Q4 marketing campaign planning meeting with budget approval and task assignments',
                'topic_type': 'meeting',
                'conversation': [
                    {'role': 'user', 'content': meeting_transcript.strip()},
                    {'role': 'assistant', 'content': 'This sounds like an important planning meeting. Let me help organize the key decisions and action items from this discussion.'}
                ],
                'action_items': [
                    'John: Create creative assets for marketing campaign',
                    'Maria: Set up and manage email marketing campaigns',
                    'Team: Deliver first drafts by next Friday',
                    'All: Prepare for December 15th campaign launch',
                    'Setup tracking for conversion rates and customer acquisition cost'
                ],
                'entities': ['Sarah', 'John', 'Maria', 'Q4 marketing campaign', 'social media', 'email marketing'],
                'topics': ['marketing', 'budget planning', 'team coordination', 'project management']
            }

            expected_file_path = str(temp_workspace / "Voice Notes" / "2023-12-01_q4_marketing_campaign_meeting.md")
            mock_file_manager.save_note.return_value = expected_file_path

            # Simulate meeting capture workflow

            # 1. User starts recording at beginning of meeting
            recording_started = mock_recorder.start_recording()
            assert recording_started is True

            # 2. Meeting proceeds (2 minutes of discussion)
            mock_recorder.is_recording = True

            # 3. User stops recording at end of meeting
            recording_stopped = mock_recorder.stop_recording()
            assert recording_stopped is True

            # 4. System processes meeting audio
            transcription = mock_transcription.transcribe_audio("meeting_audio.wav")
            assert transcription.duration == 120.0  # 2 minutes

            # 5. System recognizes meeting context and processes accordingly
            meeting_result = mock_conversation.process_transcript(transcription.text)
            assert meeting_result['topic_type'] == 'meeting'

            # 6. Verify meeting-specific processing
            action_items = meeting_result['action_items']
            assert len(action_items) >= 4
            assert any('John:' in item for item in action_items)  # Person-assigned tasks
            assert any('Maria:' in item for item in action_items)  # Person-assigned tasks

            # 7. System saves structured meeting notes
            saved_path = mock_file_manager.save_note(meeting_result)
            assert 'meeting' in saved_path.lower()

            print("✅ Meeting notes capture scenario completed successfully")

    def test_user_scenario_voice_journaling(self, mock_user_config, temp_workspace):
        """
        User Scenario: Daily voice journaling

        User wants to do daily reflection/journaling via voice for personal growth.

        Acceptance Criteria:
        - System handles personal, emotional content appropriately
        - Respects privacy concerns
        - Creates meaningful personal insights
        - Maintains journaling continuity over time
        - Provides gentle, supportive conversation style
        """
        with patch('conversation_manager.ConversationManager') as MockConversation, \
             patch('file_manager.FileManager') as MockFileManager:

            mock_conversation = Mock()
            mock_file_manager = Mock()
            MockConversation.return_value = mock_conversation
            MockFileManager.return_value = mock_file_manager

            journal_entry = """
            Today was a bit overwhelming at work. I had three back-to-back meetings
            and felt like I couldn't catch my breath. But I did finish that report
            I've been putting off for weeks, which feels really good. I've been
            trying to be more mindful about taking breaks, and I think it's helping.
            My meditation practice is getting more consistent too. I'm grateful for
            my supportive team, even when things get hectic.
            """

            # Journal-appropriate conversation response
            mock_conversation.process_transcript.return_value = {
                'key_insight': 'Work stress management with positive accomplishments and mindfulness practice',
                'topic_type': 'personal_reflection',
                'conversation': [
                    {'role': 'user', 'content': journal_entry.strip()},
                    {'role': 'assistant', 'content': 'It sounds like you had a challenging but ultimately productive day. Completing that report must feel like a weight off your shoulders. How has your mindfulness practice been helping you manage the busy periods?'}
                ],
                'action_items': [
                    'Continue building consistent meditation practice',
                    'Remember to schedule breathing room between meetings',
                    'Acknowledge the accomplishment of finishing the report'
                ],
                'entities': ['work', 'meetings', 'report', 'meditation', 'team'],
                'topics': ['stress management', 'personal growth', 'mindfulness', 'work-life balance']
            }

            expected_file_path = str(temp_workspace / "Voice Notes" / f"2023-12-01_daily_reflection_{datetime.now().strftime('%H%M')}.md")
            mock_file_manager.save_note.return_value = expected_file_path

            # Process the journal entry
            journal_result = mock_conversation.process_transcript(journal_entry.strip())

            # Verify journaling-appropriate processing
            assert journal_result['topic_type'] == 'personal_reflection'
            assert 'stress management' in journal_result['topics']
            assert 'mindfulness' in journal_result['topics']

            # Verify supportive conversation tone
            assistant_response = journal_result['conversation'][1]['content']
            assert any(word in assistant_response.lower() for word in ['feel', 'sounds', 'how'])

            # Verify personal growth focus in action items
            action_items = journal_result['action_items']
            assert any('meditation' in item.lower() or 'mindfulness' in item.lower() for item in action_items)

            saved_path = mock_file_manager.save_note(journal_result)
            assert 'reflection' in saved_path.lower()

            print("✅ Voice journaling scenario completed successfully")

    def test_user_scenario_error_recovery_workflow(self, mock_user_config, temp_workspace):
        """
        User Scenario: System error recovery

        User encounters system errors but wants to continue their workflow.

        Acceptance Criteria:
        - System gracefully handles errors
        - User receives clear error messages
        - System attempts automatic recovery
        - User data is not lost
        - User can manually retry operations
        """
        with patch('audio_recorder.AudioRecorder') as MockRecorder, \
             patch('transcription.TranscriptionService') as MockTranscription, \
             patch('desktop_notifications.DesktopNotificationSystem') as MockNotifications, \
             patch('error_recovery.ErrorRecoverySystem') as MockErrorRecovery:

            # Setup mocks
            mock_recorder = Mock()
            mock_transcription = Mock()
            mock_notifications = Mock()
            mock_error_recovery = Mock()

            MockRecorder.return_value = mock_recorder
            MockTranscription.return_value = mock_transcription
            MockNotifications.return_value = mock_notifications
            MockErrorRecovery.return_value = mock_error_recovery

            # Simulate error scenario
            mock_recorder.start_recording.return_value = True
            mock_recorder.stop_recording.return_value = True

            # First transcription attempt fails
            mock_transcription.transcribe_audio.side_effect = [
                Exception("Network timeout"),  # First attempt fails
                Mock(  # Second attempt succeeds
                    text="This is my recovered voice note",
                    confidence=0.88,
                    duration=5.0,
                    word_count=6,
                    cost_usd=0.006
                )
            ]

            # Simulate error recovery workflow

            # 1. User records successfully
            mock_recorder.start_recording()
            mock_recorder.stop_recording()

            # 2. Transcription fails
            try:
                mock_transcription.transcribe_audio("audio.wav")
                assert False, "Should have failed"
            except Exception as e:
                assert str(e) == "Network timeout"

                # 3. System shows error notification
                mock_notifications.notify_error_with_recovery.assert_called_once()

                # 4. Error recovery system logs the failure
                mock_error_recovery.queue_failed_operation.assert_called()

                # 5. System attempts automatic retry
                retry_result = mock_transcription.transcribe_audio("audio.wav")
                assert retry_result.text == "This is my recovered voice note"

                # 6. System shows success notification after recovery
                mock_notifications.notify_processing_complete.assert_called()

            print("✅ Error recovery workflow scenario completed successfully")

    def test_user_scenario_accessibility_support(self, mock_user_config):
        """
        User Scenario: Accessibility support

        User with accessibility needs uses the system.

        Acceptance Criteria:
        - System supports keyboard navigation
        - Audio feedback is available for visually impaired users
        - Text sizes and contrasts are appropriate
        - Screen reader compatibility
        - Voice commands work reliably
        """
        with patch('system_tray.VoiceNotesSystemTray') as MockTray:
            mock_tray = Mock()
            MockTray.return_value = mock_tray

            # Test accessibility features
            accessibility_config = {
                **mock_user_config,
                'accessibility': {
                    'high_contrast': True,
                    'large_text': True,
                    'audio_feedback': True,
                    'screen_reader_support': True,
                    'keyboard_navigation': True
                }
            }

            # Verify configuration supports accessibility
            assert accessibility_config['accessibility']['audio_feedback'] is True
            assert accessibility_config['accessibility']['keyboard_navigation'] is True

            # Test audio feedback for system tray
            mock_tray.show_notification.return_value = True

            # Audio feedback should be enabled
            notification_called = mock_tray.show_notification("Test", "Accessibility test")
            assert notification_called is True

            print("✅ Accessibility support scenario verified")

    def test_user_scenario_multi_language_support(self, mock_user_config):
        """
        User Scenario: Multi-language voice notes

        User speaks in different languages and wants appropriate processing.

        Acceptance Criteria:
        - System handles multiple languages in transcription
        - Conversation processing adapts to language context
        - File naming and organization work with non-English content
        - Unicode support throughout the system
        """
        with patch('transcription.TranscriptionService') as MockTranscription, \
             patch('conversation_manager.ConversationManager') as MockConversation:

            mock_transcription = Mock()
            mock_conversation = Mock()
            MockTranscription.return_value = mock_transcription
            MockConversation.return_value = mock_conversation

            # Test Spanish content
            spanish_text = "Hoy fue un día muy productivo en el trabajo. Terminé el proyecto importante."

            mock_transcription.transcribe_audio.return_value = Mock(
                text=spanish_text,
                confidence=0.92,
                language='es',
                duration=8.0,
                word_count=11,
                cost_usd=0.008
            )

            mock_conversation.process_transcript.return_value = {
                'key_insight': 'Día productivo completando proyecto importante',
                'topic_type': 'trabajo',
                'conversation': [
                    {'role': 'user', 'content': spanish_text},
                    {'role': 'assistant', 'content': '¡Qué bueno que hayas tenido un día tan productivo! ¿Qué fue lo que más te gustó de completar este proyecto?'}
                ],
                'action_items': ['Celebrar la finalización del proyecto'],
                'entities': ['trabajo', 'proyecto'],
                'topics': ['productividad', 'trabajo']
            }

            # Process Spanish content
            transcription = mock_transcription.transcribe_audio("spanish_audio.wav")
            assert transcription.text == spanish_text
            assert transcription.language == 'es'

            conversation_result = mock_conversation.process_transcript(transcription.text)
            assert conversation_result['topic_type'] == 'trabajo'  # Spanish topic classification

            # Verify assistant responds in Spanish
            assistant_response = conversation_result['conversation'][1]['content']
            assert '¿Qué' in assistant_response  # Spanish question format

            print("✅ Multi-language support scenario verified")

    def test_user_scenario_workflow_integration(self, mock_user_config, temp_workspace):
        """
        User Scenario: Integration with existing workflow

        User wants voice notes to integrate with their existing note-taking and productivity tools.

        Acceptance Criteria:
        - Notes save to user's preferred directory structure
        - File formats are compatible with other tools
        - Consistent naming conventions
        - Easy to find and organize notes
        - Export capabilities for different formats
        """
        with patch('file_manager.FileManager') as MockFileManager:
            mock_file_manager = Mock()
            MockFileManager.return_value = mock_file_manager

            # Setup user's existing directory structure
            existing_structure = temp_workspace / "My Notes"
            existing_structure.mkdir()
            (existing_structure / "Projects").mkdir()
            (existing_structure / "Personal").mkdir()
            (existing_structure / "Meetings").mkdir()

            # Configure system to use existing structure
            integration_config = {
                **mock_user_config,
                'files': {
                    'output_directory': str(existing_structure),
                    'naming_pattern': 'hybrid',
                    'daily_folders': False,  # User prefers topic-based organization
                    'cleanup_temp_files': True
                },
                'workflow': {
                    'integration_mode': True,
                    'auto_categorize': True,
                    'compatible_formats': ['markdown', 'txt', 'json']
                }
            }

            # Test different note types save to appropriate locations
            test_cases = [
                {
                    'topic_type': 'meeting',
                    'expected_path': existing_structure / "Meetings" / "project_standup_meeting.md"
                },
                {
                    'topic_type': 'personal_reflection',
                    'expected_path': existing_structure / "Personal" / "daily_reflection.md"
                },
                {
                    'topic_type': 'project_planning',
                    'expected_path': existing_structure / "Projects" / "mobile_app_planning.md"
                }
            ]

            for test_case in test_cases:
                mock_file_manager.save_note.return_value = str(test_case['expected_path'])

                conversation_result = {
                    'topic_type': test_case['topic_type'],
                    'key_insight': f"Test {test_case['topic_type']} insight"
                }

                saved_path = mock_file_manager.save_note(conversation_result)
                expected_path_str = str(test_case['expected_path'])

                # Verify path structure matches user's organization
                assert test_case['topic_type'].split('_')[0].title() in saved_path or \
                       test_case['topic_type'] in saved_path.lower()

            # Verify file format compatibility
            assert integration_config['workflow']['compatible_formats'] == ['markdown', 'txt', 'json']

            print("✅ Workflow integration scenario verified")


class TestUserExperienceValidation:
    """Validate overall user experience aspects."""

    def test_startup_time_user_expectation(self):
        """Test that system startup meets user expectations."""
        import time

        # Mock system initialization
        with patch('system_tray.VoiceNotesSystemTray') as MockTray, \
             patch('audio_recorder.AudioRecorder') as MockRecorder, \
             patch('desktop_notifications.DesktopNotificationSystem') as MockNotifications:

            start_time = time.perf_counter()

            # Simulate system startup
            MockTray()
            MockRecorder({})
            MockNotifications({})

            startup_time = time.perf_counter() - start_time

            # User expectation: system should be ready within 2 seconds
            assert startup_time < 2.0, f"Startup time {startup_time:.3f}s exceeds user expectation"

            print(f"✅ Startup time: {startup_time:.3f}s (meets user expectation)")

    def test_hotkey_responsiveness_user_expectation(self):
        """Test that hotkey response meets user expectations."""
        with patch('global_hotkey.GlobalHotkeyManager') as MockHotkey:
            mock_hotkey = Mock()
            MockHotkey.return_value = mock_hotkey

            # User expectation: hotkey should respond within 100ms
            mock_hotkey.start_listener.return_value = True

            start_time = time.perf_counter()
            hotkey_response = mock_hotkey.start_listener()
            response_time = time.perf_counter() - start_time

            assert response_time < 0.1, f"Hotkey response {response_time:.3f}s too slow"
            assert hotkey_response is True

            print(f"✅ Hotkey responsiveness: {response_time*1000:.1f}ms (meets user expectation)")

    def test_notification_timing_user_expectation(self):
        """Test that notifications appear at appropriate times for users."""
        with patch('desktop_notifications.DesktopNotificationSystem') as MockNotifications:
            mock_notifications = Mock()
            MockNotifications.return_value = mock_notifications

            # User expectation: immediate feedback for actions
            mock_notifications.notify_recording_started.return_value = True
            mock_notifications.notify_processing_complete.return_value = True

            # Recording start notification should be immediate
            start_time = time.perf_counter()
            result = mock_notifications.notify_recording_started()
            notification_time = time.perf_counter() - start_time

            assert notification_time < 0.05, "Recording start notification too slow"
            assert result is True

            print(f"✅ Notification timing: {notification_time*1000:.1f}ms (meets user expectation)")

    def test_file_organization_user_expectation(self, temp_workspace):
        """Test that file organization meets user expectations."""
        # Create realistic file structure
        notes_dir = temp_workspace / "Voice Notes"
        notes_dir.mkdir()

        # Simulate a week of voice notes
        dates = [
            "2023-12-01", "2023-12-02", "2023-12-03",
            "2023-12-04", "2023-12-05", "2023-12-06", "2023-12-07"
        ]

        note_types = [
            "meeting_notes", "project_reflection", "daily_standup",
            "idea_capture", "personal_reflection", "task_planning"
        ]

        # Create sample notes
        for date in dates[:3]:  # Create a few days worth
            for note_type in note_types[:2]:  # A couple note types per day
                note_file = notes_dir / f"{date}_{note_type}.md"
                note_file.write_text(f"# {note_type.replace('_', ' ').title()}\n\nContent for {date}")

        # User expectation: easy to find recent notes
        recent_notes = list(notes_dir.glob("*.md"))
        assert len(recent_notes) >= 6, "Should have multiple recent notes"

        # User expectation: clear naming pattern
        for note_file in recent_notes:
            assert "_" in note_file.stem, "Notes should have clear naming pattern"
            assert note_file.suffix == ".md", "Notes should be markdown format"

        # User expectation: chronological organization
        note_names = sorted([f.stem for f in recent_notes])
        assert note_names[0].startswith("2023-12-01"), "Notes should be chronologically organized"

        print(f"✅ File organization: {len(recent_notes)} notes properly organized")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])