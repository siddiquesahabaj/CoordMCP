"""
Discovery tools for CoordMCP.

Provides tools for discovering projects, agents, and workspace context.
"""

from typing import Dict, Any, Optional, List
from coordmcp.core.server import get_storage
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.context.manager import ContextManager
from coordmcp.context.file_tracker import FileTracker
from coordmcp.utils.project_resolver import (
    resolve_project,
    discover_project_by_path,
    get_projects_by_path,
    normalize_path
)
from coordmcp.logger import get_logger

logger = get_logger("tools.discovery")


def get_memory_store() -> ProjectMemoryStore:
    """Get or create the ProjectMemoryStore instance."""
    storage = get_storage()
    return ProjectMemoryStore(storage)


def get_context_manager() -> ContextManager:
    """Get or create the ContextManager instance."""
    storage = get_storage()
    file_tracker = FileTracker(storage)
    return ContextManager(storage, file_tracker)


async def discover_project(
    path: Optional[str] = None,
    max_parent_levels: int = 3
) -> Dict[str, Any]:
    """
    Discover a project by searching from a directory path.
    
    This tool searches for a CoordMCP project associated with the given directory.
    It first checks for an exact match, then searches up to 3 parent directories.
    
    Use Cases:
    - Starting work in a project directory and want to see if it's already tracked
    - Navigating to a subdirectory and finding the parent project
    - Auto-discovering projects when you don't know the project_id
    
    Args:
        path: Directory path to search from (defaults to current working directory)
        max_parent_levels: Maximum number of parent directories to search (default: 3)
        
    Returns:
        Dictionary with discovery results:
        {
            "success": True/False,
            "found": True/False,
            "project": {...} or None,
            "message": "Description of what was found",
            "distance": 0 for exact match, 1+ for parent directories, -1 if not found,
            "search_path": "The path that was searched"
        }
        
    Example:
        # Discover project in current directory
        result = await discover_project()
        
        # Discover from specific path
        result = await discover_project(path="/home/user/projects/myapp/src/components")
        
        # Result if found:
        {
            "success": True,
            "found": True,
            "project": {
                "project_id": "proj-abc-123",
                "project_name": "My App",
                "workspace_path": "/home/user/projects/myapp"
            },
            "message": "Found parent project (1 level up): My App",
            "distance": 1,
            "search_path": "/home/user/projects/myapp/src/components"
        }
    """
    try:
        memory_store = get_memory_store()
        
        found, project, message, distance = discover_project_by_path(
            memory_store=memory_store,
            path=path,
            max_parent_levels=max_parent_levels
        )
        
        if found:
            return {
                "success": True,
                "found": True,
                "project": {
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "description": project.description,
                    "workspace_path": project.workspace_path,
                    "created_at": project.created_at.isoformat() if project.created_at else None,
                    "updated_at": project.updated_at.isoformat() if project.updated_at else None
                },
                "message": message,
                "distance": distance,
                "search_path": normalize_path(path) if path else normalize_path(".")
            }
        else:
            return {
                "success": True,
                "found": False,
                "project": None,
                "message": message,
                "distance": -1,
                "search_path": normalize_path(path) if path else normalize_path(".")
            }
            
    except Exception as e:
        logger.error(f"Error discovering project: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "DiscoveryError"
        }


async def get_project(
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get project information by ID, name, or workspace path.
    
    This tool provides flexible project lookup. You can specify any combination
    of identifiers, and it will resolve to the matching project.
    
    Priority: project_id > workspace_path > project_name
    
    If multiple identifiers are provided, they must all point to the same project
    or an error is returned.
    
    Use Cases:
    - You know the project_id and want full details
    - You only know the project name
    - You have the workspace path and want to find the project
    - Validating that multiple identifiers point to the same project
    
    Args:
        project_id: Project ID (e.g., "proj-abc-123")
        project_name: Project name (e.g., "My App")
        workspace_path: Workspace directory path (e.g., "/home/user/projects/myapp")
        
    Returns:
        Dictionary with project details or error:
        {
            "success": True/False,
            "project": {...} or None,
            "message": "Success or error description"
        }
        
    Examples:
        # Get by ID
        await get_project(project_id="proj-abc-123")
        
        # Get by name
        await get_project(project_name="My App")
        
        # Get by path
        await get_project(workspace_path="/home/user/projects/myapp")
        
        # Validate multiple identifiers
        await get_project(
            project_id="proj-abc-123",
            project_name="My App"
        )
    """
    try:
        memory_store = get_memory_store()
        
        success, project, message = resolve_project(
            memory_store=memory_store,
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        
        if success:
            return {
                "success": True,
                "project": {
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "description": project.description,
                    "workspace_path": project.workspace_path,
                    "created_at": project.created_at.isoformat() if project.created_at else None,
                    "updated_at": project.updated_at.isoformat() if project.updated_at else None,
                    "created_by": project.created_by,
                    "version": project.version
                },
                "message": message
            }
        else:
            return {
                "success": False,
                "error": message,
                "error_type": "ProjectNotFoundError"
            }
            
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def list_projects(
    status: str = "active",
    workspace_base: Optional[str] = None,
    include_archived: bool = False
) -> Dict[str, Any]:
    """
    List all CoordMCP projects with optional filtering.
    
    This tool provides a comprehensive view of all projects in the system.
    Useful for browsing available projects before selecting one to work on.
    
    Use Cases:
    - See all projects in the system
    - Find projects under a specific directory
    - Check which projects are active vs archived
    
    Args:
        status: Filter by status - "active", "archived", or "all" (default: "active")
        workspace_base: Optional base directory to filter projects (e.g., "/home/user/projects")
        include_archived: Whether to include archived projects (default: False)
        
    Returns:
        Dictionary with project list:
        {
            "success": True/False,
            "projects": [
                {
                    "project_id": "...",
                    "project_name": "...",
                    "description": "...",
                    "workspace_path": "...",
                    "status": "active"
                }
            ],
            "total_count": 5
        }
        
    Examples:
        # List all active projects
        await list_projects()
        
        # List all projects including archived
        await list_projects(include_archived=True)
        
        # List projects under specific directory
        await list_projects(workspace_base="/home/user/projects")
    """
    try:
        memory_store = get_memory_store()
        
        # Get all projects
        projects = memory_store.list_projects()
        
        # Apply filters
        filtered_projects = []
        for project in projects:
            # Status filter
            if status != "all":
                # For now, all projects are considered active
                # TODO: Add status field to ProjectInfo model
                pass
            
            # Workspace base filter
            if workspace_base:
                if not project.workspace_path:
                    continue
                base_normalized = normalize_path(workspace_base)
                project_normalized = normalize_path(project.workspace_path)
                if not project_normalized.startswith(base_normalized):
                    continue
            
            filtered_projects.append(project)
        
        # Format response
        project_list = []
        for project in filtered_projects:
            project_list.append({
                "project_id": project.project_id,
                "project_name": project.project_name,
                "description": project.description,
                "workspace_path": project.workspace_path,
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "updated_at": project.updated_at.isoformat() if project.updated_at else None
            })
        
        return {
            "success": True,
            "projects": project_list,
            "total_count": len(project_list)
        }
        
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_active_agents(
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get information about active agents.
    
    This tool shows which agents are currently working, optionally filtered
    by a specific project. Useful for understanding team activity and
    coordinating with other agents.
    
    Use Cases:
    - See all active agents across all projects
    - Check who's working on a specific project before joining
    - Monitor team activity and coordination opportunities
    
    Args:
        project_id: Optional project ID to filter by
        project_name: Optional project name to filter by
        workspace_path: Optional workspace path to filter by
        
    Returns:
        Dictionary with agent information:
        {
            "success": True/False,
            "agents": [
                {
                    "agent_id": "...",
                    "agent_name": "OpenCode",
                    "agent_type": "opencode",
                    "current_project": "My App",
                    "current_objective": "Building authentication",
                    "last_active": "2024-01-20T14:30:00",
                    "locked_files_count": 2
                }
            ],
            "total_count": 3
        }
        
    Examples:
        # Get all active agents
        await get_active_agents()
        
        # Get agents working on specific project
        await get_active_agents(project_id="proj-abc-123")
        
        # Get agents by project name
        await get_active_agents(project_name="My App")
    """
    try:
        memory_store = get_memory_store()
        context_manager = get_context_manager()
        
        # Resolve project if filters provided
        target_project_id = None
        if any([project_id, project_name, workspace_path]):
            success, project, message = resolve_project(
                memory_store=memory_store,
                project_id=project_id,
                project_name=project_name,
                workspace_path=workspace_path
            )
            if success:
                target_project_id = project.project_id
            else:
                return {
                    "success": False,
                    "error": message,
                    "error_type": "ProjectNotFoundError"
                }
        
        # Get all agents
        all_agents = context_manager.get_all_agents()
        
        # Filter to active agents
        active_agents = []
        for agent in all_agents:
            if agent.status != "active":
                continue
            
            # Get agent context for current activity
            agent_context = context_manager.get_context(agent.agent_id)
            
            # If filtering by project, check if agent is working on it
            if target_project_id:
                if not agent_context or not agent_context.current_context:
                    continue
                if agent_context.current_context.project_id != target_project_id:
                    continue
            
            # Get locked files count
            locked_files = context_manager.file_tracker.get_locked_files_by_agent(
                agent.agent_id
            )
            
            # Get current project name
            current_project = None
            current_objective = None
            if agent_context and agent_context.current_context:
                current_project_id = agent_context.current_context.project_id
                current_objective = agent_context.current_context.current_objective
                # Get project name
                project = memory_store.get_project(current_project_id)
                if project:
                    current_project = project.project_name
            
            active_agents.append({
                "agent_id": agent.agent_id,
                "agent_name": agent.agent_name,
                "agent_type": agent.agent_type.value if agent.agent_type else "custom",
                "current_project": current_project,
                "current_objective": current_objective,
                "last_active": agent.last_active.isoformat() if agent.last_active else None,
                "locked_files_count": len(locked_files),
                "capabilities": agent.capabilities
            })
        
        # Sort by last_active (most recent first)
        active_agents.sort(
            key=lambda a: a["last_active"] or "",
            reverse=True
        )
        
        return {
            "success": True,
            "agents": active_agents,
            "total_count": len(active_agents)
        }
        
    except Exception as e:
        logger.error(f"Error getting active agents: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }
