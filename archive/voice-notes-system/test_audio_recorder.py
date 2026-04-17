#!/usr/bin/env python3
"""
Test script for AudioRecorder functionality

This script demonstrates and tests the audio recording capabilities.
"""

import sys
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from audio_recorder import AudioRecorder
from config_manager import ConfigManager


def test_audio_devices():
    """Test audio device detection and listing."""
    print("=== Testing Audio Device Detection ===")

    try:
        import sounddevice as sd

        print("Available audio devices:")
        devices = sd.query_devices()

        input_devices = []
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append(device)
                print(f"  Input Device {i}: {device['name']} "
                      f"({device['max_input_channels']} channels, "
                      f"{device['default_samplerate']} Hz)")

        if not input_devices:
            print("❌ No input devices found!")
            return False

        print(f"✅ Found {len(input_devices)} input device(s)")

        # Test default device
        default_input = sd.query_devices(kind='input')
        print(f"\nDefault input device: {default_input['name']}")

        return True

    except Exception as e:
        print(f"❌ Error checking audio devices: {e}")
        return False


def test_recorder_initialization():
    """Test AudioRecorder initialization."""
    print("\n=== Testing AudioRecorder Initialization ===")

    try:
        # Test with default configuration
        config = ConfigManager()
        recorder = AudioRecorder(config)

        print("✅ AudioRecorder initialized successfully")

        # Test device info
        device_info = recorder.get_device_info()
        if 'error' in device_info:
            print(f"⚠️  Device info error: {device_info['error']}")
        else:
            print(f"Using device: {device_info['name']}")
            print(f"Channels: {device_info['channels']}")
            print(f"Sample rate: {device_info['sample_rate']} Hz")

        return True

    except Exception as e:
        print(f"❌ Error initializing recorder: {e}")
        return False


def test_level_monitoring():
    """Test audio level monitoring without recording."""
    print("\n=== Testing Audio Level Monitoring ===")

    try:
        recorder = AudioRecorder()

        # Set up level callback
        max_level = 0.0
        level_count = 0

        def level_callback(level):
            nonlocal max_level, level_count
            max_level = max(max_level, level)
            level_count += 1

        recorder.set_level_callback(level_callback)

        print("Starting 3-second level monitoring test...")
        print("Please make some noise (speak, clap, etc.)")

        # Start recording briefly to test level monitoring
        if recorder.start_recording():
            time.sleep(3)
            recorder.stop_recording()

            print(f"✅ Level monitoring test completed")
            print(f"Maximum level detected: {max_level:.3f}")
            print(f"Level updates received: {level_count}")

            return True
        else:
            print("❌ Failed to start recording for level test")
            return False

    except Exception as e:
        print(f"❌ Error testing level monitoring: {e}")
        return False


def test_silence_detection():
    """Test silence detection configuration."""
    print("\n=== Testing Silence Detection ===")

    try:
        recorder = AudioRecorder()

        # Test silence detection configuration
        original_threshold = recorder.silence_threshold
        original_duration = recorder.silence_duration

        # Test valid parameters
        if recorder.detect_silence(threshold=0.02, duration=1.5):
            print("✅ Silence detection configuration updated")
        else:
            print("❌ Failed to update silence detection")
            return False

        # Test invalid parameters
        if not recorder.detect_silence(threshold=1.5):  # Invalid threshold
            print("✅ Invalid threshold correctly rejected")
        else:
            print("❌ Invalid threshold was accepted")

        if not recorder.detect_silence(duration=-1):  # Invalid duration
            print("✅ Invalid duration correctly rejected")
        else:
            print("❌ Invalid duration was accepted")

        # Restore original settings
        recorder.detect_silence(threshold=original_threshold, duration=original_duration)

        return True

    except Exception as e:
        print(f"❌ Error testing silence detection: {e}")
        return False


def test_recording_and_saving():
    """Test full recording and saving functionality."""
    print("\n=== Testing Recording and Saving ===")

    try:
        recorder = AudioRecorder()

        print("Starting 2-second recording test...")
        print("Please say something!")

        # Start recording
        if not recorder.start_recording():
            print("❌ Failed to start recording")
            return False

        # Record for 2 seconds
        time.sleep(2)

        # Stop recording
        if not recorder.stop_recording():
            print("❌ Failed to stop recording")
            return False

        # Check recording duration
        duration = recorder.get_recording_duration()
        print(f"Recording duration: {duration:.1f} seconds")

        if duration < 1.0:
            print("⚠️  Recording seems too short")

        # Save the recording
        try:
            filepath = recorder.save_audio()
            print(f"✅ Audio saved to: {filepath}")

            # Verify file exists and has content
            saved_file = Path(filepath)
            if saved_file.exists() and saved_file.stat().st_size > 1000:
                print(f"✅ Saved file verified ({saved_file.stat().st_size} bytes)")

                # Clean up test file
                saved_file.unlink()
                print("✅ Test file cleaned up")

                return True
            else:
                print("❌ Saved file is empty or missing")
                return False

        except Exception as e:
            print(f"❌ Error saving audio: {e}")
            return False

    except Exception as e:
        print(f"❌ Error in recording test: {e}")
        return False


def test_context_manager():
    """Test context manager functionality."""
    print("\n=== Testing Context Manager ===")

    try:
        with AudioRecorder() as recorder:
            print("✅ Context manager entry successful")

            # Test that recording stops automatically on exit
            recorder.start_recording()
            time.sleep(0.5)

        print("✅ Context manager exit successful")
        return True

    except Exception as e:
        print(f"❌ Error testing context manager: {e}")
        return False


def interactive_test():
    """Interactive test allowing user to control recording."""
    print("\n=== Interactive Recording Test ===")
    print("Commands: 's' = start, 'q' = stop, 'x' = exit")

    try:
        recorder = AudioRecorder()

        # Set up level monitoring
        def level_callback(level):
            if level > 0.1:  # Only show significant levels
                print(f"Level: {'█' * int(level * 20):.20s} {level:.3f}")

        recorder.set_level_callback(level_callback)

        while True:
            command = input("\nEnter command (s/q/x): ").strip().lower()

            if command == 's':
                if recorder.start_recording():
                    print("🎤 Recording started... (audio levels will be shown)")
                else:
                    print("❌ Failed to start recording")

            elif command == 'q':
                if recorder.stop_recording():
                    duration = recorder.get_recording_duration()
                    print(f"⏹️  Recording stopped. Duration: {duration:.1f}s")

                    save = input("Save recording? (y/N): ").strip().lower()
                    if save == 'y':
                        try:
                            filepath = recorder.save_audio()
                            print(f"✅ Saved to: {filepath}")
                        except Exception as e:
                            print(f"❌ Save failed: {e}")
                    else:
                        recorder.clear_recording()
                        print("Recording discarded")
                else:
                    print("No recording in progress")

            elif command == 'x':
                if recorder.is_recording:
                    recorder.stop_recording()
                print("Goodbye!")
                break

            else:
                print("Invalid command. Use 's', 'q', or 'x'")

        return True

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return True
    except Exception as e:
        print(f"❌ Error in interactive test: {e}")
        return False


def main():
    """Run all audio recorder tests."""
    print("Voice Notes System - Audio Recorder Test Suite")
    print("=" * 60)

    tests = [
        ("Audio Device Detection", test_audio_devices),
        ("Recorder Initialization", test_recorder_initialization),
        ("Level Monitoring", test_level_monitoring),
        ("Silence Detection", test_silence_detection),
        ("Recording and Saving", test_recording_and_saving),
        ("Context Manager", test_context_manager),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Audio recording system is working correctly.")

        # Offer interactive test
        interactive = input("\nRun interactive test? (y/N): ").strip().lower()
        if interactive == 'y':
            interactive_test()

        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the audio setup.")
        return 1


if __name__ == "__main__":
    sys.exit(main())