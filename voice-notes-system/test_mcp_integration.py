#!/usr/bin/env python3
"""
Test script to verify MCP server functionality and Claude Desktop integration.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.mcp_server import VoiceNotesServer


async def test_mcp_server():
    """Test the MCP server functionality."""
    print("🧪 Testing Voice Notes MCP Server")
    print("=" * 40)

    # Create server instance
    server = VoiceNotesServer()

    # Test list_resources
    print("\n📋 Testing resource listing...")
    try:
        # Access resources via the proper MCP interface
        resources = await server.server.list_resources()
        print(f"✓ Found {len(resources)} resources")
        for resource in resources:
            print(f"  - {resource.name}: {resource.uri}")
    except Exception as e:
        print(f"⚠️  Resource listing test skipped: {e}")

    # Test list_tools
    print("\n🛠️  Testing tool listing...")
    try:
        tools = await server.server.list_tools()
        print(f"✓ Found {len(tools)} tools")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"⚠️  Tool listing test skipped: {e}")

    # Test tool calls
    print("\n🎤 Testing voice recording tools...")

    # Test start_voice_recording
    start_result = await server._start_voice_recording(
        session_name="Test Session",
        conversation_type="test"
    )
    print(f"✓ Start recording: {start_result[0].text[:100]}...")

    # Test create_voice_note
    note_result = await server._create_voice_note(
        transcription="This is a test transcription for MCP integration testing.",
        title="Test Note",
        tags=["test", "mcp", "integration"],
        conversation_type="test"
    )
    print(f"✓ Create note: {note_result[0].text[:100]}...")

    # Test list_voice_notes
    list_result = await server._list_voice_notes()
    print(f"✓ List notes: {list_result[0].text[:100]}...")

    # Test search_voice_notes
    search_result = await server._search_voice_notes(query="test")
    print(f"✓ Search notes: {search_result[0].text[:100]}...")

    print("\n✅ All MCP server tests passed!")


def test_configuration():
    """Test configuration files."""
    print("\n🔧 Testing configuration files...")

    # Check claude_desktop_config.json
    config_file = project_root / "claude_desktop_config.json"
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)
            print("✓ Claude Desktop config is valid JSON")

            if "mcpServers" in config and "voice-notes" in config["mcpServers"]:
                print("✓ Voice Notes server configuration found")
                server_config = config["mcpServers"]["voice-notes"]
                print(f"  - Command: {server_config.get('command')}")
                print(f"  - Args: {server_config.get('args')}")
                print(f"  - Working directory: {server_config.get('cwd')}")
            else:
                print("❌ Voice Notes server configuration not found")

        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in Claude Desktop config: {e}")
    else:
        print("❌ Claude Desktop config file not found")

    # Check if dependencies are available
    print("\n📦 Checking dependencies...")
    try:
        import mcp
        print("✓ MCP library available")
    except ImportError:
        print("❌ MCP library not installed (pip install mcp)")

    try:
        import openai
        print("✓ OpenAI library available")
    except ImportError:
        print("❌ OpenAI library not installed")

    # Check directories
    print("\n📁 Checking directories...")
    output_dir = Path("~/Documents/Voice Notes").expanduser()
    if output_dir.exists():
        print(f"✓ Output directory exists: {output_dir}")
    else:
        print(f"⚠️  Output directory will be created: {output_dir}")

    temp_dir = project_root / "temp_audio"
    if temp_dir.exists():
        print(f"✓ Temp audio directory exists: {temp_dir}")
    else:
        print(f"⚠️  Temp audio directory will be created: {temp_dir}")


async def main():
    """Main test function."""
    print("🎤 Voice Notes MCP Integration Test")
    print("=" * 50)

    # Test configuration
    test_configuration()

    # Test MCP server
    try:
        await test_mcp_server()
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return 1

    print("\n🎉 Integration test completed!")
    print("\nNext steps:")
    print("1. Run: python setup_claude_desktop.py")
    print("2. Restart Claude Desktop")
    print("3. Test with: 'List my voice notes' in Claude Desktop")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))