# Voice Notes System - Installation Guide

Quick setup guide to get Voice Notes System running on your computer.

## Prerequisites

- **Python 3.9+** installed on your system
- **Microphone** (built-in or external)
- **OpenAI API key** (for transcription)
- **Internet connection** (for AI processing)

## Quick Installation (5 minutes)

### Step 1: Download and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/voice-notes-system.git
cd voice-notes-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Get OpenAI API Key

1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign up or log in to your account
3. Click "Create new secret key"
4. Copy the API key (starts with `sk-`)

**Cost**: ~$0.006 per minute of audio (~1 cent per voice note)

### Step 3: Configure the System

```bash
# Run the setup script
python setup_config.py
```

When prompted:
- Enter your OpenAI API key
- Choose your notes directory (default: `~/Documents/Voice Notes`)
- Select your preferred processing mode (Standard recommended)

### Step 4: Test Your Setup

```bash
# Validate configuration
python validate_config.py

# Test audio recording
python test_audio_recorder.py

# Test the complete system
python -c "from src.system_tray import VoiceNotesSystemTray; print('✅ System ready!')"
```

### Step 5: Start the Application

```bash
# Start Voice Notes System
python -m src.voice_notes_app
```

You should see:
- System tray icon (green circle)
- "Voice Notes - Ready" tooltip
- Success notification

## Platform-Specific Instructions

### macOS Setup

```bash
# Install system dependencies
brew install portaudio

# Grant microphone permissions
# Go to: System Preferences > Security & Privacy > Microphone
# Enable for Terminal and/or your Python app

# Test global hotkey
# Default: Cmd+Shift+R
```

### Windows Setup

```bash
# Install system dependencies (if needed)
pip install pyaudio  # May require Visual Studio Build Tools

# Grant microphone permissions
# Go to: Settings > Privacy > Microphone
# Enable for the application

# Test global hotkey
# Default: Ctrl+Shift+R
```

### Linux Setup

```bash
# Install system dependencies
sudo apt-get install portaudio19-dev python3-dev
# Or for other distros:
# sudo dnf install portaudio-devel python3-devel
# sudo pacman -S portaudio python

# Install Python audio packages
pip install pyaudio

# Test global hotkey
# Default: Ctrl+Shift+R
```

## First Voice Note

1. **Start Recording**: Press `Cmd+Shift+R` (macOS) or `Ctrl+Shift+R` (Windows/Linux)
2. **Speak**: "This is my first voice note test. I want to see how the AI processes my thoughts about getting started with this system."
3. **Stop Recording**: Press the hotkey again
4. **Wait**: Processing takes 30-60 seconds
5. **Check Result**: Look in your notes directory for the generated file

## Configuration Quick Reference

### Essential Settings (config/config.yaml)

```yaml
# API Configuration
api:
  openai:
    api_key: "your-key-here"  # Or set OPENAI_API_KEY environment variable

# File Settings
files:
  output_directory: "~/Documents/Voice Notes"
  daily_folders: true

# Processing Mode
processing:
  default_mode: "standard"  # quick, standard, deep

# Hotkeys
hotkeys:
  record_toggle: "cmd+shift+r"  # macOS
  # record_toggle: "ctrl+shift+r"  # Windows/Linux
```

### Environment Variables (Alternative to config file)

```bash
# Set API key via environment
export OPENAI_API_KEY="your-key-here"

# Set notes directory
export VOICE_NOTES_DIR="~/Documents/Voice Notes"
```

## Troubleshooting Quick Fixes

### "No module named 'src'"
```bash
# Make sure you're in the voice-notes-system directory
cd voice-notes-system
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
```

### "ModuleNotFoundError: No module named 'openai'"
```bash
pip install -r requirements.txt
```

### "Permission denied" for microphone
- **macOS**: System Preferences > Security & Privacy > Microphone
- **Windows**: Settings > Privacy > Microphone
- **Linux**: Check pulseaudio/alsa permissions

### "API key invalid"
- Double-check your OpenAI API key
- Ensure you have credits in your OpenAI account
- Try setting the key as environment variable: `export OPENAI_API_KEY="sk-..."`

### "System tray not showing"
- **macOS**: Check system tray (top-right corner)
- **Windows**: Check hidden icons in system tray
- **Linux**: Ensure system tray/notification area is enabled

## Verification Checklist

After installation, verify these work:

- [ ] `python --version` shows 3.9+
- [ ] Virtual environment is activated (see `(venv)` in terminal)
- [ ] `python validate_config.py` passes all checks
- [ ] System tray icon appears when starting the app
- [ ] Global hotkey triggers recording (icon turns red)
- [ ] Test recording completes and saves a note
- [ ] Generated note contains transcription and AI insights

## Getting Help

If you encounter issues:

1. **Check logs**: `logs/voice_notes.log`
2. **Run diagnostics**: `python validate_config.py`
3. **Test components individually**:
   - Audio: `python test_audio_recorder.py`
   - Config: `python validate_config.py`
   - API: Check OpenAI account and billing

4. **Common solutions**:
   - Restart the application
   - Check internet connection
   - Verify API key and billing
   - Update Python dependencies

## Next Steps

Once installed:

1. **Read the [User Guide](USER_GUIDE.md)** for detailed usage instructions
2. **Customize your configuration** in `config/config.yaml`
3. **Set up your workflow** with your preferred note-taking app
4. **Start capturing voice notes** regularly

## Uninstallation

To remove Voice Notes System:

```bash
# Stop the application
# Kill system tray process if running

# Remove the directory
rm -rf voice-notes-system

# Remove any global shortcuts or startup items
# (Platform-specific)
```

Your voice notes files will remain in your configured notes directory.

---

**🎉 Congratulations! You're ready to start using Voice Notes System.**

**First command to try**: Press your hotkey and say "Hello Voice Notes, this is my first recording!"