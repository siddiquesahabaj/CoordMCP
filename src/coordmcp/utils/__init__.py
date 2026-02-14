"""
CoordMCP utilities package.

This package contains utility modules for validation, plugins, and helpers.
"""

from coordmcp.utils.validation import (
    validate_required_fields,
    validate_project_id,
    validate_agent_id,
    validate_enum_field,
    validate_file_path,
    validate_length,
    validate_memory_tool,
    validate_context_tool,
    validate_architecture_tool,
)

from coordmcp.utils.project_resolver import (
    resolve_project,
    discover_project_by_path,
    get_projects_by_path,
    is_workspace_path_unique,
    validate_workspace_path,
    normalize_path,
)

__all__ = [
    "validate_required_fields",
    "validate_project_id",
    "validate_agent_id",
    "validate_enum_field",
    "validate_file_path",
    "validate_length",
    "validate_memory_tool",
    "validate_context_tool",
    "validate_architecture_tool",
    "resolve_project",
    "discover_project_by_path",
    "get_projects_by_path",
    "is_workspace_path_unique",
    "validate_workspace_path",
    "normalize_path",
]
