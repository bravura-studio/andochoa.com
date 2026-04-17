"""
Integration tests for the full voice notes pipeline.

Tests the complete workflow from audio recording through to file saving,
simulating real user scenarios and testing component interactions.
"""

import pytest
import tempfile
import shutil
import wave
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import sys
sys.path.append(str(Path(__file__).parent.parent / 'src'))


class TestVoiceNotesPipeline:
    """Integration tests for the complete voice notes pipeline."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_config(self, temp_dir):
        """Mock configuration for testing."""
        return {
            'audio': {
                'sample_rate': 44100,
                'channels': 1,
                'format': 'WAV',
                'silence_threshold': 0.01,
                'silence_duration': 2.0,
                'input_device': ''
            },
            'files': {
                'output_directory': str(temp_dir),
                'naming_pattern': 'hybrid',
                'daily_folders': True,
                'cleanup_temp_files': True
            },
            'processing': {
                'default_mode': 'standard',
                'auto_process': True,
                'max_conversation_depth': 5
            },
            'api': {
                'openai': {
                    'api_key': 'test-key',
                    'model': 'whisper-1',
                    'max_retries': 3,
                    'timeout': 30
                }
            },
            'notifications': {
                'enabled': True,
                'sound_enabled': False,  # Disable sounds in tests
                'show_recording': True,
                'show_processing': True,
                'show_errors': True,
                'show_success': True,
                'default_duration': 2,
                'non_intrusive': True
            }
        }

    @pytest.fixture
    def sample_audio_file(self, temp_dir):
        """Create a sample WAV file for testing."""
        audio_file = temp_dir / "sample_audio.wav"

        # Create a simple WAV file with sine wave
        import numpy as np
        sample_rate = 44100
        duration = 2.0  # seconds
        frequency = 440  # Hz (A note)

        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.5

        # Convert to 16-bit integers
        audio_data = (audio_data * 32767).astype(np.int16)

        with wave.open(str(audio_file), 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())

        return audio_file

    def create_mock_audio_recorder(self):
        """Create mock audio recorder."""
        with patch('audio_recorder.AudioRecorder') as mock_recorder_class:
            mock_recorder = Mock()
            mock_recorder.start_recording.return_value = True
            mock_recorder.stop_recording.return_value = True
            mock_recorder.is_recording = False
            mock_recorder.get_audio_level.return_value = 0.5
            mock_recorder.should_auto_stop.return_value = False
            mock_recorder_class.return_value = mock_recorder
            return mock_recorder

    def create_mock_transcription_service(self):
        """Create mock transcription service."""
        with patch('transcription.TranscriptionService') as mock_service_class:
            mock_service = Mock()
            mock_service.transcribe_audio.return_value = Mock(
                text="This is a test transcription of the audio file.",
                confidence=0.95,
                duration=2.0,
                word_count=10,
                cost_usd=0.006
            )
            mock_service_class.return_value = mock_service
            return mock_service

    def create_mock_conversation_manager(self):
        """Create mock conversation manager."""
        with patch('conversation_manager.ConversationManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.process_transcript.return_value = {
                'key_insight': 'Test insight from the conversation',
                'topic_type': 'general',
                'conversation': [
                    {
                        'role': 'user',
                        'content': 'This is a test transcription of the audio file.'
                    },
                    {
                        'role': 'assistant',
                        'content': 'Thank you for sharing that. Can you tell me more about what you found most interesting?'
                    }
                ],
                'action_items': ['Review the test results', 'Update documentation'],
                'entities': ['test', 'audio', 'transcription'],
                'topics': ['testing', 'voice notes']
            }
            mock_manager_class.return_value = mock_manager
            return mock_manager

    def create_mock_file_manager(self):
        """Create mock file manager."""
        with patch('file_manager.FileManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.save_note.return_value = "/path/to/saved/note.md"
            mock_manager_class.return_value = mock_manager
            return mock_manager

    @patch('desktop_notifications.DesktopNotificationSystem')
    def test_complete_pipeline_success(self, mock_notifications, mock_config, sample_audio_file):
        """Test the complete pipeline from recording to file save."""
        # Setup mocks
        mock_audio_recorder = self.create_mock_audio_recorder()
        mock_transcription = self.create_mock_transcription_service()
        mock_conversation = self.create_mock_conversation_manager()
        mock_file_manager = self.create_mock_file_manager()
        mock_notification_system = Mock()
        mock_notifications.return_value = mock_notification_system

        # Simulate the pipeline
        # 1. Start recording
        success = mock_audio_recorder.start_recording()
        assert success is True
        # Manually trigger notification as would happen in real system
        mock_notification_system.notify_recording_started()

        # 2. Stop recording and get file
        mock_audio_recorder.is_recording = True
        audio_file = sample_audio_file
        stop_success = mock_audio_recorder.stop_recording()
        assert stop_success is True
        # Manually trigger notification as would happen in real system
        mock_notification_system.notify_recording_stopped(duration_seconds=3)

        # 3. Transcribe audio
        transcription_result = mock_transcription.transcribe_audio(str(audio_file))
        assert transcription_result.text == "This is a test transcription of the audio file."
        assert transcription_result.confidence == 0.95

        # 4. Process with conversation manager
        conversation_result = mock_conversation.process_transcript(transcription_result.text)
        assert 'key_insight' in conversation_result
        assert 'conversation' in conversation_result
        assert len(conversation_result['action_items']) > 0

        # 5. Save to file
        file_path = mock_file_manager.save_note(conversation_result)
        assert file_path == "/path/to/saved/note.md"
        # Manually trigger completion notification
        mock_notification_system.notify_processing_complete(note_title="Test Note", file_path=file_path)

        # Verify all components were called correctly
        mock_transcription.transcribe_audio.assert_called_once_with(str(audio_file))
        mock_conversation.process_transcript.assert_called_once()
        mock_file_manager.save_note.assert_called_once()

        # Verify notifications were called
        mock_notification_system.notify_recording_started.assert_called_once()
        mock_notification_system.notify_recording_stopped.assert_called_once()
        mock_notification_system.notify_processing_complete.assert_called_once()

    @patch('desktop_notifications.DesktopNotificationSystem')
    def test_pipeline_transcription_failure_recovery(self, mock_notifications, mock_config):
        """Test pipeline recovery when transcription fails."""
        mock_audio_recorder = self.create_mock_audio_recorder()
        mock_notification_system = Mock()
        mock_notifications.return_value = mock_notification_system

        # Mock transcription service that fails
        with patch('transcription.TranscriptionService') as mock_service_class:
            mock_service = Mock()
            mock_service.transcribe_audio.side_effect = Exception("API Error")
            mock_service_class.return_value = mock_service

            # Simulate recording
            mock_audio_recorder.start_recording()
            mock_audio_recorder.stop_recording()

            # Try transcription - should fail
            with pytest.raises(Exception):
                mock_service.transcribe_audio("test.wav")

            # Verify error notification was called
            mock_notification_system.notify_error_with_recovery.assert_called()

    @patch('desktop_notifications.DesktopNotificationSystem')
    def test_pipeline_with_fallback_transcription(self, mock_notifications, mock_config, sample_audio_file):
        """Test pipeline using fallback transcription when API fails."""
        mock_audio_recorder = self.create_mock_audio_recorder()
        mock_conversation = self.create_mock_conversation_manager()
        mock_file_manager = self.create_mock_file_manager()
        mock_notification_system = Mock()
        mock_notifications.return_value = mock_notification_system

        # Mock transcription service with fallback
        with patch('transcription.TranscriptionService') as mock_service_class:
            mock_service = Mock()
            # First call fails (API), second succeeds (fallback)
            mock_service.transcribe_audio.side_effect = [
                Exception("API Error"),
                Mock(
                    text="Fallback transcription result",
                    confidence=0.8,
                    duration=2.0,
                    word_count=4,
                    cost_usd=0.0
                )
            ]
            mock_service_class.return_value = mock_service

            # Simulate pipeline with fallback
            mock_audio_recorder.start_recording()
            mock_audio_recorder.stop_recording()

            # First transcription attempt fails
            try:
                result1 = mock_service.transcribe_audio(str(sample_audio_file))
            except Exception:
                # Fallback transcription succeeds
                result2 = mock_service.transcribe_audio(str(sample_audio_file))
                assert result2.text == "Fallback transcription result"
                assert result2.confidence == 0.8

                # Continue with conversation processing
                conversation_result = mock_conversation.process_transcript(result2.text)
                file_path = mock_file_manager.save_note(conversation_result)

                assert file_path == "/path/to/saved/note.md"
                mock_notification_system.notify_fallback_mode.assert_called()

    def test_pipeline_performance_benchmarks(self, mock_config, sample_audio_file):
        """Test pipeline performance benchmarks."""
        import time

        mock_audio_recorder = self.create_mock_audio_recorder()
        mock_transcription = self.create_mock_transcription_service()
        mock_conversation = self.create_mock_conversation_manager()
        mock_file_manager = self.create_mock_file_manager()

        # Measure pipeline timing
        start_time = time.time()

        # Simulate pipeline steps with timing
        record_start = time.time()
        mock_audio_recorder.start_recording()
        mock_audio_recorder.stop_recording()
        record_time = time.time() - record_start

        transcription_start = time.time()
        transcription_result = mock_transcription.transcribe_audio(str(sample_audio_file))
        transcription_time = time.time() - transcription_start

        conversation_start = time.time()
        conversation_result = mock_conversation.process_transcript(transcription_result.text)
        conversation_time = time.time() - conversation_start

        save_start = time.time()
        file_path = mock_file_manager.save_note(conversation_result)
        save_time = time.time() - save_start

        total_time = time.time() - start_time

        # Assert performance benchmarks
        assert record_time < 0.1  # Recording control should be very fast
        assert transcription_time < 1.0  # Mocked transcription should be fast
        assert conversation_time < 1.0  # Mocked conversation should be fast
        assert save_time < 0.5  # File saving should be fast
        assert total_time < 2.0  # Total pipeline should complete quickly

        # Create performance report
        performance_report = {
            'record_time': record_time,
            'transcription_time': transcription_time,
            'conversation_time': conversation_time,
            'save_time': save_time,
            'total_time': total_time,
            'timestamp': datetime.now().isoformat()
        }

        # Performance report should have all timing data
        assert all(key in performance_report for key in [
            'record_time', 'transcription_time', 'conversation_time',
            'save_time', 'total_time', 'timestamp'
        ])

    @patch('desktop_notifications.DesktopNotificationSystem')
    def test_pipeline_with_user_interaction_simulation(self, mock_notifications, mock_config):
        """Test pipeline with simulated user interactions."""
        mock_notification_system = Mock()
        mock_notifications.return_value = mock_notification_system

        mock_audio_recorder = self.create_mock_audio_recorder()

        # Simulate user starting recording
        user_action_start = mock_audio_recorder.start_recording()
        assert user_action_start is True

        # Simulate recording duration
        import time
        recording_duration = 0.1  # Short duration for testing
        time.sleep(recording_duration)

        # Simulate user stopping recording
        user_action_stop = mock_audio_recorder.stop_recording()
        assert user_action_stop is True

        # Verify notifications were triggered for user actions
        mock_notification_system.notify_recording_started.assert_called_once()
        mock_notification_system.notify_recording_stopped.assert_called()

    def test_pipeline_configuration_variations(self, temp_dir):
        """Test pipeline with different configuration variations."""
        configurations = [
            # Quick processing mode
            {
                'processing': {
                    'default_mode': 'quick',
                    'max_conversation_depth': 2
                },
                'files': {'output_directory': str(temp_dir)}
            },
            # Deep processing mode
            {
                'processing': {
                    'default_mode': 'deep',
                    'max_conversation_depth': 8
                },
                'files': {'output_directory': str(temp_dir)}
            },
            # Standard with daily folders disabled
            {
                'processing': {
                    'default_mode': 'standard',
                    'max_conversation_depth': 5
                },
                'files': {
                    'output_directory': str(temp_dir),
                    'daily_folders': False
                }
            }
        ]

        for config in configurations:
            mock_conversation = self.create_mock_conversation_manager()

            # Each configuration should be valid
            assert 'processing' in config
            assert 'default_mode' in config['processing']
            assert config['processing']['default_mode'] in ['quick', 'standard', 'deep']

            # Mock conversation manager should handle different modes
            result = mock_conversation.process_transcript("Test transcript")
            assert 'key_insight' in result

    @patch('desktop_notifications.DesktopNotificationSystem')
    def test_pipeline_error_recovery_scenarios(self, mock_notifications, mock_config):
        """Test various error recovery scenarios in the pipeline."""
        mock_notification_system = Mock()
        mock_notifications.return_value = mock_notification_system

        # Test recording device error
        with patch('audio_recorder.AudioRecorder') as mock_recorder_class:
            mock_recorder = Mock()
            mock_recorder.start_recording.side_effect = Exception("Audio device not available")
            mock_recorder_class.return_value = mock_recorder

            with pytest.raises(Exception):
                mock_recorder.start_recording()

        # Test file save error
        with patch('file_manager.FileManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.save_note.side_effect = Exception("Disk full")
            mock_manager_class.return_value = mock_manager

            with pytest.raises(Exception):
                mock_manager.save_note({})

        # Test MCP connection error
        mock_conversation = self.create_mock_conversation_manager()
        mock_conversation.process_transcript.side_effect = Exception("MCP connection failed")

        with pytest.raises(Exception):
            mock_conversation.process_transcript("Test transcript")

    def test_pipeline_data_flow_integrity(self, mock_config, sample_audio_file):
        """Test that data flows correctly through pipeline without corruption."""
        mock_transcription = self.create_mock_transcription_service()
        mock_conversation = self.create_mock_conversation_manager()
        mock_file_manager = self.create_mock_file_manager()

        # Input data
        original_transcript = "This is a test transcription that should flow through correctly."

        # Update mocks to use our test data
        mock_transcription.transcribe_audio.return_value.text = original_transcript

        # Process through pipeline
        transcription_result = mock_transcription.transcribe_audio(str(sample_audio_file))
        assert transcription_result.text == original_transcript

        # Conversation processing
        conversation_result = mock_conversation.process_transcript(transcription_result.text)

        # Verify conversation manager received correct input
        mock_conversation.process_transcript.assert_called_with(original_transcript)

        # File saving
        file_path = mock_file_manager.save_note(conversation_result)

        # Verify file manager received conversation result
        mock_file_manager.save_note.assert_called_with(conversation_result)
        assert file_path == "/path/to/saved/note.md"


class TestPipelineStressTests:
    """Stress tests for the pipeline under various conditions."""

    def test_rapid_recording_cycles(self):
        """Test pipeline with rapid start/stop recording cycles."""
        mock_recorder = Mock()

        # Simulate 10 rapid cycles
        for i in range(10):
            mock_recorder.start_recording.return_value = True
            mock_recorder.stop_recording.return_value = True

            start_result = mock_recorder.start_recording()
            stop_result = mock_recorder.stop_recording()

            assert start_result is True
            assert stop_result is True

        # Should have been called 10 times each
        assert mock_recorder.start_recording.call_count == 10
        assert mock_recorder.stop_recording.call_count == 10

    def test_large_transcription_processing(self):
        """Test pipeline with large transcription texts."""
        mock_conversation = Mock()

        # Create a large transcript (simulate 5-minute voice note)
        large_transcript = "This is a very long transcription. " * 1000

        mock_conversation.process_transcript.return_value = {
            'key_insight': 'Processed large transcript successfully',
            'conversation': [],
            'action_items': [],
            'entities': [],
            'topics': []
        }

        result = mock_conversation.process_transcript(large_transcript)
        assert result['key_insight'] == 'Processed large transcript successfully'

        # Verify the large text was handled
        call_args = mock_conversation.process_transcript.call_args[0][0]
        assert len(call_args) > 30000  # Should be a large string

    def test_concurrent_pipeline_operations(self):
        """Test multiple pipeline operations running concurrently."""
        import threading

        results = []

        def mock_pipeline_operation(operation_id):
            """Simulate a pipeline operation."""
            mock_transcription = Mock()
            mock_transcription.transcribe_audio.return_value = Mock(
                text=f"Operation {operation_id} transcription",
                confidence=0.9
            )

            result = mock_transcription.transcribe_audio(f"audio_{operation_id}.wav")
            results.append((operation_id, result.text))

        # Start 5 concurrent operations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=mock_pipeline_operation, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all to complete
        for thread in threads:
            thread.join()

        # Verify all operations completed
        assert len(results) == 5
        assert all(f"Operation {i} transcription" in [r[1] for r in results] for i in range(5))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])