import os
import time
import threading
import queue
from pathlib import Path
from typing import Optional, Callable, List
from datetime import datetime

import numpy as np
import sounddevice as sd
import soundfile as sf

try:
    from .config_manager import ConfigManager
except ImportError:
    from config_manager import ConfigManager


class AudioRecorder:
    """Audio recording system with silence detection and level monitoring."""

    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize audio recorder.

        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager or ConfigManager()
        self.audio_config = self.config.get_audio_config()

        # Audio settings from configuration
        self.sample_rate = self.audio_config.get('sample_rate', 44100)
        self.channels = self.audio_config.get('channels', 1)
        self.format = self.audio_config.get('format', 'WAV')

        # Silence detection settings
        self.silence_threshold = self.audio_config.get('silence_threshold', 0.01)
        self.silence_duration = self.audio_config.get('silence_duration', 2.0)

        # Input device
        input_device = self.audio_config.get('input_device', '')
        self.input_device = input_device if input_device else None

        # Recording state
        self.is_recording = False
        self.recording_thread: Optional[threading.Thread] = None
        self.audio_queue = queue.Queue()
        self.recorded_frames: List[np.ndarray] = []

        # Monitoring
        self.current_level = 0.0
        self.level_callback: Optional[Callable[[float], None]] = None
        self.silence_start_time: Optional[float] = None

        # Temporary file management - use absolute path in project directory
        project_root = Path(__file__).parent.parent
        self.temp_dir = project_root / "temp_audio"
        try:
            self.temp_dir.mkdir(exist_ok=True)
        except (OSError, PermissionError) as e:
            # Fallback to user's temporary directory if project dir is read-only
            import tempfile
            self.temp_dir = Path(tempfile.gettempdir()) / "voice_notes_temp"
            self.temp_dir.mkdir(exist_ok=True)
            print(f"Warning: Using fallback temp directory: {self.temp_dir} (Original error: {e})")

        # Verify audio device availability
        self._check_audio_devices()

    def _check_audio_devices(self):
        """Check available audio input devices."""
        try:
            devices = sd.query_devices()
            input_devices = [d for d in devices if d['max_input_channels'] > 0]

            if not input_devices:
                raise RuntimeError("No audio input devices found")

            if self.input_device is None:
                # Use default input device
                default_device = sd.query_devices(kind='input')
                print(f"Using default input device: {default_device['name']}")
            else:
                # Verify specified device exists
                device_found = False
                for device in input_devices:
                    if self.input_device in device['name']:
                        device_found = True
                        print(f"Using specified input device: {device['name']}")
                        break

                if not device_found:
                    print(f"Warning: Specified device '{self.input_device}' not found")
                    print("Available input devices:")
                    for i, device in enumerate(input_devices):
                        print(f"  {i}: {device['name']}")
                    self.input_device = None

        except Exception as e:
            print(f"Warning: Could not check audio devices: {e}")

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback function for audio stream.

        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Timing information
            status: Stream status
        """
        if status:
            print(f"Audio callback status: {status}")

        # Calculate current audio level (RMS)
        if len(indata) > 0:
            self.current_level = float(np.sqrt(np.mean(indata**2)))

            # Notify level callback if registered
            if self.level_callback:
                self.level_callback(self.current_level)

            # Add audio data to queue for processing
            self.audio_queue.put(indata.copy())

    def start_recording(self) -> bool:
        """Start audio recording.

        Returns:
            True if recording started successfully, False otherwise
        """
        if self.is_recording:
            print("Recording is already in progress")
            return False

        try:
            # Clear previous recording data
            self.recorded_frames.clear()
            self.silence_start_time = None

            # Start audio stream
            self.stream = sd.InputStream(
                callback=self._audio_callback,
                channels=self.channels,
                samplerate=self.sample_rate,
                device=self.input_device,
                dtype=np.float32
            )

            self.stream.start()
            self.is_recording = True

            # Start recording thread to process audio data
            self.recording_thread = threading.Thread(target=self._recording_loop)
            self.recording_thread.daemon = True
            self.recording_thread.start()

            print(f"Recording started - Sample rate: {self.sample_rate}Hz, Channels: {self.channels}")
            return True

        except Exception as e:
            print(f"Failed to start recording: {e}")
            self.is_recording = False
            return False

    def stop_recording(self) -> bool:
        """Stop audio recording.

        Returns:
            True if recording stopped successfully, False otherwise
        """
        if not self.is_recording:
            print("No recording in progress")
            return False

        try:
            self.is_recording = False

            # Stop audio stream
            if hasattr(self, 'stream'):
                self.stream.stop()
                self.stream.close()

            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                # Don't try to join the current thread
                if self.recording_thread != threading.current_thread():
                    self.recording_thread.join(timeout=1.0)

            print("Recording stopped")
            return True

        except Exception as e:
            print(f"Error stopping recording: {e}")
            return False

    def _recording_loop(self):
        """Main recording loop that processes audio data."""
        while self.is_recording:
            try:
                # Get audio data from queue with timeout
                audio_data = self.audio_queue.get(timeout=0.1)
                self.recorded_frames.append(audio_data)

                # Check for silence detection
                if self._should_auto_stop(audio_data):
                    print("Auto-stopping recording due to silence")
                    self.stop_recording()
                    break

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in recording loop: {e}")
                break

    def _should_auto_stop(self, audio_data: np.ndarray) -> bool:
        """Check if recording should auto-stop due to silence.

        Args:
            audio_data: Current audio frame

        Returns:
            True if should auto-stop, False otherwise
        """
        if not audio_data.size:
            return False

        # Calculate RMS level for this frame
        rms_level = float(np.sqrt(np.mean(audio_data**2)))

        if rms_level < self.silence_threshold:
            # We're in silence
            if self.silence_start_time is None:
                self.silence_start_time = time.time()
            elif time.time() - self.silence_start_time >= self.silence_duration:
                # Silence duration exceeded
                return True
        else:
            # Sound detected, reset silence timer
            self.silence_start_time = None

        return False

    def detect_silence(self, threshold: Optional[float] = None, duration: Optional[float] = None) -> bool:
        """Configure silence detection parameters.

        Args:
            threshold: Silence threshold (0.0 to 1.0)
            duration: Silence duration in seconds

        Returns:
            True if parameters updated successfully
        """
        try:
            if threshold is not None:
                if 0.0 <= threshold <= 1.0:
                    self.silence_threshold = threshold
                else:
                    print("Warning: Threshold must be between 0.0 and 1.0")
                    return False

            if duration is not None:
                if duration > 0:
                    self.silence_duration = duration
                else:
                    print("Warning: Duration must be positive")
                    return False

            print(f"Silence detection: threshold={self.silence_threshold}, duration={self.silence_duration}s")
            return True

        except Exception as e:
            print(f"Error configuring silence detection: {e}")
            return False

    def get_audio_level(self) -> float:
        """Get current audio level.

        Returns:
            Current RMS audio level (0.0 to 1.0)
        """
        return min(self.current_level, 1.0)

    def set_level_callback(self, callback: Callable[[float], None]):
        """Set callback function for audio level monitoring.

        Args:
            callback: Function to call with audio level updates
        """
        self.level_callback = callback

    def save_audio(self, filepath: Optional[str] = None) -> str:
        """Save recorded audio to file.

        Args:
            filepath: Output file path. If None, generates timestamp-based name.

        Returns:
            Path to saved audio file

        Raises:
            ValueError: If no audio data recorded
            RuntimeError: If save operation fails
        """
        if not self.recorded_frames:
            raise ValueError("No audio data to save")

        try:
            # Generate filepath if not provided
            if filepath is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"recording_{timestamp}.wav"
                filepath = str(self.temp_dir / filename)

            # Ensure directory exists
            output_path = Path(filepath)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Concatenate all recorded frames
            if self.recorded_frames:
                audio_data = np.concatenate(self.recorded_frames, axis=0)
            else:
                # Create empty audio data if no frames
                audio_data = np.zeros((0, self.channels), dtype=np.float32)

            # Save to WAV file
            sf.write(
                filepath,
                audio_data,
                self.sample_rate,
                format='WAV',
                subtype='PCM_16'
            )

            print(f"Audio saved to: {filepath}")
            print(f"Duration: {len(audio_data) / self.sample_rate:.1f} seconds")

            return filepath

        except Exception as e:
            raise RuntimeError(f"Failed to save audio: {e}")

    def get_recording_duration(self) -> float:
        """Get duration of current/last recording in seconds.

        Returns:
            Recording duration in seconds
        """
        if not self.recorded_frames:
            return 0.0

        total_frames = sum(len(frame) for frame in self.recorded_frames)
        return total_frames / self.sample_rate

    def clear_recording(self):
        """Clear recorded audio data."""
        self.recorded_frames.clear()
        self.silence_start_time = None
        print("Recording data cleared")

    def get_device_info(self) -> dict:
        """Get information about current audio device.

        Returns:
            Dictionary with device information
        """
        try:
            if self.input_device is None:
                device = sd.query_devices(kind='input')
            else:
                devices = sd.query_devices()
                device = None
                for d in devices:
                    if self.input_device in d['name']:
                        device = d
                        break

                if device is None:
                    device = sd.query_devices(kind='input')

            return {
                'name': device['name'],
                'channels': device['max_input_channels'],
                'sample_rate': device['default_samplerate'],
                'hostapi': device['hostapi']
            }

        except Exception as e:
            return {'error': str(e)}

    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up old temporary audio files.

        Args:
            max_age_hours: Maximum age of files to keep in hours
        """
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600

            for file_path in self.temp_dir.glob("*.wav"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        print(f"Cleaned up old temp file: {file_path}")

        except Exception as e:
            print(f"Error cleaning up temp files: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure recording is stopped."""
        if self.is_recording:
            self.stop_recording()