"""
Main Voice Notes Application with Error Recovery and Graceful Degradation.

Integrates all components of the voice notes system with comprehensive error handling,
automatic recovery, and graceful degradation capabilities.
"""

import asyncio
import logging
import os
import signal
import sys
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable

try:
    from .config_manager import ConfigManager
    from .audio_recorder import AudioRecorder
    from .transcription import TranscriptionService
    from .mcp_client import MCPClient, MockMCPClient
    from .conversation_manager import ConversationManager
    from .markdown_formatter import MarkdownFormatter
    from .file_manager import FileManager
    from .error_recovery import (
        ErrorRecoverySystem, ErrorType, ErrorSeverity, with_error_recovery
    )
    from .global_hotkey import GlobalHotkeyManager
except ImportError:
    # Handle direct execution
    from config_manager import ConfigManager
    from audio_recorder import AudioRecorder
    from transcription import TranscriptionService
    from mcp_client import MCPClient, MockMCPClient
    from conversation_manager import ConversationManager
    from markdown_formatter import MarkdownFormatter
    from file_manager import FileManager
    from error_recovery import (
        ErrorRecoverySystem, ErrorType, ErrorSeverity, with_error_recovery
    )
    from global_hotkey import GlobalHotkeyManager

logger = logging.getLogger(__name__)


class VoiceNotesApp:
    """Main application with integrated error recovery and graceful degradation."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the voice notes application.

        Args:
            config_path: Path to configuration file
        """
        # Initialize configuration
        config_dir = Path(config_path).parent
        self.config_manager = ConfigManager(config_dir)
        self.config = self.config_manager.config

        # Initialize error recovery system
        self.error_recovery = ErrorRecoverySystem(
            data_dir=self.config.get('files', {}).get('logs_directory', 'logs'),
            max_queue_size=100
        )

        # Application state
        self.is_running = False
        self.current_status = "ready"  # ready, recording, processing, error
        self.recording_start_time: Optional[datetime] = None
        self.last_error: Optional[str] = None

        # Component instances
        self.audio_recorder: Optional[AudioRecorder] = None
        self.transcription_service: Optional[TranscriptionService] = None
        self.mcp_client: Optional[MCPClient] = None
        self.conversation_manager: Optional[ConversationManager] = None
        self.file_manager: Optional[FileManager] = None
        self.hotkey_manager: Optional[GlobalHotkeyManager] = None

        # Degraded services fallbacks
        self.degraded_mode = False
        self.unavailable_services: List[str] = []

        # Background tasks
        self.recovery_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None

        # Callbacks for UI updates
        self.status_callbacks: List[Callable[[str], None]] = []
        self.error_callbacks: List[Callable[[str, str], None]] = []

        # Initialize components
        self._initialize_components()

        # Register retry functions
        self._register_retry_functions()

        logger.info("VoiceNotesApp initialized successfully")

    def _initialize_components(self):
        """Initialize all application components with error handling."""
        # Audio Recorder
        try:
            self.audio_recorder = AudioRecorder(self.config_manager)
            logger.info("Audio recorder initialized")
        except Exception as e:
            self._handle_component_failure("audio_recorder", e)

        # Transcription Service
        try:
            self.transcription_service = TranscriptionService(self.config_manager)
            logger.info("Transcription service initialized")
        except Exception as e:
            self._handle_component_failure("transcription_service", e)

        # MCP Client
        try:
            mcp_config = self.config.get('mcp', {})
            if mcp_config.get('enabled', True):
                server_url = mcp_config.get('server_url', 'http://localhost:8000')
                api_key = mcp_config.get('api_key')

                if mcp_config.get('use_mock', False):
                    self.mcp_client = MockMCPClient()
                    logger.info("Mock MCP client initialized")
                else:
                    self.mcp_client = MCPClient(server_url, api_key)
                    logger.info("MCP client initialized")
            else:
                logger.info("MCP client disabled in configuration")
        except Exception as e:
            self._handle_component_failure("mcp_client", e)
            # Fall back to mock client
            try:
                self.mcp_client = MockMCPClient()
                logger.info("Falling back to mock MCP client")
            except Exception as mock_e:
                self._handle_component_failure("mcp_fallback", mock_e)

        # Conversation Manager
        try:
            self.conversation_manager = ConversationManager()
            logger.info("Conversation manager initialized")
        except Exception as e:
            self._handle_component_failure("conversation_manager", e)

        # File Manager
        try:
            self.file_manager = FileManager(self.config)
            logger.info("File manager initialized")
        except Exception as e:
            self._handle_component_failure("file_manager", e)

        # Global Hotkey Manager
        try:
            self.hotkey_manager = GlobalHotkeyManager(
                config_manager=self.config_manager,
                audio_recorder=self.audio_recorder
            )
            # Set up callbacks for hotkey events
            self.hotkey_manager.set_callbacks(
                on_recording_start=self._on_recording_start,
                on_recording_stop=self._on_recording_stop,
                on_error=self._on_hotkey_error
            )
            logger.info("Global hotkey manager initialized")
        except Exception as e:
            self._handle_component_failure("hotkey_manager", e)

        # Check if we're in degraded mode
        if self.unavailable_services:
            self.degraded_mode = True
            self.current_status = "error"
            logger.warning(f"Running in degraded mode. Unavailable services: {', '.join(self.unavailable_services)}")

    def _handle_component_failure(self, component: str, error: Exception):
        """Handle failure to initialize a component."""
        self.unavailable_services.append(component)

        error_id = self.error_recovery.log_error(
            error=error,
            error_type=ErrorType.SYSTEM,
            severity=ErrorSeverity.HIGH,
            context={'component': component, 'initialization': True},
            user_message=f"Failed to initialize {component.replace('_', ' ')}"
        )

        logger.error(f"Failed to initialize {component}: {error}")

    def _register_retry_functions(self):
        """Register functions that can be retried by the error recovery system."""
        self.error_recovery.register_retry_function('transcribe_audio', self._retry_transcription)
        self.error_recovery.register_retry_function('save_voice_note', self._retry_save_note)
        self.error_recovery.register_retry_function('send_to_mcp', self._retry_mcp_request)

    async def start(self):
        """Start the voice notes application."""
        if self.is_running:
            logger.warning("Application is already running")
            return

        self.is_running = True

        try:
            # Start hotkey manager if available
            if self.hotkey_manager and 'hotkey_manager' not in self.unavailable_services:
                self.hotkey_manager.start()

            # Start background tasks
            self.recovery_task = asyncio.create_task(self._recovery_loop())
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())

            # Update status
            self.current_status = "error" if self.degraded_mode else "ready"
            self._notify_status_change(self.current_status)

            logger.info(f"Voice Notes application started {'in degraded mode' if self.degraded_mode else 'successfully'}")

        except Exception as e:
            self.error_recovery.log_error(
                error=e,
                error_type=ErrorType.SYSTEM,
                severity=ErrorSeverity.CRITICAL,
                context={'operation': 'start_application'}
            )
            logger.error(f"Failed to start application: {e}")
            raise

    async def stop(self):
        """Stop the voice notes application."""
        if not self.is_running:
            return

        logger.info("Stopping Voice Notes application...")
        self.is_running = False

        try:
            # Stop hotkey manager
            if self.hotkey_manager:
                self.hotkey_manager.stop()

            # Stop recording if active
            if self.current_status == "recording" and self.audio_recorder:
                await self._stop_recording()

            # Cancel background tasks
            if self.recovery_task:
                self.recovery_task.cancel()
            if self.cleanup_task:
                self.cleanup_task.cancel()

            # Close MCP client
            if self.mcp_client and hasattr(self.mcp_client, 'disconnect'):
                await self.mcp_client.disconnect()

            logger.info("Voice Notes application stopped")

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    @with_error_recovery(error_type=ErrorType.AUDIO_RECORDING, severity=ErrorSeverity.MEDIUM)
    async def _start_recording(self):
        """Start audio recording with error recovery."""
        if not self.audio_recorder or 'audio_recorder' in self.unavailable_services:
            raise RuntimeError("Audio recorder not available")

        if self.current_status == "recording":
            logger.warning("Recording is already in progress")
            return

        success = self.audio_recorder.start_recording()
        if success:
            self.current_status = "recording"
            self.recording_start_time = datetime.now()
            self._notify_status_change("recording")
            logger.info("Started recording")
        else:
            raise RuntimeError("Failed to start recording")

    @with_error_recovery(error_type=ErrorType.AUDIO_RECORDING, severity=ErrorSeverity.MEDIUM)
    async def _stop_recording(self):
        """Stop audio recording and process the audio."""
        if not self.audio_recorder or self.current_status != "recording":
            return

        success = self.audio_recorder.stop_recording()
        if not success:
            raise RuntimeError("Failed to stop recording")

        # Change status to processing
        self.current_status = "processing"
        self._notify_status_change("processing")

        try:
            # Save audio file
            audio_file = self.audio_recorder.save_audio()
            logger.info(f"Audio saved to: {audio_file}")

            # Process the audio
            await self._process_audio_file(audio_file)

        except Exception as e:
            self.current_status = "error"
            self._notify_status_change("error")
            self._notify_error("Recording processing failed", str(e))
            raise
        finally:
            # Reset recording state
            self.recording_start_time = None

    @with_error_recovery(error_type=ErrorType.TRANSCRIPTION, severity=ErrorSeverity.MEDIUM)
    async def _process_audio_file(self, audio_file: str):
        """Process audio file through the full pipeline."""
        try:
            # Step 1: Transcription
            transcript_result = await self._transcribe_audio(audio_file)

            # Step 2: Conversation (if MCP available)
            conversation_result = None
            if self.mcp_client and self.conversation_manager and 'mcp_client' not in self.unavailable_services:
                try:
                    conversation_result = await self._process_conversation(transcript_result.text)
                except Exception as e:
                    logger.warning(f"Conversation processing failed, continuing with transcript only: {e}")

            # Step 3: Format and save
            await self._save_processed_note(transcript_result, conversation_result, audio_file)

            # Update status
            self.current_status = "ready"
            self._notify_status_change("ready")

            logger.info("Audio processing completed successfully")

        except Exception as e:
            self.current_status = "error"
            self._notify_status_change("error")
            self._notify_error("Audio processing failed", str(e))
            raise

    async def _transcribe_audio(self, audio_file: str):
        """Transcribe audio with fallback handling."""
        if not self.transcription_service:
            raise RuntimeError("Transcription service not available")

        try:
            # Try primary transcription
            result = self.transcription_service.transcribe_audio(audio_file)
            logger.info(f"Transcription successful: {len(result.text)} characters")
            return result

        except Exception as e:
            # Try fallback transcription
            logger.warning(f"Primary transcription failed, trying fallback: {e}")
            try:
                result = self.transcription_service.fallback_transcription(audio_file)
                logger.info(f"Fallback transcription successful: {len(result.text)} characters")
                return result
            except Exception as fallback_e:
                logger.error(f"Fallback transcription also failed: {fallback_e}")
                raise RuntimeError(f"All transcription methods failed: {e}")

    async def _process_conversation(self, transcript: str):
        """Process conversation through MCP client."""
        if not self.conversation_manager:
            return None

        # Analyze topic and generate conversation
        topic_type, topic_reasoning = self.conversation_manager.analyze_topic_type(transcript)
        conversation_style = self.conversation_manager.select_conversation_style(topic_type)

        # Start conversation with MCP
        conversation_id = await self.mcp_client.start_conversation(
            initial_message=transcript,
            conversation_type="voice_note",
            metadata={'topic_type': topic_type.value}
        )

        # Conduct adaptive conversation
        exchanges = []
        max_exchanges = 5  # Configurable limit

        for i in range(max_exchanges):
            follow_up = self.conversation_manager.generate_followup(
                context={'transcript': transcript, 'exchanges': exchanges},
                depth=1
            )

            if not follow_up:
                break

            response = await self.mcp_client.continue_conversation(conversation_id, follow_up)

            exchanges.append({
                'prompt': follow_up,
                'response': response.get('response', ''),
                'timestamp': datetime.now()
            })

            # Check if conversation should continue
            if not self.conversation_manager.should_continue(response.get('response', '')):
                break

        # End conversation
        summary = await self.mcp_client.end_conversation(conversation_id)

        return {
            'conversation_id': conversation_id,
            'exchanges': exchanges,
            'summary': summary,
            'topic_type': topic_type,
            'topic_reasoning': topic_reasoning
        }

    async def _save_processed_note(self, transcript_result, conversation_result, audio_file: str):
        """Save the processed note to file system."""
        if not self.file_manager:
            raise RuntimeError("File manager not available")

        # Prepare conversation_data for MarkdownFormatter/FileManager
        conversation_data = {}
        exchanges = []

        # Initial transcript as first exchange for formatting
        transcript_text = getattr(transcript_result, 'text', str(transcript_result))
        exchanges.append({'speaker': 'Initial', 'content': transcript_text})

        # Include conversation exchanges if available
        if conversation_result and isinstance(conversation_result, dict):
            # conversation_result['exchanges'] are dicts with 'prompt' and 'response'
            conv_exchanges = []
            for ex in conversation_result.get('exchanges', []):
                # Convert to ConversationExchange-like shape
                conv_exchanges.append({'speaker': 'AI', 'content': ex.get('prompt', '')})
                conv_exchanges.append({'speaker': 'User', 'content': ex.get('response', '')})
            conversation_data['exchanges'] = conv_exchanges
            # Also include raw context history if present
            if 'summary' in conversation_result:
                conversation_data['summary'] = conversation_result['summary']
            conversation_data['topic_type'] = conversation_result.get('topic_type').value if conversation_result.get('topic_type') else None
        else:
            # Minimal conversation data containing only transcript
            conversation_data['text'] = transcript_text

        # Build ConversationMetadata
        from markdown_formatter import ConversationMetadata  # Local import to avoid cycles
        created_at = datetime.now()
        total_exchanges = len(conversation_data.get('exchanges', [])) // 2  # AI/User pairs
        conversation_text = transcript_text
        if 'exchanges' in conversation_data:
            conversation_text = "\n".join([ex['content'] for ex in conversation_data['exchanges'] if ex.get('content')])

        topic_type = conversation_result.get('topic_type').value if isinstance(conversation_result, dict) and conversation_result.get('topic_type') else 'other'
        depth_level = 'standard'
        completion_reason = 'conversation not started' if not conversation_result else 'conversation processed'

        metadata_obj = ConversationMetadata(
            topic_type=topic_type,
            depth_level=depth_level,
            total_exchanges=total_exchanges,
            conversation_length=len(conversation_text),
            completion_reason=completion_reason,
            created_at=created_at
        )

        # Save using FileManager
        save_result = self.file_manager.save_voice_note(conversation_data, metadata_obj, temp_files=[audio_file])

        if not save_result.success:
            raise RuntimeError(f"Failed to save note: {save_result.error}")

        logger.info(f"Note saved successfully: {save_result.file_path}")

        # Clean up temporary audio file if FileManager didn't already
        if not save_result.cleanup_performed:
            try:
                Path(audio_file).unlink()
                logger.info("Temporary audio file cleaned up")
            except Exception as e:
                logger.warning(f"Could not clean up audio file: {e}")

    def _on_recording_start(self, session_id: str):
        """Callback when recording starts via hotkey."""
        logger.info(f"Hotkey recording started: {session_id}")
        self.current_status = "recording"
        self.recording_start_time = datetime.now()

    def _on_recording_stop(self, session_id: str, file_path: str, duration: float):
        """Callback when recording stops via hotkey."""
        logger.info(f"Hotkey recording stopped: {session_id}, duration: {duration}s")
        self.current_status = "processing"
        # Process the recorded audio in a separate thread
        import threading
        thread = threading.Thread(target=self._process_audio_file_sync, args=(file_path,))
        thread.daemon = True
        thread.start()

    def _process_audio_file_sync(self, audio_file: str):
        """Synchronous wrapper for _process_audio_file."""
        try:
            # Run the async method in a new event loop
            import asyncio
            asyncio.run(self._process_audio_file(audio_file))
        except Exception as e:
            logger.error(f"Error in sync audio processing: {e}")
            self.current_status = "error"

    def _on_hotkey_error(self, exception: Exception):
        """Callback when hotkey system encounters an error."""
        logger.error(f"Hotkey error: {exception}")
        self.current_status = "error"

    def _hotkey_triggered(self):
        """Handle global hotkey trigger (legacy method)."""
        if self.current_status == "recording":
            asyncio.create_task(self._stop_recording())
        else:
            asyncio.create_task(self._start_recording())

    async def _recovery_loop(self):
        """Background loop for processing error recovery queue."""
        while self.is_running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                if not self.is_running:
                    break

                # Process recovery queue
                result = await self.error_recovery.process_recovery_queue()

                if result['processed'] > 0:
                    logger.info(f"Recovery processing: {result}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in recovery loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def _cleanup_loop(self):
        """Background loop for cleanup tasks."""
        while self.is_running:
            try:
                await asyncio.sleep(3600)  # Run every hour

                if not self.is_running:
                    break

                # Clean up old error data
                self.error_recovery.cleanup_old_data(days=7)

                # Clean up temp audio files
                if self.audio_recorder:
                    self.audio_recorder.cleanup_temp_files(max_age_hours=24)

                # Clean up transcription cache
                if self.transcription_service:
                    self.transcription_service.cleanup_cache(max_age_days=7)

                logger.info("Cleanup tasks completed")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes on error

    # Retry function implementations
    async def _retry_transcription(self, audio_file: str, *args, **kwargs):
        """Retry transcription operation."""
        return await self._transcribe_audio(audio_file)

    async def _retry_save_note(self, content: str, metadata: Dict[str, Any], *args, **kwargs):
        """Retry note saving operation."""
        return await self._save_processed_note(
            metadata.get('transcript_result'),
            metadata.get('conversation_result'),
            metadata.get('audio_file', '')
        )

    async def _retry_mcp_request(self, message: str, *args, **kwargs):
        """Retry MCP request operation."""
        if not self.mcp_client:
            raise RuntimeError("MCP client not available")

        return await self.mcp_client.send_message(message)

    # Status and error notification methods
    def add_status_callback(self, callback: Callable[[str], None]):
        """Add callback for status changes."""
        self.status_callbacks.append(callback)

    def add_error_callback(self, callback: Callable[[str, str], None]):
        """Add callback for error notifications."""
        self.error_callbacks.append(callback)

    def _notify_status_change(self, status: str):
        """Notify all status callbacks of status change."""
        for callback in self.status_callbacks:
            try:
                callback(status)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")

    def _notify_error(self, title: str, message: str):
        """Notify all error callbacks of error."""
        for callback in self.error_callbacks:
            try:
                callback(title, message)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")

    # Public interface methods
    async def toggle_recording(self):
        """Toggle recording state (start if stopped, stop if recording)."""
        if self.current_status == "recording":
            await self._stop_recording()
        else:
            await self._start_recording()

    def get_status(self) -> Dict[str, Any]:
        """Get current application status."""
        return {
            'current_status': self.current_status,
            'is_running': self.is_running,
            'degraded_mode': self.degraded_mode,
            'unavailable_services': self.unavailable_services,
            'recording_duration': (
                (datetime.now() - self.recording_start_time).total_seconds()
                if self.recording_start_time else None
            ),
            'error_summary': self.error_recovery.get_error_summary(),
            'recovery_status': self.error_recovery.get_recovery_status()
        }

    def get_recent_errors(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent errors."""
        return [err.to_dict() for err in self.error_recovery.error_history
                if (datetime.now() - err.timestamp).total_seconds() < hours * 3600]


# Application entry point and signal handling
def setup_signal_handlers(app: VoiceNotesApp):
    """Set up graceful shutdown signal handlers."""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        if app.is_running:
            # Create a new event loop for shutdown if we're not in the main thread
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            loop.run_until_complete(app.stop())
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


async def main():
    """Main application entry point."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/voice_notes.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Create and start application
    app = VoiceNotesApp()
    setup_signal_handlers(app)

    try:
        await app.start()

        # Keep running
        while app.is_running:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        await app.stop()


if __name__ == "__main__":
    asyncio.run(main())