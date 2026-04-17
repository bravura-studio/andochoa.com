# Voice Notes System - API Reference

Complete API documentation for all classes, methods, and interfaces in the Voice Notes System.

## Core APIs

### AudioRecorder

**Location**: `src/audio_recorder.py`

Audio recording functionality with silence detection and level monitoring.

#### Class Definition

```python
class AudioRecorder:
    """Handles audio recording with configurable parameters and silence detection."""

    def __init__(self, config: dict):
        """Initialize audio recorder with configuration.

        Args:
            config: Audio configuration dictionary containing:
                - sample_rate: Audio sample rate (default: 44100)
                - channels: Number of audio channels (default: 1)
                - chunk_size: Audio chunk size (default: 1024)
                - silence_threshold: Silence detection threshold (default: 0.01)
                - silence_duration: Silence duration in seconds (default: 2.0)
        """
```

#### Methods

##### start_recording()

```python
def start_recording(self) -> None:
    """Start recording audio from the default microphone.

    Raises:
        AudioRecordingError: If microphone is unavailable or already recording.
        PermissionError: If microphone access is denied.

    Example:
        >>> recorder = AudioRecorder(config)
        >>> recorder.start_recording()
    """
```

##### stop_recording()

```python
def stop_recording(self) -> str:
    """Stop recording and save audio to temporary file.

    Returns:
        str: Path to the saved audio file.

    Raises:
        AudioRecordingError: If not currently recording or save fails.

    Example:
        >>> audio_file = recorder.stop_recording()
        >>> print(f"Audio saved to: {audio_file}")
    """
```

##### detect_silence()

```python
def detect_silence(self, threshold: Optional[float] = None,
                  duration: Optional[float] = None) -> bool:
    """Check if silence has been detected for the specified duration.

    Args:
        threshold: Silence threshold override (0.0 to 1.0).
        duration: Silence duration override in seconds.

    Returns:
        bool: True if silence detected for specified duration.

    Example:
        >>> if recorder.detect_silence(threshold=0.005, duration=3.0):
        ...     recorder.stop_recording()
    """
```

##### get_audio_level()

```python
def get_audio_level(self) -> float:
    """Get current audio input level.

    Returns:
        float: Current audio level (0.0 = silence, 1.0 = maximum).

    Example:
        >>> level = recorder.get_audio_level()
        >>> print(f"Audio level: {level:.2%}")
    """
```

### TranscriptionService

**Location**: `src/transcription.py`

OpenAI Whisper API integration with cost tracking and error handling.

#### Class Definition

```python
class TranscriptionService:
    """Handles audio transcription using OpenAI Whisper API."""

    def __init__(self, api_key: str, config: dict):
        """Initialize transcription service.

        Args:
            api_key: OpenAI API key.
            config: Transcription configuration dictionary.
        """
```

#### Methods

##### transcribe_audio()

```python
def transcribe_audio(self, audio_file: str,
                    language: Optional[str] = None,
                    prompt: Optional[str] = None) -> dict:
    """Transcribe audio file using OpenAI Whisper API.

    Args:
        audio_file: Path to audio file (WAV, MP3, M4A, etc.).
        language: Optional language code (e.g., 'en', 'es', 'fr').
        prompt: Optional prompt to guide transcription.

    Returns:
        dict: Transcription result containing:
            - text: The transcribed text
            - language: Detected/specified language
            - duration: Audio duration in seconds
            - cost: API cost for this request
            - confidence: Confidence score (if available)
            - timestamp: Transcription timestamp

    Raises:
        TranscriptionError: If API request fails.
        FileNotFoundError: If audio file doesn't exist.

    Example:
        >>> service = TranscriptionService(api_key, config)
        >>> result = service.transcribe_audio('recording.wav', language='en')
        >>> print(result['text'])
    """
```

##### track_usage()

```python
def track_usage(self, duration: float, cost: float,
                request_type: str = 'transcription') -> None:
    """Track API usage for cost monitoring.

    Args:
        duration: Audio duration in seconds.
        cost: API cost for the request.
        request_type: Type of request ('transcription', 'translation').

    Example:
        >>> service.track_usage(duration=45.5, cost=0.27, request_type='transcription')
    """
```

##### get_usage_stats()

```python
def get_usage_stats(self, period: str = 'day') -> dict:
    """Get usage statistics for specified period.

    Args:
        period: Statistics period ('day', 'week', 'month').

    Returns:
        dict: Usage statistics containing:
            - total_requests: Number of API requests
            - total_duration: Total audio duration processed
            - total_cost: Total API costs
            - average_cost_per_minute: Cost efficiency metric

    Example:
        >>> stats = service.get_usage_stats('week')
        >>> print(f"Weekly cost: ${stats['total_cost']:.2f}")
    """
```

### ConversationManager

**Location**: `src/conversation_manager.py`

AI-powered conversation management with adaptive depth and topic analysis.

#### Class Definition

```python
class ConversationManager:
    """Manages AI conversations with adaptive questioning and topic analysis."""

    def __init__(self, mcp_client, prompt_templates: PromptTemplates, config: dict):
        """Initialize conversation manager.

        Args:
            mcp_client: MCP client for AI communication.
            prompt_templates: Loaded prompt templates.
            config: Conversation configuration.
        """
```

#### Methods

##### analyze_topic_type()

```python
def analyze_topic_type(self, transcript: str) -> str:
    """Analyze transcript to determine topic type.

    Args:
        transcript: Transcribed text to analyze.

    Returns:
        str: Topic type ('struggles', 'wins', 'metrics', 'brainstorm', 'general').

    Example:
        >>> manager = ConversationManager(client, templates, config)
        >>> topic = manager.analyze_topic_type("I'm struggling with productivity")
        >>> print(topic)  # 'struggles'
    """
```

##### start_conversation()

```python
def start_conversation(self, transcript: str,
                      processing_mode: str = 'standard',
                      topic_hint: Optional[str] = None) -> dict:
    """Start a new conversation based on transcript.

    Args:
        transcript: Initial transcript to process.
        processing_mode: Processing mode ('quick', 'standard', 'deep').
        topic_hint: Optional topic type hint.

    Returns:
        dict: Conversation state containing:
            - conversation_id: Unique conversation identifier
            - topic_type: Detected topic type
            - exchanges: List of conversation exchanges
            - depth: Current conversation depth
            - should_continue: Whether to continue conversation

    Example:
        >>> conversation = manager.start_conversation(
        ...     "I had a breakthrough with my project today",
        ...     processing_mode='deep'
        ... )
    """
```

##### generate_followup()

```python
def generate_followup(self, conversation_state: dict) -> Optional[str]:
    """Generate follow-up question based on conversation state.

    Args:
        conversation_state: Current conversation state.

    Returns:
        Optional[str]: Follow-up question or None if conversation should end.

    Example:
        >>> followup = manager.generate_followup(conversation_state)
        >>> if followup:
        ...     print(f"AI: {followup}")
    """
```

##### process_response()

```python
def process_response(self, conversation_state: dict,
                    user_response: str) -> dict:
    """Process user response and update conversation state.

    Args:
        conversation_state: Current conversation state.
        user_response: User's response to follow-up question.

    Returns:
        dict: Updated conversation state.

    Example:
        >>> updated_state = manager.process_response(state, "Actually, yes...")
    """
```

### MarkdownFormatter

**Location**: `src/markdown_formatter.py`

Formats conversations into structured markdown with metadata and action items.

#### Class Definition

```python
class MarkdownFormatter:
    """Formats conversation data into structured markdown notes."""

    def __init__(self, config: dict):
        """Initialize markdown formatter with configuration."""
```

#### Methods

##### format_note()

```python
def format_note(self, conversation_data: dict,
               metadata: Optional[dict] = None) -> str:
    """Format complete conversation into markdown note.

    Args:
        conversation_data: Complete conversation data.
        metadata: Optional metadata to include in frontmatter.

    Returns:
        str: Formatted markdown content.

    Example:
        >>> formatter = MarkdownFormatter(config)
        >>> markdown = formatter.format_note(conversation_data)
        >>> print(markdown[:100])  # Preview first 100 characters
    """
```

##### create_frontmatter()

```python
def create_frontmatter(self, metadata: dict) -> str:
    """Create YAML frontmatter for the note.

    Args:
        metadata: Metadata dictionary containing:
            - title: Note title
            - date: Creation date
            - topic_type: Topic classification
            - tags: List of tags
            - processing_mode: Used processing mode

    Returns:
        str: YAML frontmatter block.

    Example:
        >>> frontmatter = formatter.create_frontmatter({
        ...     'title': 'Project Breakthrough',
        ...     'topic_type': 'wins',
        ...     'tags': ['productivity', 'breakthrough']
        ... })
    """
```

##### extract_action_items()

```python
def extract_action_items(self, conversation_text: str) -> List[str]:
    """Extract action items from conversation text.

    Args:
        conversation_text: Full conversation text.

    Returns:
        List[str]: List of extracted action items.

    Example:
        >>> items = formatter.extract_action_items(conversation_text)
        >>> for item in items:
        ...     print(f"- [ ] {item}")
    """
```

##### generate_title()

```python
def generate_title(self, key_insight: str, topic_type: str) -> str:
    """Generate meaningful title from conversation content.

    Args:
        key_insight: Main insight from the conversation.
        topic_type: Type of topic discussed.

    Returns:
        str: Generated title.

    Example:
        >>> title = formatter.generate_title(
        ...     "Found new approach to user onboarding",
        ...     "wins"
        ... )
        >>> print(title)  # "User Onboarding Breakthrough"
    """
```

### MCP Client

**Location**: `src/mcp_client.py`

Model Context Protocol client for Claude Desktop integration.

#### Class Definition

```python
class MCPClient:
    """MCP client for communicating with Claude Desktop."""

    def __init__(self, config: dict):
        """Initialize MCP client with configuration."""
```

#### Methods

##### send_message()

```python
async def send_message(self, message: str,
                      context: Optional[dict] = None) -> dict:
    """Send message to Claude via MCP.

    Args:
        message: Message to send to Claude.
        context: Optional context dictionary.

    Returns:
        dict: Response from Claude containing:
            - content: Response text
            - type: Response type
            - metadata: Additional metadata

    Raises:
        MCPConnectionError: If connection to Claude fails.

    Example:
        >>> client = MCPClient(config)
        >>> response = await client.send_message(
        ...     "Help me understand this transcript",
        ...     context={'transcript': transcript_text}
        ... )
    """
```

##### register_tool()

```python
def register_tool(self, tool_name: str, tool_schema: dict) -> None:
    """Register a tool with the MCP server.

    Args:
        tool_name: Name of the tool to register.
        tool_schema: JSON schema for the tool.

    Example:
        >>> client.register_tool('start_recording', {
        ...     'description': 'Start voice recording',
        ...     'parameters': {...}
        ... })
    """
```

### System Tray Interface

**Location**: `src/system_tray.py`

System tray application providing user interface and status indication.

#### Class Definition

```python
class VoiceNotesSystemTray:
    """System tray interface for Voice Notes System."""

    def __init__(self, voice_notes_app):
        """Initialize system tray with reference to main application."""
```

#### Methods

##### start()

```python
def start(self) -> None:
    """Start the system tray application.

    This method blocks and runs the tray application event loop.
    Call this from the main thread.

    Example:
        >>> tray = VoiceNotesSystemTray(app)
        >>> tray.start()  # Blocks until application exits
    """
```

##### update_status()

```python
def update_status(self, status: str, message: Optional[str] = None) -> None:
    """Update tray icon status and tooltip.

    Args:
        status: Status identifier ('ready', 'recording', 'processing', 'error').
        message: Optional status message for tooltip.

    Example:
        >>> tray.update_status('recording', 'Recording in progress...')
    """
```

##### show_notification()

```python
def show_notification(self, title: str, message: str,
                     notification_type: str = 'info') -> None:
    """Show system notification.

    Args:
        title: Notification title.
        message: Notification message.
        notification_type: Type ('info', 'warning', 'error', 'success').

    Example:
        >>> tray.show_notification(
        ...     'Recording Complete',
        ...     'Voice note saved successfully',
        ...     'success'
        ... )
    """
```

## Configuration APIs

### ConfigManager

**Location**: `src/config_manager.py`

Configuration management with validation and defaults.

#### Methods

##### load_config()

```python
def load_config(config_path: Optional[str] = None) -> dict:
    """Load configuration from YAML file with validation.

    Args:
        config_path: Optional path to config file.

    Returns:
        dict: Validated configuration dictionary.

    Raises:
        ConfigurationError: If config is invalid or missing.

    Example:
        >>> config = load_config('config/config.yaml')
    """
```

##### validate_config()

```python
def validate_config(config: dict) -> bool:
    """Validate configuration structure and values.

    Args:
        config: Configuration dictionary to validate.

    Returns:
        bool: True if valid, raises exception if invalid.

    Raises:
        ConfigurationError: If validation fails with details.
    """
```

### PromptTemplates

**Location**: `src/prompt_templates.py`

Prompt template management and loading.

#### Methods

##### load_templates()

```python
def load_templates(templates_path: str) -> PromptTemplates:
    """Load prompt templates from YAML file.

    Args:
        templates_path: Path to prompts.yaml file.

    Returns:
        PromptTemplates: Loaded template manager.

    Example:
        >>> templates = load_templates('config/prompts.yaml')
    """
```

##### get_prompt()

```python
def get_prompt(self, category: str, prompt_type: str,
              variables: Optional[dict] = None) -> str:
    """Get formatted prompt for specified category and type.

    Args:
        category: Prompt category ('analysis', 'followup', 'completion').
        prompt_type: Specific prompt type within category.
        variables: Variables to substitute in template.

    Returns:
        str: Formatted prompt text.

    Example:
        >>> prompt = templates.get_prompt(
        ...     'followup',
        ...     'struggles',
        ...     {'context': 'productivity issues'}
        ... )
    """
```

## Error Handling APIs

### Custom Exceptions

All custom exceptions inherit from `VoiceNotesError`:

```python
class VoiceNotesError(Exception):
    """Base exception for Voice Notes System."""
    pass

class AudioRecordingError(VoiceNotesError):
    """Audio recording related errors."""
    pass

class TranscriptionError(VoiceNotesError):
    """Transcription service errors."""
    pass

class ConversationError(VoiceNotesError):
    """Conversation management errors."""
    pass

class ConfigurationError(VoiceNotesError):
    """Configuration validation errors."""
    pass

class MCPConnectionError(VoiceNotesError):
    """MCP communication errors."""
    pass

class FileOperationError(VoiceNotesError):
    """File system operation errors."""
    pass
```

### ErrorRecoverySystem

**Location**: `src/error_recovery.py`

Comprehensive error recovery with retry logic and graceful degradation.

#### Methods

##### add_to_retry_queue()

```python
def add_to_retry_queue(self, operation: dict, priority: int = 1) -> str:
    """Add failed operation to retry queue.

    Args:
        operation: Operation details dictionary.
        priority: Priority level (1=high, 2=medium, 3=low).

    Returns:
        str: Queue item ID for tracking.

    Example:
        >>> recovery = ErrorRecoverySystem(config)
        >>> item_id = recovery.add_to_retry_queue({
        ...     'type': 'transcription',
        ...     'audio_file': 'recording.wav',
        ...     'attempt': 1
        ... }, priority=1)
    """
```

##### process_retry_queue()

```python
async def process_retry_queue(self) -> None:
    """Process items in the retry queue with exponential backoff.

    This method runs continuously in the background,
    processing failed operations according to retry policies.
    """
```

## MCP Server Tools

The following tools are exposed via MCP for Claude Desktop integration:

### start_voice_recording

```json
{
  "name": "start_voice_recording",
  "description": "Start a new voice recording session",
  "inputSchema": {
    "type": "object",
    "properties": {
      "session_name": {
        "type": "string",
        "description": "Optional name for the recording session"
      },
      "processing_mode": {
        "type": "string",
        "enum": ["quick", "standard", "deep"],
        "default": "standard",
        "description": "Processing depth for the conversation"
      },
      "topic_type": {
        "type": "string",
        "enum": ["struggles", "wins", "metrics", "brainstorm", "general"],
        "description": "Optional hint about the topic type"
      }
    }
  }
}
```

### stop_voice_recording

```json
{
  "name": "stop_voice_recording",
  "description": "Stop an active voice recording session",
  "inputSchema": {
    "type": "object",
    "properties": {
      "session_id": {
        "type": "string",
        "description": "ID of the session to stop"
      }
    },
    "required": ["session_id"]
  }
}
```

### transcribe_audio_file

```json
{
  "name": "transcribe_audio_file",
  "description": "Transcribe an existing audio file",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": {
        "type": "string",
        "description": "Path to the audio file to transcribe"
      },
      "language": {
        "type": "string",
        "description": "Optional language code (e.g., 'en', 'es')"
      }
    },
    "required": ["file_path"]
  }
}
```

### create_voice_note

```json
{
  "name": "create_voice_note",
  "description": "Create a formatted voice note from text",
  "inputSchema": {
    "type": "object",
    "properties": {
      "content": {
        "type": "string",
        "description": "Text content to format as a voice note"
      },
      "title": {
        "type": "string",
        "description": "Optional title for the note"
      },
      "topic_type": {
        "type": "string",
        "enum": ["struggles", "wins", "metrics", "brainstorm", "general"],
        "description": "Type of content"
      }
    },
    "required": ["content"]
  }
}
```

### list_voice_notes

```json
{
  "name": "list_voice_notes",
  "description": "List all voice notes with metadata",
  "inputSchema": {
    "type": "object",
    "properties": {
      "limit": {
        "type": "number",
        "default": 10,
        "description": "Maximum number of notes to return"
      },
      "filter": {
        "type": "string",
        "description": "Optional filter string for note content"
      },
      "topic_type": {
        "type": "string",
        "enum": ["struggles", "wins", "metrics", "brainstorm", "general"],
        "description": "Filter by topic type"
      }
    }
  }
}
```

### search_voice_notes

```json
{
  "name": "search_voice_notes",
  "description": "Search voice notes by content",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query"
      },
      "limit": {
        "type": "number",
        "default": 10,
        "description": "Maximum number of results"
      }
    },
    "required": ["query"]
  }
}
```

## Type Definitions

### Common Types

```python
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AudioConfig:
    sample_rate: int = 44100
    channels: int = 1
    chunk_size: int = 1024
    silence_threshold: float = 0.01
    silence_duration: float = 2.0

@dataclass
class ConversationExchange:
    speaker: str  # 'user' or 'ai'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ConversationState:
    conversation_id: str
    topic_type: str
    processing_mode: str
    exchanges: List[ConversationExchange]
    depth: int
    should_continue: bool
    metadata: Dict[str, Any]

@dataclass
class TranscriptionResult:
    text: str
    language: str
    duration: float
    cost: float
    confidence: Optional[float] = None
    timestamp: datetime = None

@dataclass
class VoiceNote:
    id: str
    title: str
    content: str
    topic_type: str
    created_at: datetime
    file_path: str
    metadata: Dict[str, Any]
```

---

This API reference provides comprehensive documentation for all public interfaces in the Voice Notes System. For implementation examples and usage patterns, see the Developer Guide.