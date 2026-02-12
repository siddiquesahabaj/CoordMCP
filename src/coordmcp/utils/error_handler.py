"""
Enhanced error handling utilities for CoordMCP.

This module provides robust error handling mechanisms including:
- Retry mechanisms for transient failures
- Error categorization and recovery suggestions
- Secure error message generation
- Exception context preservation
"""

import functools
import logging
import time
from typing import Callable, TypeVar, Optional, List, Dict, Any, Union
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ErrorCategory(Enum):
    """Categories of errors for appropriate handling strategies."""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    RATE_LIMIT = "rate_limit"
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    INTERNAL = "internal"
    TIMEOUT = "timeout"


class ErrorInfo:
    """Structured error information for API responses."""
    
    def __init__(
        self,
        message: str,
        error_type: str,
        category: ErrorCategory,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
        retryable: bool = False
    ):
        self.message = message
        self.error_type = error_type
        self.category = category
        self.details = details or {}
        self.suggestions = suggestions or []
        self.retryable = retryable
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "success": False,
            "error": self.message,
            "error_type": self.error_type,
            "category": self.category.value,
            "details": self.details if self.details else None,
            "suggestions": self.suggestions if self.suggestions else None,
            "retryable": self.retryable
        }


def with_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
) -> Callable:
    """
    Decorator that implements retry logic with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback function called on each retry
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    
                    if on_retry:
                        try:
                            on_retry(attempt, e, current_delay)
                        except Exception as callback_error:
                            logger.error(f"Retry callback error: {callback_error}")
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


def handle_errors(
    error_type: str = "InternalError",
    category: ErrorCategory = ErrorCategory.INTERNAL,
    log_level: int = logging.ERROR,
    include_traceback: bool = False,
    suggestions: Optional[List[str]] = None
) -> Callable:
    """
    Decorator that provides standardized error handling.
    
    Args:
        error_type: Type identifier for the error
        category: Error category for handling strategy
        log_level: Logging level for errors
        include_traceback: Whether to include traceback in error details
        suggestions: List of recovery suggestions
        
    Returns:
        Decorated function with error handling
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Union[T, Dict[str, Any]]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Union[T, Dict[str, Any]]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the error
                error_msg = f"Error in {func.__name__}: {type(e).__name__}"
                if log_level == logging.DEBUG:
                    logger.debug(error_msg, exc_info=include_traceback)
                elif log_level == logging.INFO:
                    logger.info(error_msg, exc_info=include_traceback)
                elif log_level == logging.WARNING:
                    logger.warning(error_msg, exc_info=include_traceback)
                else:
                    logger.error(error_msg, exc_info=include_traceback)
                
                # Create error info
                error_info = ErrorInfo(
                    message=str(e) if isinstance(e, (ValueError, TypeError)) else "An error occurred",
                    error_type=error_type,
                    category=category,
                    suggestions=suggestions,
                    retryable=category in [ErrorCategory.TRANSIENT, ErrorCategory.TIMEOUT]
                )
                
                # Return error response
                return error_info.to_dict()
        
        return wrapper
    return decorator


def safe_execute(
    func: Callable[..., T],
    *args,
    default: Optional[T] = None,
    error_msg: str = "Operation failed",
    **kwargs
) -> Optional[T]:
    """
    Safely execute a function, returning default on failure.
    
    Args:
        func: Function to execute
        args: Positional arguments
        default: Default value to return on failure
        error_msg: Error message to log on failure
        kwargs: Keyword arguments
        
    Returns:
        Function result or default value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"{error_msg}: {type(e).__name__}")
        return default


def categorize_exception(exc: Exception) -> ErrorCategory:
    """
    Categorize an exception for appropriate handling.
    
    Args:
        exc: Exception to categorize
        
    Returns:
        Error category
    """
    from coordmcp.errors import (
        ProjectNotFoundError, AgentNotFoundError, FileLockError,
        DataValidationError, ConflictError, StorageError
    )
    
    if isinstance(exc, (ProjectNotFoundError, AgentNotFoundError)):
        return ErrorCategory.NOT_FOUND
    elif isinstance(exc, DataValidationError):
        return ErrorCategory.VALIDATION
    elif isinstance(exc, FileLockError):
        return ErrorCategory.CONFLICT
    elif isinstance(exc, ConflictError):
        return ErrorCategory.CONFLICT
    elif isinstance(exc, StorageError):
        return ErrorCategory.TRANSIENT
    elif isinstance(exc, (TimeoutError,)):
        return ErrorCategory.TIMEOUT
    elif isinstance(exc, (PermissionError,)):
        return ErrorCategory.AUTHORIZATION
    elif isinstance(exc, (ValueError, TypeError)):
        return ErrorCategory.VALIDATION
    else:
        return ErrorCategory.INTERNAL


def get_error_suggestions(category: ErrorCategory, context: Optional[Dict] = None) -> List[str]:
    """
    Get recovery suggestions based on error category.
    
    Args:
        category: Error category
        context: Optional context for more specific suggestions
        
    Returns:
        List of suggestions
    """
    suggestions_map = {
        ErrorCategory.VALIDATION: [
            "Check that all required fields are provided and valid",
            "Verify data types match expected format",
            "Review the API documentation for correct parameter usage"
        ],
        ErrorCategory.NOT_FOUND: [
            "Verify the ID is correct and the resource exists",
            "Check if the resource has been deleted",
            "Ensure you have the correct project/agent ID"
        ],
        ErrorCategory.CONFLICT: [
            "Wait for the current operation to complete",
            "Coordinate with other agents to avoid conflicts",
            "Check file lock status before attempting operation"
        ],
        ErrorCategory.TRANSIENT: [
            "Retry the operation after a brief delay",
            "Check system status and resource availability",
            "Contact support if the issue persists"
        ],
        ErrorCategory.TIMEOUT: [
            "Retry the operation",
            "Check network connectivity",
            "Consider breaking the operation into smaller chunks"
        ],
        ErrorCategory.INTERNAL: [
            "Try the operation again",
            "Check system logs for more details",
            "Contact support if the issue persists"
        ]
    }
    
    return suggestions_map.get(category, ["Contact support for assistance"])


class SecureErrorHandler:
    """
    Handler for generating secure error messages that don't leak sensitive info.
    """
    
    # Patterns that might indicate sensitive information
    SENSITIVE_PATTERNS = [
        r'password[=:]\s*\S+',
        r'token[=:]\s*\S+',
        r'secret[=:]\s*\S+',
        r'key[=:]\s*\S+',
        r'api[_-]?key[=:]\s*\S+',
        r'auth[=:]\s*\S+',
        r'credential[=:]\s*\S+',
    ]
    
    @classmethod
    def sanitize_message(cls, message: str) -> str:
        """
        Remove potentially sensitive information from error messages.
        
        Args:
            message: Original error message
            
        Returns:
            Sanitized message
        """
        import re
        
        sanitized = message
        for pattern in cls.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    @classmethod
    def create_safe_error(
        cls,
        message: str,
        error_type: str = "Error",
        log_full_error: bool = True
    ) -> Dict[str, Any]:
        """
        Create a safe error response that doesn't leak sensitive data.
        
        Args:
            message: Error message (will be sanitized for user display)
            error_type: Type of error
            log_full_error: Whether to log the full error internally
            
        Returns:
            Safe error response dictionary
        """
        # Log full error for debugging (internal only)
        if log_full_error:
            logger.error(f"[{error_type}] {message}")
        
        # Return sanitized version to user
        safe_message = cls.sanitize_message(message)
        
        return {
            "success": False,
            "error": safe_message,
            "error_type": error_type
        }


# Common validation helpers
def validate_uuid(value: str, field_name: str = "id") -> Optional[str]:
    """
    Validate UUID format.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Error message if invalid, None if valid
    """
    import re
    
    if not value or not isinstance(value, str):
        return f"{field_name} is required and must be a string"
    
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    
    if not uuid_pattern.match(value):
        return f"{field_name} must be a valid UUID format"
    
    return None


def validate_required(value: Any, field_name: str) -> Optional[str]:
    """
    Validate that a required field is present and not empty.
    
    Args:
        value: Value to validate
        field_name: Name of the field
        
    Returns:
        Error message if invalid, None if valid
    """
    if value is None:
        return f"{field_name} is required"
    
    if isinstance(value, str) and not value.strip():
        return f"{field_name} cannot be empty"
    
    if isinstance(value, list) and len(value) == 0:
        return f"{field_name} cannot be empty"
    
    return None


def validate_string_length(
    value: str,
    field_name: str,
    min_length: int = 1,
    max_length: int = 1000
) -> Optional[str]:
    """
    Validate string length.
    
    Args:
        value: String to validate
        field_name: Name of the field
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        Error message if invalid, None if valid
    """
    if not isinstance(value, str):
        return f"{field_name} must be a string"
    
    if len(value) < min_length:
        return f"{field_name} must be at least {min_length} characters"
    
    if len(value) > max_length:
        return f"{field_name} must be no more than {max_length} characters"
    
    return None


def validate_enum_value(
    value: str,
    field_name: str,
    allowed_values: List[str]
) -> Optional[str]:
    """
    Validate that a value is in the allowed enum values.
    
    Args:
        value: Value to validate
        field_name: Name of the field
        allowed_values: List of allowed values
        
    Returns:
        Error message if invalid, None if valid
    """
    if value not in allowed_values:
        return f"{field_name} must be one of: {', '.join(allowed_values)}"
    
    return None


def validate_file_path(value: str, field_name: str = "file_path") -> Optional[str]:
    """
    Validate file path to prevent directory traversal.
    
    Args:
        value: File path to validate
        field_name: Name of the field
        
    Returns:
        Error message if invalid, None if valid
    """
    if not isinstance(value, str):
        return f"{field_name} must be a string"
    
    # Check for path traversal attempts
    if ".." in value:
        return f"{field_name} contains invalid path traversal characters"
    
    # Check for absolute paths
    if value.startswith("/") or value.startswith("\\"):
        return f"{field_name} must be a relative path"
    
    # Check for null bytes
    if "\x00" in value:
        return f"{field_name} contains invalid characters"
    
    return None
