"""
Error Recovery System for Voice Notes.

Provides comprehensive error handling and recovery mechanisms including:
- Queue for failed processing operations
- Automatic retry with exponential backoff
- Graceful degradation
- Detailed error logging with debugging info
- User-friendly error messages
"""

import os
import json
import time
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import hashlib
from functools import wraps


logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of errors that can occur in the voice notes system."""
    AUDIO_RECORDING = "audio_recording"
    TRANSCRIPTION = "transcription"
    MCP_CONNECTION = "mcp_connection"
    CONVERSATION = "conversation"
    FILE_SAVE = "file_save"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryAction(Enum):
    """Available recovery actions."""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ABORT = "abort"
    MANUAL = "manual"


@dataclass
class ErrorInfo:
    """Detailed information about an error occurrence."""
    error_id: str
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    user_message: str
    timestamp: datetime
    context: Dict[str, Any]
    stack_trace: Optional[str] = None
    recovery_action: Optional[RecoveryAction] = None
    retry_count: int = 0
    max_retries: int = 3
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['error_type'] = self.error_type.value
        data['severity'] = self.severity.value
        data['recovery_action'] = self.recovery_action.value if self.recovery_action else None
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorInfo':
        """Create from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['error_type'] = ErrorType(data['error_type'])
        data['severity'] = ErrorSeverity(data['severity'])
        if data['recovery_action']:
            data['recovery_action'] = RecoveryAction(data['recovery_action'])
        return cls(**data)


@dataclass
class FailedOperation:
    """Information about a failed operation that can be retried."""
    operation_id: str
    function_name: str
    args: List[Any]
    kwargs: Dict[str, Any]
    error_info: ErrorInfo
    next_retry: datetime
    original_data: Optional[bytes] = None  # Serialized original data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'operation_id': self.operation_id,
            'function_name': self.function_name,
            'args': self.args,
            'kwargs': self.kwargs,
            'error_info': self.error_info.to_dict(),
            'next_retry': self.next_retry.isoformat(),
            'original_data': self.original_data.decode('utf-8') if self.original_data else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FailedOperation':
        """Create from dictionary."""
        data['error_info'] = ErrorInfo.from_dict(data['error_info'])
        data['next_retry'] = datetime.fromisoformat(data['next_retry'])
        if data['original_data']:
            data['original_data'] = data['original_data'].encode('utf-8')
        return cls(**data)


class ErrorRecoverySystem:
    """Comprehensive error recovery system."""

    def __init__(self, data_dir: str = "logs", max_queue_size: int = 100):
        """Initialize the error recovery system.

        Args:
            data_dir: Directory to store error logs and recovery queue
            max_queue_size: Maximum number of failed operations to queue
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.max_queue_size = max_queue_size
        self.error_log_file = self.data_dir / "error_log.jsonl"
        self.recovery_queue_file = self.data_dir / "recovery_queue.json"

        # In-memory structures
        self.recovery_queue: List[FailedOperation] = []
        self.error_history: List[ErrorInfo] = []
        self.retry_functions: Dict[str, Callable] = {}

        # Recovery settings
        self.max_retry_delay = 300  # 5 minutes maximum delay
        self.base_retry_delay = 1  # 1 second base delay
        self.backoff_multiplier = 2  # Exponential backoff

        # Load existing data
        self._load_recovery_queue()
        self._load_recent_errors()

        logger.info(f"ErrorRecoverySystem initialized with {len(self.recovery_queue)} queued operations")

    def _load_recovery_queue(self):
        """Load recovery queue from persistent storage."""
        try:
            if self.recovery_queue_file.exists():
                with open(self.recovery_queue_file, 'r') as f:
                    data = json.load(f)
                    self.recovery_queue = [FailedOperation.from_dict(op) for op in data]

                # Clean up expired operations
                now = datetime.now()
                self.recovery_queue = [op for op in self.recovery_queue if op.next_retry > now - timedelta(hours=24)]

                logger.info(f"Loaded {len(self.recovery_queue)} operations from recovery queue")
        except Exception as e:
            logger.warning(f"Could not load recovery queue: {e}")
            self.recovery_queue = []

    def _save_recovery_queue(self):
        """Save recovery queue to persistent storage."""
        try:
            data = [op.to_dict() for op in self.recovery_queue]
            with open(self.recovery_queue_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Could not save recovery queue: {e}")

    def _load_recent_errors(self):
        """Load recent errors from error log."""
        try:
            if self.error_log_file.exists():
                cutoff_time = datetime.now() - timedelta(hours=24)

                with open(self.error_log_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            try:
                                data = json.loads(line)
                                error_info = ErrorInfo.from_dict(data)
                                if error_info.timestamp > cutoff_time:
                                    self.error_history.append(error_info)
                            except Exception:
                                continue  # Skip malformed lines

                logger.info(f"Loaded {len(self.error_history)} recent errors")
        except Exception as e:
            logger.warning(f"Could not load error history: {e}")

    def log_error(self,
                  error: Exception,
                  error_type: ErrorType = ErrorType.UNKNOWN,
                  severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                  context: Dict[str, Any] = None,
                  user_message: str = None) -> str:
        """Log an error with full context information.

        Args:
            error: The exception that occurred
            error_type: Category of error
            severity: Severity level
            context: Additional context information
            user_message: User-friendly error message

        Returns:
            Error ID for tracking
        """
        import traceback

        # Generate unique error ID
        error_id = hashlib.md5(
            f"{error_type.value}{str(error)}{time.time()}".encode()
        ).hexdigest()[:12]

        # Generate user-friendly message if not provided
        if not user_message:
            user_message = self._generate_user_message(error, error_type)

        # Create error info
        error_info = ErrorInfo(
            error_id=error_id,
            error_type=error_type,
            severity=severity,
            message=str(error),
            user_message=user_message,
            timestamp=datetime.now(),
            context=context or {},
            stack_trace=traceback.format_exc()
        )

        # Add to history
        self.error_history.append(error_info)

        # Log to file
        self._append_error_to_log(error_info)

        logger.error(f"Error logged [{error_id}]: {error}")

        return error_id

    def _append_error_to_log(self, error_info: ErrorInfo):
        """Append error to persistent log file."""
        try:
            with open(self.error_log_file, 'a') as f:
                f.write(json.dumps(error_info.to_dict(), default=str) + '\n')
        except Exception as e:
            logger.error(f"Could not write to error log: {e}")

    def _generate_user_message(self, error: Exception, error_type: ErrorType) -> str:
        """Generate user-friendly error message."""
        error_str = str(error).lower()

        messages = {
            ErrorType.AUDIO_RECORDING: {
                'default': 'Failed to record audio. Please check your microphone.',
                'device': 'Audio device not available. Please check your microphone connection.',
                'permission': 'Microphone access denied. Please enable microphone permissions.',
            },
            ErrorType.TRANSCRIPTION: {
                'default': 'Failed to transcribe audio. Please try again.',
                'api': 'Transcription service unavailable. Using fallback method.',
                'cost': 'Daily transcription limit reached. Please try again tomorrow.',
                'network': 'Network connection issue. Retrying transcription...'
            },
            ErrorType.MCP_CONNECTION: {
                'default': 'Failed to connect to conversation service.',
                'timeout': 'Conversation service timed out. Please try again.',
                'auth': 'Authentication failed. Please check your configuration.'
            },
            ErrorType.FILE_SAVE: {
                'default': 'Failed to save voice note. Please check file permissions.',
                'disk': 'Not enough disk space. Please free up space and try again.',
                'permission': 'Permission denied. Please check folder permissions.'
            },
            ErrorType.NETWORK: {
                'default': 'Network connection issue. Please check your internet connection.',
                'timeout': 'Request timed out. Please try again.',
                'dns': 'DNS resolution failed. Please check your network settings.'
            }
        }

        category_messages = messages.get(error_type, {})

        # Try to match specific error patterns
        for key, message in category_messages.items():
            if key != 'default' and key in error_str:
                return message

        return category_messages.get('default', f'An error occurred: {str(error)}')

    def queue_failed_operation(self,
                              function_name: str,
                              args: List[Any] = None,
                              kwargs: Dict[str, Any] = None,
                              error_info: ErrorInfo = None,
                              original_data: Any = None) -> str:
        """Queue a failed operation for retry.

        Args:
            function_name: Name of the function that failed
            args: Function arguments
            kwargs: Function keyword arguments
            error_info: Associated error information
            original_data: Original data to preserve

        Returns:
            Operation ID for tracking
        """
        if len(self.recovery_queue) >= self.max_queue_size:
            logger.warning("Recovery queue is full, removing oldest operation")
            self.recovery_queue.pop(0)

        operation_id = hashlib.md5(
            f"{function_name}{time.time()}".encode()
        ).hexdigest()[:12]

        # Calculate next retry time
        retry_count = error_info.retry_count if error_info else 0
        delay = min(
            self.base_retry_delay * (self.backoff_multiplier ** retry_count),
            self.max_retry_delay
        )
        next_retry = datetime.now() + timedelta(seconds=delay)

        # Serialize original data if provided
        serialized_data = None
        if original_data is not None:
            try:
                serialized_data = pickle.dumps(original_data)
            except Exception as e:
                logger.warning(f"Could not serialize original data: {e}")

        # Create failed operation
        failed_op = FailedOperation(
            operation_id=operation_id,
            function_name=function_name,
            args=args or [],
            kwargs=kwargs or {},
            error_info=error_info,
            next_retry=next_retry,
            original_data=serialized_data
        )

        self.recovery_queue.append(failed_op)
        self._save_recovery_queue()

        logger.info(f"Queued failed operation [{operation_id}] for retry at {next_retry}")

        return operation_id

    def register_retry_function(self, function_name: str, function: Callable):
        """Register a function that can be retried.

        Args:
            function_name: Name to identify the function
            function: The actual function to retry
        """
        self.retry_functions[function_name] = function
        logger.debug(f"Registered retry function: {function_name}")

    async def process_recovery_queue(self) -> Dict[str, Any]:
        """Process all items in the recovery queue that are ready for retry.

        Returns:
            Summary of processing results
        """
        now = datetime.now()
        ready_operations = [op for op in self.recovery_queue if op.next_retry <= now]

        if not ready_operations:
            return {'processed': 0, 'succeeded': 0, 'failed': 0, 'deferred': 0}

        logger.info(f"Processing {len(ready_operations)} ready operations from recovery queue")

        succeeded = 0
        failed = 0
        deferred = 0

        for operation in ready_operations:
            try:
                result = await self._retry_operation(operation)
                if result:
                    succeeded += 1
                    self.recovery_queue.remove(operation)
                    if operation.error_info:
                        operation.error_info.resolved = True
                else:
                    # Operation still failing, check if we should keep retrying
                    if operation.error_info and operation.error_info.retry_count >= operation.error_info.max_retries:
                        failed += 1
                        self.recovery_queue.remove(operation)
                        logger.warning(f"Operation {operation.operation_id} exceeded max retries, removing from queue")
                    else:
                        deferred += 1
                        # Update retry time and count
                        if operation.error_info:
                            operation.error_info.retry_count += 1
                        retry_count = operation.error_info.retry_count if operation.error_info else 1
                        delay = min(
                            self.base_retry_delay * (self.backoff_multiplier ** retry_count),
                            self.max_retry_delay
                        )
                        operation.next_retry = datetime.now() + timedelta(seconds=delay)

            except Exception as e:
                logger.error(f"Error processing operation {operation.operation_id}: {e}")
                failed += 1
                self.recovery_queue.remove(operation)

        # Save updated queue
        self._save_recovery_queue()

        result = {
            'processed': len(ready_operations),
            'succeeded': succeeded,
            'failed': failed,
            'deferred': deferred
        }

        logger.info(f"Recovery queue processing complete: {result}")
        return result

    async def _retry_operation(self, operation: FailedOperation) -> bool:
        """Retry a failed operation.

        Args:
            operation: The failed operation to retry

        Returns:
            True if successful, False if still failing
        """
        function_name = operation.function_name

        if function_name not in self.retry_functions:
            logger.error(f"Retry function '{function_name}' not registered")
            return False

        function = self.retry_functions[function_name]

        try:
            # Deserialize original data if available
            original_data = None
            if operation.original_data:
                try:
                    original_data = pickle.loads(operation.original_data)
                except Exception as e:
                    logger.warning(f"Could not deserialize original data: {e}")

            # Add original data to kwargs if available
            if original_data:
                operation.kwargs['_original_data'] = original_data

            # Call the function
            if asyncio.iscoroutinefunction(function):
                await function(*operation.args, **operation.kwargs)
            else:
                function(*operation.args, **operation.kwargs)

            logger.info(f"Successfully retried operation {operation.operation_id}")
            return True

        except Exception as e:
            logger.warning(f"Retry of operation {operation.operation_id} failed: {e}")
            # Log the retry failure
            self.log_error(
                error=e,
                error_type=operation.error_info.error_type if operation.error_info else ErrorType.UNKNOWN,
                severity=ErrorSeverity.MEDIUM,
                context={'operation_id': operation.operation_id, 'retry_count': operation.error_info.retry_count if operation.error_info else 0},
                user_message=f"Retry attempt failed: {self._generate_user_message(e, operation.error_info.error_type if operation.error_info else ErrorType.UNKNOWN)}"
            )
            return False

    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of errors in the specified time period.

        Args:
            hours: Time period in hours to analyze

        Returns:
            Error summary statistics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [err for err in self.error_history if err.timestamp > cutoff_time]

        if not recent_errors:
            return {
                'total_errors': 0,
                'period_hours': hours,
                'by_type': {},
                'by_severity': {},
                'resolution_rate': 0.0
            }

        # Group by type
        by_type = {}
        for error in recent_errors:
            error_type = error.error_type.value
            by_type[error_type] = by_type.get(error_type, 0) + 1

        # Group by severity
        by_severity = {}
        for error in recent_errors:
            severity = error.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1

        # Calculate resolution rate
        resolved_count = sum(1 for err in recent_errors if err.resolved)
        resolution_rate = resolved_count / len(recent_errors) if recent_errors else 0.0

        return {
            'total_errors': len(recent_errors),
            'period_hours': hours,
            'by_type': by_type,
            'by_severity': by_severity,
            'resolution_rate': round(resolution_rate * 100, 1),
            'queue_size': len(self.recovery_queue)
        }

    def get_recovery_status(self) -> Dict[str, Any]:
        """Get current status of the recovery system."""
        now = datetime.now()
        ready_count = sum(1 for op in self.recovery_queue if op.next_retry <= now)

        return {
            'queue_size': len(self.recovery_queue),
            'ready_for_retry': ready_count,
            'next_retry': min([op.next_retry for op in self.recovery_queue]) if self.recovery_queue else None,
            'recent_errors': len(self.error_history),
            'uptime_hours': (now - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() / 3600
        }

    def cleanup_old_data(self, days: int = 7):
        """Clean up old error logs and recovery queue items.

        Args:
            days: Number of days of data to keep
        """
        cutoff_time = datetime.now() - timedelta(days=days)

        # Clean error history
        original_count = len(self.error_history)
        self.error_history = [err for err in self.error_history if err.timestamp > cutoff_time]

        # Clean recovery queue
        original_queue_size = len(self.recovery_queue)
        self.recovery_queue = [op for op in self.recovery_queue if op.next_retry > cutoff_time]

        # Save updated queue
        self._save_recovery_queue()

        logger.info(f"Cleanup complete: removed {original_count - len(self.error_history)} old errors, "
                   f"{original_queue_size - len(self.recovery_queue)} old queue items")


def with_error_recovery(error_type: ErrorType = ErrorType.UNKNOWN,
                       severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                       recovery_system: ErrorRecoverySystem = None,
                       queue_on_failure: bool = True):
    """Decorator to add automatic error recovery to functions.

    Args:
        error_type: Type of error this function might produce
        severity: Default severity level for errors
        recovery_system: Recovery system instance to use
        queue_on_failure: Whether to queue failed operations for retry
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if recovery_system:
                    error_id = recovery_system.log_error(
                        error=e,
                        error_type=error_type,
                        severity=severity,
                        context={'function': func.__name__, 'args_count': len(args), 'kwargs_keys': list(kwargs.keys())}
                    )

                    if queue_on_failure:
                        recovery_system.queue_failed_operation(
                            function_name=func.__name__,
                            args=list(args),
                            kwargs=kwargs,
                            error_info=recovery_system.error_history[-1]  # Last logged error
                        )

                raise  # Re-raise the exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if recovery_system:
                    error_id = recovery_system.log_error(
                        error=e,
                        error_type=error_type,
                        severity=severity,
                        context={'function': func.__name__, 'args_count': len(args), 'kwargs_keys': list(kwargs.keys())}
                    )

                    if queue_on_failure:
                        recovery_system.queue_failed_operation(
                            function_name=func.__name__,
                            args=list(args),
                            kwargs=kwargs,
                            error_info=recovery_system.error_history[-1]  # Last logged error
                        )

                raise  # Re-raise the exception

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator