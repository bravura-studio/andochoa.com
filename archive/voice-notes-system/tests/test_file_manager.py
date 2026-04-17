"""
Test FileManager implementation.
"""

import tempfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock
import unittest

# Add the src directory to the path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import with absolute path handling
try:
    from file_manager import FileManager, SaveResult
    from markdown_formatter import ConversationMetadata
except ImportError:
    # Handle relative imports by adjusting the import path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from src.file_manager import FileManager, SaveResult
    from src.markdown_formatter import ConversationMetadata


def test_file_manager_import():
    """Test that FileManager can be imported successfully."""
    assert FileManager is not None
    print("✓ FileManager import test passed")


def test_create_hybrid_filename():
    """Test hybrid filename creation."""
    # Create a temporary config
    config = {
        'files': {
            'naming_pattern': 'hybrid',
            'output_directory': '/tmp/test_voice_notes'
        }
    }

    fm = FileManager(config)

    # Create test metadata
    metadata = ConversationMetadata(
        topic_type='struggle',
        depth_level='standard',
        total_exchanges=3,
        conversation_length=500,
        completion_reason='natural_end',
        created_at=datetime(2024, 9, 22, 10, 30, 0)
    )

    # Test hybrid filename creation
    title = "Struggle: Learning Python Programming"
    filename = fm.create_hybrid_filename(title, metadata)

    expected = "2024-09-22_Learning-Python-Programming.md"
    assert filename == expected, f"Expected {expected}, got {filename}"
    print("✓ Hybrid filename creation test passed")


def test_clean_title_for_filename():
    """Test title cleaning for filename."""
    config = {
        'files': {
            'naming_pattern': 'hybrid',
            'output_directory': '/tmp/test_voice_notes'
        }
    }

    fm = FileManager(config)

    # Test various title cleaning scenarios
    test_cases = [
        ("Struggle: Learning Python Programming", "Learning-Python-Programming"),
        ("Idea: Building a New App", "Building-a-New-App"),
        ("My Voice Note Session", "My-Voice-Note-Session"),
        ("Test with special chars <>/\\|?*", "Test-with-special-chars"),
        ("", "voice-note"),  # Empty title fallback
    ]

    for input_title, expected in test_cases:
        result = fm._clean_title_for_filename(input_title)
        assert result == expected, f"For '{input_title}', expected '{expected}', got '{result}'"

    print("✓ Title cleaning test passed")


def test_get_save_directory():
    """Test save directory creation."""
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {
            'files': {
                'output_directory': temp_dir,
                'daily_folders': True
            }
        }

        fm = FileManager(config)

        # Create test metadata
        metadata = ConversationMetadata(
            topic_type='struggle',
            depth_level='standard',
            total_exchanges=3,
            conversation_length=500,
            completion_reason='natural_end',
            created_at=datetime(2024, 9, 22, 10, 30, 0)
        )

        # Test directory creation
        save_dir = fm.get_save_directory(metadata)
        expected_dir = Path(temp_dir) / "2024-09-22"

        assert save_dir == expected_dir, f"Expected {expected_dir}, got {save_dir}"
        assert save_dir.exists(), "Save directory should be created"
        print("✓ Save directory creation test passed")


def test_handle_file_conflicts():
    """Test file conflict resolution."""
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {
            'files': {
                'output_directory': temp_dir,
                'daily_folders': False
            }
        }

        fm = FileManager(config)

        # Create a test file that will cause a conflict
        test_file = Path(temp_dir) / "test_note.md"
        test_file.write_text("Existing content")

        # Test conflict resolution
        resolved_path, conflict_resolved = fm.handle_file_conflicts(test_file)

        expected_path = Path(temp_dir) / "test_note_01.md"
        assert resolved_path == expected_path, f"Expected {expected_path}, got {resolved_path}"
        assert conflict_resolved == True, "Conflict should be marked as resolved"
        print("✓ File conflict resolution test passed")


def test_cleanup_temporary_files():
    """Test temporary file cleanup."""
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        config = {
            'files': {
                'output_directory': temp_dir,
                'cleanup_temp_files': True
            }
        }

        fm = FileManager(config)

        # Create temporary test files
        temp_file1 = Path(temp_dir) / "temp1.wav"
        temp_file2 = Path(temp_dir) / "temp2.wav"
        temp_file1.write_text("temp audio data 1")
        temp_file2.write_text("temp audio data 2")

        # Test cleanup
        temp_files = [str(temp_file1), str(temp_file2)]
        result = fm.cleanup_temporary_files(temp_files)

        assert result == True, "Cleanup should succeed"
        assert not temp_file1.exists(), "Temp file 1 should be deleted"
        assert not temp_file2.exists(), "Temp file 2 should be deleted"
        print("✓ Temporary file cleanup test passed")


if __name__ == "__main__":
    # Run all tests
    try:
        test_file_manager_import()
        test_create_hybrid_filename()
        test_clean_title_for_filename()
        test_get_save_directory()
        test_handle_file_conflicts()
        test_cleanup_temporary_files()
        print("\n✅ All FileManager tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)