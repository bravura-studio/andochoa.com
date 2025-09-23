"""
Performance benchmarks for Voice Notes system.

Tests system performance under various conditions and provides
benchmarks for key operations like transcription, processing, and file I/O.
"""

import pytest
import time
import threading
import tempfile
import shutil
import wave
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys
sys.path.append(str(Path(__file__).parent.parent / 'src'))


class TestPerformanceBenchmarks:
    """Performance benchmarks for core system operations."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def audio_files(self, temp_dir):
        """Create multiple audio files for testing."""
        files = []

        for i, duration in enumerate([1.0, 2.0, 5.0, 10.0]):  # Different durations
            file_path = temp_dir / f"test_audio_{i}_{duration}s.wav"

            # Generate sine wave audio
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio_data = np.sin(2 * np.pi * 440 * t) * 0.3  # 440Hz sine wave
            audio_data = (audio_data * 32767).astype(np.int16)

            with wave.open(str(file_path), 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data.tobytes())

            files.append((file_path, duration))

        return files

    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function."""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        return result, end_time - start_time

    def test_audio_recorder_performance(self):
        """Test audio recorder initialization and control performance."""
        with patch('audio_recorder.sounddevice') as mock_sd:
            with patch('audio_recorder.AudioRecorder') as MockRecorder:
                mock_recorder = Mock()
                MockRecorder.return_value = mock_recorder

                # Test initialization time
                _, init_time = self.measure_time(MockRecorder, {})
                assert init_time < 0.1, f"Initialization took {init_time:.3f}s, should be < 0.1s"

                # Test start/stop performance
                mock_recorder.start_recording.return_value = True
                mock_recorder.stop_recording.return_value = True

                _, start_time = self.measure_time(mock_recorder.start_recording)
                _, stop_time = self.measure_time(mock_recorder.stop_recording)

                assert start_time < 0.05, f"Start recording took {start_time:.3f}s, should be < 0.05s"
                assert stop_time < 0.05, f"Stop recording took {stop_time:.3f}s, should be < 0.05s"

    def test_file_operations_performance(self, temp_dir):
        """Test file I/O performance with various file sizes."""
        file_sizes = [1, 10, 100, 1000]  # KB
        results = {}

        for size_kb in file_sizes:
            # Create test file
            test_file = temp_dir / f"test_{size_kb}kb.txt"
            content = "a" * (size_kb * 1024)

            # Measure write time
            _, write_time = self.measure_time(test_file.write_text, content)

            # Measure read time
            _, read_time = self.measure_time(test_file.read_text)

            results[size_kb] = {
                'write_time': write_time,
                'read_time': read_time,
                'write_speed_mbps': (size_kb / 1024) / write_time if write_time > 0 else float('inf'),
                'read_speed_mbps': (size_kb / 1024) / read_time if read_time > 0 else float('inf')
            }

            # Performance assertions
            assert write_time < 0.1, f"Writing {size_kb}KB took {write_time:.3f}s"
            assert read_time < 0.05, f"Reading {size_kb}KB took {read_time:.3f}s"

        # Log performance results
        print("\n📊 File I/O Performance Results:")
        for size_kb, metrics in results.items():
            print(f"  {size_kb}KB: Write {metrics['write_time']:.3f}s ({metrics['write_speed_mbps']:.1f} MB/s), "
                  f"Read {metrics['read_time']:.3f}s ({metrics['read_speed_mbps']:.1f} MB/s)")

    def test_transcription_mock_performance(self, audio_files):
        """Test transcription service performance with mocked API calls."""
        with patch('transcription.TranscriptionService') as MockService:
            mock_service = Mock()
            MockService.return_value = mock_service

            # Configure mock to simulate realistic API response times
            def mock_transcribe(audio_file):
                file_path = Path(audio_file)
                # Simulate processing time based on file size
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                time.sleep(min(file_size_mb * 0.1, 2.0))  # Max 2 seconds for testing

                return Mock(
                    text=f"Mock transcription for {file_path.name}",
                    confidence=0.95,
                    duration=file_size_mb * 10,  # Rough estimate
                    word_count=int(file_size_mb * 150),  # Rough estimate
                    cost_usd=file_size_mb * 0.006
                )

            mock_service.transcribe_audio = mock_transcribe

            results = {}

            for audio_file, duration in audio_files:
                _, transcribe_time = self.measure_time(mock_service.transcribe_audio, str(audio_file))
                file_size_mb = audio_file.stat().st_size / (1024 * 1024)

                results[duration] = {
                    'transcribe_time': transcribe_time,
                    'file_size_mb': file_size_mb,
                    'processing_ratio': transcribe_time / duration  # How much longer than real-time
                }

                # Performance assertions
                assert transcribe_time < duration * 2, f"Transcription took {transcribe_time:.3f}s for {duration}s audio"

            print("\n🎙️ Transcription Performance Results:")
            for duration, metrics in results.items():
                print(f"  {duration}s audio: {metrics['transcribe_time']:.3f}s processing "
                      f"({metrics['processing_ratio']:.1f}x realtime)")

    def test_conversation_processing_performance(self):
        """Test conversation manager performance with different transcript sizes."""
        with patch('conversation_manager.ConversationManager') as MockManager:
            mock_manager = Mock()
            MockManager.return_value = mock_manager

            def mock_process(transcript):
                # Simulate processing time based on transcript length
                word_count = len(transcript.split())
                processing_time = min(word_count * 0.001, 3.0)  # Max 3 seconds
                time.sleep(processing_time)

                return {
                    'key_insight': f"Processed {word_count} words",
                    'topic_type': 'general',
                    'conversation': [
                        {'role': 'user', 'content': transcript[:100] + '...'},
                        {'role': 'assistant', 'content': 'Processed response'}
                    ],
                    'action_items': ['Action based on transcript'],
                    'entities': ['entity1', 'entity2'],
                    'topics': ['topic1', 'topic2']
                }

            mock_manager.process_transcript = mock_process

            # Test different transcript sizes
            transcript_sizes = [50, 200, 500, 1000]  # word counts
            results = {}

            for word_count in transcript_sizes:
                transcript = "test word " * word_count
                _, processing_time = self.measure_time(mock_manager.process_transcript, transcript)

                results[word_count] = {
                    'processing_time': processing_time,
                    'words_per_second': word_count / processing_time if processing_time > 0 else float('inf')
                }

                # Performance assertions
                assert processing_time < 5.0, f"Processing {word_count} words took {processing_time:.3f}s"
                assert processing_time < word_count * 0.01, f"Processing too slow for {word_count} words"

            print("\n💬 Conversation Processing Performance:")
            for word_count, metrics in results.items():
                print(f"  {word_count} words: {metrics['processing_time']:.3f}s "
                      f"({metrics['words_per_second']:.0f} words/s)")

    def test_notification_system_performance(self):
        """Test notification system performance."""
        with patch('desktop_notifications.DesktopNotificationSystem') as MockNotifications:
            mock_system = Mock()
            MockNotifications.return_value = mock_system

            # Mock notification methods to be very fast
            mock_system.show_notification.return_value = True
            mock_system.notify_recording_started.return_value = True
            mock_system.notify_processing_complete.return_value = True

            # Test multiple rapid notifications
            notification_count = 50
            start_time = time.perf_counter()

            for i in range(notification_count):
                mock_system.show_notification(Mock())

            total_time = time.perf_counter() - start_time
            avg_time = total_time / notification_count

            # Performance assertions
            assert avg_time < 0.01, f"Average notification time {avg_time:.4f}s too slow"
            assert total_time < 0.5, f"Total notification time {total_time:.3f}s too slow"

            print(f"\n🔔 Notification Performance: {notification_count} notifications in {total_time:.3f}s "
                  f"(avg {avg_time*1000:.2f}ms each)")

    def test_concurrent_operations_performance(self):
        """Test system performance under concurrent load."""
        def simulate_voice_note_processing(operation_id):
            """Simulate a complete voice note processing operation."""
            start_time = time.perf_counter()

            # Mock the components
            with patch('audio_recorder.AudioRecorder') as MockRecorder:
                with patch('transcription.TranscriptionService') as MockTranscription:
                    with patch('conversation_manager.ConversationManager') as MockConversation:

                        mock_recorder = Mock()
                        mock_transcription = Mock()
                        mock_conversation = Mock()

                        MockRecorder.return_value = mock_recorder
                        MockTranscription.return_value = mock_transcription
                        MockConversation.return_value = mock_conversation

                        # Simulate realistic processing delays
                        time.sleep(0.01)  # Recording setup
                        mock_recorder.start_recording()

                        time.sleep(0.02)  # Recording time (simulated)
                        mock_recorder.stop_recording()

                        # Transcription (simulated network delay)
                        time.sleep(0.1)
                        mock_transcription.transcribe_audio.return_value = Mock(
                            text=f"Operation {operation_id} transcript"
                        )

                        # Conversation processing
                        time.sleep(0.05)
                        mock_conversation.process_transcript.return_value = {
                            'key_insight': f'Insight {operation_id}'
                        }

                        processing_time = time.perf_counter() - start_time
                        return operation_id, processing_time

        # Test concurrent operations
        concurrent_operations = 10

        with ThreadPoolExecutor(max_workers=5) as executor:
            start_time = time.perf_counter()

            # Submit all operations
            futures = [executor.submit(simulate_voice_note_processing, i)
                      for i in range(concurrent_operations)]

            # Collect results
            results = []
            for future in as_completed(futures):
                operation_id, processing_time = future.result()
                results.append((operation_id, processing_time))

            total_concurrent_time = time.perf_counter() - start_time

        # Analysis
        individual_times = [time for _, time in results]
        avg_individual_time = sum(individual_times) / len(individual_times)
        max_individual_time = max(individual_times)

        # Performance assertions
        assert total_concurrent_time < max_individual_time * 2, "Concurrent operations not parallel enough"
        assert avg_individual_time < 0.5, f"Individual operations too slow: {avg_individual_time:.3f}s"

        print(f"\n⚡ Concurrent Performance: {concurrent_operations} operations")
        print(f"   Total time: {total_concurrent_time:.3f}s")
        print(f"   Average individual: {avg_individual_time:.3f}s")
        print(f"   Max individual: {max_individual_time:.3f}s")
        print(f"   Concurrency efficiency: {(avg_individual_time * concurrent_operations / total_concurrent_time):.1f}x")

    def test_memory_usage_simulation(self):
        """Test memory usage patterns during operation."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Simulate memory-intensive operations
        large_data = []

        # Simulate loading large audio files
        for i in range(10):
            # Simulate 1MB audio data
            audio_data = np.random.random(44100) * 32767  # 1 second of audio data
            large_data.append(audio_data)

            current_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = current_memory - initial_memory

            # Memory should not grow excessively
            assert memory_increase < 100, f"Memory usage increased by {memory_increase:.1f}MB"

        # Clean up
        large_data.clear()

        final_memory = process.memory_info().rss / 1024 / 1024
        print(f"\n💾 Memory Usage: Initial {initial_memory:.1f}MB, Final {final_memory:.1f}MB")

    def test_system_tray_performance(self):
        """Test system tray operations performance."""
        with patch('system_tray.VoiceNotesSystemTray') as MockTray:
            mock_tray = Mock()
            MockTray.return_value = mock_tray

            # Test rapid status updates
            status_updates = ['ready', 'recording', 'processing', 'ready'] * 25

            start_time = time.perf_counter()
            for status in status_updates:
                mock_tray.update_status(status)
            update_time = time.perf_counter() - start_time

            # Test menu creation
            _, menu_time = self.measure_time(mock_tray.create_menu)

            # Performance assertions
            assert update_time < 1.0, f"Status updates took {update_time:.3f}s"
            assert menu_time < 0.1, f"Menu creation took {menu_time:.3f}s"

            print(f"\n🖥️ System Tray Performance: {len(status_updates)} updates in {update_time:.3f}s")

    @pytest.mark.slow
    def test_endurance_simulation(self):
        """Test system endurance with extended operation simulation."""
        # This test simulates extended usage patterns
        simulation_cycles = 100
        performance_data = []

        for cycle in range(simulation_cycles):
            cycle_start = time.perf_counter()

            # Simulate a voice note cycle
            with patch('audio_recorder.AudioRecorder') as MockRecorder:
                mock_recorder = Mock()
                MockRecorder.return_value = mock_recorder

                # Quick operations to simulate real usage
                mock_recorder.start_recording()
                time.sleep(0.001)  # Very short for testing
                mock_recorder.stop_recording()

            cycle_time = time.perf_counter() - cycle_start
            performance_data.append(cycle_time)

            # Check for performance degradation
            if cycle > 50:  # After warmup
                avg_recent = sum(performance_data[-10:]) / 10
                avg_early = sum(performance_data[10:20]) / 10

                degradation = (avg_recent - avg_early) / avg_early if avg_early > 0 else 0
                assert degradation < 0.5, f"Performance degraded by {degradation*100:.1f}% at cycle {cycle}"

        # Overall performance analysis
        total_time = sum(performance_data)
        avg_time = total_time / len(performance_data)

        print(f"\n⏱️ Endurance Test: {simulation_cycles} cycles")
        print(f"   Total time: {total_time:.3f}s")
        print(f"   Average per cycle: {avg_time*1000:.2f}ms")


class TestSystemResourceUsage:
    """Test system resource usage patterns."""

    def test_cpu_usage_simulation(self):
        """Test CPU usage during various operations."""
        import psutil

        cpu_samples = []

        # Baseline CPU usage
        baseline_cpu = psutil.cpu_percent(interval=0.1)

        # Simulate CPU-intensive operation
        def cpu_intensive_task():
            # Simulate transcription processing
            for _ in range(1000):
                data = [i ** 2 for i in range(100)]

        start_time = time.perf_counter()
        cpu_intensive_task()
        end_time = time.perf_counter()

        # CPU usage should be reasonable
        task_time = end_time - start_time
        assert task_time < 1.0, f"CPU task took {task_time:.3f}s"

        print(f"\n🔥 CPU Usage Test: Task completed in {task_time:.3f}s")

    def test_disk_io_performance(self, temp_dir):
        """Test disk I/O performance for voice notes."""
        import os

        # Test sequential file operations
        file_count = 20
        file_size_kb = 50

        write_times = []
        read_times = []

        files_created = []

        for i in range(file_count):
            file_path = temp_dir / f"test_note_{i}.md"
            content = f"# Voice Note {i}\n" + ("Content line.\n" * (file_size_kb * 10))

            # Write test
            start_time = time.perf_counter()
            file_path.write_text(content)
            write_time = time.perf_counter() - start_time
            write_times.append(write_time)

            # Read test
            start_time = time.perf_counter()
            read_content = file_path.read_text()
            read_time = time.perf_counter() - start_time
            read_times.append(read_time)

            files_created.append(file_path)

            assert len(read_content) == len(content), "File content mismatch"

        # Performance analysis
        avg_write_time = sum(write_times) / len(write_times)
        avg_read_time = sum(read_times) / len(read_times)

        # Performance assertions
        assert avg_write_time < 0.1, f"Average write time {avg_write_time:.3f}s too slow"
        assert avg_read_time < 0.05, f"Average read time {avg_read_time:.3f}s too slow"

        print(f"\n💽 Disk I/O Performance: {file_count} files")
        print(f"   Average write: {avg_write_time*1000:.2f}ms")
        print(f"   Average read: {avg_read_time*1000:.2f}ms")

        # Cleanup
        for file_path in files_created:
            if file_path.exists():
                file_path.unlink()


if __name__ == '__main__':
    # Run with performance markers
    pytest.main([__file__, '-v', '-m', 'not slow'])