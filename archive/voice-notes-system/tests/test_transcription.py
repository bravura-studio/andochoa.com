"""
Tests for transcription service with Whisper API integration.
"""

import unittest
import tempfile
import json
import os
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from src.transcription import (
        TranscriptionService, TranscriptionResult, CostTracker, UsageMetrics
    )
    from src.config_manager import ConfigManager
except ImportError:
    from transcription import (
        TranscriptionService, TranscriptionResult, CostTracker, UsageMetrics
    )
    from config_manager import ConfigManager


class TestTranscriptionResult(unittest.TestCase):
    """Test cases for TranscriptionResult dataclass."""

    def test_initialization(self):
        """Test basic initialization."""
        result = TranscriptionResult(
            text="Hello world",
            duration=1.5,
            language="en"
        )

        self.assertEqual(result.text, "Hello world")
        self.assertEqual(result.duration, 1.5)
        self.assertEqual(result.language, "en")
        self.assertEqual(result.word_count, 2)
        self.assertIsInstance(result.timestamp, datetime)

    def test_word_count_calculation(self):
        """Test automatic word count calculation."""
        result = TranscriptionResult(
            text="This is a test sentence with multiple words",
            duration=2.0
        )
        self.assertEqual(result.word_count, 8)

    def test_empty_text(self):
        """Test handling of empty text."""
        result = TranscriptionResult(text="", duration=1.0)
        self.assertEqual(result.word_count, 0)


class TestUsageMetrics(unittest.TestCase):
    """Test cases for UsageMetrics dataclass."""

    def test_initialization(self):
        """Test metrics initialization."""
        metrics = UsageMetrics()
        self.assertEqual(metrics.total_requests, 0)
        self.assertEqual(metrics.total_cost, 0.0)
        self.assertIsInstance(metrics.last_reset, datetime)

    def test_custom_initialization(self):
        """Test metrics with custom values."""
        timestamp = datetime.now()
        metrics = UsageMetrics(
            total_requests=10,
            total_cost=1.5,
            last_reset=timestamp
        )
        self.assertEqual(metrics.total_requests, 10)
        self.assertEqual(metrics.total_cost, 1.5)
        self.assertEqual(metrics.last_reset, timestamp)


class TestCostTracker(unittest.TestCase):
    """Test cases for CostTracker."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.tracker = CostTracker(data_dir=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test tracker initialization."""
        self.assertIsInstance(self.tracker.metrics, UsageMetrics)
        self.assertEqual(self.tracker.metrics.total_requests, 0)

    def test_track_usage_whisper(self):
        """Test usage tracking for Whisper API."""
        cost = self.tracker.track_usage(2.5, "whisper")

        expected_cost = 2.5 * CostTracker.WHISPER_COST_PER_MINUTE
        self.assertEqual(cost, expected_cost)
        self.assertEqual(self.tracker.metrics.total_requests, 1)
        self.assertEqual(self.tracker.metrics.total_duration, 2.5)
        self.assertEqual(self.tracker.metrics.total_cost, expected_cost)

    def test_track_usage_free_service(self):
        """Test usage tracking for free services."""
        cost = self.tracker.track_usage(1.0, "google_free")

        self.assertEqual(cost, 0.0)
        self.assertEqual(self.tracker.metrics.total_requests, 1)
        self.assertEqual(self.tracker.metrics.total_duration, 1.0)
        self.assertEqual(self.tracker.metrics.total_cost, 0.0)

    def test_get_usage_summary(self):
        """Test usage summary generation."""
        self.tracker.track_usage(1.0, "whisper")
        summary = self.tracker.get_usage_summary()

        self.assertIn("total_requests", summary)
        self.assertIn("total_cost", summary)
        self.assertEqual(summary["total_requests"], 1)

    def test_check_limits(self):
        """Test limit checking."""
        # Add some usage
        self.tracker.track_usage(100, "whisper")  # $0.60

        limits = self.tracker.check_limits(daily_limit=1.0, monthly_limit=10.0)

        self.assertIn("daily_usage", limits)
        self.assertIn("daily_percentage", limits)
        self.assertFalse(limits["daily_exceeded"])
        self.assertFalse(limits["monthly_exceeded"])

    def test_check_limits_exceeded(self):
        """Test limit exceeded detection."""
        # Add usage that exceeds limits
        self.tracker.track_usage(200, "whisper")  # $1.20

        limits = self.tracker.check_limits(daily_limit=1.0, monthly_limit=10.0)

        self.assertTrue(limits["daily_exceeded"])
        self.assertFalse(limits["monthly_exceeded"])

    @patch('src.transcription.json.dump')
    def test_save_metrics(self, mock_dump):
        """Test metrics saving."""
        self.tracker.track_usage(1.0, "whisper")
        mock_dump.assert_called()

    @patch('builtins.open', mock_open(read_data='{"total_requests": 5, "total_cost": 0.5}'))
    def test_load_metrics(self):
        """Test metrics loading from file."""
        # Create new tracker that should load existing data
        new_tracker = CostTracker(data_dir=self.temp_dir)
        # Note: Due to mocking, actual file won't be created, but we can test the method


class TestTranscriptionService(unittest.TestCase):
    """Test cases for TranscriptionService."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock config manager
        self.mock_config = Mock(spec=ConfigManager)
        self.mock_config.get_openai_config.return_value = {
            'api_key': 'test_key',
            'model': 'whisper-1',
            'max_retries': 3,
            'timeout': 30
        }
        self.mock_config.get_cost_management_config.return_value = {
            'daily_limit': 5.0,
            'monthly_limit': 50.0,
            'track_usage': True
        }

        # Create temp directory for testing
        self.temp_dir = tempfile.mkdtemp()

        # Mock OpenAI client
        with patch('src.transcription.openai') as mock_openai:
            self.service = TranscriptionService(config_manager=self.mock_config)
            self.service.cache_dir = Path(self.temp_dir) / "cache"
            self.service.cache_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test service initialization."""
        self.assertEqual(self.service.api_key, 'test_key')
        self.assertEqual(self.service.model, 'whisper-1')
        self.assertEqual(self.service.max_retries, 3)
        self.assertIsNotNone(self.service.cost_tracker)

    def test_initialization_no_api_key(self):
        """Test initialization without API key."""
        self.mock_config.get_openai_config.return_value = {'api_key': ''}

        with patch('src.transcription.openai'):
            service = TranscriptionService(config_manager=self.mock_config)
            self.assertIsNone(service.openai_client)

    def test_get_file_hash(self):
        """Test file hash generation."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"test audio data")
            tmp_file_path = tmp_file.name

        try:
            hash1 = self.service._get_file_hash(tmp_file_path)
            hash2 = self.service._get_file_hash(tmp_file_path)

            # Same file should produce same hash
            self.assertEqual(hash1, hash2)
            self.assertIsInstance(hash1, str)
            self.assertTrue(len(hash1) > 0)
        finally:
            os.unlink(tmp_file_path)

    def test_get_file_hash_error(self):
        """Test file hash generation with error."""
        # Non-existent file should return timestamp-based fallback
        hash_result = self.service._get_file_hash("/nonexistent/file.wav")
        self.assertIsInstance(hash_result, str)

    @patch('src.transcription.sf.SoundFile')
    def test_get_audio_duration(self, mock_sf):
        """Test audio duration calculation."""
        # Mock soundfile
        mock_file = Mock()
        mock_file.__len__ = Mock(return_value=44100)  # 1 second of audio
        mock_file.samplerate = 44100
        mock_sf.return_value.__enter__.return_value = mock_file

        duration = self.service._get_audio_duration("test.wav")

        # Should be 1 second = 1/60 minutes
        expected_duration = 1.0 / 60.0
        self.assertAlmostEqual(duration, expected_duration, places=3)

    def test_get_audio_duration_fallback(self):
        """Test audio duration fallback calculation."""
        with patch('src.transcription.sf.SoundFile', side_effect=Exception("No soundfile")):
            with patch('pathlib.Path.stat') as mock_stat:
                # Mock file size (1MB = rough estimate of ~0.38 minutes)
                mock_stat.return_value.st_size = 1024 * 1024

                duration = self.service._get_audio_duration("test.wav")
                self.assertGreater(duration, 0)

    @patch('src.transcription.Path')
    def test_cache_result(self, mock_path):
        """Test result caching."""
        result = TranscriptionResult(
            text="Test transcription",
            duration=1.5,
            language="en"
        )

        # Mock file operations
        mock_file = mock_open()
        cache_file = Mock()
        cache_file.open = mock_file
        mock_path.return_value = cache_file

        with patch('builtins.open', mock_file):
            self.service._cache_result("test_hash", result)

    def test_check_cost_limits(self):
        """Test cost limit checking."""
        # Mock cost tracker with low limits
        self.service.daily_limit = 1.0
        self.service.monthly_limit = 10.0

        # Small cost should pass
        self.assertTrue(self.service._check_cost_limits(0.1))

    def test_check_cost_limits_exceeded(self):
        """Test cost limit exceeded."""
        # Mock cost tracker
        mock_tracker = Mock()
        mock_tracker.check_limits.return_value = {
            'daily_usage': 0.9,
            'monthly_usage': 5.0
        }
        self.service.cost_tracker = mock_tracker
        self.service.daily_limit = 1.0

        # Cost that would exceed daily limit
        self.assertFalse(self.service._check_cost_limits(0.2))

    def test_handle_api_error(self):
        """Test API error handling."""
        # Test different error types
        errors = [
            (FileNotFoundError("File not found"), "Audio file not found"),
            (ValueError("No API key"), "OpenAI API key not configured"),
            (RuntimeError("Rate limit exceeded"), "API rate limit exceeded"),
            (RuntimeError("cost limits"), "Daily or monthly cost limit exceeded"),
            (Exception("Unknown error"), "Transcription error: Unknown error")
        ]

        for error, expected_message in errors:
            with self.subTest(error=error):
                message = self.service.handle_api_error(error)
                self.assertIn(expected_message.split(":")[0], message)

    @patch('src.transcription.openai')
    def test_call_whisper_api_success(self, mock_openai):
        """Test successful Whisper API call."""
        # Mock successful API response
        mock_response = {
            'text': 'Hello world',
            'language': 'en'
        }
        mock_openai.Audio.transcribe.return_value = mock_response

        # Mock audio file
        mock_audio = Mock()

        result = self.service._call_whisper_api(mock_audio)
        self.assertEqual(result['text'], 'Hello world')
        self.assertEqual(result['language'], 'en')

    @patch('src.transcription.openai')
    @patch('src.transcription.time.sleep')
    def test_call_whisper_api_retry(self, mock_sleep, mock_openai):
        """Test Whisper API retry logic."""
        import openai

        # Mock rate limit error followed by success
        mock_openai.error.RateLimitError = openai.error.RateLimitError
        mock_openai.Audio.transcribe.side_effect = [
            openai.error.RateLimitError("Rate limited"),
            {'text': 'Hello world', 'language': 'en'}
        ]

        mock_audio = Mock()
        result = self.service._call_whisper_api(mock_audio)

        # Should succeed after retry
        self.assertEqual(result['text'], 'Hello world')
        mock_sleep.assert_called_once()  # Should have slept for retry

    @patch('src.transcription.openai')
    def test_call_whisper_api_max_retries(self, mock_openai):
        """Test Whisper API max retries exceeded."""
        import openai

        # Mock persistent error
        mock_openai.error.RateLimitError = openai.error.RateLimitError
        mock_openai.Audio.transcribe.side_effect = openai.error.RateLimitError("Rate limited")

        mock_audio = Mock()

        with self.assertRaises(RuntimeError):
            self.service._call_whisper_api(mock_audio)

    @patch('builtins.open', mock_open(read_data=b"fake audio data"))
    @patch('src.transcription.Path')
    def test_transcribe_audio_file_not_found(self, mock_path):
        """Test transcription with non-existent file."""
        mock_path.return_value.exists.return_value = False

        with self.assertRaises(FileNotFoundError):
            self.service.transcribe_audio("nonexistent.wav")

    def test_transcribe_audio_no_api_key(self):
        """Test transcription without API key."""
        self.service.api_key = None
        self.service.openai_client = None

        with self.assertRaises(ValueError):
            self.service.transcribe_audio("test.wav")

    @patch('speech_recognition.Recognizer')
    @patch('speech_recognition.AudioFile')
    def test_fallback_transcription_success(self, mock_audio_file, mock_recognizer):
        """Test successful fallback transcription."""
        # Mock speech recognition
        mock_rec_instance = Mock()
        mock_recognizer.return_value = mock_rec_instance
        mock_rec_instance.record.return_value = "mock_audio_data"
        mock_rec_instance.recognize_google.return_value = "Hello from fallback"

        # Create temp audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(b"fake audio")
            tmp_file_path = tmp_file.name

        try:
            result = self.service.fallback_transcription(tmp_file_path)

            self.assertEqual(result.text, "Hello from fallback")
            self.assertEqual(result.api_used, "google_free")
            self.assertEqual(result.cost_estimate, 0.0)
        finally:
            os.unlink(tmp_file_path)

    def test_fallback_transcription_import_error(self):
        """Test fallback transcription when speech_recognition not available."""
        with patch('builtins.__import__', side_effect=ImportError("No module")):
            result = self.service.fallback_transcription("test.wav")

            self.assertIn("not available", result.text)
            self.assertEqual(result.api_used, "fallback_unavailable")

    def test_get_usage_summary(self):
        """Test usage summary retrieval."""
        summary = self.service.get_usage_summary()

        self.assertIn("api_key_configured", summary)
        self.assertIn("model", summary)
        self.assertTrue(summary["api_key_configured"])
        self.assertEqual(summary["model"], "whisper-1")

    def test_get_usage_summary_no_tracking(self):
        """Test usage summary when tracking disabled."""
        self.service.cost_tracker = None

        summary = self.service.get_usage_summary()
        self.assertTrue(summary["tracking_disabled"])

    def test_cleanup_cache(self):
        """Test cache cleanup."""
        # Create some old cache files
        old_file = self.service.cache_dir / "old_file.json"
        new_file = self.service.cache_dir / "new_file.json"

        old_file.write_text('{"test": "old"}')
        new_file.write_text('{"test": "new"}')

        # Make old file appear old
        old_time = time.time() - (8 * 24 * 3600)  # 8 days ago
        os.utime(old_file, (old_time, old_time))

        # Clean up files older than 7 days
        self.service.cleanup_cache(max_age_days=7)

        # Old file should be gone, new file should remain
        self.assertFalse(old_file.exists())
        self.assertTrue(new_file.exists())


class TestTranscriptionIntegration(unittest.TestCase):
    """Integration tests for transcription service."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.config = ConfigManager()

    @patch('src.transcription.openai')
    def test_full_integration_mock(self, mock_openai):
        """Test full transcription flow with mocked API."""
        # Mock API response
        mock_openai.Audio.transcribe.return_value = {
            'text': 'This is a test transcription from integration test',
            'language': 'en'
        }

        # Create service
        service = TranscriptionService(config_manager=self.config)
        service.api_key = "test_key"  # Override for testing
        service.openai_client = mock_openai

        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(b"fake audio data for testing")
            tmp_file_path = tmp_file.name

        try:
            # Test transcription
            result = service.transcribe_audio(tmp_file_path)

            self.assertIsInstance(result, TranscriptionResult)
            self.assertEqual(result.text, 'This is a test transcription from integration test')
            self.assertEqual(result.language, 'en')
            self.assertEqual(result.api_used, 'whisper')
            self.assertGreater(result.word_count, 0)
        finally:
            os.unlink(tmp_file_path)

    def test_cost_tracking_integration(self):
        """Test cost tracking integration."""
        # Create service with cost tracking
        service = TranscriptionService()

        if service.cost_tracker:
            # Test usage tracking
            initial_summary = service.get_usage_summary()

            # Simulate API usage
            service.cost_tracker.track_usage(2.0, "whisper")

            updated_summary = service.get_usage_summary()

            # Check that metrics were updated
            self.assertGreater(
                updated_summary.get("total_requests", 0),
                initial_summary.get("total_requests", 0)
            )


if __name__ == '__main__':
    unittest.main()