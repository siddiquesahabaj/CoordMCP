"""
Input validation decorators for CoordMCP tools.

This module provides decorators for validating tool inputs before execution.
"""

from functools import wraps
from typing import Callable, Any, List, Optional
from coordmcp.logger import get_logger
from coordmcp.errors import DataValidationError

logger = get_logger("validation")


def validate_required_fields(*required_fields: str):
    """
    Decorator to validate that required fields are present and not empty.
    
    Args:
        *required_fields: Names of required fields
        
    Example:
        @validate_required_fields("project_id", "title", "description")
        async def save_decision(project_id: str, title: str, description: str, ...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check kwargs for required fields
            for field in required_fields:
                value = kwargs.get(field)
                if value is None or (isinstance(value, str) and not value.strip()):
                    error_msg = f"Required field '{field}' is missing or empty"
                    logger.warning(f"Validation failed: {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "error_type": "ValidationError",
                        "suggestions": [f"Provide a valid value for '{field}'"]
                    }
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_project_id(func: Callable) -> Callable:
    """
    Decorator to validate project_id format.
    
    Validates that project_id is a valid UUID string.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        project_id = kwargs.get("project_id") or (args[0] if args else None)
        
        if project_id:
            # Basic UUID format validation
            import re
            uuid_pattern = re.compile(
                r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
                re.IGNORECASE
            )
            if not uuid_pattern.match(str(project_id)):
                logger.warning(f"Invalid project_id format: {project_id}")
                return {
                    "success": False,
                    "error": f"Invalid project_id format: {project_id}",
                    "error_type": "ValidationError",
                    "suggestions": ["Project ID should be a valid UUID (e.g., '550e8400-e29b-41d4-a716-446655440000')"]
                }
        
        return await func(*args, **kwargs)
    
    return wrapper


def validate_agent_id(func: Callable) -> Callable:
    """
    Decorator to validate agent_id format.
    
    Validates that agent_id is a valid UUID string.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        agent_id = kwargs.get("agent_id") or (args[0] if args else None)
        
        if agent_id:
            import re
            uuid_pattern = re.compile(
                r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
                re.IGNORECASE
            )
            if not uuid_pattern.match(str(agent_id)):
                logger.warning(f"Invalid agent_id format: {agent_id}")
                return {
                    "success": False,
                    "error": f"Invalid agent_id format: {agent_id}",
                    "error_type": "ValidationError",
                    "suggestions": ["Agent ID should be a valid UUID"]
                }
        
        return await func(*args, **kwargs)
    
    return wrapper


def validate_enum_field(field_name: str, allowed_values: List[str]):
    """
    Decorator to validate that a field has one of the allowed values.
    
    Args:
        field_name: Name of the field to validate
        allowed_values: List of allowed values
        
    Example:
        @validate_enum_field("status", ["active", "archived", "all"])
        async def get_project_decisions(project_id: str, status: str = "all"):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            value = kwargs.get(field_name)
            
            if value is not None and value not in allowed_values:
                error_msg = f"Invalid value for '{field_name}': {value}"
                logger.warning(f"Validation failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "error_type": "ValidationError",
                    "suggestions": [f"Allowed values: {', '.join(allowed_values)}"]
                }
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_file_path(field_name: str = "file_path"):
    """
    Decorator to validate file path format.
    
    Args:
        field_name: Name of the file path field
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            file_path = kwargs.get(field_name)
            
            if file_path:
                # Check for path traversal attempts
                if ".." in str(file_path) or file_path.startswith("/"):
                    logger.warning(f"Invalid file path: {file_path}")
                    return {
                        "success": False,
                        "error": f"Invalid file path: {file_path}",
                        "error_type": "ValidationError",
                        "suggestions": ["Use relative paths (e.g., 'src/main.py')"]
                    }
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_length(field_name: str, min_length: int = 0, max_length: int = 1000):
    """
    Decorator to validate string length.
    
    Args:
        field_name: Name of the field to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            value = kwargs.get(field_name)
            
            if value is not None:
                str_value = str(value)
                if len(str_value) < min_length:
                    error_msg = f"'{field_name}' is too short (min {min_length} characters)"
                    return {
                        "success": False,
                        "error": error_msg,
                        "error_type": "ValidationError"
                    }
                if len(str_value) > max_length:
                    error_msg = f"'{field_name}' is too long (max {max_length} characters)"
                    return {
                        "success": False,
                        "error": error_msg,
                        "error_type": "ValidationError"
                    }
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Predefined validation sets for common use cases
validate_memory_tool = validate_required_fields("project_id")
validate_context_tool = validate_required_fields("agent_id", "project_id")
validate_architecture_tool = validate_required_fields("project_id")
