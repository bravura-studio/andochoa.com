# Voice Notes System - Troubleshooting Guide

This guide provides solutions for common issues and problems you might encounter while using Voice Notes System.

## Quick Diagnostic Commands

Before troubleshooting specific issues, run these diagnostic commands:

```bash
# Check system status
python validate_config.py

# Test audio system
python test_audio_recorder.py

# Check API connectivity
python test_mcp_integration.py

# View recent logs
tail -50 logs/voice_notes.log
```

## Issue Categories

- [Audio and Recording Issues](#audio-and-recording-issues)
- [Transcription Problems](#transcription-problems)
- [AI Processing Issues](#ai-processing-issues)
- [File and Storage Problems](#file-and-storage-problems)
- [System Integration Issues](#system-integration-issues)
- [Performance Problems](#performance-problems)
- [Configuration Issues](#configuration-issues)

## Audio and Recording Issues

### No Microphone Detected

**Symptoms**: "No audio devices found" or "Permission denied"

**Solutions**:

1. **Check Hardware**:
   ```bash
   # List available audio devices
   python test_audio_recorder.py --list-devices
   ```

2. **Grant Permissions**:
   - **macOS**: System Preferences > Security & Privacy > Privacy > Microphone
   - **Windows**: Settings > Privacy > Microphone > Allow apps to access microphone
   - **Linux**: Check pulseaudio/alsa permissions

3. **Test Audio Device**:
   ```bash
   # Test default microphone
   python test_audio_recorder.py --test-recording
   ```

4. **Configure Specific Device**:
   ```yaml
   # In config/config.yaml
   audio:
     input_device: "Your Microphone Name"
   ```

### Poor Recording Quality

**Symptoms**: Muffled audio, low volume, background noise

**Solutions**:

1. **Check Microphone Position**:
   - Position 6-12 inches from your mouth
   - Avoid covering microphone with hand
   - Use external microphone if built-in quality is poor

2. **Adjust Audio Settings**:
   ```yaml
   audio:
     sample_rate: 44100      # Higher = better quality
     silence_threshold: 0.01  # Lower = more sensitive
   ```

3. **Environment Setup**:
   - Record in quiet room
   - Minimize background noise
   - Avoid echo-prone spaces
   - Close windows and doors

4. **Test Different Devices**:
   ```bash
   python test_audio_recorder.py --device "Device Name"
   ```

### Recording Auto-Stop Issues

**Symptoms**: Recording stops too early or doesn't stop automatically

**Solutions**:

1. **Adjust Silence Detection**:
   ```yaml
   audio:
     silence_threshold: 0.02   # Try values 0.01-0.05
     silence_duration: 3.0     # Try values 2.0-5.0
   ```

2. **Speak More Consistently**:
   - Avoid long pauses (>2 seconds)
   - Maintain steady volume
   - Use "um" or "uh" instead of complete silence

3. **Manual Control**:
   - Use hotkey to manually stop recording
   - Disable auto-stop in configuration:
   ```yaml
   audio:
     auto_stop_enabled: false
   ```

### Global Hotkey Not Working

**Symptoms**: Pressing hotkey doesn't start recording

**Solutions**:

1. **Check Key Conflicts**:
   - Close other applications using same hotkey
   - Try different key combination:
   ```yaml
   hotkeys:
     record_toggle: "cmd+shift+v"  # Try different key
   ```

2. **Permissions**:
   - **macOS**: System Preferences > Security & Privacy > Accessibility
   - **Windows**: Run as administrator
   - **Linux**: Check window manager permissions

3. **Test Alternative Keys**:
   ```yaml
   hotkeys:
     record_toggle: "f9"        # Function key
     # or
     record_toggle: "ctrl+alt+r" # Different modifier
   ```

4. **Use System Tray**:
   - Right-click system tray icon
   - Select "🎤 Start Recording"

## Transcription Problems

### API Authentication Errors

**Symptoms**: "Invalid API key", "Authentication failed"

**Solutions**:

1. **Verify API Key**:
   ```bash
   # Check if key is set
   echo $OPENAI_API_KEY

   # Test API key
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

2. **Update API Key**:
   ```bash
   # Option 1: Environment variable
   export OPENAI_API_KEY="sk-your-actual-key-here"

   # Option 2: Config file
   # Edit config/config.yaml
   ```

3. **Check Account Status**:
   - Visit [OpenAI Platform](https://platform.openai.com/account)
   - Verify billing information
   - Check usage limits

### Network Connection Issues

**Symptoms**: "Connection timeout", "Network error"

**Solutions**:

1. **Test Internet Connection**:
   ```bash
   ping api.openai.com
   curl -I https://api.openai.com/v1/models
   ```

2. **Check Firewall/Proxy**:
   - Allow connections to api.openai.com
   - Configure proxy settings if needed:
   ```yaml
   api:
     openai:
       proxy: "http://proxy.company.com:8080"
   ```

3. **Retry Configuration**:
   ```yaml
   api:
     openai:
       max_retries: 5
       timeout: 60
   ```

### Poor Transcription Accuracy

**Symptoms**: Incorrect words, missing content, gibberish

**Solutions**:

1. **Improve Audio Quality**:
   - Speak clearly and at normal pace
   - Reduce background noise
   - Use better microphone
   - Record in shorter segments (< 2 minutes)

2. **Language and Accent**:
   - Specify language in config:
   ```yaml
   api:
     openai:
       language: "en"  # or "es", "fr", etc.
   ```

3. **Content Guidelines**:
   - Use standard language (avoid heavy slang)
   - Spell out numbers and abbreviations
   - Provide context for technical terms
   - Speak one thought at a time

### Cost and Usage Issues

**Symptoms**: "Daily limit exceeded", "High API costs"

**Solutions**:

1. **Monitor Usage**:
   ```bash
   # Check current usage
   python -c "from src.transcription import CostTracker; CostTracker().get_usage_summary()"
   ```

2. **Adjust Limits**:
   ```yaml
   cost_management:
     daily_limit: 10.00    # Increase limit
     monthly_limit: 100.00
     track_usage: true
   ```

3. **Optimize Usage**:
   - Use shorter recordings
   - Combine multiple thoughts in one recording
   - Use Quick mode for simple notes
   - Avoid re-recording the same content

## AI Processing Issues

### MCP Connection Failures

**Symptoms**: "MCP server unavailable", "Conversation processing failed"

**Solutions**:

1. **Check MCP Server**:
   ```bash
   python test_mcp_integration.py
   ```

2. **Restart Services**:
   - Restart Voice Notes application
   - Restart Claude Desktop (if using)
   - Check MCP server logs

3. **Fallback Configuration**:
   ```yaml
   degradation:
     fallback_services:
       conversation:
         skip_on_failure: true  # Save transcription only
   ```

### Poor AI Responses

**Symptoms**: Irrelevant responses, no insights generated, repetitive content

**Solutions**:

1. **Improve Input Quality**:
   - Provide more context in your recording
   - Be specific about your topic
   - Express thoughts and feelings clearly
   - Ask questions or wonder about implications

2. **Adjust Processing Mode**:
   ```yaml
   processing:
     default_mode: "deep"  # Try deeper processing
   ```

3. **Customize Prompts**:
   - Edit `config/prompts.yaml`
   - Add domain-specific prompts
   - Adjust conversation style

### No Action Items Generated

**Symptoms**: Action items section is empty or generic

**Solutions**:

1. **Use Action-Oriented Language**:
   - "I need to..."
   - "I should..."
   - "Next, I'll..."
   - "By Friday, I want to..."

2. **Be Specific**:
   - Include timelines and deadlines
   - Mention specific people or resources
   - State clear outcomes or deliverables

3. **Review Generated Content**:
   - Check if action items are in the conversation
   - Look for tasks mentioned in insights
   - Manually add missing action items

## File and Storage Problems

### Notes Not Saving

**Symptoms**: No files created, empty files, permission errors

**Solutions**:

1. **Check Directory Permissions**:
   ```bash
   # Test write permissions
   touch "~/Documents/Voice Notes/test.txt"
   rm "~/Documents/Voice Notes/test.txt"
   ```

2. **Create Directory**:
   ```bash
   mkdir -p "~/Documents/Voice Notes"
   ```

3. **Verify Configuration**:
   ```yaml
   files:
     output_directory: "/full/path/to/notes"  # Use absolute path
   ```

4. **Check Disk Space**:
   ```bash
   df -h ~/Documents
   ```

### File Naming Issues

**Symptoms**: Unclear file names, duplicates, special characters

**Solutions**:

1. **Adjust Naming Pattern**:
   ```yaml
   files:
     naming_pattern: "hybrid"  # date, topic, hybrid
   ```

2. **Improve Initial Context**:
   - Start recordings with clear topic statement
   - "This is about the marketing project..."
   - "Today's standup meeting notes..."

3. **Manual Renaming**:
   - Edit file names after generation
   - Use consistent naming convention
   - Add tags or prefixes for organization

### Temporary File Cleanup

**Symptoms**: Disk space filling up, old audio files remaining

**Solutions**:

1. **Enable Auto-Cleanup**:
   ```yaml
   files:
     cleanup_temp_files: true
   ```

2. **Manual Cleanup**:
   ```bash
   # Remove old temp files
   rm -f temp_audio/*.wav
   ```

3. **Automated Cleanup Script**:
   ```bash
   # Add to cron job or task scheduler
   find temp_audio/ -name "*.wav" -mtime +1 -delete
   ```

## System Integration Issues

### System Tray Problems

**Symptoms**: No tray icon, icon not updating, menu not working

**Solutions**:

1. **Check System Tray Support**:
   ```bash
   python -c "import pystray; print('System tray supported')"
   ```

2. **Platform-Specific Fixes**:
   - **macOS**: Check if menu bar has space
   - **Windows**: Check hidden icons, notification area settings
   - **Linux**: Ensure system tray/notification area is enabled

3. **Restart Application**:
   ```bash
   # Stop application
   pkill -f voice_notes_app

   # Start again
   python -m src.voice_notes_app
   ```

### Notification Issues

**Symptoms**: No notifications, notifications not showing, wrong content

**Solutions**:

1. **Enable Notifications**:
   ```yaml
   notifications:
     enabled: true
     system_notifications: true
   ```

2. **Platform Permissions**:
   - **macOS**: System Preferences > Notifications
   - **Windows**: Settings > System > Notifications
   - **Linux**: Check desktop environment notification settings

3. **Test Notifications**:
   ```bash
   python demo_notifications.py
   ```

### Startup Issues

**Symptoms**: Application won't start, crashes on launch, import errors

**Solutions**:

1. **Check Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Python Version**:
   ```bash
   python --version  # Should be 3.9+
   ```

3. **Virtual Environment**:
   ```bash
   # Ensure virtual environment is activated
   which python  # Should point to venv/bin/python
   ```

4. **Import Errors**:
   ```bash
   # Test individual components
   python -c "from src.audio_recorder import AudioRecorder"
   python -c "from src.system_tray import VoiceNotesSystemTray"
   ```

## Performance Problems

### Slow Processing

**Symptoms**: Long wait times, application freezing, timeout errors

**Solutions**:

1. **Check System Resources**:
   ```bash
   # Monitor CPU and memory
   top
   # or
   htop
   ```

2. **Reduce Processing Complexity**:
   ```yaml
   processing:
     default_mode: "quick"
     max_conversation_depth: 3
   ```

3. **Network Optimization**:
   - Use wired internet connection
   - Check network latency to OpenAI servers
   - Avoid peak usage times

4. **Application Restart**:
   ```bash
   # Restart application daily for long-term use
   pkill -f voice_notes_app
   python -m src.voice_notes_app
   ```

### High Memory Usage

**Symptoms**: System slowdown, memory warnings, application crashes

**Solutions**:

1. **Monitor Memory Usage**:
   ```bash
   ps aux | grep voice_notes
   ```

2. **Reduce Memory Footprint**:
   ```yaml
   audio:
     sample_rate: 22050  # Lower quality = less memory

   processing:
     max_conversation_depth: 3  # Fewer exchanges
   ```

3. **Regular Restarts**:
   - Restart application daily
   - Clear temporary files
   - Close other memory-intensive applications

### Network Timeouts

**Symptoms**: "Request timeout", "Connection lost", processing failures

**Solutions**:

1. **Increase Timeouts**:
   ```yaml
   api:
     openai:
       timeout: 120  # Increase from default 30s
   ```

2. **Retry Configuration**:
   ```yaml
   api:
     openai:
       max_retries: 5
       retry_delay: 2.0
   ```

3. **Network Diagnostics**:
   ```bash
   # Test connection speed
   speedtest-cli

   # Test API endpoint
   curl -w "@curl-format.txt" -s -o /dev/null https://api.openai.com/v1/models
   ```

## Configuration Issues

### Config File Problems

**Symptoms**: "Config file not found", "Invalid configuration", settings not applied

**Solutions**:

1. **Recreate Config File**:
   ```bash
   python setup_config.py
   ```

2. **Validate YAML Syntax**:
   ```bash
   python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
   ```

3. **Reset to Defaults**:
   ```bash
   # Backup current config
   cp config/config.yaml config/config.yaml.backup

   # Restore default
   cp config/config.yaml.template config/config.yaml
   ```

### Environment Variables

**Symptoms**: Environment variables not recognized, config not loading

**Solutions**:

1. **Check Environment Variables**:
   ```bash
   env | grep OPENAI
   env | grep VOICE_NOTES
   ```

2. **Set Persistent Variables**:
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export OPENAI_API_KEY="your-key"
   export VOICE_NOTES_DIR="~/Documents/Voice Notes"
   ```

3. **Priority Order**:
   - Environment variables override config file
   - Config file overrides defaults
   - Command line args override everything

## Getting Additional Help

### Log Analysis

**Viewing Logs**:
```bash
# Recent logs
tail -50 logs/voice_notes.log

# Real-time logging
tail -f logs/voice_notes.log

# Error logs only
grep ERROR logs/voice_notes.log

# Debug mode
# Set logging.level: DEBUG in config
```

### Debug Mode

**Enable Debug Logging**:
```yaml
logging:
  level: DEBUG
  file: "logs/voice_notes_debug.log"
```

**Debug Commands**:
```bash
# Test individual components
python test_audio_recorder.py --debug
python validate_config.py --verbose
python demo_notifications.py
```

### System Information

**Collect System Info**:
```bash
# System details
uname -a
python --version
pip list | grep -E "(openai|pystray|sounddevice)"

# Voice Notes specific
python -c "from src import __version__; print(__version__)"
ls -la config/
du -sh logs/
```

### Reporting Issues

When reporting problems, include:

1. **System Information**:
   - Operating system and version
   - Python version
   - Voice Notes version

2. **Configuration** (remove API keys):
   - Relevant config.yaml sections
   - Environment variables

3. **Error Details**:
   - Complete error message
   - Steps to reproduce
   - Recent log entries

4. **Attempts Made**:
   - Solutions already tried
   - Results of diagnostic commands

### Support Resources

- **GitHub Issues**: Technical problems and bug reports
- **Documentation**: Complete user and developer guides
- **Community Forums**: User discussions and tips
- **Email Support**: Account and billing questions

---

## Prevention Tips

### Regular Maintenance

- **Daily**: Restart application after heavy use
- **Weekly**: Check disk space and clean temp files
- **Monthly**: Update dependencies and review usage costs
- **Quarterly**: Backup configuration and notes

### Best Practices

- **Keep recordings under 2 minutes** for optimal processing
- **Monitor API usage** to avoid unexpected costs
- **Use Quick mode** for simple notes to save time and money
- **Provide context** in recordings for better AI processing
- **Test after system updates** to ensure compatibility

### Monitoring

```bash
# Create monitoring script
echo '#!/bin/bash
echo "Voice Notes System Status Check"
python validate_config.py
echo "Disk space:"
df -h ~/Documents
echo "Recent errors:"
tail -10 logs/voice_notes.log | grep ERROR
' > check_system.sh
chmod +x check_system.sh
```

Run this script regularly to catch issues early.

---

**Need immediate help?** Try the quick diagnostic: `python validate_config.py && python test_audio_recorder.py`