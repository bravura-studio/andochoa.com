# Voice Notes System - User Guide

Welcome to the Voice Notes System! This guide will help you get started with AI-powered voice note capture and processing.

## Table of Contents

1. [What is Voice Notes System?](#what-is-voice-notes-system)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Initial Setup](#initial-setup)
5. [Basic Usage](#basic-usage)
6. [Advanced Features](#advanced-features)
7. [Configuration](#configuration)
8. [Tips and Best Practices](#tips-and-best-practices)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

## What is Voice Notes System?

Voice Notes System is an AI-powered application that transforms your voice recordings into structured, actionable notes. It uses advanced speech recognition and conversation AI to:

- **Capture voice recordings** with global hotkeys
- **Transcribe audio** using OpenAI Whisper
- **Process transcriptions** with intelligent conversation AI
- **Generate structured notes** with insights and action items
- **Organize content** automatically in your preferred format

### Key Benefits

✅ **Effortless Capture**: Record thoughts instantly with global hotkeys
✅ **Smart Processing**: AI extracts insights and action items
✅ **Automatic Organization**: Notes saved with intelligent naming and structure
✅ **Conversation Flow**: AI asks follow-up questions for deeper insights
✅ **Multiple Modes**: Quick, standard, or deep processing options

## Quick Start

### 5-Minute Setup

1. **Install** the Voice Notes System
2. **Configure** your API keys (OpenAI required)
3. **Set** your preferred notes directory
4. **Test** recording with `Cmd+Shift+R` (macOS) or `Ctrl+Shift+R` (Windows/Linux)
5. **Start** capturing voice notes!

### Your First Voice Note

1. Press `Cmd+Shift+R` to start recording
2. Speak for 10-30 seconds about any topic
3. Press `Cmd+Shift+R` again to stop
4. Wait for processing (30-60 seconds)
5. Find your note in the configured directory

## Installation

### System Requirements

- **Operating System**: macOS 10.14+, Windows 10+, or Linux (Ubuntu 18.04+)
- **Python**: 3.9 or higher
- **Microphone**: Built-in or external microphone
- **Internet**: Required for AI processing
- **Storage**: 500MB free space minimum

### Installation Methods

#### Method 1: Pre-built Application (Recommended)
```bash
# Download the latest release
# Double-click the installer
# Follow setup wizard
```

#### Method 2: From Source
```bash
# Clone repository
git clone https://github.com/your-org/voice-notes-system.git
cd voice-notes-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run setup script
python setup_config.py
```

## Initial Setup

### 1. API Configuration

The system requires an OpenAI API key for transcription services:

1. **Get OpenAI API Key**:
   - Visit [OpenAI API](https://platform.openai.com/api-keys)
   - Create account and generate API key
   - Note: Transcription costs ~$0.006 per minute

2. **Configure API Key**:
   ```bash
   # Option 1: Environment variable (recommended)
   export OPENAI_API_KEY="your-api-key-here"

   # Option 2: Configuration file
   # Edit config/config.yaml and add your key
   ```

### 2. Notes Directory Setup

Choose where your voice notes will be saved:

1. **Default Location**: `~/Documents/Voice Notes`
2. **Custom Location**: Edit `config/config.yaml`:
   ```yaml
   files:
     output_directory: "/path/to/your/notes"
   ```

### 3. Audio Device Configuration

The system automatically detects your default microphone. To use a specific device:

1. **List Available Devices**:
   ```bash
   python test_audio_recorder.py --list-devices
   ```

2. **Set Preferred Device**:
   ```yaml
   audio:
     input_device: "Device Name"
   ```

### 4. Test Your Setup

Run the configuration validator:
```bash
python validate_config.py
```

## Basic Usage

### Recording Voice Notes

#### Global Hotkeys (Default)
- **Start/Stop Recording**: `Cmd+Shift+R` (macOS) or `Ctrl+Shift+R` (Windows/Linux)
- **Cancel Recording**: `Escape`

#### System Tray Menu
1. Right-click the system tray icon
2. Select "🎤 Start Recording"
3. Speak your message
4. Right-click again and select "🛑 Stop Recording"

#### Audio Feedback
- **Recording Start**: Subtle notification sound
- **Recording Active**: Red system tray icon
- **Processing**: Yellow system tray icon with spinner
- **Complete**: Green icon with success notification

### Processing Modes

#### Quick Mode
- **Best for**: Short reminders, tasks, quick thoughts
- **Processing time**: 15-30 seconds
- **Conversation depth**: 1-2 exchanges
- **Use case**: "Remind me to call Sarah tomorrow"

#### Standard Mode (Default)
- **Best for**: General notes, meeting summaries, project updates
- **Processing time**: 30-60 seconds
- **Conversation depth**: 3-5 exchanges
- **Use case**: Daily standup summaries, project reflections

#### Deep Mode
- **Best for**: Complex thinking, brainstorming, detailed analysis
- **Processing time**: 60-120 seconds
- **Conversation depth**: 5-8 exchanges
- **Use case**: Strategic planning, problem-solving sessions

### Understanding Your Notes

Generated notes include:

#### YAML Frontmatter
```yaml
---
title: "Daily Standup Reflection"
date: "2023-12-01T14:30:00"
topic_type: "meeting"
processing_mode: "standard"
confidence: 0.95
duration: 45
word_count: 127
---
```

#### Note Structure
- **Summary**: Key insight extracted from your voice note
- **Conversation**: AI dialogue that helped develop the content
- **Action Items**: Specific tasks identified from your note
- **Key Insights**: Important themes and observations
- **Related Topics**: Automatically detected subject areas

## Advanced Features

### Adaptive Processing

The system automatically adjusts processing depth based on:
- **Content complexity**: Technical vs. simple content
- **Emotional intensity**: High-energy vs. calm reflections
- **Length and detail**: Brief vs. comprehensive input
- **User engagement**: Responsive vs. tired responses

### Smart File Organization

#### Automatic Naming
Files are named using hybrid patterns:
```
2023-12-01_project_planning_session.md
2023-12-01_daily_reflection_1430.md
2023-12-01_meeting_with_sarah.md
```

#### Directory Structure
```
Voice Notes/
├── 2023-12-01/
│   ├── morning_standup.md
│   ├── project_brainstorm.md
│   └── evening_reflection.md
├── 2023-12-02/
│   └── client_meeting_notes.md
└── templates/
    └── meeting_template.md
```

### Integration Features

#### Obsidian Compatibility
- Markdown format with YAML frontmatter
- Wikilink generation for related topics
- Tag support for organization
- Daily note integration

#### Export Options
- **Markdown**: Standard format
- **Plain Text**: Simple text files
- **JSON**: Structured data export
- **PDF**: Formatted documents (planned)

### Notification System

#### Desktop Notifications
- **Recording started**: Immediate feedback
- **Processing complete**: Note ready notification
- **Error alerts**: Clear error messages with actions
- **Daily summaries**: Usage statistics

#### Notification Preferences
```yaml
notifications:
  enabled: true
  show_recording: true
  show_processing: true
  show_success: true
  sound_enabled: true
  non_intrusive: false  # Set to true for quieter notifications
```

## Configuration

### Configuration File Location
- **macOS**: `~/Documents/Voice Notes/config/config.yaml`
- **Windows**: `%USERPROFILE%\Documents\Voice Notes\config\config.yaml`
- **Linux**: `~/Documents/Voice Notes/config/config.yaml`

### Key Configuration Options

#### Audio Settings
```yaml
audio:
  sample_rate: 44100        # Audio quality
  channels: 1               # Mono recording
  silence_threshold: 0.01   # Silence detection sensitivity
  silence_duration: 2.0     # Auto-stop after silence (seconds)
```

#### Processing Settings
```yaml
processing:
  default_mode: "standard"  # quick, standard, deep
  auto_process: true        # Process immediately after recording
  max_conversation_depth: 5 # Maximum AI exchanges
```

#### File Management
```yaml
files:
  output_directory: "~/Documents/Build in public/Content Bank/1-raw-ideas"
  naming_pattern: "hybrid"  # date, topic, hybrid
  daily_folders: true       # Create folders by date
  cleanup_temp_files: true  # Remove temporary audio files
```

#### Cost Management
```yaml
cost_management:
  daily_limit: 5.00         # Daily spending limit (USD)
  monthly_limit: 50.00      # Monthly spending limit (USD)
  track_usage: true         # Monitor API costs
  warning_threshold: 80     # Warn at 80% of limit
```

### Customizing Hotkeys

Edit the hotkeys section:
```yaml
hotkeys:
  record_toggle: "cmd+shift+r"  # Start/stop recording
  cancel: "escape"              # Cancel current recording
  audio_feedback: true          # Enable sound feedback
```

**Available Key Combinations**:
- macOS: `cmd`, `shift`, `alt`, `ctrl` + letter/number
- Windows/Linux: `ctrl`, `shift`, `alt`, `win` + letter/number

## Tips and Best Practices

### Recording Quality

#### Environment
✅ **Quiet space**: Minimize background noise
✅ **Consistent distance**: Stay 6-12 inches from microphone
✅ **Speak clearly**: Normal pace, clear pronunciation
❌ **Avoid**: Windy locations, multiple speakers, phone calls

#### Content Structure
✅ **Start with context**: "This is about the marketing project..."
✅ **Be specific**: Include names, dates, and details
✅ **Think out loud**: Share your reasoning process
✅ **End with intent**: "The main thing I want to remember is..."

### Maximizing AI Processing

#### For Better Insights
- **Share background**: Provide context for better AI understanding
- **Be emotional**: Express feelings and reactions for richer processing
- **Ask questions**: Wonder aloud about implications or next steps
- **Make connections**: Relate to previous experiences or knowledge

#### For Better Action Items
- **Use action words**: "I need to...", "I should...", "Next, I'll..."
- **Include timelines**: "By Friday...", "Next week...", "Tomorrow..."
- **Be specific**: "Call John about the proposal" vs. "Follow up"
- **Mention priorities**: "Most important...", "Critical...", "Nice to have..."

### Organization Strategies

#### Daily Practice
- **Morning reflections**: Plan your day and priorities
- **Mid-day check-ins**: Process meetings and decisions
- **Evening reviews**: Capture lessons and prepare for tomorrow

#### Project Management
- **Weekly reviews**: Assess progress and obstacles
- **Decision logs**: Record important choices and reasoning
- **Learning captures**: Document insights and discoveries

#### Personal Development
- **Goal tracking**: Regular progress updates
- **Gratitude notes**: Positive reflection practice
- **Challenge processing**: Work through difficult situations

### Cost Optimization

#### Reduce API Costs
- Use **Quick mode** for simple notes
- Keep recordings **under 2 minutes** when possible
- Avoid **duplicate recordings** of the same content
- Monitor your **daily usage** in the system tray

#### Maximize Value
- Combine **multiple thoughts** in one recording
- Use voice notes for **complex thinking** where AI adds value
- Focus on **important decisions** and insights
- Review and **act on generated action items**

## Troubleshooting

### Common Issues

#### Recording Problems

**Issue**: "No microphone detected"
- **Solution**: Check microphone connection and permissions
- **macOS**: System Preferences > Security & Privacy > Microphone
- **Windows**: Settings > Privacy > Microphone
- **Test**: Run `python test_audio_recorder.py`

**Issue**: "Recording quality is poor"
- **Solution**:
  - Check microphone positioning (6-12 inches)
  - Reduce background noise
  - Test different audio devices
  - Adjust `silence_threshold` in config

**Issue**: "Auto-stop not working"
- **Solution**:
  - Adjust `silence_duration` (try 3.0-5.0 seconds)
  - Increase `silence_threshold` (try 0.02-0.05)
  - Speak more consistently without long pauses

#### Transcription Problems

**Issue**: "Transcription failed - API error"
- **Solution**:
  - Check OpenAI API key is valid
  - Verify internet connection
  - Check API usage limits and billing
  - Try recording a shorter clip

**Issue**: "Poor transcription accuracy"
- **Solution**:
  - Speak more slowly and clearly
  - Use standard language (avoid slang/jargon)
  - Ensure good audio quality
  - Try shorter recordings (under 2 minutes)

**Issue**: "Transcription is expensive"
- **Solution**:
  - Set daily/monthly limits in config
  - Use shorter recordings
  - Combine multiple thoughts in one recording
  - Monitor usage in system tray

#### Processing Problems

**Issue**: "AI conversation doesn't make sense"
- **Solution**:
  - Provide more context in your initial recording
  - Be more specific about your topic
  - Try a different processing mode
  - Ensure transcription quality is good

**Issue**: "No action items generated"
- **Solution**:
  - Use action-oriented language ("I need to...")
  - Be explicit about next steps
  - Include timelines and specifics
  - Try Deep mode for complex content

**Issue**: "Processing takes too long"
- **Solution**:
  - Use Quick mode for simple notes
  - Check internet connection speed
  - Try shorter recordings
  - Restart the application

#### File and Organization Issues

**Issue**: "Notes not saving to correct location"
- **Solution**:
  - Check `output_directory` in config.yaml
  - Verify directory permissions
  - Create directory manually if needed
  - Test with `python validate_config.py`

**Issue**: "File names are unclear"
- **Solution**:
  - Switch to `hybrid` naming pattern
  - Be more specific in your initial topic statement
  - Manually rename files as needed
  - Adjust the AI prompts for better title generation

#### System Integration Issues

**Issue**: "System tray icon not appearing"
- **Solution**:
  - Restart the application
  - Check system tray settings (Windows)
  - Try running as administrator (Windows)
  - Install system tray dependencies

**Issue**: "Global hotkeys not working"
- **Solution**:
  - Check for conflicting applications
  - Try different key combinations
  - Run application with elevated permissions
  - Test with system tray menu instead

### Performance Issues

#### Slow Performance
1. **Check system resources**: CPU, memory, disk space
2. **Close unnecessary applications**
3. **Restart the Voice Notes application**
4. **Clear temporary files**: Check `temp_audio/` directory
5. **Update to latest version**

#### High Memory Usage
1. **Restart application daily** for long-term use
2. **Clear old temporary files**
3. **Reduce `max_conversation_depth`**
4. **Use Quick mode more frequently**

### Getting Help

#### Log Files
Check log files for detailed error information:
- **Location**: `logs/voice_notes.log`
- **Recent errors**: Last 100 lines usually contain relevant info
- **Debug mode**: Set `logging.level: DEBUG` in config

#### System Information
When reporting issues, include:
- Operating system and version
- Python version (`python --version`)
- Voice Notes version
- Configuration settings (remove API keys)
- Error messages from logs

#### Support Channels
- **GitHub Issues**: Technical problems and feature requests
- **Documentation**: This guide and developer docs
- **Community**: User forums and discussions
- **Email Support**: For account and billing issues

## FAQ

### General Questions

**Q: How much does it cost to use Voice Notes?**
A: The main cost is OpenAI API usage, approximately $0.006 per minute of audio. A typical 1-minute voice note costs less than 1 cent.

**Q: Is my voice data private and secure?**
A: Audio is temporarily stored locally and sent to OpenAI for transcription. Enable local-only mode in config for complete privacy (reduces functionality).

**Q: Can I use this offline?**
A: Limited functionality is available offline (recording and basic transcription). Full AI processing requires internet connection.

**Q: What languages are supported?**
A: OpenAI Whisper supports 50+ languages. The conversation AI works best with English but can handle other major languages.

### Technical Questions

**Q: Can I integrate with my existing note-taking app?**
A: Yes! Notes are saved as standard Markdown files compatible with Obsidian, Notion, Logseq, and other apps.

**Q: How do I backup my voice notes?**
A: Notes are saved as regular files in your specified directory. Use your preferred backup solution (iCloud, Dropbox, Git, etc.).

**Q: Can I change the AI prompts?**
A: Yes! Edit `config/prompts.yaml` to customize how the AI processes your voice notes.

**Q: Does this work with my specific microphone/headset?**
A: The system works with any microphone recognized by your operating system. Test with `python test_audio_recorder.py --list-devices`.

### Usage Questions

**Q: What makes a good voice note?**
A: Be specific, provide context, think out loud, and express your thoughts naturally. The AI works better with authentic, conversational content.

**Q: How long should my recordings be?**
A: 30 seconds to 2 minutes is optimal. Longer recordings work but may be more expensive and slower to process.

**Q: Can I edit the generated notes?**
A: Absolutely! Notes are saved as editable Markdown files. Add, modify, or reorganize content as needed.

**Q: How do I organize notes by project or topic?**
A: Use topic-specific language in your recordings, enable daily folders, or manually organize files. Future versions will include automatic tagging.

### Troubleshooting FAQ

**Q: Why isn't my hotkey working?**
A: Check for conflicting applications, verify the key combination in config, and ensure the app is running in the system tray.

**Q: The transcription is inaccurate. How can I improve it?**
A: Speak clearly at normal pace, minimize background noise, use standard language, and ensure good microphone quality.

**Q: I'm getting API errors. What should I do?**
A: Verify your OpenAI API key, check your account billing, ensure internet connectivity, and review usage limits.

**Q: The AI responses don't seem relevant. How can I fix this?**
A: Provide more context in your initial recording, be specific about your topic, and try different processing modes.

---

## Getting Started Checklist

- [ ] Install Voice Notes System
- [ ] Configure OpenAI API key
- [ ] Set notes directory location
- [ ] Test recording with hotkey
- [ ] Record your first voice note
- [ ] Review generated note structure
- [ ] Customize configuration as needed
- [ ] Integrate with your existing workflow

**Ready to start capturing better voice notes? Press `Cmd+Shift+R` and speak your first thought!**

---

*For technical documentation and developer information, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)*