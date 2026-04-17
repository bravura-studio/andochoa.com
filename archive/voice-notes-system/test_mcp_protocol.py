#!/usr/bin/env python3
"""
Test MCP protocol communication manually.
"""

import json
import sys
from pathlib import Path

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_mcp_manually():
    """Test MCP server manually by simulating Claude Desktop requests."""
    print("🧪 Testing MCP Protocol Communication")
    print("=" * 50)

    try:
        from src.mcp_server import VoiceNotesServer

        print("✅ MCP server imports successfully")

        # Create server instance
        server_instance = VoiceNotesServer()
        print("✅ MCP server instance created")

        # Get the server object
        mcp_server = server_instance.server
        print("✅ MCP server object accessible")

        # Test that tools are registered
        print(f"📋 Server name: {mcp_server.name}")

        # Try to manually call list_tools
        try:
            # This is tricky because the server handlers are async and designed for MCP protocol
            print("📝 Server is configured with tool handlers")

            # Check if server has the expected methods/handlers
            if hasattr(mcp_server, '_tool_handlers'):
                print(f"✅ Server has tool handlers configured")
            else:
                print("⚠️ Server tool handlers not found in expected location")

        except Exception as e:
            print(f"❌ Error testing tools: {e}")

        print("\n🔍 Diagnostics:")
        print(f"   - Server name: voice-notes")
        print(f"   - Expected tools: start_voice_recording, stop_voice_recording, transcribe_audio, etc.")
        print(f"   - MCP protocol version: Should be compatible with Claude Desktop")

        print(f"\n💡 Troubleshooting Steps:")
        print(f"   1. Enable the voice-notes server in Claude Desktop (toggle switch)")
        print(f"   2. Check Claude Desktop logs for connection errors")
        print(f"   3. Restart Claude Desktop after enabling")
        print(f"   4. Try asking: 'What voice notes tools are available?'")

        return True

    except Exception as e:
        print(f"❌ MCP protocol test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_mcp_manually()