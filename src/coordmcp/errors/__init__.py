"""
CoordMCP Exceptions Module

Centralized exception classes for error handling throughout CoordMCP.
"""

from typing import Optional


class CoordMCPError(Exception):
    """Base exception for all CoordMCP errors."""
    pass


class ProjectNotFoundError(CoordMCPError):
    """Raised when a project is not found."""
    
    def __init__(self, project_id: str, message: Optional[str] = None):
        self.project_id = project_id
        self.message = message or f"Project not found: {project_id}"
        super().__init__(self.message)


class AgentNotFoundError(CoordMCPError):
    """Raised when an agent is not found in the registry."""
    
    def __init__(self, agent_id: str, message: Optional[str] = None):
        self.agent_id = agent_id
        self.message = message or f"Agent not found: {agent_id}"
        super().__init__(self.message)


class FileLockError(CoordMCPError):
    """Raised when a file lock operation fails."""
    
    def __init__(self, file_path: str, locked_by: Optional[str] = None, message: Optional[str] = None, conflicts: Optional[list] = None):
        self.file_path = file_path
        self.locked_by = locked_by
        self.conflicts = conflicts or []
        
        if message:
            self.message = message
        elif locked_by:
            self.message = f"File '{file_path}' is locked by agent: {locked_by}"
        else:
            self.message = f"File lock error for: {file_path}"
        
        # Pass conflicts to super() so they appear in args
        super().__init__(self.message, self.conflicts)


class ContextError(CoordMCPError):
    """Raised when a context operation fails."""

    def __init__(self, agent_id: str, message: Optional[str] = None):
        self.agent_id = agent_id
        self.message = message or f"Context error for agent: {agent_id}"
        super().__init__(self.message)


class DataValidationError(CoordMCPError):
    """Raised when data validation fails."""

    def __init__(self, field: Optional[str] = None, message: Optional[str] = None):
        self.field = field
        if message:
            self.message = message
        elif field:
            self.message = f"Validation error for field: {field}"
        else:
            self.message = "Data validation error"
        super().__init__(self.message)


class DataCorruptionError(CoordMCPError):
    """Raised when data file corruption is detected."""

    def __init__(self, file_path: str, message: Optional[str] = None):
        self.file_path = file_path
        self.message = message or f"Data corruption detected in: {file_path}"
        super().__init__(self.message)


class StorageError(CoordMCPError):
    """Raised when a storage operation fails."""

    def __init__(self, operation: str, key: Optional[str] = None, message: Optional[str] = None):
        self.operation = operation
        self.key = key

        if message:
            self.message = message
        elif key:
            self.message = f"Storage error during {operation} for key: {key}"
        else:
            self.message = f"Storage error during {operation}"

        super().__init__(self.message)


class RecommendationError(CoordMCPError):
    """Raised when architecture recommendation fails."""

    def __init__(self, project_id: str, message: Optional[str] = None):
        self.project_id = project_id
        self.message = message or f"Recommendation error for project: {project_id}"
        super().__init__(self.message)


class ValidationError(CoordMCPError):
    """Raised when code structure validation fails."""

    def __init__(self, file_path: Optional[str] = None, message: Optional[str] = None):
        self.file_path = file_path

        if message:
            self.message = message
        elif file_path:
            self.message = f"Validation error for file: {file_path}"
        else:
            self.message = "Validation error"

        super().__init__(self.message)


class ConflictError(CoordMCPError):
    """Raised when a conflict is detected (e.g., concurrent modifications)."""

    def __init__(self, resource: str, message: Optional[str] = None):
        self.resource = resource
        self.message = message or f"Conflict detected for resource: {resource}"
        super().__init__(self.message)


class ConfigurationError(CoordMCPError):
    """Raised when there's a configuration error."""

    def __init__(self, setting: Optional[str] = None, message: Optional[str] = None):
        self.setting = setting

        if message:
            self.message = message
        elif setting:
            self.message = f"Configuration error for setting: {setting}"
        else:
            self.message = "Configuration error"

        super().__init__(self.message)


class NotImplementedError(CoordMCPError):
    """Raised when a feature is not yet implemented."""

    def __init__(self, feature: Optional[str] = None, message: Optional[str] = None):
        self.feature = feature

        if message:
            self.message = message
        elif feature:
            self.message = f"Feature not implemented: {feature}"
        else:
            self.message = "Feature not implemented"

        super().__init__(self.message)


# Export all exceptions
__all__ = [
    "CoordMCPError",
    "ProjectNotFoundError",
    "AgentNotFoundError",
    "FileLockError",
    "ContextError",
    "DataValidationError",
    "DataCorruptionError",
    "StorageError",
    "RecommendationError",
    "ValidationError",
    "ConflictError",
    "ConfigurationError",
    "NotImplementedError",
]
