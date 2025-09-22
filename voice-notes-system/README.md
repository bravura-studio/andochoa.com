# Voice Notes System

An intelligent voice recording and conversation system that captures audio, transcribes it using OpenAI Whisper, and integrates with Claude Desktop via MCP (Model Context Protocol) to provide seamless AI-powered voice note management.

## Features

- **Global Hotkey Recording**: Instant voice capture with Cmd+Shift+R
- **AI Transcription**: High-quality transcription using OpenAI Whisper
- **Claude Desktop Integration**: Seamless integration with Claude Pro via MCP server
- **AI-Powered Note Management**: Ask Claude to manage, search, and organize your voice notes
- **Markdown Output**: Formatted notes saved to your Obsidian vault or specified directory
- **System Tray Interface**: Unobtrusive background operation
- **Privacy-First**: Local processing options and secure credential storage

## Quick Start

1. **Set up the environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   ```

2. **Configure API keys**:
   ```bash
   python setup_config.py
   ```

3. **Validate setup**:
   ```bash
   python validate_config.py
   ```

4. **Set up Claude Desktop integration**:
   ```bash
   python setup_claude_desktop.py
   ```

5. **Start the MCP server** (optional - runs automatically with Claude Desktop):
   ```bash
   python start_mcp_server.py
   ```

## Configuration

### Environment Variables

The system uses environment variables for secure credential storage. Copy `.env.template` to `.env` and configure:

```bash
cp .env.template .env
```

Required environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required for transcription)

MCP server environment variables (configured automatically):

- `VOICE_NOTES_MCP_MODE`: Set to "server" for Claude Desktop integration
- `VOICE_NOTES_MCP_HOST`: MCP server host (default: localhost)
- `VOICE_NOTES_MCP_PORT`: MCP server port (default: 8000)

Optional environment variables:

- `VOICE_NOTES_OUTPUT_DIR`: Custom output directory
- `VOICE_NOTES_CONFIG_DIR`: Custom configuration directory
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Configuration Files

Main configuration is in `config/config.yaml`:

- **Audio settings**: Sample rate, channels, silence detection
- **Processing options**: Conversation depth, processing modes
- **File management**: Output directory, naming patterns
- **UI settings**: Notifications, status colors
- **Privacy controls**: Local-only mode, encryption options

Conversation prompts are in `config/prompts.yaml`:

- **Topic analysis**: Automatic classification of input
- **Conversation styles**: Adaptive responses by topic type
- **Follow-up prompts**: Context-aware question templates

### Setup Scripts

The project includes helpful setup and validation scripts:

#### `setup_config.py`
Interactive setup script that guides you through:
- API key configuration
- MCP server setup
- Directory configuration
- Basic validation

#### `validate_config.py`
Comprehensive validation script that checks:
- File structure integrity
- Python dependencies
- Configuration validity
- API connectivity

## Project Structure

```
voice-notes-system/
├── src/                     # Source code
│   ├── __init__.py
│   ├── config_manager.py    # Configuration management
│   ├── mcp_client.py       # MCP server client
│   ├── audio_recorder.py   # Audio recording (TASK-003)
│   ├── transcription.py    # Whisper integration (TASK-005)
│   ├── conversation_manager.py  # AI conversations (TASK-008)
│   ├── file_manager.py     # Markdown output (TASK-011)
│   └── system_tray.py      # UI interface (TASK-014)
├── config/                 # Configuration files
│   ├── config.yaml         # Main configuration
│   └── prompts.yaml        # Conversation templates
├── tests/                  # Test files
├── logs/                   # Application logs
├── temp_audio/             # Temporary audio files
├── requirements.txt        # Python dependencies
├── setup_config.py         # Configuration setup script
├── validate_config.py      # Validation script
├── .env.template          # Environment template
└── .gitignore             # Git ignore rules
```

## API Requirements

### OpenAI API

You'll need an OpenAI API key with access to:
- **Whisper API**: For audio transcription
- **GPT models**: For conversation management (via MCP)

Cost estimates:
- Whisper API: ~$0.006 per minute of audio
- GPT API: Variable based on conversation length

## Claude Desktop Integration

The Voice Notes System now acts as an MCP (Model Context Protocol) server for Claude Desktop, allowing you to interact with your voice notes directly through Claude Pro.

### Available Commands in Claude Desktop

Once configured, you can use these commands in Claude Desktop:

- **"Start a voice recording session"** - Begin recording audio
- **"Stop voice recording [session_id]"** - End an active recording
- **"Transcribe this audio file: [path]"** - Process audio with Whisper
- **"Create a voice note from: [text]"** - Format text as a structured note
- **"List my voice notes"** - Show all existing notes with metadata
- **"Search my voice notes for: [query]"** - Find specific content in notes

### Example Usage

```
You: "Start a voice recording session for a brainstorming meeting"
Claude: Started voice recording session: session_20240919_143022
        Session name: brainstorming meeting
        Type: brainstorm
        Use stop_voice_recording with session_id 'session_20240919_143022' when finished.

You: "List my voice notes from this week"
Claude: ## Voice Notes

        - **20240918_ProjectIdeas_Meeting.md**
          - Modified: 2024-09-18T14:30:22
          - Size: 2,456 bytes

        - **20240917_PersonalReflection_Journal.md**
          - Modified: 2024-09-17T09:15:33
          - Size: 1,823 bytes
```

### MCP Server Configuration

The system automatically configures itself as an MCP server. No external MCP server setup is required.

## Security & Privacy

- **Secure Credential Storage**: API keys stored in environment variables
- **File Permissions**: Configuration files set to owner-only access
- **Local Processing Options**: Can run in local-only mode
- **Temporary File Cleanup**: Audio files automatically cleaned up
- **No Data Persistence**: Conversations not stored unless explicitly saved

## Development Status

This project follows a structured implementation plan:

- ✅ **TASK-001**: Development Environment Setup
- ✅ **TASK-002**: API Keys and Configuration
- 🔄 **TASK-003**: Audio Recording Module (Next)
- ⏳ **TASK-004**: Global Hotkey Integration
- ⏳ **TASK-005**: Whisper API Integration
- ⏳ **TASK-007**: MCP Server Integration
- ⏳ **TASK-008**: Conversation Manager Core

See `tasks/voice-notes-implementation-tasks.md` for the complete implementation roadmap.

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   ValueError: OpenAI API key not found
   ```
   - Run `python setup_config.py` to configure API keys
   - Ensure `.env` file exists and contains `OPENAI_API_KEY`

2. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'openai'
   ```
   - Activate virtual environment: `source venv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`

3. **Permission Errors**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   - Check file permissions on configuration files
   - Ensure output directory is writable

4. **MCP Connection Failed**
   ```
   aiohttp.ClientError: Failed to connect to MCP server
   ```
   - MCP server is optional - system will use mock client
   - Verify `MCP_SERVER_URL` if you have a server configured

### Getting Help

1. Run the validation script: `python validate_config.py`
2. Check the logs in `logs/voice_notes.log`
3. Review configuration in `config/config.yaml`

## Contributing

This project follows a test-driven development approach:

1. All features have corresponding tests in `tests/`
2. Code follows Black formatting standards
3. Commits use conventional commit format
4. Each task is implemented incrementally

## License

[License to be determined]