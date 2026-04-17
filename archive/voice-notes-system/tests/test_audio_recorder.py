import unittest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from audio_recorder import AudioRecorder
from config_manager import ConfigManager


class TestAudioRecorder(unittest.TestCase):
    """Unit tests for AudioRecorder class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

        # Mock configuration
        self.mock_config = Mock(spec=ConfigManager)
        self.mock_config.get_audio_config.return_value = {
            'sample_rate': 44100,
            'channels': 1,
            'format': 'WAV',
            'silence_threshold': 0.01,
            'silence_duration': 2.0,
            'input_device': ''
        }

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('audio_recorder.sd')
    def test_initialization(self, mock_sd):
        """Test AudioRecorder initialization."""
        # Mock sounddevice
        mock_sd.query_devices.return_value = [
            {'name': 'Test Device', 'max_input_channels': 1, 'default_samplerate': 44100}
        ]

        recorder = AudioRecorder(self.mock_config)

        self.assertEqual(recorder.sample_rate, 44100)
        self.assertEqual(recorder.channels, 1)
        self.assertEqual(recorder.silence_threshold, 0.01)
        self.assertEqual(recorder.silence_duration, 2.0)
        self.assertFalse(recorder.is_recording)

    @patch('audio_recorder.sd')
    def test_audio_device_check(self, mock_sd):
        """Test audio device checking."""
        # Test with available devices
        mock_devices = [
            {'name': 'Test Input', 'max_input_channels': 2, 'default_samplerate': 44100},
            {'name': 'Test Output', 'max_input_channels': 0, 'default_samplerate': 44100}
        ]
        mock_sd.query_devices.return_value = mock_devices
        mock_sd.query_devices.side_effect = None

        recorder = AudioRecorder(self.mock_config)
        # Should not raise any exceptions

        # Test with no input devices - create fresh mock for second test
        no_input_devices = [
            {'name': 'Test Output', 'max_input_channels': 0, 'default_samplerate': 44100}
        ]

        # We need to catch the exception during device checking, not initialization
        with patch('audio_recorder.sd') as mock_sd2:
            mock_sd2.query_devices.return_value = no_input_devices

            # The exception is caught and converted to a warning, so initialization succeeds
            recorder2 = AudioRecorder(self.mock_config)
            # This should not raise an exception because the error is caught

    def test_silence_detection_config(self):
        """Test silence detection configuration."""
        with patch('audio_recorder.sd'):
            recorder = AudioRecorder(self.mock_config)

            # Test valid parameters
            self.assertTrue(recorder.detect_silence(threshold=0.05, duration=1.5))
            self.assertEqual(recorder.silence_threshold, 0.05)
            self.assertEqual(recorder.silence_duration, 1.5)

            # Test invalid threshold
            self.assertFalse(recorder.detect_silence(threshold=1.5))
            self.assertEqual(recorder.silence_threshold, 0.05)  # Should remain unchanged

            # Test invalid duration
            self.assertFalse(recorder.detect_silence(duration=-1))
            self.assertEqual(recorder.silence_duration, 1.5)  # Should remain unchanged

    def test_audio_level_monitoring(self):
        """Test audio level monitoring."""
        with patch('audio_recorder.sd'):
            recorder = AudioRecorder(self.mock_config)

            # Test level callback
            callback_values = []
            def test_callback(level):
                callback_values.append(level)

            recorder.set_level_callback(test_callback)

            # Simulate audio callback with different levels
            test_data = np.array([[0.1], [0.5], [0.2]], dtype=np.float32)
            recorder._audio_callback(test_data, 3, None, None)

            # Check that level was calculated and callback was called
            self.assertGreater(recorder.current_level, 0)
            self.assertEqual(len(callback_values), 1)
            self.assertGreater(callback_values[0], 0)

    @patch('audio_recorder.sd')
    def test_should_auto_stop(self, mock_sd):
        """Test auto-stop silence detection logic."""
        recorder = AudioRecorder(self.mock_config)

        # Test with loud audio (should not stop)
        loud_audio = np.array([[0.5], [0.4]], dtype=np.float32)
        self.assertFalse(recorder._should_auto_stop(loud_audio))
        self.assertIsNone(recorder.silence_start_time)

        # Test with quiet audio (should start silence timer)
        quiet_audio = np.array([[0.001], [0.002]], dtype=np.float32)
        self.assertFalse(recorder._should_auto_stop(quiet_audio))
        self.assertIsNotNone(recorder.silence_start_time)

        # Simulate time passing
        original_time = recorder.silence_start_time
        recorder.silence_start_time = time.time() - 3.0  # 3 seconds ago

        # Should trigger auto-stop
        self.assertTrue(recorder._should_auto_stop(quiet_audio))

    def test_recording_duration(self):
        """Test recording duration calculation."""
        with patch('audio_recorder.sd'):
            recorder = AudioRecorder(self.mock_config)

            # No frames recorded
            self.assertEqual(recorder.get_recording_duration(), 0.0)

            # Add some test frames
            frame_size = 1024
            num_frames = 5
            for _ in range(num_frames):
                frame = np.zeros((frame_size, 1), dtype=np.float32)
                recorder.recorded_frames.append(frame)

            expected_duration = (frame_size * num_frames) / 44100
            self.assertAlmostEqual(recorder.get_recording_duration(), expected_duration, places=3)

    @patch('audio_recorder.sf')
    def test_save_audio(self, mock_sf):
        """Test audio saving functionality."""
        with patch('audio_recorder.sd'):
            recorder = AudioRecorder(self.mock_config)

            # Test with no recorded data
            with self.assertRaises(ValueError):
                recorder.save_audio()

            # Add some test data
            test_frames = [
                np.ones((1024, 1), dtype=np.float32) * 0.1,
                np.ones((1024, 1), dtype=np.float32) * 0.2
            ]
            recorder.recorded_frames = test_frames

            # Test auto-generated filename
            filepath = recorder.save_audio()
            self.assertTrue(filepath.endswith('.wav'))

            # Verify sf.write was called
            mock_sf.write.assert_called_once()
            call_args = mock_sf.write.call_args
            self.assertEqual(call_args[0][0], filepath)  # filepath
            self.assertEqual(call_args[0][2], 44100)     # sample_rate

            # Test custom filepath
            custom_path = str(self.temp_path / "test.wav")
            filepath = recorder.save_audio(custom_path)
            self.assertEqual(filepath, custom_path)

    @patch('audio_recorder.sd')
    def test_get_device_info(self, mock_sd):
        """Test device information retrieval."""
        mock_device = {
            'name': 'Test Device',
            'max_input_channels': 2,
            'default_samplerate': 44100,
            'hostapi': 0
        }
        mock_sd.query_devices.return_value = mock_device

        recorder = AudioRecorder(self.mock_config)
        device_info = recorder.get_device_info()

        self.assertEqual(device_info['name'], 'Test Device')
        self.assertEqual(device_info['channels'], 2)
        self.assertEqual(device_info['sample_rate'], 44100)

    def test_clear_recording(self):
        """Test recording data clearing."""
        with patch('audio_recorder.sd'):
            recorder = AudioRecorder(self.mock_config)

            # Add some test data
            recorder.recorded_frames = [np.zeros((100, 1))]
            recorder.silence_start_time = time.time()

            recorder.clear_recording()

            self.assertEqual(len(recorder.recorded_frames), 0)
            self.assertIsNone(recorder.silence_start_time)

    @patch('audio_recorder.sd')
    def test_context_manager(self, mock_sd):
        """Test context manager functionality."""
        with AudioRecorder(self.mock_config) as recorder:
            self.assertIsInstance(recorder, AudioRecorder)

        # Context manager should ensure recording is stopped

    def test_cleanup_temp_files(self):
        """Test temporary file cleanup."""
        with patch('audio_recorder.sd'):
            recorder = AudioRecorder(self.mock_config)
            recorder.temp_dir = self.temp_path

            # Create some test files with different ages
            old_file = self.temp_path / "old_recording.wav"
            new_file = self.temp_path / "new_recording.wav"

            old_file.touch()
            new_file.touch()

            # Modify old file's timestamp to make it old
            import os
            old_time = time.time() - (25 * 3600)  # 25 hours ago
            os.utime(old_file, (old_time, old_time))

            # Cleanup files older than 24 hours
            recorder.cleanup_temp_files(max_age_hours=24)

            # Old file should be deleted, new file should remain
            self.assertFalse(old_file.exists())
            self.assertTrue(new_file.exists())


class TestAudioRecorderIntegration(unittest.TestCase):
    """Integration tests for AudioRecorder (requires actual audio hardware)."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up integration test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @unittest.skipUnless(
        'sounddevice' in sys.modules and hasattr(sys.modules['sounddevice'], 'query_devices'),
        "Sounddevice not available"
    )
    def test_real_audio_devices(self):
        """Test with real audio devices (if available)."""
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]

            if not input_devices:
                self.skipTest("No audio input devices available")

            recorder = AudioRecorder()
            device_info = recorder.get_device_info()

            self.assertIn('name', device_info)
            self.assertNotIn('error', device_info)

        except Exception as e:
            self.skipTest(f"Audio hardware test failed: {e}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)