# Voice Notes System - Developer Guide

This guide provides technical documentation for developers working on or extending the Voice Notes System.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [API Documentation](#api-documentation)
3. [Extension Points](#extension-points)
4. [Development Setup](#development-setup)
5. [Testing Framework](#testing-framework)
6. [Deployment Instructions](#deployment-instructions)
7. [Contributing Guidelines](#contributing-guidelines)
8. [Code Standards](#code-standards)

## Architecture Overview

### System Components

The Voice Notes System follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Interface │    │  Core Services  │    │   External APIs │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ System Tray     │    │ Audio Recorder  │    │ OpenAI Whisper  │
│ Global Hotkeys  │    │ Transcription   │    │ Claude MCP      │
│ Notifications   │    │ Conversation Mgr│    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
               ┌─────────────────────────────────┐
               │        Core Application         │
               │     (VoiceNotesApp)            │
               │                                 │
               │ ┌─────────────────────────────┐ │
               │ │    Configuration Manager    │ │
               │ │    Error Recovery System    │ │
               │ │    File Manager             │ │
               │ └─────────────────────────────┘ │
               └─────────────────────────────────┘
```

### Key Components

#### 1. Audio Processing Pipeline
- **AudioRecorder** (`src/audio_recorder.py`): Captures audio with silence detection
- **TranscriptionService** (`src/transcription.py`): Handles Whisper API integration
- **Global Hotkey** (`src/global_hotkey.py`): System-wide recording triggers

#### 2. AI Conversation Engine
- **ConversationManager** (`src/conversation_manager.py`): Manages adaptive conversations
- **PromptTemplates** (`src/prompt_templates.py`): Template system for AI prompts
- **MCP Client** (`src/mcp_client.py`): Claude Desktop integration

#### 3. File Management
- **MarkdownFormatter** (`src/markdown_formatter.py`): Structures output notes
- **FileManager** (`src/file_manager.py`): Handles file operations and organization

#### 4. System Integration
- **VoiceNotesSystemTray** (`src/system_tray.py`): User interface and status
- **ErrorRecoverySystem** (`src/error_recovery.py`): Graceful error handling
- **ConfigManager** (`src/config_manager.py`): Configuration management

### Data Flow

```
Voice Input → AudioRecorder → TranscriptionService → ConversationManager
                                                            │
                                                            ▼
MarkdownFormatter ← FileManager ← AI Response Processing ←──┘
```

## API Documentation

### Core Classes

#### AudioRecorder

```python
class AudioRecorder:
    """Handles audio recording with silence detection."""

    def start_recording(self) -> None:
        """Start recording audio from default microphone."""

    def stop_recording(self) -> str:
        """Stop recording and return filepath to saved audio."""

    def detect_silence(self, threshold: float, duration: float) -> bool:
        """Check if silence detected for specified duration."""

    def get_audio_level(self) -> float:
        """Get current audio input level (0.0 to 1.0)."""
```

#### TranscriptionService

```python
class TranscriptionService:
    """OpenAI Whisper API integration for audio transcription."""

    def transcribe_audio(self, audio_file: str) -> dict:
        """Transcribe audio file using Whisper API."""

    def track_usage(self, duration: float, cost: float) -> None:
        """Track API usage for cost monitoring."""

    def handle_api_error(self, error: Exception) -> dict:
        """Handle API errors with fallback responses."""
```

#### ConversationManager

```python
class ConversationManager:
    """Manages AI-powered conversations with adaptive depth."""

    def analyze_topic_type(self, transcript: str) -> str:
        """Classify transcript into topic categories."""

    def select_conversation_style(self, topic_type: str) -> dict:
        """Choose appropriate conversation style for topic."""

    def generate_followup(self, context: dict, depth: int) -> str:
        """Generate contextual follow-up questions."""

    def should_continue(self, response: str) -> bool:
        """Determine if conversation should continue."""
```

#### MarkdownFormatter

```python
class MarkdownFormatter:
    """Formats conversations into structured markdown."""

    def create_frontmatter(self, metadata: dict) -> str:
        """Generate YAML frontmatter for notes."""

    def format_conversation(self, exchanges: list) -> str:
        """Format conversation exchanges with proper structure."""

    def extract_action_items(self, text: str) -> list:
        """Extract actionable items from conversation."""

    def generate_title(self, key_insight: str) -> str:
        """Auto-generate meaningful note titles."""
```

### Configuration Schema

#### config.yaml Structure

```yaml
audio:
  sample_rate: 44100
  channels: 1
  chunk_size: 1024
  silence_threshold: 0.01
  silence_duration: 2.0

processing:
  modes:
    quick: {max_depth: 1, timeout: 30}
    standard: {max_depth: 3, timeout: 120}
    deep: {max_depth: 5, timeout: 300}
  default_mode: "standard"

file_management:
  output_directory: "~/Documents/Voice Notes"
  filename_pattern: "{date}_{topic}_{type}.md"
  temp_audio_dir: "temp_audio"

ui:
  system_tray:
    show_timer: true
    show_recent_count: 5
  notifications:
    enabled: true
    sound: true

privacy:
  local_only_mode: false
  encrypt_temp_files: false
  auto_cleanup: true
```

### MCP Server Integration

#### Available Tools

The system exposes these tools via MCP for Claude Desktop:

1. **start_voice_recording**
   ```json
   {
     "name": "start_voice_recording",
     "description": "Start a new voice recording session",
     "inputSchema": {
       "type": "object",
       "properties": {
         "session_name": {"type": "string"},
         "processing_mode": {"type": "string", "enum": ["quick", "standard", "deep"]}
       }
     }
   }
   ```

2. **stop_voice_recording**
   ```json
   {
     "name": "stop_voice_recording",
     "description": "Stop an active recording session",
     "inputSchema": {
       "type": "object",
       "properties": {
         "session_id": {"type": "string", "required": true}
       }
     }
   }
   ```

3. **list_voice_notes**
   ```json
   {
     "name": "list_voice_notes",
     "description": "List all voice notes with metadata",
     "inputSchema": {
       "type": "object",
       "properties": {
         "limit": {"type": "number", "default": 10},
         "filter": {"type": "string"}
       }
     }
   }
   ```

## Extension Points

### 1. Custom Transcription Services

Extend the transcription system by implementing the `TranscriptionProvider` interface:

```python
from abc import ABC, abstractmethod

class TranscriptionProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_file: str) -> dict:
        """Transcribe audio file and return results."""
        pass

    @abstractmethod
    def get_cost_estimate(self, duration: float) -> float:
        """Estimate transcription cost for given duration."""
        pass

# Example implementation
class LocalWhisperProvider(TranscriptionProvider):
    def transcribe(self, audio_file: str) -> dict:
        # Local Whisper implementation
        pass
```

### 2. Custom Output Formats

Add new output formats by extending `OutputFormatter`:

```python
class CustomFormatter(OutputFormatter):
    def format_note(self, conversation: dict) -> str:
        # Custom formatting logic
        pass

    def get_file_extension(self) -> str:
        return ".custom"
```

### 3. Additional AI Providers

Integrate other AI services:

```python
class CustomAIProvider(ConversationProvider):
    def generate_response(self, prompt: str, context: dict) -> str:
        # Custom AI provider implementation
        pass
```

### 4. Custom Storage Backends

Implement alternative storage solutions:

```python
class CloudStorageManager(StorageProvider):
    def save_note(self, content: str, metadata: dict) -> str:
        # Cloud storage implementation
        pass
```

## Development Setup

### Prerequisites

- Python 3.9+
- Poetry (recommended) or pip
- Git
- OpenAI API key

### Local Development

```bash
# Clone repository
git clone https://github.com/your-org/voice-notes-system.git
cd voice-notes-system

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Set up pre-commit hooks
pre-commit install

# Copy environment template
cp .env.template .env
# Edit .env with your API keys

# Run setup and validation
python setup_config.py
python validate_config.py
```

### Development Dependencies

```txt
# requirements-dev.txt
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
black>=23.0.0
flake8>=5.0.0
mypy>=1.0.0
pre-commit>=3.0.0
```

## Testing Framework

### Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_audio_recorder.py
│   ├── test_transcription.py
│   ├── test_conversation_manager.py
│   └── test_markdown_formatter.py
├── integration/             # Integration tests
│   ├── test_full_pipeline.py
│   └── test_mcp_integration.py
├── performance/             # Performance benchmarks
│   └── test_performance.py
└── fixtures/               # Test data and mocks
    ├── sample_audio/
    └── mock_responses/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/           # Unit tests only
pytest tests/integration/   # Integration tests only
pytest -m performance      # Performance tests only

# Run tests in parallel
pytest -n auto
```

### Test Configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --disable-warnings
    --cov=src
    --cov-branch
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Tests that take more than 1 second
```

## Deployment Instructions

### Production Build

```bash
# Clean environment
rm -rf venv/ __pycache__/ .pytest_cache/

# Create production environment
python -m venv venv-prod
source venv-prod/bin/activate

# Install production dependencies only
pip install -r requirements.txt

# Run production validation
python validate_config.py --production

# Create distribution package
python setup.py sdist bdist_wheel
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Set environment variables
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO

# Create non-root user
RUN useradd -m voicenotes
USER voicenotes

# Expose MCP server port
EXPOSE 8000

CMD ["python", "-m", "src.mcp_server"]
```

### systemd Service (Linux)

```ini
# /etc/systemd/system/voice-notes.service
[Unit]
Description=Voice Notes System
After=network.target

[Service]
Type=simple
User=voicenotes
WorkingDirectory=/opt/voice-notes-system
Environment=PATH=/opt/voice-notes-system/venv/bin
ExecStart=/opt/voice-notes-system/venv/bin/python -m src.voice_notes_app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### macOS LaunchAgent

```xml
<!-- ~/Library/LaunchAgents/com.voicenotes.app.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.voicenotes.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>-m</string>
        <string>src.voice_notes_app</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Applications/Voice Notes System</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

## Contributing Guidelines

### Code Review Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature-name`
3. **Implement** your changes following our coding standards
4. **Write** comprehensive tests for new functionality
5. **Run** the full test suite: `pytest`
6. **Format** code: `black src/ tests/`
7. **Lint** code: `flake8 src/ tests/`
8. **Type check**: `mypy src/`
9. **Commit** using conventional commit format
10. **Push** branch and create a Pull Request

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(audio): add silence detection with configurable thresholds

- Implements adaptive silence detection
- Adds configuration options for threshold and duration
- Includes comprehensive test coverage

Closes #123
```

### Pull Request Guidelines

**PR Title**: Use conventional commit format
**Description**: Include:
- Summary of changes
- Motivation and context
- Testing performed
- Breaking changes (if any)
- Screenshots (for UI changes)

**Checklist**:
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)

### Issue Templates

#### Bug Report
```markdown
**Describe the bug**
Clear description of the issue.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g. macOS 12.0]
- Python version: [e.g. 3.11]
- Voice Notes version: [e.g. 1.0.0]

**Additional context**
Any other context about the problem.
```

#### Feature Request
```markdown
**Is your feature request related to a problem?**
Clear description of the problem.

**Describe the solution you'd like**
Clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features considered.

**Additional context**
Any other context or screenshots.
```

## Code Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these specifics:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Use `isort` for import ordering

### Type Annotations

Use type hints for all public functions:

```python
from typing import Optional, List, Dict, Any

def process_audio(
    audio_file: str,
    options: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Process audio file and return transcript segments."""
    pass
```

### Documentation Standards

#### Docstring Format

Use Google-style docstrings:

```python
def transcribe_audio(self, audio_file: str, language: Optional[str] = None) -> dict:
    """Transcribe audio file using OpenAI Whisper API.

    Args:
        audio_file: Path to the audio file to transcribe.
        language: Optional language code (e.g., 'en', 'es'). If None,
                 auto-detection is used.

    Returns:
        Dictionary containing transcription results with keys:
        - 'text': The transcribed text
        - 'confidence': Confidence score (0.0 to 1.0)
        - 'duration': Audio duration in seconds
        - 'cost': API cost for this request

    Raises:
        TranscriptionError: If the API request fails or audio is invalid.
        ConfigurationError: If API key is not configured.

    Example:
        >>> service = TranscriptionService()
        >>> result = service.transcribe_audio('meeting.wav')
        >>> print(result['text'])
        'Welcome to today's meeting...'
    """
```

### Error Handling

Use specific exception types:

```python
class VoiceNotesError(Exception):
    """Base exception for Voice Notes System."""
    pass

class AudioRecordingError(VoiceNotesError):
    """Raised when audio recording fails."""
    pass

class TranscriptionError(VoiceNotesError):
    """Raised when transcription fails."""
    pass

class ConfigurationError(VoiceNotesError):
    """Raised when configuration is invalid."""
    pass
```

### Logging Standards

Use structured logging:

```python
import logging
import structlog

logger = structlog.get_logger(__name__)

def process_recording(session_id: str) -> None:
    logger.info("Starting recording processing", session_id=session_id)
    try:
        # Processing logic
        logger.info("Recording processed successfully",
                   session_id=session_id,
                   duration=duration)
    except Exception as e:
        logger.error("Recording processing failed",
                    session_id=session_id,
                    error=str(e),
                    exc_info=True)
        raise
```

---

This developer guide provides the foundation for contributing to and extending the Voice Notes System. For questions or clarifications, please open an issue or contact the maintainers.