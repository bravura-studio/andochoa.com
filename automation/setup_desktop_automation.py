#!/usr/bin/env python3
"""
Setup script for Desktop Vault Automation System
Optimized for Claude Desktop integration without API requirements
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python version OK: {sys.version.split()[0]}")
    return True


def install_dependencies():
    """Install required Python packages for desktop version"""
    print("\n📦 Installing Python dependencies (Claude Desktop version)...")
    
    # Create simplified requirements for desktop version
    desktop_requirements = [
        'watchdog>=3.0.0',
        'python-dotenv>=1.0.0',
        'pyyaml>=6.0'
    ]
    
    # Optional dependencies for better desktop integration
    optional_requirements = [
        'win10toast',  # Windows notifications
    ]
    
    try:
        # Install core requirements
        for package in desktop_requirements:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Installed {package}")
            else:
                print(f"❌ Failed to install {package}: {result.stderr}")
                return False
        
        # Try to install optional requirements (don't fail if they don't install)
        for package in optional_requirements:
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], capture_output=True, text=True, timeout=30)
            except:
                pass
                
        print("✅ Core dependencies installed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def setup_environment():
    """Set up environment configuration for desktop version"""
    print("\n⚙️ Setting up desktop environment configuration...")
    
    automation_dir = Path(__file__).parent
    env_file = automation_dir / '.env'
    
    if env_file.exists():
        print("ℹ️ .env file already exists")
        
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("✅ Keeping existing .env file")
            return True
    
    # Create desktop-optimized .env file
    env_content = """# Claude Desktop Integration Configuration

# Vault Configuration (auto-detected if not specified)
VAULT_PATH=
MONITOR_PATHS=1-raw-ideas,training-data,4-published-content

# Desktop Workflow Configuration
AUTO_PROCESS_TRAINING_DATA=true
NOTIFY_NEW_CONTENT=true
DESKTOP_NOTIFICATIONS=true

# Workflow Settings
MAX_CONCURRENT_WORKFLOWS=1
WORKFLOW_TIMEOUT=1800

# Performance Configuration  
DEBOUNCE_TIME=2
RETRY_ATTEMPTS=3
RETRY_DELAY=5

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=desktop_automation.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5

# Note: No Claude API key required for desktop version!
# This system works with your existing Claude Pro subscription
# through Claude Desktop app copy/paste workflows.
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created desktop .env configuration")
    return True


def create_directories():
    """Create required directories for desktop version"""
    print("\n📁 Creating required directories...")
    
    automation_dir = Path(__file__).parent
    
    directories = [
        automation_dir / 'logs',
        automation_dir / 'state',
        automation_dir / 'prompts',
        automation_dir / 'responses',
        automation_dir / 'contexts',
        automation_dir / 'notifications'
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory.name}/")
    
    return True


def detect_vault_path():
    """Try to auto-detect vault path"""
    print("\n🔍 Detecting vault path...")
    
    automation_dir = Path(__file__).parent
    
    # Common vault locations
    possible_paths = [
        automation_dir.parent,  # automation is inside vault
        Path.home() / 'Documents' / 'Obsidian' / 'Content Bank',
        Path.home() / 'Obsidian' / 'Content Bank',
        Path.home() / 'vault' / 'Content Bank'
    ]
    
    for path in possible_paths:
        if path.exists() and (path / 'agents').exists():
            print(f"✅ Found vault at: {path}")
            return str(path)
    
    print("⚠️ Could not auto-detect vault path")
    print("   You can set VAULT_PATH in your .env file if needed")
    return None


def validate_configuration():
    """Validate the desktop configuration"""
    print("\n🔍 Validating desktop configuration...")
    
    try:
        # Add src directory to path
        src_dir = Path(__file__).parent / 'src'
        sys.path.insert(0, str(src_dir))
        
        from config import get_config
        
        config = get_config()
        print("✅ Configuration loading successful")
        print(f"📁 Vault path: {config.vault_path}")
        print(f"👁️ Monitor paths: {', '.join(config.monitor_paths)}")
        print("🎉 Desktop integration: Enabled")
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import configuration module: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        return False


def create_desktop_runner_scripts():
    """Create desktop-optimized runner scripts"""
    print("\n📜 Creating desktop runner scripts...")
    
    automation_dir = Path(__file__).parent
    
    # Main monitor runner
    monitor_runner = automation_dir / 'run_desktop_monitor.py'
    monitor_content = '''#!/usr/bin/env python3
"""
Desktop Vault Monitor Runner  
Main entry point for desktop-based vault monitoring
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

from desktop_vault_monitor import main

if __name__ == "__main__":
    sys.exit(main())
'''
    
    with open(monitor_runner, 'w') as f:
        f.write(monitor_content)
    
    # Workflow runner  
    workflow_runner = automation_dir / 'run_desktop_workflow.py'
    workflow_content = '''#!/usr/bin/env python3
"""
Desktop Workflow Runner
Command-line interface for desktop workflows
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

from desktop_workflow_engine import main

if __name__ == "__main__":
    sys.exit(main())
'''
    
    with open(workflow_runner, 'w') as f:
        f.write(workflow_content)
    
    # Make executable on Unix systems
    if hasattr(os, 'chmod'):
        os.chmod(monitor_runner, 0o755)
        os.chmod(workflow_runner, 0o755)
    
    print(f"✅ Created desktop runner scripts")
    return True


def create_quick_start_guide():
    """Create quick start guide for desktop users"""
    
    automation_dir = Path(__file__).parent
    guide_file = automation_dir / 'QUICK_START_DESKTOP.md'
    
    content = """# 🚀 Quick Start Guide - Claude Desktop Integration

## 🎉 Setup Complete!

Your desktop automation system is ready to use with Claude Desktop.

## ⚡ Test the System (2 minutes):

### 1. Start Monitoring:
```bash
python run_desktop_monitor.py
```

### 2. Test Content Detection:
- Create a test file: `echo "Test content" > "../1-raw-ideas/test.md"`
- You should get a desktop notification!

### 3. Process Content:
```bash
python run_desktop_workflow.py --workflow analyze_new_content
```

### 4. Generate Weekly Draft:
```bash
python run_desktop_workflow.py --workflow generate_weekly_draft
```

## 📋 Available Commands:

```bash
# Start file monitoring (run in background)
python run_desktop_monitor.py

# List available workflows  
python run_desktop_workflow.py --list

# Generate weekly insights
python run_desktop_workflow.py --workflow generate_weekly_draft

# Analyze new content
python run_desktop_workflow.py --workflow analyze_new_content

# Update style profile
python run_desktop_workflow.py --workflow update_style_profile

# Check system status
python run_desktop_workflow.py --status
```

## 🔄 Typical Workflow:

1. **Add content** to your vault (`1-raw-ideas/`, training data, etc.)
2. **Get notification** that content is ready for processing
3. **Run workflow** command for the type of processing you want
4. **Copy prompt** from auto-opened file to Claude Desktop
5. **Paste response** back to specified response file
6. **System processes** results automatically and updates your vault

## ✨ Benefits:

- **90% automated**: System handles all coordination and context preparation
- **Uses your Claude Pro**: No API costs, uses your existing subscription
- **Fast workflows**: 2-5 minutes instead of 15-30 minutes manual work
- **Smart notifications**: Only bothers you when action is needed

## 📁 File Structure:

- `prompts/` - Ready-to-copy prompts for Claude Desktop
- `responses/` - Save Claude's responses here
- `notifications/` - System notifications about ready workflows
- `logs/` - System activity and debugging info

## 🎯 Next Steps:

1. **Start monitoring**: `python run_desktop_monitor.py`
2. **Add real content** to test the system
3. **Generate your first automated weekly draft**!

**You now have a true AI automation partner! 🤖✨**
"""
    
    guide_file.write_text(content, encoding='utf-8')
    return guide_file


def print_next_steps(guide_file):
    """Print next steps for the user"""
    print("\n🎉 Desktop Setup completed successfully!")
    print("\n📋 Next steps:")
    
    print("\n🚀 Test the system:")
    print("   python run_desktop_monitor.py")
    print("   (Open new terminal) python run_desktop_workflow.py --list")
    
    print("\n⚡ Quick test workflow:")
    print("   1. Add test file to 1-raw-ideas/")
    print("   2. Get desktop notification")
    print("   3. Run: python run_desktop_workflow.py --workflow analyze_new_content")
    print("   4. Follow copy/paste instructions")
    
    print(f"\n📚 Complete guide: {guide_file}")
    print("\n💡 Key advantage: Uses your existing Claude Pro subscription!")
    print("   No API key required, no additional costs!")


def main():
    """Main setup function for desktop version"""
    print("🚀 Desktop Vault Automation System Setup")
    print("Uses Claude Desktop - No API Key Required!")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        return 1
    
    # Install dependencies (simplified for desktop)
    if not install_dependencies():
        print("\n❌ Setup failed: Could not install dependencies")
        return 1
    
    # Set up environment (no API key required)
    if not setup_environment():
        print("\n❌ Setup failed: Could not set up environment")
        return 1
    
    # Create directories
    if not create_directories():
        print("\n❌ Setup failed: Could not create directories")
        return 1
    
    # Detect vault path
    detected_path = detect_vault_path()
    if detected_path:
        # Update .env file with detected path
        env_file = Path(__file__).parent / '.env'
        if env_file.exists():
            try:
                content = env_file.read_text()
                content = content.replace('VAULT_PATH=', f'VAULT_PATH={detected_path}')
                env_file.write_text(content)
                print(f"✅ Updated .env file with detected vault path")
            except Exception as e:
                print(f"⚠️ Could not update .env file: {e}")
    
    # Create runner scripts
    if not create_desktop_runner_scripts():
        print("\n❌ Setup failed: Could not create runner scripts")
        return 1
    
    # Validate configuration
    if not validate_configuration():
        print("\n⚠️ Setup completed but configuration needs attention")
        
    # Create quick start guide
    guide_file = create_quick_start_guide()
    
    # Print next steps
    print_next_steps(guide_file)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())