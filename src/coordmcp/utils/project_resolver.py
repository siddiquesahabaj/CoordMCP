"""
Project resolution utilities for flexible project lookup.

Provides functions to resolve projects by ID, name, or workspace path.
"""

import os
from pathlib import Path
from typing import Optional, Tuple, List
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.memory.models import ProjectInfo
from coordmcp.logger import get_logger

logger = get_logger("utils.project_resolver")


def normalize_path(path: str) -> str:
    """
    Normalize a path to absolute, resolved form.
    
    Args:
        path: Input path string
        
    Returns:
        Normalized absolute path
    """
    return os.path.normpath(os.path.abspath(path))


def paths_equal(path1: str, path2: str) -> bool:
    """
    Compare two paths for equality, handling Windows case-insensitivity.
    
    On Windows, drive letters and paths are case-insensitive, so this function
    normalizes both paths and performs case-insensitive comparison.
    On Unix-like systems, paths remain case-sensitive.
    
    Args:
        path1: First path to compare
        path2: Second path to compare
        
    Returns:
        True if paths are equal, False otherwise
    """
    if not path1 or not path2:
        return False
    
    # Normalize both paths
    norm1 = normalize_path(path1)
    norm2 = normalize_path(path2)
    
    # On Windows, compare case-insensitively
    if os.name == 'nt':  # Windows
        norm1 = norm1.lower()
        norm2 = norm2.lower()
    
    return norm1 == norm2


def validate_workspace_path(path: str) -> Tuple[bool, str]:
    """
    Validate a workspace path for project creation.
    
    Args:
        path: Path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path:
        return False, "workspace_path is required"
    
    # Normalize
    normalized = normalize_path(path)
    
    # Check if absolute
    if not os.path.isabs(normalized):
        return False, f"workspace_path must be an absolute path, got: {path}"
    
    # Check if exists
    if not os.path.exists(normalized):
        return False, f"workspace_path does not exist: {normalized}"
    
    # Check if directory
    if not os.path.isdir(normalized):
        return False, f"workspace_path must be a directory: {normalized}"
    
    return True, ""


def resolve_project(
    memory_store: ProjectMemoryStore,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None
) -> Tuple[bool, Optional[ProjectInfo], str]:
    """
    Resolve a project by ID, name, or workspace path.
    
    Priority: project_id > workspace_path > project_name
    
    If multiple identifiers provided, validates they all point to the same project.
    
    Args:
        memory_store: Project memory store instance
        project_id: Optional project ID
        project_name: Optional project name
        workspace_path: Optional workspace path
        
    Returns:
        Tuple of (success, project_info, message)
    """
    if not any([project_id, project_name, workspace_path]):
        return False, None, "At least one of project_id, project_name, or workspace_path must be provided"
    
    found_projects = []
    
    # Try to find by project_id (highest priority)
    if project_id:
        project = memory_store.get_project_info(project_id)
        if project:
            found_projects.append(("project_id", project))
        else:
            return False, None, f"No project found with ID: {project_id}"
    
    # Try to find by workspace_path
    if workspace_path:
        normalized_path = normalize_path(workspace_path)
        all_projects = memory_store.list_projects()
        for proj in all_projects:
            if proj.workspace_path and paths_equal(proj.workspace_path, workspace_path):
                found_projects.append(("workspace_path", proj))
                break
    
    # Try to find by project_name
    if project_name:
        all_projects = memory_store.list_projects()
        matching = [p for p in all_projects if p.project_name.lower() == project_name.lower()]
        if len(matching) == 1:
            found_projects.append(("project_name", matching[0]))
        elif len(matching) > 1:
            # Multiple projects with same name
            ids = [p.project_id for p in matching]
            return False, None, f"Multiple projects found with name '{project_name}'. Use project_id to specify: {', '.join(ids)}"
    
    # Check if we found any project
    if not found_projects:
        return False, None, "No project found matching the provided criteria"
    
    # If multiple identifiers provided, verify they point to same project
    if len(found_projects) > 1:
        # Get unique project IDs
        unique_ids = set(p.project_id for _, p in found_projects)
        if len(unique_ids) > 1:
            # Different identifiers point to different projects
            details = [f"{source}: {proj.project_name} ({proj.project_id})" for source, proj in found_projects]
            return False, None, f"Provided identifiers point to different projects: {'; '.join(details)}"
    
    # Return the found project
    _, project = found_projects[0]
    return True, project, f"Found project: {project.project_name}"


def discover_project_by_path(
    memory_store: ProjectMemoryStore,
    path: Optional[str] = None,
    max_parent_levels: int = 3
) -> Tuple[bool, Optional[ProjectInfo], str, int]:
    """
    Discover a project by searching from a path.
    
    Searches for exact match first, then parent directories up to max_parent_levels.
    
    Args:
        memory_store: Project memory store instance
        path: Path to search from (defaults to current working directory)
        max_parent_levels: Maximum number of parent directories to search
        
    Returns:
        Tuple of (found, project_info, message, distance)
        distance: 0=exact, 1=parent, 2=grandparent, etc., -1=not found
    """
    if path is None:
        path = os.getcwd()
    
    normalized_start = normalize_path(path)
    
    # Check if the path itself is a workspace
    all_projects = memory_store.list_projects()
    
    for level in range(max_parent_levels + 1):
        current_path = normalized_start
        # Go up 'level' directories
        for _ in range(level):
            parent = os.path.dirname(current_path)
            if parent == current_path:  # Reached root
                break
            current_path = parent
        
        # Search for project with this path
        for project in all_projects:
            if project.workspace_path and paths_equal(project.workspace_path, current_path):
                if level == 0:
                    return True, project, f"Found exact match: {project.project_name}", 0
                else:
                    return True, project, f"Found parent project ({level} level{'s' if level > 1 else ''} up): {project.project_name}", level
    
    return False, None, f"No project found within {max_parent_levels} parent directories of {normalized_start}", -1


def get_projects_by_path(
    memory_store: ProjectMemoryStore,
    base_path: str,
    recursive: bool = True
) -> List[ProjectInfo]:
    """
    Get all projects under a base path.
    
    Args:
        memory_store: Project memory store instance
        base_path: Base directory to search
        recursive: If True, search recursively in subdirectories
        
    Returns:
        List of projects within the base path
    """
    normalized_base = normalize_path(base_path)
    all_projects = memory_store.list_projects()
    
    matching_projects = []
    
    for project in all_projects:
        if not project.workspace_path:
            continue
        
        normalized_project = normalize_path(project.workspace_path)
        
        if recursive:
            # Check if project path starts with base path
            if normalized_project.startswith(normalized_base + os.sep) or paths_equal(normalized_project, base_path):
                matching_projects.append(project)
        else:
            # Only direct children (same parent directory)
            project_parent = os.path.dirname(normalized_project)
            if paths_equal(project_parent, base_path):
                matching_projects.append(project)
    
    # Sort by name
    matching_projects.sort(key=lambda p: p.project_name)
    return matching_projects


def is_workspace_path_unique(
    memory_store: ProjectMemoryStore,
    workspace_path: str,
    exclude_project_id: Optional[str] = None
) -> bool:
    """
    Check if a workspace path is unique (not used by another project).
    
    Args:
        memory_store: Project memory store instance
        workspace_path: Path to check
        exclude_project_id: Optional project ID to exclude from check (for updates)
        
    Returns:
        True if path is unique, False otherwise
    """
    normalized_new = normalize_path(workspace_path)
    all_projects = memory_store.list_projects()
    
    for project in all_projects:
        if exclude_project_id and project.project_id == exclude_project_id:
            continue
        
        if project.workspace_path and paths_equal(project.workspace_path, workspace_path):
            return False
    
    return True
