#!/usr/bin/env python3
"""
Quick Voice Note - Simple script for immediate voice note creation
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from audio_recorder import AudioRecorder
from transcription import TranscriptionService
from config_manager import ConfigManager
import time

def main():
    """Create a quick voice note."""
    print("🎙️  Quick Voice Note Creator")
    print("=" * 40)

    # Initialize components
    try:
        config_manager = ConfigManager()

        # Simple audio config
        audio_config = {
            'sample_rate': 44100,
            'channels': 1,
            'chunk_size': 1024,
            'silence_threshold': 0.01,
            'silence_duration': 2.0
        }

        recorder = AudioRecorder(audio_config)
        transcription_service = TranscriptionService(config_manager)

        print("✅ System ready!")
        print("\nPress ENTER to start recording, then press ENTER again to stop...")
        input()

        print("🔴 Recording... speak now!")
        recorder.start_recording()

        input("Press ENTER to stop recording...")

        audio_file = recorder.stop_recording()
        print(f"✅ Recording saved: {audio_file}")

        print("🔄 Transcribing...")
        result = transcription_service.transcribe_audio(audio_file)

        print("\n" + "="*50)
        print("📝 TRANSCRIPTION:")
        print("="*50)
        print(result['text'])
        print("\n" + "="*50)
        print(f"Duration: {result.get('duration', 'unknown')} seconds")
        print(f"Cost: ${result.get('cost', 0):.4f}")

        # Clean up
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print("🧹 Temporary audio file cleaned up")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()