# Python Automation System - File Watcher Implementation

## System Overview

The Python File Watcher provides real-time monitoring of your Obsidian vault and automatically triggers appropriate workflows based on file changes.

### Core Components

1. **vault_monitor.py** - Main file watching and event handling
2. **workflow_engine.py** - Workflow coordination and execution  
3. **claude_integration.py** - Claude API interface for agent execution
4. **config.py** - Configuration management
5. **setup_automation.py** - Installation and setup script

### Architecture

```
File Changes → Vault Monitor → Workflow Engine → Claude Integration → Results
     ↓              ↓              ↓              ↓              ↓
New Content →  Event Detection → Agent Selection → API Calls → Vault Updates
Training Data → Rule Matching → Queue Management → Context Prep → State Tracking
```

### Installation Requirements

```bash
pip install watchdog requests python-dotenv schedule
```

### Environment Setup

Create `.env` file in your automation directory:
```bash
# Claude API Configuration
CLAUDE_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-3-sonnet-20241022

# Vault Configuration  
VAULT_PATH=/path/to/your/obsidian/vault/Content Bank
MONITOR_PATHS=1-raw-ideas,training-data,4-published-content

# Workflow Configuration
AUTO_ANALYSIS=true
WEEKLY_DRAFT_DAY=friday
WEEKLY_DRAFT_TIME=14:00
BACKGROUND_PROCESSING=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=automation.log
```

### Directory Structure

```
automation/
├── src/
│   ├── vault_monitor.py
│   ├── workflow_engine.py  
│   ├── claude_integration.py
│   ├── config.py
│   └── utils.py
├── logs/
├── state/
│   ├── workflow_state.json
│   ├── processing_queue.json
│   └── performance_metrics.json
├── .env
├── requirements.txt
├── setup_automation.py
└── run_monitor.py
```

## Usage

### Start Monitoring
```bash
python run_monitor.py
```

### Manual Workflow Triggers
```bash
python -m src.workflow_engine --workflow weekly_draft
python -m src.workflow_engine --workflow process_new_content
python -m src.workflow_engine --workflow update_training_data
```

### Configuration
Edit `.env` file for your specific setup and preferences.

## Features

### Automatic Detection
- **New Raw Ideas**: Triggers analysis and connection workflows
- **Training Data Updates**: Updates style profile and worldview index  
- **Published Content**: Integrates into knowledge base
- **File Modifications**: Re-analyzes changed content

### Background Processing
- **Queue Management**: Handles multiple files and workflows
- **Priority System**: Critical updates processed first
- **Error Handling**: Automatic retry and recovery
- **Performance Tracking**: Metrics collection and optimization

### Scheduled Operations  
- **Weekly Drafts**: Automatic generation on configured schedule
- **System Optimization**: Monthly performance review and tuning
- **Backup and State Management**: Regular state saves and cleanup

## Next Steps

1. **Review configuration** in `.env` file
2. **Install dependencies** using pip
3. **Run setup script** to initialize system
4. **Test with sample content** to validate automation
5. **Configure scheduling** for your preferred workflow timing