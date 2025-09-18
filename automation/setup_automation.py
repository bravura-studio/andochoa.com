#!/usr/bin/env python3
"""
Setup script for Vault Automation System
Handles installation, configuration, and initial setup
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
    """Install required Python packages"""
    print("\n📦 Installing Python dependencies...")
    
    requirements_file = Path(__file__).parent / 'requirements.txt'
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False


def setup_environment():
    """Set up environment configuration"""
    print("\n⚙️ Setting up environment configuration...")
    
    automation_dir = Path(__file__).parent
    env_file = automation_dir / '.env'
    env_example = automation_dir / '.env.example'
    
    if env_file.exists():
        print("ℹ️ .env file already exists")
        
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("✅ Keeping existing .env file")
            return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print(f"✅ Created .env file from template")
        print(f"📝 Please edit {env_file} to configure your settings")
        return True
    else:
        print("❌ .env.example template not found")
        return False


def create_directories():
    """Create required directories"""
    print("\n📁 Creating required directories...")
    
    automation_dir = Path(__file__).parent
    
    directories = [
        automation_dir / 'logs',
        automation_dir / 'state',
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")
    
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
    print("   Please set VAULT_PATH in your .env file")
    return None


def validate_configuration():
    """Validate the configuration"""
    print("\n🔍 Validating configuration...")
    
    try:
        # Add src directory to path
        src_dir = Path(__file__).parent / 'src'
        sys.path.insert(0, str(src_dir))
        
        from config import validate_environment
        
        if validate_environment():
            print("✅ Configuration validation passed")
            return True
        else:
            print("❌ Configuration validation failed")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import configuration module: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        return False


def create_service_script():
    """Create service runner script"""
    print("\n📜 Creating service runner script...")
    
    automation_dir = Path(__file__).parent
    runner_script = automation_dir / 'run_monitor.py'
    
    script_content = '''#!/usr/bin/env python3
"""
Vault Monitor Runner
Main entry point for starting the vault monitoring service
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

from vault_monitor import main

if __name__ == "__main__":
    sys.exit(main())
'''
    
    with open(runner_script, 'w') as f:
        f.write(script_content)
    
    # Make executable on Unix systems
    if hasattr(os, 'chmod'):
        os.chmod(runner_script, 0o755)
    
    print(f"✅ Created runner script: {runner_script}")
    return True


def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit the .env file to configure your settings:")
    print(f"   - Set CLAUDE_API_KEY to your Claude API key")
    print(f"   - Verify VAULT_PATH points to your vault")
    print(f"   - Adjust other settings as needed")
    print("\n2. Test the configuration:")
    print(f"   python -m src.config")
    print("\n3. Start the vault monitor:")
    print(f"   python run_monitor.py")
    print("\n4. Or run individual workflows:")
    print(f"   python -m src.workflow_engine --workflow analyze_new_content")
    
    print("\n📚 For more information, see README.md")


def main():
    """Main setup function"""
    print("🚀 Vault Automation System Setup")
    print("=" * 40)
    
    # Check prerequisites
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed: Could not install dependencies")
        return 1
    
    # Set up environment
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
                with open(env_file, 'r') as f:
                    content = f.read()
                
                # Replace placeholder vault path
                content = content.replace(
                    '/path/to/your/obsidian/vault/Content Bank',
                    detected_path
                )
                
                with open(env_file, 'w') as f:
                    f.write(content)
                
                print(f"✅ Updated .env file with detected vault path")
                
            except Exception as e:
                print(f"⚠️ Could not update .env file: {e}")
    
    # Create runner script
    if not create_service_script():
        print("\n❌ Setup failed: Could not create runner script")
        return 1
    
    # Validate configuration
    if not validate_configuration():
        print("\n⚠️ Setup completed but configuration needs attention")
        print("   Please review and fix the issues above")
    
    # Print next steps
    print_next_steps()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())