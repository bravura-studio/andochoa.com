"""
Whisper API transcription service with cost tracking and error handling.

This module provides robust transcription capabilities using OpenAI's Whisper API
with retry logic, cost tracking, and comprehensive error handling.
"""

import os
import time
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from .config_manager import ConfigManager
except ImportError:
    from config_manager import ConfigManager


@dataclass
class TranscriptionResult:
    """Result of a transcription operation."""
    text: str
    duration: float
    language: Optional[str] = None
    confidence: Optional[float] = None
    word_count: int = 0
    cost_estimate: float = 0.0
    api_used: str = "whisper"
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.word_count == 0 and self.text:
            self.word_count = len(self.text.split())


@dataclass
class UsageMetrics:
    """API usage metrics for cost tracking."""
    total_requests: int = 0
    total_duration: float = 0.0
    total_cost: float = 0.0
    daily_cost: float = 0.0
    monthly_cost: float = 0.0
    last_reset: datetime = None

    def __post_init__(self):
        if self.last_reset is None:
            self.last_reset = datetime.now()


class CostTracker:
    """Tracks API usage and costs."""

    # Whisper API pricing (per minute of audio)
    WHISPER_COST_PER_MINUTE = 0.006  # $0.006 per minute

    def __init__(self, data_dir: str = "logs"):
        """Initialize cost tracker.

        Args:
            data_dir: Directory to store usage data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.usage_file = self.data_dir / "usage_metrics.json"
        self.logger = logging.getLogger(__name__)

        # Load existing metrics
        self.metrics = self._load_metrics()

    def _load_metrics(self) -> UsageMetrics:
        """Load usage metrics from file."""
        try:
            if self.usage_file.exists():
                with open(self.usage_file, 'r') as f:
                    data = json.load(f)
                    # Convert timestamp strings back to datetime objects
                    if 'last_reset' in data:
                        data['last_reset'] = datetime.fromisoformat(data['last_reset'])
                    return UsageMetrics(**data)
        except Exception as e:
            self.logger.warning(f"Could not load usage metrics: {e}")

        return UsageMetrics()

    def _save_metrics(self):
        """Save usage metrics to file."""
        try:
            data = asdict(self.metrics)
            # Convert datetime to string for JSON serialization
            if 'last_reset' in data and data['last_reset']:
                data['last_reset'] = data['last_reset'].isoformat()

            with open(self.usage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save usage metrics: {e}")

    def track_usage(self, duration_minutes: float, api_name: str = "whisper") -> float:
        """Track API usage and return cost.

        Args:
            duration_minutes: Duration of audio in minutes
            api_name: Name of API used

        Returns:
            Cost of this request
        """
        # Calculate cost
        if api_name.lower() == "whisper":
            cost = duration_minutes * self.WHISPER_COST_PER_MINUTE
        else:
            cost = 0.0  # Free fallback services

        # Update metrics
        self.metrics.total_requests += 1
        self.metrics.total_duration += duration_minutes
        self.metrics.total_cost += cost

        # Reset daily/monthly if needed
        now = datetime.now()
        if self._is_new_day():
            self.metrics.daily_cost = cost
        else:
            self.metrics.daily_cost += cost

        if self._is_new_month():
            self.metrics.monthly_cost = cost
        else:
            self.metrics.monthly_cost += cost

        # Save metrics
        self._save_metrics()

        self.logger.info(f"Usage tracked: {duration_minutes:.2f}min, ${cost:.4f}")
        return cost

    def _is_new_day(self) -> bool:
        """Check if it's a new day since last reset."""
        if not self.metrics.last_reset:
            return True
        return self.metrics.last_reset.date() < datetime.now().date()

    def _is_new_month(self) -> bool:
        """Check if it's a new month since last reset."""
        if not self.metrics.last_reset:
            return True
        now = datetime.now()
        last = self.metrics.last_reset
        return (now.year, now.month) != (last.year, last.month)

    def get_usage_summary(self) -> Dict[str, Any]:
        """Get current usage summary."""
        return {
            "total_requests": self.metrics.total_requests,
            "total_duration_minutes": round(self.metrics.total_duration, 2),
            "total_cost": round(self.metrics.total_cost, 4),
            "daily_cost": round(self.metrics.daily_cost, 4),
            "monthly_cost": round(self.metrics.monthly_cost, 4),
            "average_cost_per_minute": (
                round(self.metrics.total_cost / self.metrics.total_duration, 4)
                if self.metrics.total_duration > 0 else 0
            ),
            "last_updated": datetime.now().isoformat()
        }

    def check_limits(self, daily_limit: float, monthly_limit: float) -> Dict[str, Any]:
        """Check if usage is approaching limits.

        Args:
            daily_limit: Daily spending limit
            monthly_limit: Monthly spending limit

        Returns:
            Dictionary with limit status
        """
        daily_pct = (self.metrics.daily_cost / daily_limit * 100) if daily_limit > 0 else 0
        monthly_pct = (self.metrics.monthly_cost / monthly_limit * 100) if monthly_limit > 0 else 0

        return {
            "daily_usage": round(self.metrics.daily_cost, 4),
            "daily_limit": daily_limit,
            "daily_percentage": round(daily_pct, 1),
            "monthly_usage": round(self.metrics.monthly_cost, 4),
            "monthly_limit": monthly_limit,
            "monthly_percentage": round(monthly_pct, 1),
            "daily_exceeded": daily_pct >= 100,
            "monthly_exceeded": monthly_pct >= 100,
            "daily_warning": daily_pct >= 80,
            "monthly_warning": monthly_pct >= 80
        }


class TranscriptionService:
    """Whisper API transcription service with retry logic and cost tracking."""

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize transcription service.

        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager or ConfigManager()
        self.logger = logging.getLogger(__name__)

        # Get API configuration
        openai_config = self.config.get_openai_config()

        self.api_key = openai_config.get('api_key') or os.getenv('OPENAI_API_KEY')
        self.model = openai_config.get('model', 'whisper-1')
        self.max_retries = openai_config.get('max_retries', 3)
        self.timeout = openai_config.get('timeout', 30)

        # Cost management
        cost_config = self.config.get_cost_management_config()
        self.daily_limit = cost_config.get('daily_limit', 5.0)
        self.monthly_limit = cost_config.get('monthly_limit', 50.0)
        self.track_usage_enabled = cost_config.get('track_usage', True)

        # Initialize OpenAI v1 client only (no legacy fallback)
        if self.api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.api_key)
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI v1 client: {e}")
                self.openai_client = None
        else:
            self.logger.warning("No OpenAI API key found. Transcription will not work.")
            self.openai_client = None

        # Initialize cost tracker
        self.cost_tracker = CostTracker() if self.track_usage_enabled else None

        # Setup retry strategy
        self.session = self._create_session()

        # Cache for preventing duplicate requests
        self.cache_dir = Path("temp_audio") / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry strategy."""
        session = requests.Session()

        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,  # Exponential backoff: 1, 2, 4 seconds
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_file_hash(self, file_path: str) -> str:
        """Generate hash for audio file to prevent duplicate processing."""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5()
                for chunk in iter(lambda: f.read(4096), b""):
                    file_hash.update(chunk)
                return file_hash.hexdigest()
        except Exception as e:
            self.logger.warning(f"Could not generate file hash: {e}")
            return str(time.time())  # Fallback to timestamp

    def _get_cached_result(self, file_hash: str) -> Optional[TranscriptionResult]:
        """Get cached transcription result if available."""
        cache_file = self.cache_dir / f"{file_hash}.json"
        try:
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    # Convert timestamp string back to datetime
                    if 'timestamp' in data:
                        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                    return TranscriptionResult(**data)
        except Exception as e:
            self.logger.debug(f"Could not load cached result: {e}")
        return None

    def _cache_result(self, file_hash: str, result: TranscriptionResult):
        """Cache transcription result."""
        cache_file = self.cache_dir / f"{file_hash}.json"
        try:
            data = asdict(result)
            # Convert datetime to string for JSON serialization
            if 'timestamp' in data and data['timestamp']:
                data['timestamp'] = data['timestamp'].isoformat()

            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not cache result: {e}")

    def _get_audio_duration(self, file_path: str) -> float:
        """Get audio file duration in minutes."""
        try:
            import soundfile as sf
            with sf.SoundFile(file_path) as f:
                duration_seconds = len(f) / f.samplerate
                return duration_seconds / 60.0
        except Exception as e:
            self.logger.warning(f"Could not get audio duration: {e}")
            # Fallback: estimate based on file size (rough approximation)
            try:
                file_size = Path(file_path).stat().st_size
                # Rough estimate: 1 minute of 44.1kHz mono audio ≈ 2.6MB
                estimated_minutes = file_size / (2.6 * 1024 * 1024)
                return max(0.1, estimated_minutes)  # Minimum 0.1 minutes
            except:
                return 1.0  # Default fallback

    def _check_cost_limits(self, estimated_cost: float) -> bool:
        """Check if request would exceed cost limits."""
        if not self.cost_tracker:
            return True

        limits = self.cost_tracker.check_limits(self.daily_limit, self.monthly_limit)

        # Check if adding this cost would exceed limits
        new_daily = limits['daily_usage'] + estimated_cost
        new_monthly = limits['monthly_usage'] + estimated_cost

        if new_daily > self.daily_limit:
            self.logger.error(f"Request would exceed daily limit: ${new_daily:.4f} > ${self.daily_limit}")
            return False

        if new_monthly > self.monthly_limit:
            self.logger.error(f"Request would exceed monthly limit: ${new_monthly:.4f} > ${self.monthly_limit}")
            return False

        # Warn if approaching limits
        if new_daily / self.daily_limit >= 0.8:
            self.logger.warning(f"Approaching daily limit: ${new_daily:.4f} / ${self.daily_limit}")

        if new_monthly / self.monthly_limit >= 0.8:
            self.logger.warning(f"Approaching monthly limit: ${new_monthly:.4f} / ${self.monthly_limit}")

        return True

    def transcribe_audio(self, audio_file: str, use_cache: bool = True) -> TranscriptionResult:
        """Transcribe audio file using Whisper API.

        Args:
            audio_file: Path to audio file
            use_cache: Whether to use cached results

        Returns:
            TranscriptionResult with text and metadata

        Raises:
            FileNotFoundError: If audio file doesn't exist
            ValueError: If API key is not configured
            RuntimeError: If transcription fails after retries
        """
        if not Path(audio_file).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        if not self.api_key or not self.openai_client:
            raise ValueError("OpenAI API key not configured")

        # Get file info
        file_hash = self._get_file_hash(audio_file)
        duration_minutes = self._get_audio_duration(audio_file)
        estimated_cost = duration_minutes * CostTracker.WHISPER_COST_PER_MINUTE

        # Check cache first
        if use_cache:
            cached_result = self._get_cached_result(file_hash)
            if cached_result:
                self.logger.info(f"Using cached transcription for {Path(audio_file).name}")
                return cached_result

        # Check cost limits
        if not self._check_cost_limits(estimated_cost):
            raise RuntimeError("Request would exceed cost limits")

        self.logger.info(f"Transcribing {Path(audio_file).name} ({duration_minutes:.2f}min, ~${estimated_cost:.4f})")

        start_time = time.time()

        try:
            # Open audio file
            with open(audio_file, 'rb') as audio:
                # Call Whisper API with retry logic
                response = self._call_whisper_api(audio)

            # Parse response
            text = response.get('text', '').strip()
            language = response.get('language')

            # Track actual cost
            actual_cost = 0.0
            if self.cost_tracker:
                actual_cost = self.cost_tracker.track_usage(duration_minutes, "whisper")

            # Create result
            result = TranscriptionResult(
                text=text,
                duration=duration_minutes,
                language=language,
                confidence=None,  # Whisper API doesn't provide confidence
                cost_estimate=actual_cost,
                api_used="whisper"
            )

            # Cache result
            if use_cache:
                self._cache_result(file_hash, result)

            elapsed_time = time.time() - start_time
            self.logger.info(f"Transcription completed in {elapsed_time:.2f}s")

            return result

        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Transcription failed: {e}")

    def _call_whisper_api(self, audio_file) -> Dict[str, Any]:
        """Call Whisper API with retry logic."""
        for attempt in range(self.max_retries + 1):
            try:
                # Require v1 client with audio.transcriptions.create
                if not (self.openai_client and hasattr(self.openai_client, "audio") and hasattr(self.openai_client.audio, "transcriptions")):
                    raise RuntimeError("OpenAI client not initialized with v1 SDK; cannot transcribe")

                response = self.openai_client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    response_format="json"
                )
                # Convert client object to dict when needed
                if isinstance(response, dict):
                    return response
                # Some clients use pydantic with model_dump
                if hasattr(response, "model_dump"):
                    return response.model_dump(mode="json")
                # Fallback: try common attributes
                return {k: getattr(response, k) for k in ("text", "language") if hasattr(response, k)}

            except Exception as e:
                # Handle OpenAI API errors
                error_message = str(e).lower()

                if "rate limit" in error_message or "429" in str(e):
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        self.logger.warning(f"Rate limit hit, retrying in {wait_time}s (attempt {attempt + 1})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RuntimeError(f"Rate limit exceeded after {self.max_retries} retries") from e

                elif "connection" in error_message or "network" in error_message:
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        self.logger.warning(f"API connection error, retrying in {wait_time}s (attempt {attempt + 1})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RuntimeError(f"API connection failed after {self.max_retries} retries") from e

                elif str(e).strip().startswith("5"):  # crude server-error detection
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        self.logger.warning(f"Server error, retrying in {wait_time}s (attempt {attempt + 1})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise RuntimeError(f"Server error after {self.max_retries} retries: {e}") from e
                else:
                    self.logger.error(f"Transcription API error: {e}")
                    raise RuntimeError(f"Transcription failed: {e}") from e

    def fallback_transcription(self, audio_file: str) -> TranscriptionResult:
        """Fallback transcription using local speech recognition.

        Args:
            audio_file: Path to audio file

        Returns:
            TranscriptionResult with lower quality transcription
        """
        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()
            duration_minutes = self._get_audio_duration(audio_file)

            # Convert to WAV if needed and load
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)

            # Try Google Speech Recognition (free)
            try:
                text = recognizer.recognize_google(audio_data)
                api_used = "google_free"
            except sr.UnknownValueError:
                text = "[Could not understand audio]"
                api_used = "fallback_failed"
            except sr.RequestError:
                # Try offline recognition if available
                try:
                    text = recognizer.recognize_sphinx(audio_data)
                    api_used = "sphinx_offline"
                except:
                    text = "[Transcription failed - offline recognition not available]"
                    api_used = "fallback_failed"

            self.logger.info(f"Fallback transcription completed using {api_used}")

            return TranscriptionResult(
                text=text,
                duration=duration_minutes,
                language="en",  # Assume English for fallback
                confidence=0.6,  # Lower confidence for fallback
                cost_estimate=0.0,  # Free fallback
                api_used=api_used
            )

        except ImportError:
            self.logger.error("speech_recognition not available for fallback")
            return TranscriptionResult(
                text="[Fallback transcription not available - missing dependencies]",
                duration=self._get_audio_duration(audio_file),
                cost_estimate=0.0,
                api_used="fallback_unavailable"
            )
        except Exception as e:
            self.logger.error(f"Fallback transcription failed: {e}")
            return TranscriptionResult(
                text="[Fallback transcription failed]",
                duration=self._get_audio_duration(audio_file),
                cost_estimate=0.0,
                api_used="fallback_error"
            )

    def handle_api_error(self, error: Exception) -> str:
        """Handle and categorize API errors.

        Args:
            error: The exception that occurred

        Returns:
            User-friendly error message
        """
        if isinstance(error, FileNotFoundError):
            return "Audio file not found"
        elif isinstance(error, ValueError):
            return "OpenAI API key not configured"
        elif "Rate limit" in str(error):
            return "API rate limit exceeded. Please try again later."
        elif "cost limits" in str(error):
            return "Daily or monthly cost limit exceeded"
        elif "API connection" in str(error):
            return "Failed to connect to OpenAI API. Check your internet connection."
        elif "API error" in str(error):
            return "OpenAI API error. Please try again later."
        else:
            return f"Transcription error: {str(error)}"

    def get_usage_summary(self) -> Dict[str, Any]:
        """Get API usage summary."""
        if not self.cost_tracker:
            return {"tracking_disabled": True}

        summary = self.cost_tracker.get_usage_summary()
        limits = self.cost_tracker.check_limits(self.daily_limit, self.monthly_limit)

        return {
            **summary,
            "limits": limits,
            "api_key_configured": bool(self.api_key),
            "model": self.model
        }

    def cleanup_cache(self, max_age_days: int = 7):
        """Clean up old cached transcription results.

        Args:
            max_age_days: Maximum age of cached files to keep
        """
        try:
            cutoff_time = time.time() - (max_age_days * 24 * 3600)
            cleaned_count = 0

            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file.stat().st_mtime < cutoff_time:
                    cache_file.unlink()
                    cleaned_count += 1

            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} old cache files")

        except Exception as e:
            self.logger.warning(f"Error cleaning cache: {e}")