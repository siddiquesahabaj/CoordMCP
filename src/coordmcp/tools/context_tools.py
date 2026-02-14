"""
Context management tools for CoordMCP FastMCP server.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4

from coordmcp.core.server import get_storage
from coordmcp.context.manager import ContextManager
from coordmcp.context.file_tracker import FileTracker
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.logger import get_logger
from coordmcp.errors import FileLockError
from coordmcp.tools.memory_tools import resolve_project_id

logger = get_logger("tools.context")


def get_context_manager() -> ContextManager:
    """Get or create the ContextManager instance."""
    storage = get_storage()
    file_tracker = FileTracker(storage)
    return ContextManager(storage, file_tracker)


def get_file_tracker() -> FileTracker:
    """Get or create the FileTracker instance."""
    storage = get_storage()
    return FileTracker(storage)


def get_memory_store() -> ProjectMemoryStore:
    """Get or create the ProjectMemoryStore instance."""
    storage = get_storage()
    return ProjectMemoryStore(storage)


# ==================== Agent Registration Tools ====================

async def register_agent(
    agent_name: str,
    agent_type: str,
    capabilities: Optional[List[str]] = None,
    version: str = "1.0.0"
) -> Dict[str, Any]:
    """
    Register a new agent or reconnect to an existing agent.
    
    If an agent with the same name already exists and is active, this will
    reconnect to that agent instead of creating a new one. This enables
    session persistence across multiple OpenCode/Agent sessions.
    
    Args:
        agent_name: Name of the agent (e.g., "OpenCode", "Cursor", "ClaudeCode")
        agent_type: Type (opencode, cursor, claude_code, custom)
        capabilities: List of agent capabilities
        version: Agent version
        
    Returns:
        Dictionary with agent_id and success status
        
    Example:
        # First session - creates new agent
        result = await register_agent("OpenCode", "opencode", ["python", "fastapi"])
        # Returns: {"success": True, "agent_id": "abc-123", "message": "..."}
        
        # Second session - reconnects to same agent
        result = await register_agent("OpenCode", "opencode", ["python", "fastapi"])
        # Returns: {"success": True, "agent_id": "abc-123", "message": "..."} (same ID!)
    """
    # Input validation
    if not agent_name or not isinstance(agent_name, str):
        return {
            "success": False,
            "error": "agent_name is required and must be a non-empty string",
            "error_type": "ValidationError"
        }
    
    if not agent_type or not isinstance(agent_type, str):
        return {
            "success": False,
            "error": "agent_type is required and must be a non-empty string",
            "error_type": "ValidationError"
        }
    
    # Validate agent_type against allowed values
    valid_agent_types = ["opencode", "cursor", "claude_code", "custom"]
    if agent_type not in valid_agent_types:
        return {
            "success": False,
            "error": f"Invalid agent_type. Must be one of: {', '.join(valid_agent_types)}",
            "error_type": "ValidationError"
        }
    
    # Validate capabilities and set default
    if capabilities is None:
        capabilities = []
    elif not isinstance(capabilities, list):
        return {
            "success": False,
            "error": "capabilities must be a list of strings",
            "error_type": "ValidationError"
        }
    
    # Validate version
    if not version or not isinstance(version, str):
        return {
            "success": False,
            "error": "version must be a non-empty string",
            "error_type": "ValidationError"
        }
    
    try:
        manager = get_context_manager()
        
        agent_id = manager.register_agent(
            agent_name=agent_name,
            agent_type=agent_type,
            capabilities=capabilities,
            version=version
        )
        
        # Check if this was a reconnection by looking at existing agents
        all_agents = manager.get_all_agents()
        is_reconnect = any(a.agent_name == agent_name and a.agent_id == agent_id and a.total_sessions > 0 for a in all_agents)
        
        if is_reconnect:
            message = f"Agent '{agent_name}' reconnected successfully. Previous context restored."
        else:
            message = f"Agent '{agent_name}' registered successfully"
        
        return {
            "success": True,
            "agent_id": agent_id,
            "message": message
        }
    except ValueError as e:
        logger.error(f"Validation error registering agent: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "ValidationError"
        }
    except Exception as e:
        logger.error(f"Error registering agent: {type(e).__name__}")
        return {
            "success": False,
            "error": "Internal server error occurred",
            "error_type": "InternalError"
        }


async def get_agents_list(status: str = "all") -> Dict[str, Any]:
    """
    Get list of all registered agents.
    
    Args:
        status: Filter by status (active, inactive, deprecated, all)
        
    Returns:
        Dictionary with list of agents
    """
    try:
        manager = get_context_manager()
        agents = manager.get_all_agents()
        
        # Filter by status if specified
        if status != "all":
            agents = [a for a in agents if a.status == status]
        
        return {
            "success": True,
            "agents": [a.dict() for a in agents],
            "count": len(agents)
        }
    except Exception as e:
        logger.error(f"Error getting agents list: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_agent_profile(agent_id: str) -> Dict[str, Any]:
    """
    Get an agent's profile information.
    
    Args:
        agent_id: Agent ID
        
    Returns:
        Dictionary with agent profile
    """
    try:
        manager = get_context_manager()
        agent = manager.get_agent(agent_id)
        
        if not agent:
            return {
                "success": False,
                "error": f"Agent {agent_id} not found",
                "error_type": "AgentNotFound"
            }
        
        return {
            "success": True,
            "agent": agent.dict()
        }
    except Exception as e:
        logger.error(f"Error getting agent profile: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


# ==================== Context Management Tools ====================

async def start_context(
    agent_id: str,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    objective: str = "",
    task_description: str = "",
    priority: str = "medium",
    current_file: str = ""
) -> Dict[str, Any]:
    """
    Start a new work context for an agent.
    
    Args:
        agent_id: Agent ID
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name to look up (alternative to project_id)
        workspace_path: Workspace path to look up (alternative to project_id)
        objective: Current objective
        task_description: Detailed task description
        priority: Priority level (critical, high, medium, low)
        current_file: Current file being worked on
        
    Returns:
        Dictionary with context information
        
    Examples:
        # By project ID
        result = await start_context("agent-123", project_id="proj-456", objective="Fix bug")
        
        # By project name
        result = await start_context("agent-123", project_name="My Project", objective="Fix bug")
        
        # By workspace path
        result = await start_context("agent-123", workspace_path="/path/to/project", objective="Fix bug")
    """
    try:
        manager = get_context_manager()
        memory_store = get_memory_store()
        
        # Check if agent exists
        agent = manager.get_agent(agent_id)
        if not agent:
            return {
                "success": False,
                "error": f"Agent {agent_id} not found. Please register first.",
                "error_type": "AgentNotFound"
            }
        
        # Resolve project
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        if not success:
            return {"success": False, "error": message, "error_type": "ProjectNotFound"}
        
        # Type assertion: resolved_id is guaranteed to be str when success is True
        assert resolved_id is not None
        
        # Check if project exists
        if not memory_store.project_exists(resolved_id):
            return {
                "success": False,
                "error": f"Project {resolved_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        # Start context
        context = manager.start_context(
            agent_id=agent_id,
            project_id=resolved_id,
            objective=objective,
            task_description=task_description,
            priority=priority,
            current_file=current_file
        )
        
        return {
            "success": True,
            "context": context.dict(),
            "message": f"Context started: {objective}"
        }
    except Exception as e:
        logger.error(f"Error starting context: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_agent_context(agent_id: str) -> Dict[str, Any]:
    """
    Get current context for an agent.
    
    Args:
        agent_id: Agent ID
        
    Returns:
        Dictionary with agent context
    """
    try:
        manager = get_context_manager()
        
        # Check if agent exists
        agent = manager.get_agent(agent_id)
        if not agent:
            return {
                "success": False,
                "error": f"Agent {agent_id} not found",
                "error_type": "AgentNotFound"
            }
        
        # Get full context
        context = manager.get_context(agent_id)
        
        if not context:
            return {
                "success": True,
                "context": None,
                "message": "No active context for this agent"
            }
        
        return {
            "success": True,
            "context": context.dict()
        }
    except Exception as e:
        logger.error(f"Error getting agent context: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def switch_context(
    agent_id: str,
    to_project_id: str,
    to_objective: str,
    task_description: str = "",
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Switch agent context between projects or objectives.
    
    Args:
        agent_id: Agent ID
        to_project_id: Target project ID
        to_objective: New objective
        task_description: New task description
        priority: Priority level
        
    Returns:
        Dictionary with new context information
    """
    try:
        manager = get_context_manager()
        memory_store = get_memory_store()
        
        # Check if agent exists
        agent = manager.get_agent(agent_id)
        if not agent:
            return {
                "success": False,
                "error": f"Agent {agent_id} not found",
                "error_type": "AgentNotFound"
            }
        
        # Check if project exists
        if not memory_store.project_exists(to_project_id):
            return {
                "success": False,
                "error": f"Project {to_project_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        # Switch context
        context = manager.switch_context(
            agent_id=agent_id,
            new_project_id=to_project_id,
            new_objective=to_objective,
            task_description=task_description,
            priority=priority
        )
        
        return {
            "success": True,
            "context": context.dict(),
            "message": f"Context switched to: {to_objective}"
        }
    except Exception as e:
        logger.error(f"Error switching context: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def end_context(agent_id: str) -> Dict[str, Any]:
    """
    End an agent's current context.
    
    Args:
        agent_id: Agent ID
        
    Returns:
        Dictionary with success status
    """
    try:
        manager = get_context_manager()
        
        success = manager.end_context(agent_id)
        
        if success:
            return {
                "success": True,
                "message": "Context ended successfully"
            }
        else:
            return {
                "success": False,
                "error": "No active context to end",
                "error_type": "NoActiveContext"
            }
    except Exception as e:
        logger.error(f"Error ending context: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


# ==================== File Locking Tools ====================

async def lock_files(
    agent_id: str,
    project_id: str,
    files: List[str],
    reason: str,
    expected_duration_minutes: int = 60
) -> Dict[str, Any]:
    """
    Lock files to prevent conflicts between agents.
    
    Args:
        agent_id: Agent ID
        project_id: Project ID
        files: List of file paths to lock
        reason: Reason for locking
        expected_duration_minutes: Expected duration in minutes
        
    Returns:
        Dictionary with locked files or conflicts
    """
    try:
        tracker = get_file_tracker()
        manager = get_context_manager()
        memory_store = get_memory_store()
        
        # Check if agent exists
        agent = manager.get_agent(agent_id)
        if not agent:
            return {
                "success": False,
                "error": f"Agent {agent_id} not found",
                "error_type": "AgentNotFound"
            }
        
        # Check if project exists
        if not memory_store.project_exists(project_id):
            return {
                "success": False,
                "error": f"Project {project_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        # Calculate expected unlock time
        expected_unlock_time = datetime.now() + timedelta(minutes=expected_duration_minutes)
        
        # Lock files
        result = tracker.lock_files(
            agent_id=agent_id,
            project_id=project_id,
            files=files,
            reason=reason,
            expected_unlock_time=expected_unlock_time
        )
        
        return result
        
    except FileLockError as e:
        # Return conflict information
        return {
            "success": False,
            "error": str(e),
            "error_type": "FileLockConflict",
            "conflicts": e.args[1] if len(e.args) > 1 else []
        }
    except Exception as e:
        logger.error(f"Error locking files: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def unlock_files(
    agent_id: str,
    project_id: str,
    files: List[str]
) -> Dict[str, Any]:
    """
    Unlock files after work is complete.
    
    Args:
        agent_id: Agent ID
        project_id: Project ID
        files: List of file paths to unlock
        
    Returns:
        Dictionary with unlocked files
    """
    try:
        tracker = get_file_tracker()
        
        result = tracker.unlock_files(
            agent_id=agent_id,
            project_id=project_id,
            files=files
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error unlocking files: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_locked_files(
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get list of currently locked files in a project.
    
    Args:
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name to look up (alternative to project_id)
        workspace_path: Workspace path to look up (alternative to project_id)
        
    Returns:
        Dictionary with locked files by agent
        
    Examples:
        # By project ID
        result = await get_locked_files(project_id="proj-456")
        
        # By project name
        result = await get_locked_files(project_name="My Project")
        
        # By workspace path
        result = await get_locked_files(workspace_path="/path/to/project")
    """
    try:
        tracker = get_file_tracker()
        memory_store = get_memory_store()
        
        # Resolve project
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        if not success:
            return {"success": False, "error": message, "error_type": "ProjectNotFound"}
        
        # Type assertion: resolved_id is guaranteed to be str when success is True
        assert resolved_id is not None
        
        # Check if project exists
        if not memory_store.project_exists(resolved_id):
            return {
                "success": False,
                "error": f"Project {resolved_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        result = tracker.get_locked_files(resolved_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting locked files: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


# ==================== Session & Context History Tools ====================

async def get_context_history(agent_id: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get recent context history for an agent.
    
    Args:
        agent_id: Agent ID
        limit: Maximum number of entries
        
    Returns:
        Dictionary with context history
    """
    try:
        manager = get_context_manager()
        
        entries = manager.get_context_history(agent_id, limit)
        
        return {
            "success": True,
            "history": [e.dict() for e in entries],
            "count": len(entries)
        }
    except Exception as e:
        logger.error(f"Error getting context history: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_session_log(agent_id: str, limit: int = 50) -> Dict[str, Any]:
    """
    Get session log for an agent.
    
    Args:
        agent_id: Agent ID
        limit: Maximum number of entries
        
    Returns:
        Dictionary with session log
    """
    try:
        manager = get_context_manager()
        
        entries = manager.get_session_log(agent_id, limit)
        
        return {
            "success": True,
            "log": [e.dict() for e in entries],
            "count": len(entries)
        }
    except Exception as e:
        logger.error(f"Error getting session log: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_agents_in_project(
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get all agents currently working in a project.
    
    Args:
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name to look up (alternative to project_id)
        workspace_path: Workspace path to look up (alternative to project_id)
        
    Returns:
        Dictionary with list of active agents
        
    Examples:
        # By project ID
        result = await get_agents_in_project(project_id="proj-456")
        
        # By project name
        result = await get_agents_in_project(project_name="My Project")
        
        # By workspace path
        result = await get_agents_in_project(workspace_path="/path/to/project")
    """
    try:
        manager = get_context_manager()
        memory_store = get_memory_store()
        
        # Resolve project
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        if not success:
            return {"success": False, "error": message, "error_type": "ProjectNotFound"}
        
        # Type assertion: resolved_id is guaranteed to be str when success is True
        assert resolved_id is not None
        
        # Check if project exists
        if not memory_store.project_exists(resolved_id):
            return {
                "success": False,
                "error": f"Project {resolved_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        agents = manager.get_agents_in_project(resolved_id)
        
        return {
            "success": True,
            "agents": agents,
            "count": len(agents)
        }
    except Exception as e:
        logger.error(f"Error getting agents in project: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }
