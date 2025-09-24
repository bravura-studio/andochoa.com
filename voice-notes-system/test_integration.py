#!/usr/bin/env python3
"""
Test script for the integrated MCP voice notes workflow.
This tests the basic components without requiring Claude Desktop.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.mcp_server import VoiceNotesServer
from mcp.types import TextContent

async def test_workflow():
    """Test the basic integrated workflow."""
    print("🧪 Testing Voice Notes Integration Workflow")
    print("=" * 50)

    # Initialize the server (but don't run it)
    server = VoiceNotesServer()

    print("✅ Server initialized successfully")
    print(f"📁 Output directory: {server.output_dir}")
    print(f"🎵 Audio temp directory: {server.temp_audio_dir}")
    print(f"🤖 Components loaded:")
    print(f"   - Audio Recorder: {type(server.audio_recorder).__name__}")
    print(f"   - Transcription Service: {type(server.transcription_service).__name__}")
    print(f"   - Conversation Manager: {type(server.conversation_manager).__name__}")

    # Test creating a voice note with conversation (using mock transcription)
    print("\n📝 Testing voice note creation with AI conversation...")

    mock_transcription = """
    I've been thinking about our user onboarding process. We're getting a lot of
    signups but people seem to drop off quickly. I wonder if we're asking for too
    much information upfront. Maybe we should try a progressive disclosure approach
    where we only ask for email initially and then gather more details as users
    engage with the product. What do you think about reducing friction in the
    first step?
    """

    try:
        result = await server._create_voice_note(
            transcription=mock_transcription.strip(),
            title="User Onboarding Thoughts",
            tags=["onboarding", "user_experience", "conversion"],
            conversation_type="brainstorm",
            enable_conversation=True,
            processing_mode="standard"
        )

        if result and len(result) > 0:
            print("✅ Voice note created successfully!")
            response = result[0].text
            print("📋 Server response:")
            print("-" * 30)
            print(response)

            # Extract conversation session ID from response
            if "Session ID:" in response:
                session_id_line = [line for line in response.split('\n') if 'Session ID:' in line][0]
                session_id = session_id_line.split('`')[1]  # Extract from backticks
                print(f"\n🎯 Extracted conversation session ID: {session_id}")

                # Test continuing the conversation
                print("\n💬 Testing conversation continuation...")

                mock_user_response = """
                You're absolutely right about the friction. I've been looking at our analytics
                and we lose about 60% of users at the signup form. A progressive disclosure
                approach sounds smart. We could start with just email and password, then ask
                for company details after they complete their first task. That way they're
                already invested in the product.
                """

                continue_result = await server._continue_conversation(
                    session_id=session_id,
                    user_response=mock_user_response.strip()
                )

                if continue_result and len(continue_result) > 0:
                    print("✅ Conversation continuation successful!")
                    print("🤖 AI response:")
                    print("-" * 30)
                    print(continue_result[0].text)

                    # Test ending the conversation
                    print(f"\n🏁 Testing conversation completion...")

                    end_result = await server._end_conversation(session_id=session_id)

                    if end_result and len(end_result) > 0:
                        print("✅ Conversation ended successfully!")
                        print("📊 Final summary:")
                        print("-" * 30)
                        print(end_result[0].text)
                    else:
                        print("❌ Failed to end conversation")
                else:
                    print("❌ Failed to continue conversation")
            else:
                print("⚠️ No conversation session ID found in response")
        else:
            print("❌ Failed to create voice note")

    except Exception as e:
        print(f"❌ Error during workflow test: {e}")
        import traceback
        traceback.print_exc()

    # Test listing voice notes
    print(f"\n📋 Testing voice notes listing...")
    try:
        list_result = await server._list_voice_notes(limit=5)
        if list_result and len(list_result) > 0:
            print("✅ Voice notes listed successfully!")
            print("📄 Notes list:")
            print("-" * 30)
            print(list_result[0].text)
        else:
            print("❌ Failed to list voice notes")
    except Exception as e:
        print(f"❌ Error listing voice notes: {e}")

    print(f"\n🎉 Integration test completed!")
    print("💡 To test the full workflow with Claude Desktop:")
    print("   1. Start the MCP server: python start_mcp_server.py")
    print("   2. In Claude Desktop, try: 'Start a voice recording session'")
    print("   3. Use: 'Stop voice recording session_id'")
    print("   4. Use: 'Transcribe audio file: /path/to/audio.wav'")
    print("   5. Use: 'Create voice note from transcription with conversation'")

if __name__ == "__main__":
    asyncio.run(test_workflow())