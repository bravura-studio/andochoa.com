#!/usr/bin/env python3
"""
Setup script to configure Claude Desktop to connect to the Voice Notes MCP server.
"""

import json
import os
import shutil
from pathlib import Path
import platform


def get_claude_desktop_config_path():
    """Get the Claude Desktop configuration file path based on the operating system."""
    system = platform.system()

    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "Windows":
        return Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    elif system == "Linux":
        return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"
    else:
        raise OSError(f"Unsupported operating system: {system}")


def backup_existing_config(config_path):
    """Create a backup of the existing Claude Desktop configuration."""
    if config_path.exists():
        backup_path = config_path.with_suffix('.json.backup')
        shutil.copy2(config_path, backup_path)
        print(f"✓ Created backup at: {backup_path}")
        return True
    return False


def merge_configurations(existing_config, new_server_config):
    """Merge the voice-notes server configuration with existing Claude Desktop config."""
    if not existing_config:
        existing_config = {}

    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}

    # Add or update the voice-notes server configuration
    existing_config["mcpServers"]["voice-notes"] = new_server_config["mcpServers"]["voice-notes"]

    return existing_config


def setup_claude_desktop_integration():
    """Set up Claude Desktop to connect to the Voice Notes MCP server."""
    print("🔧 Setting up Claude Desktop integration for Voice Notes...")

    # Get the current working directory (voice-notes-system root)
    project_root = Path.cwd()
    config_file = project_root / "claude_desktop_config.json"

    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        return False

    # Load our voice-notes server configuration
    with open(config_file, 'r') as f:
        voice_notes_config = json.load(f)

    # Update the working directory path to be absolute
    voice_notes_config["mcpServers"]["voice-notes"]["cwd"] = str(project_root)

    # Update environment paths
    env_vars = voice_notes_config["mcpServers"]["voice-notes"]["env"]
    env_vars["PYTHONPATH"] = str(project_root)

    # Ensure output directory exists
    output_dir = Path(env_vars["VOICE_NOTES_OUTPUT_DIR"]).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get Claude Desktop configuration path
    try:
        claude_config_path = get_claude_desktop_config_path()
    except OSError as e:
        print(f"❌ {e}")
        return False

    # Ensure Claude Desktop config directory exists
    claude_config_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing Claude Desktop configuration
    existing_config = {}
    if claude_config_path.exists():
        try:
            with open(claude_config_path, 'r') as f:
                existing_config = json.load(f)
            print(f"✓ Found existing Claude Desktop configuration")
        except json.JSONDecodeError:
            print(f"⚠️  Existing configuration file is invalid JSON, creating new one")
            backup_existing_config(claude_config_path)

    # Merge configurations
    merged_config = merge_configurations(existing_config, voice_notes_config)

    # Write the updated configuration
    try:
        with open(claude_config_path, 'w') as f:
            json.dump(merged_config, f, indent=2)

        print(f"✓ Claude Desktop configuration updated: {claude_config_path}")
        print(f"✓ Voice Notes output directory: {output_dir}")

        # Show next steps
        print("\n📋 Next Steps:")
        print("1. Restart Claude Desktop for the changes to take effect")
        print("2. In Claude Desktop, you should now see 'voice-notes' as an available MCP server")
        print("3. You can ask Claude to:")
        print("   - 'Start a voice recording session'")
        print("   - 'List my voice notes'")
        print("   - 'Search my voice notes for [topic]'")
        print("   - 'Create a voice note from this text: [content]'")

        return True

    except Exception as e:
        print(f"❌ Failed to write configuration: {e}")
        return False


def verify_dependencies():
    """Verify that required dependencies are installed."""
    print("🔍 Verifying dependencies...")

    try:
        import mcp
        print("✓ MCP library is installed")
    except ImportError:
        print("❌ MCP library not found. Install with: pip install mcp")
        return False

    # Check if virtual environment is activated
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Virtual environment is active")
    else:
        print("⚠️  Virtual environment not detected. Consider activating your venv.")

    return True


def main():
    """Main setup function."""
    print("🎤 Voice Notes - Claude Desktop Integration Setup")
    print("=" * 50)

    # Verify dependencies
    if not verify_dependencies():
        return 1

    # Setup Claude Desktop integration
    if setup_claude_desktop_integration():
        print("\n🎉 Setup completed successfully!")
        print("\nTo test the integration:")
        print("1. Restart Claude Desktop")
        print("2. Open a new conversation")
        print("3. Try: 'List my voice notes' or 'What voice note tools are available?'")
        return 0
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())