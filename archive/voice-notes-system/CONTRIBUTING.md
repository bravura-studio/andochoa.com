# Contributing to Voice Notes System

We welcome contributions to the Voice Notes System! This document provides guidelines for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Process](#development-process)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)
8. [Issue Guidelines](#issue-guidelines)
9. [Community](#community)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background, experience level, gender identity, sexual orientation, disability, race, ethnicity, religion, or nationality.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Use of sexualized language or imagery
- Personal attacks or insulting comments
- Harassment, public or private
- Publishing others' private information without permission
- Any conduct that could reasonably be considered inappropriate

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of audio processing concepts
- Familiarity with async/await patterns
- Understanding of AI/ML concepts (helpful but not required)

### Setting Up Development Environment

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/voice-notes-system.git
   cd voice-notes-system
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Set up pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Configure environment**
   ```bash
   cp .env.template .env
   # Edit .env with your API keys
   ```

6. **Run tests to verify setup**
   ```bash
   pytest
   ```

### Development Dependencies

Required for development:

```txt
# requirements-dev.txt
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
black>=23.0.0
flake8>=5.0.0
mypy>=1.0.0
pre-commit>=3.0.0
bandit>=1.7.0
```

## Development Process

### Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   # or
   git checkout -b docs/documentation-update
   ```

2. **Make your changes**
   - Write code following our coding standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run all tests
   pytest

   # Run with coverage
   pytest --cov=src --cov-report=html

   # Run specific test categories
   pytest tests/unit/
   pytest tests/integration/
   ```

4. **Format and lint code**
   ```bash
   # Format code
   black src/ tests/

   # Lint code
   flake8 src/ tests/

   # Type checking
   mypy src/

   # Security check
   bandit -r src/
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new audio processing feature"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

### Branch Naming Convention

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation changes
- `refactor/description` - Code refactoring
- `test/description` - Test improvements
- `chore/description` - Maintenance tasks

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with these specifics:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces (no tabs)
- **String quotes**: Double quotes preferred
- **Import organization**: Use `isort`

### Code Formatting

We use [Black](https://black.readthedocs.io/) for automatic code formatting:

```bash
# Format all code
black src/ tests/

# Check formatting without changes
black --check src/ tests/
```

### Type Hints

All new code must include type hints:

```python
from typing import Optional, List, Dict, Any
from pathlib import Path

def process_audio_file(
    file_path: Path,
    options: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Process audio file and return transcript segments.

    Args:
        file_path: Path to the audio file.
        options: Optional processing options.

    Returns:
        List of transcript segments.

    Raises:
        AudioProcessingError: If processing fails.
    """
    # Implementation here
    pass
```

### Docstring Standards

Use Google-style docstrings:

```python
def transcribe_audio(self, audio_file: str, language: Optional[str] = None) -> dict:
    """Transcribe audio file using OpenAI Whisper API.

    This method sends the audio file to the Whisper API and returns
    the transcription results with metadata.

    Args:
        audio_file: Path to the audio file to transcribe.
        language: Optional language code (e.g., 'en', 'es'). If None,
                 auto-detection is used.

    Returns:
        Dictionary containing transcription results:
            text (str): The transcribed text
            confidence (float): Confidence score (0.0 to 1.0)
            duration (float): Audio duration in seconds
            cost (float): API cost for this request

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

Use specific exception types and proper error handling:

```python
class VoiceNotesError(Exception):
    """Base exception for Voice Notes System."""
    pass

class AudioRecordingError(VoiceNotesError):
    """Raised when audio recording fails."""
    pass

def start_recording(self) -> None:
    """Start audio recording."""
    try:
        self._initialize_audio_stream()
    except OSError as e:
        logger.error("Failed to initialize audio stream", exc_info=True)
        raise AudioRecordingError(f"Microphone unavailable: {e}") from e
```

### Logging

Use structured logging with appropriate levels:

```python
import logging
import structlog

logger = structlog.get_logger(__name__)

def process_recording(session_id: str) -> None:
    """Process a recording session."""
    logger.info("Starting recording processing", session_id=session_id)

    try:
        # Processing logic here
        duration = process_audio()
        logger.info(
            "Recording processed successfully",
            session_id=session_id,
            duration=duration
        )
    except Exception as e:
        logger.error(
            "Recording processing failed",
            session_id=session_id,
            error=str(e),
            exc_info=True
        )
        raise
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_audio_recorder.py
│   ├── test_transcription.py
│   └── test_conversation_manager.py
├── integration/             # Integration tests
│   ├── test_full_pipeline.py
│   └── test_mcp_integration.py
├── performance/             # Performance tests
│   └── test_performance.py
└── fixtures/               # Test data and mocks
    ├── sample_audio/
    └── mock_responses/
```

### Writing Tests

#### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
from src.audio_recorder import AudioRecorder, AudioRecordingError

class TestAudioRecorder:
    """Test cases for AudioRecorder class."""

    @pytest.fixture
    def config(self):
        """Audio recorder configuration fixture."""
        return {
            'sample_rate': 44100,
            'channels': 1,
            'chunk_size': 1024
        }

    @pytest.fixture
    def recorder(self, config):
        """AudioRecorder instance fixture."""
        return AudioRecorder(config)

    def test_start_recording_success(self, recorder):
        """Test successful recording start."""
        with patch('sounddevice.InputStream') as mock_stream:
            recorder.start_recording()
            assert recorder.is_recording
            mock_stream.assert_called_once()

    def test_start_recording_already_recording(self, recorder):
        """Test error when starting recording while already recording."""
        recorder._is_recording = True

        with pytest.raises(AudioRecordingError, match="Already recording"):
            recorder.start_recording()

    @patch('sounddevice.InputStream')
    def test_audio_level_calculation(self, mock_stream, recorder):
        """Test audio level calculation."""
        # Mock audio data
        mock_stream.return_value.read.return_value = (
            np.array([[0.5], [0.3], [0.8]]), False
        )

        level = recorder.get_audio_level()
        assert 0.0 <= level <= 1.0
```

#### Integration Tests

```python
import pytest
import tempfile
from pathlib import Path
from src.voice_notes_app import VoiceNotesApp

class TestFullPipeline:
    """Integration tests for complete voice notes pipeline."""

    @pytest.fixture
    async def app(self):
        """VoiceNotesApp instance for testing."""
        config = {
            'audio': {'sample_rate': 44100},
            'processing': {'default_mode': 'quick'},
            'file_management': {'output_directory': tempfile.mkdtemp()}
        }
        return VoiceNotesApp(config)

    @pytest.mark.asyncio
    async def test_complete_voice_note_creation(self, app):
        """Test complete pipeline from audio to note."""
        # Use test audio file
        test_audio = Path('tests/fixtures/sample_audio/test_recording.wav')

        # Process the audio
        result = await app.process_audio_file(str(test_audio))

        # Verify results
        assert result['status'] == 'completed'
        assert 'note_path' in result
        assert Path(result['note_path']).exists()

        # Verify note content
        with open(result['note_path']) as f:
            content = f.read()
            assert '---' in content  # YAML frontmatter
            assert '# ' in content   # Title
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
    --cov-report=html:htmlcov
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Tests that take more than 1 second
    api: Tests that require API access
```

### Test Coverage

Maintain high test coverage:

- **Minimum**: 80% overall coverage
- **Target**: 90% overall coverage
- **Critical components**: 95% coverage (audio, transcription, conversation)

```bash
# Generate coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Documentation

### Types of Documentation

1. **Code Documentation**: Docstrings and inline comments
2. **API Documentation**: Detailed API reference
3. **User Documentation**: Installation and usage guides
4. **Developer Documentation**: Architecture and contribution guides

### Documentation Standards

#### README Files

Each module should have a clear README explaining:
- Purpose and functionality
- Installation/setup instructions
- Basic usage examples
- Configuration options
- Troubleshooting tips

#### API Documentation

All public methods must have comprehensive docstrings with:
- Purpose description
- Parameter descriptions with types
- Return value description with type
- Raised exceptions
- Usage examples

#### Changelog

Maintain `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/):

```markdown
# Changelog

## [Unreleased]

### Added
- New voice activity detection feature

### Changed
- Improved transcription accuracy

### Fixed
- Fixed memory leak in audio processing

## [1.0.0] - 2024-01-15

### Added
- Initial release
- Audio recording functionality
- Whisper integration
- Claude Desktop integration
```

## Pull Request Process

### Before Submitting

- [ ] Tests pass locally (`pytest`)
- [ ] Code is formatted (`black src/ tests/`)
- [ ] Linting is clean (`flake8 src/ tests/`)
- [ ] Type checking passes (`mypy src/`)
- [ ] Documentation is updated
- [ ] Changelog is updated (if applicable)

### PR Title Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(audio): add silence detection with configurable thresholds
fix(transcription): handle API timeout errors gracefully
docs(api): update API reference for new endpoints
```

### PR Description Template

```markdown
## Summary

Brief description of changes and motivation.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing

Describe testing performed:
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Screenshots

If applicable, add screenshots to help explain your changes.

## Checklist

- [ ] My code follows the style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests, linting, and security checks
2. **Code Review**: Maintainers review code for quality, design, and standards
3. **Testing**: Reviewers may test functionality manually
4. **Documentation Review**: Ensure documentation is accurate and complete
5. **Approval**: At least one maintainer approval required
6. **Merge**: Squash and merge preferred for clean history

## Issue Guidelines

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. macOS 12.0, Ubuntu 20.04, Windows 11]
- Python version: [e.g. 3.11.2]
- Voice Notes version: [e.g. 1.0.0]
- Hardware: [e.g. MacBook Pro M2, relevant for audio issues]

**Configuration:**
- Processing mode: [quick/standard/deep]
- Audio settings: [sample rate, etc.]
- Relevant config values

**Logs**
```
Include relevant log snippets or attach log files
```

**Additional context**
Add any other context about the problem here.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Use cases**
Describe specific use cases for this feature.

**Implementation notes**
If you have ideas about implementation, share them here.

**Additional context**
Add any other context or screenshots about the feature request here.
```

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested
- `priority/high`: High priority issues
- `priority/medium`: Medium priority issues
- `priority/low`: Low priority issues

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Pull Requests**: Code review and collaboration

### Getting Help

1. Check existing documentation
2. Search existing issues
3. Ask in GitHub Discussions
4. Open a new issue if needed

### Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes for significant contributions
- Special recognition for first-time contributors

### Becoming a Maintainer

Regular contributors may be invited to become maintainers based on:
- Quality of contributions
- Understanding of codebase
- Community involvement
- Commitment to project goals

---

Thank you for contributing to Voice Notes System! Your contributions help make voice note capture and processing more accessible and powerful for everyone.