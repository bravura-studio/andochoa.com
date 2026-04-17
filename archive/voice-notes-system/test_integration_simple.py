#!/usr/bin/env python3
"""
Simple test for voice notes components integration.
Tests the core functionality without MCP server dependencies.
"""

import sys
import os
from pathlib import Path

# Add the src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_components():
    """Test the individual components."""
    print("🧪 Testing Voice Notes Components")
    print("=" * 40)

    try:
        from config_manager import ConfigManager
        print("✅ ConfigManager imported successfully")

        config = ConfigManager()
        print(f"📁 Output directory: {config.get_files_config().get('output_directory', 'Not set')}")

    except ImportError as e:
        print(f"❌ ConfigManager import failed: {e}")
        return False

    try:
        from conversation_manager import ConversationManager
        print("✅ ConversationManager imported successfully")

        # Test conversation analysis
        conv_manager = ConversationManager()

        test_transcript = """
        I've been struggling with our user onboarding process. We're losing
        too many users at signup. I think we need to reduce friction by asking
        for less information upfront and using progressive disclosure instead.
        """

        topic_type, reasoning = conv_manager.analyze_topic_type(test_transcript.strip())
        print(f"📋 Topic analysis: {topic_type.value} - {reasoning}")

        # Test conversation state creation
        conversation_state = conv_manager.create_conversation_state(test_transcript.strip())
        print(f"🤖 Conversation state: {conversation_state.topic_type.value}, {conversation_state.depth_level.value}")

        # Test initial prompt generation
        initial_prompt, state = conv_manager.generate_initial_prompt(test_transcript.strip())
        print(f"💬 Initial AI prompt: {initial_prompt}")

    except ImportError as e:
        print(f"❌ ConversationManager import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ ConversationManager test failed: {e}")
        return False

    try:
        from transcription import TranscriptionService
        print("✅ TranscriptionService imported successfully")

        # Don't test actual transcription without API key
        service = TranscriptionService(config)
        print(f"🎵 API key configured: {bool(service.api_key)}")

    except ImportError as e:
        print(f"❌ TranscriptionService import failed: {e}")
        return False

    try:
        from audio_recorder import AudioRecorder
        print("✅ AudioRecorder imported successfully")

        recorder = AudioRecorder(config)
        device_info = recorder.get_device_info()
        print(f"🎤 Audio device: {device_info.get('name', 'Unknown')}")

    except ImportError as e:
        print(f"❌ AudioRecorder import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️ AudioRecorder initialization warning: {e}")

    print(f"\n🎉 Component integration test completed!")
    print("✅ All core components are properly integrated")

    return True

def test_workflow_simulation():
    """Simulate the workflow without actual audio/API calls."""
    print(f"\n📋 Testing Workflow Simulation")
    print("=" * 40)

    try:
        from conversation_manager import ConversationManager

        conv_manager = ConversationManager()

        # Simulate transcription result
        mock_transcription = """
        I'm excited about the new progressive onboarding idea we discussed.
        The team seems really enthusiastic about implementing it. I think
        we should start with an MVP that just collects email and password,
        then progressively asks for more details as users engage.
        """

        # Create conversation state
        initial_prompt, conversation_state = conv_manager.generate_initial_prompt(
            mock_transcription.strip(), processing_mode="standard"
        )

        print(f"🎯 Topic detected: {conversation_state.topic_type.value}")
        print(f"📏 Conversation depth: {conversation_state.depth_level.value}")
        print(f"💬 AI initial prompt: {initial_prompt}")

        # Simulate user response
        mock_user_response = """
        Yes, I'm really excited too! The analytics clearly show we're losing
        people at the signup form. An MVP approach makes sense. We could
        A/B test it against our current form to measure the improvement.
        """

        # Continue conversation
        next_prompt = conv_manager.generate_followup(conversation_state)
        if next_prompt:
            conv_manager.update_conversation_context(
                conversation_state, mock_user_response.strip(), initial_prompt
            )
            print(f"🔄 Follow-up prompt: {next_prompt}")

        # Check if should continue
        should_continue = conv_manager.should_continue(conversation_state, mock_user_response)
        print(f"➡️ Should continue conversation: {should_continue}")

        # Finalize conversation
        insights = conv_manager.finalize_conversation(conversation_state)
        print(f"📊 Final insights:")
        print(f"   - Topic: {insights['topic_type']}")
        print(f"   - Exchanges: {insights['total_exchanges']}")
        print(f"   - Reason: {insights['completion_reason']}")

        print("✅ Workflow simulation successful!")
        return True

    except Exception as e:
        print(f"❌ Workflow simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_components()
    if success:
        test_workflow_simulation()

    print(f"\n💡 Next steps to test full integration:")
    print("   1. Ensure MCP dependencies are installed for Claude Desktop")
    print("   2. Set up OpenAI API key in .env file")
    print("   3. Test audio recording with microphone")
    print("   4. Test full workflow through Claude Desktop MCP interface")