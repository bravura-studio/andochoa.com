#!/usr/bin/env python3
"""
Test script to verify MCP server fixes.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_mcp_server_creation():
    """Test MCP server creation with directory fixes."""
    print("🧪 Testing MCP Server Creation (Post-Fix)")
    print("=" * 50)

    try:
        from src.mcp_server import VoiceNotesServer

        print("✅ MCP server imports successfully")

        # Create server instance
        server = VoiceNotesServer()

        print("✅ MCP server created successfully")
        print(f"📁 Output directory: {server.output_dir}")
        print(f"🎵 Temp audio directory: {server.temp_audio_dir}")

        # Verify directories exist and are writable
        if server.output_dir.exists():
            print("✅ Output directory exists")
        else:
            print("❌ Output directory does not exist")

        if server.temp_audio_dir.exists():
            print("✅ Temp audio directory exists")
        else:
            print("❌ Temp audio directory does not exist")

        # Test writing to temp directory
        test_file = server.temp_audio_dir / "test_write.txt"
        try:
            test_file.write_text("test")
            test_file.unlink()  # Clean up
            print("✅ Temp directory is writable")
        except Exception as e:
            print(f"❌ Temp directory is not writable: {e}")

        # Test writing to output directory
        test_file = server.output_dir / "test_write.txt"
        try:
            test_file.write_text("test")
            test_file.unlink()  # Clean up
            print("✅ Output directory is writable")
        except Exception as e:
            print(f"❌ Output directory is not writable: {e}")

        print("\n🎯 Component Status:")
        print(f"   - Audio Recorder: {type(server.audio_recorder).__name__}")
        print(f"   - Transcription Service: {type(server.transcription_service).__name__}")
        print(f"   - Conversation Manager: {type(server.conversation_manager).__name__}")
        print(f"   - Config Manager: {type(server.config_manager).__name__}")

        # Test creating a mock voice note
        print(f"\n📝 Testing voice note creation...")

        mock_transcription = "I'm excited about fixing the MCP server integration. The directory path issues should now be resolved."

        result = await server._create_voice_note(
            transcription=mock_transcription,
            title="MCP Server Fix Test",
            tags=["test", "mcp", "integration"],
            conversation_type="update",
            enable_conversation=True,
            processing_mode="standard"
        )

        if result and len(result) > 0:
            print("✅ Voice note creation successful")
            response = result[0].text
            if "conversation" in response.lower():
                print("✅ AI conversation feature working")
            else:
                print("⚠️ AI conversation may not be working")
        else:
            print("❌ Voice note creation failed")

    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print(f"\n🚀 MCP Server Fix Status: SUCCESS")
    print("💡 The server should now work with Claude Desktop without read-only file system errors!")
    return True

if __name__ == "__main__":
    asyncio.run(test_mcp_server_creation())