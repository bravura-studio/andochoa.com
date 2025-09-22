"""
Unit tests for the Error Recovery System.
"""

import os
import sys
import unittest
import asyncio
import tempfile
import shutil
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from error_recovery import (
    ErrorRecoverySystem, ErrorType, ErrorSeverity, RecoveryAction,
    ErrorInfo, FailedOperation, with_error_recovery
)


class TestErrorRecoverySystem(unittest.TestCase):
    """Test cases for ErrorRecoverySystem."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.recovery_system = ErrorRecoverySystem(data_dir=self.temp_dir, max_queue_size=10)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_error(self):
        """Test error logging functionality."""
        test_error = ValueError("Test error")
        context = {"test_key": "test_value"}

        error_id = self.recovery_system.log_error(
            error=test_error,
            error_type=ErrorType.TRANSCRIPTION,
            severity=ErrorSeverity.MEDIUM,
            context=context,
            user_message="Test user message"
        )

        # Check that error was logged
        self.assertIsNotNone(error_id)
        self.assertEqual(len(self.recovery_system.error_history), 1)

        # Check error details
        logged_error = self.recovery_system.error_history[0]
        self.assertEqual(logged_error.error_id, error_id)
        self.assertEqual(logged_error.error_type, ErrorType.TRANSCRIPTION)
        self.assertEqual(logged_error.severity, ErrorSeverity.MEDIUM)
        self.assertEqual(logged_error.message, "Test error")
        self.assertEqual(logged_error.user_message, "Test user message")
        self.assertEqual(logged_error.context, context)

    def test_queue_failed_operation(self):
        """Test queuing failed operations."""
        error_info = ErrorInfo(
            error_id="test_error",
            error_type=ErrorType.MCP_CONNECTION,
            severity=ErrorSeverity.HIGH,
            message="Test error",
            user_message="Connection failed",
            timestamp=datetime.now(),
            context={}
        )

        operation_id = self.recovery_system.queue_failed_operation(
            function_name="test_function",
            args=["arg1", "arg2"],
            kwargs={"key": "value"},
            error_info=error_info
        )

        # Check that operation was queued
        self.assertIsNotNone(operation_id)
        self.assertEqual(len(self.recovery_system.recovery_queue), 1)

        # Check operation details
        queued_op = self.recovery_system.recovery_queue[0]
        self.assertEqual(queued_op.operation_id, operation_id)
        self.assertEqual(queued_op.function_name, "test_function")
        self.assertEqual(queued_op.args, ["arg1", "arg2"])
        self.assertEqual(queued_op.kwargs, {"key": "value"})
        self.assertEqual(queued_op.error_info, error_info)

    def test_register_retry_function(self):
        """Test registering retry functions."""
        def test_function(*args, **kwargs):
            return "success"

        self.recovery_system.register_retry_function("test_function", test_function)

        # Check that function was registered
        self.assertIn("test_function", self.recovery_system.retry_functions)
        self.assertEqual(self.recovery_system.retry_functions["test_function"], test_function)

    def test_max_queue_size_limit(self):
        """Test that queue respects maximum size limit."""
        # Fill queue beyond max size
        for i in range(15):  # max_queue_size is 10
            self.recovery_system.queue_failed_operation(
                function_name=f"test_function_{i}",
                args=[],
                kwargs={}
            )

        # Check that queue size is limited
        self.assertEqual(len(self.recovery_system.recovery_queue), 10)

    def test_error_summary(self):
        """Test error summary generation."""
        # Log some errors
        for i in range(5):
            error_type = ErrorType.TRANSCRIPTION if i % 2 == 0 else ErrorType.MCP_CONNECTION
            severity = ErrorSeverity.LOW if i % 3 == 0 else ErrorSeverity.HIGH

            self.recovery_system.log_error(
                error=ValueError(f"Error {i}"),
                error_type=error_type,
                severity=severity
            )

        summary = self.recovery_system.get_error_summary(hours=24)

        # Check summary structure
        self.assertEqual(summary['total_errors'], 5)
        self.assertIn('by_type', summary)
        self.assertIn('by_severity', summary)
        self.assertIn('resolution_rate', summary)
        self.assertIn('queue_size', summary)

        # Check type breakdown
        self.assertEqual(summary['by_type']['transcription'], 3)
        self.assertEqual(summary['by_type']['mcp_connection'], 2)

    def test_recovery_status(self):
        """Test recovery status reporting."""
        # Queue some operations
        for i in range(3):
            self.recovery_system.queue_failed_operation(
                function_name=f"test_function_{i}",
                args=[],
                kwargs={}
            )

        status = self.recovery_system.get_recovery_status()

        # Check status structure
        self.assertIn('queue_size', status)
        self.assertIn('ready_for_retry', status)
        self.assertIn('next_retry', status)
        self.assertIn('recent_errors', status)
        self.assertIn('uptime_hours', status)

        self.assertEqual(status['queue_size'], 3)

    def test_generate_user_message(self):
        """Test user-friendly error message generation."""
        # Test transcription error with API pattern - should trigger 'api' case
        error = ValueError("api timeout")
        message = self.recovery_system._generate_user_message(error, ErrorType.TRANSCRIPTION)
        self.assertTrue("transcription" in message.lower() or "service" in message.lower())

        # Test audio recording error
        error = RuntimeError("device not found")
        message = self.recovery_system._generate_user_message(error, ErrorType.AUDIO_RECORDING)
        self.assertTrue("audio" in message.lower() or "microphone" in message.lower())

        # Test network error
        error = ConnectionError("connection failed")
        message = self.recovery_system._generate_user_message(error, ErrorType.NETWORK)
        self.assertTrue("network" in message.lower() or "connection" in message.lower())

        # Test default case
        error = ValueError("unknown error")
        message = self.recovery_system._generate_user_message(error, ErrorType.TRANSCRIPTION)
        self.assertIn("failed", message.lower())

    def test_cleanup_old_data(self):
        """Test cleanup of old error data."""
        # Add old error
        old_error = ErrorInfo(
            error_id="old_error",
            error_type=ErrorType.SYSTEM,
            severity=ErrorSeverity.LOW,
            message="Old error",
            user_message="Old error occurred",
            timestamp=datetime.now() - timedelta(days=10),
            context={}
        )
        self.recovery_system.error_history.append(old_error)

        # Add recent error
        recent_error = ErrorInfo(
            error_id="recent_error",
            error_type=ErrorType.SYSTEM,
            severity=ErrorSeverity.LOW,
            message="Recent error",
            user_message="Recent error occurred",
            timestamp=datetime.now(),
            context={}
        )
        self.recovery_system.error_history.append(recent_error)

        # Cleanup old data (keep 7 days)
        self.recovery_system.cleanup_old_data(days=7)

        # Check that only recent error remains
        self.assertEqual(len(self.recovery_system.error_history), 1)
        self.assertEqual(self.recovery_system.error_history[0].error_id, "recent_error")


class TestErrorRecoveryIntegration(unittest.IsolatedAsyncioTestCase):
    """Test cases for async error recovery functionality."""

    async def asyncSetUp(self):
        """Set up async test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.recovery_system = ErrorRecoverySystem(data_dir=self.temp_dir, max_queue_size=10)

    async def asyncTearDown(self):
        """Clean up async test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    async def test_process_recovery_queue_success(self):
        """Test successful processing of recovery queue."""
        # Register a mock retry function
        mock_function = AsyncMock(return_value="success")
        self.recovery_system.register_retry_function("test_function", mock_function)

        # Queue a failed operation
        error_info = ErrorInfo(
            error_id="test_error",
            error_type=ErrorType.TRANSCRIPTION,
            severity=ErrorSeverity.MEDIUM,
            message="Test error",
            user_message="Test failed",
            timestamp=datetime.now(),
            context={},
            retry_count=0,
            max_retries=3
        )

        self.recovery_system.queue_failed_operation(
            function_name="test_function",
            args=["arg1"],
            kwargs={"key": "value"},
            error_info=error_info
        )

        # Set next_retry to now so it's ready for processing
        self.recovery_system.recovery_queue[0].next_retry = datetime.now()

        # Process the queue
        result = await self.recovery_system.process_recovery_queue()

        # Check results
        self.assertEqual(result['processed'], 1)
        self.assertEqual(result['succeeded'], 1)
        self.assertEqual(result['failed'], 0)
        self.assertEqual(len(self.recovery_system.recovery_queue), 0)

        # Check that function was called
        mock_function.assert_called_once_with("arg1", key="value")

    async def test_process_recovery_queue_failure(self):
        """Test handling of continued failures in recovery queue."""
        # Register a mock retry function that fails
        mock_function = AsyncMock(side_effect=ValueError("Still failing"))
        self.recovery_system.register_retry_function("test_function", mock_function)

        # Queue a failed operation
        error_info = ErrorInfo(
            error_id="test_error",
            error_type=ErrorType.TRANSCRIPTION,
            severity=ErrorSeverity.MEDIUM,
            message="Test error",
            user_message="Test failed",
            timestamp=datetime.now(),
            context={},
            retry_count=0,
            max_retries=1  # Low max retries for testing
        )

        self.recovery_system.queue_failed_operation(
            function_name="test_function",
            args=["arg1"],
            kwargs={"key": "value"},
            error_info=error_info
        )

        # Set next_retry to now so it's ready for processing
        self.recovery_system.recovery_queue[0].next_retry = datetime.now()

        # Process the queue multiple times to exceed max retries
        await self.recovery_system.process_recovery_queue()  # First failure

        # Set next_retry again for second attempt
        if self.recovery_system.recovery_queue:
            self.recovery_system.recovery_queue[0].next_retry = datetime.now()
            await self.recovery_system.process_recovery_queue()  # Second failure, should remove from queue

        # Check that operation was removed after exceeding max retries
        self.assertEqual(len(self.recovery_system.recovery_queue), 0)

    async def test_with_error_recovery_decorator(self):
        """Test the error recovery decorator."""
        # Create a function that fails then succeeds
        call_count = 0

        @with_error_recovery(
            error_type=ErrorType.TRANSCRIPTION,
            severity=ErrorSeverity.MEDIUM,
            recovery_system=self.recovery_system
        )
        async def failing_function(arg):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("First call fails")
            return f"Success with {arg}"

        # Test that exception is still raised but logged
        with self.assertRaises(ValueError):
            await failing_function("test")

        # Check that error was logged
        self.assertEqual(len(self.recovery_system.error_history), 1)

        # Check that operation was queued
        self.assertEqual(len(self.recovery_system.recovery_queue), 1)

    def test_error_info_serialization(self):
        """Test ErrorInfo serialization and deserialization."""
        error_info = ErrorInfo(
            error_id="test_error",
            error_type=ErrorType.TRANSCRIPTION,
            severity=ErrorSeverity.HIGH,
            message="Test error message",
            user_message="User friendly message",
            timestamp=datetime.now(),
            context={"key": "value"},
            recovery_action=RecoveryAction.RETRY,
            retry_count=2,
            max_retries=3,
            resolved=False
        )

        # Test to_dict
        data = error_info.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['error_type'], 'transcription')
        self.assertEqual(data['severity'], 'high')
        self.assertEqual(data['recovery_action'], 'retry')

        # Test from_dict
        restored_error = ErrorInfo.from_dict(data)
        self.assertEqual(restored_error.error_id, error_info.error_id)
        self.assertEqual(restored_error.error_type, error_info.error_type)
        self.assertEqual(restored_error.severity, error_info.severity)
        self.assertEqual(restored_error.recovery_action, error_info.recovery_action)

    def test_failed_operation_serialization(self):
        """Test FailedOperation serialization and deserialization."""
        error_info = ErrorInfo(
            error_id="test_error",
            error_type=ErrorType.MCP_CONNECTION,
            severity=ErrorSeverity.MEDIUM,
            message="Connection failed",
            user_message="Could not connect",
            timestamp=datetime.now(),
            context={}
        )

        failed_op = FailedOperation(
            operation_id="test_op",
            function_name="connect_to_server",
            args=["server_url"],
            kwargs={"timeout": 30},
            error_info=error_info,
            next_retry=datetime.now() + timedelta(minutes=1)
        )

        # Test to_dict
        data = failed_op.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['function_name'], 'connect_to_server')
        self.assertEqual(data['args'], ["server_url"])
        self.assertEqual(data['kwargs'], {"timeout": 30})

        # Test from_dict
        restored_op = FailedOperation.from_dict(data)
        self.assertEqual(restored_op.operation_id, failed_op.operation_id)
        self.assertEqual(restored_op.function_name, failed_op.function_name)
        self.assertEqual(restored_op.args, failed_op.args)
        self.assertEqual(restored_op.kwargs, failed_op.kwargs)


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.DEBUG)

    # Run tests
    unittest.main()