"""
Task management tools for CoordMCP.

Provides full task lifecycle management including creation, assignment, tracking,
and completion with support for task dependencies and branching.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4

from coordmcp.core.server import get_storage
from coordmcp.context.manager import ContextManager
from coordmcp.context.file_tracker import FileTracker
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.memory.models import Task, TaskStatus, ActivityFeedItem
from coordmcp.logger import get_logger
from coordmcp.tools.memory_tools import resolve_project_id

logger = get_logger("tools.task")


def get_context_manager() -> ContextManager:
    """Get or create the ContextManager instance."""
    storage = get_storage()
    file_tracker = FileTracker(storage)
    return ContextManager(storage, file_tracker)


def get_memory_store() -> ProjectMemoryStore:
    """Get or create the ProjectMemoryStore instance."""
    storage = get_storage()
    return ProjectMemoryStore(storage)


async def create_task(
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    title: str = "",
    description: str = "",
    requested_agent_id: Optional[str] = None,
    priority: str = "medium",
    related_files: Optional[List[str]] = None,
    depends_on: Optional[List[str]] = None,
    parent_task_id: Optional[str] = None,
    estimated_hours: float = 0
) -> Dict[str, Any]:
    """
    Create a new task in a project.
    
    Args:
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name to look up (alternative to project_id)
        workspace_path: Workspace path to look up (alternative to project_id)
        title: Task title
        description: Task description
        requested_agent_id: Agent explicitly requested by user (optional)
        priority: Task priority (critical, high, medium, low)
        related_files: List of related file paths
        depends_on: List of task IDs this task depends on
        parent_task_id: Parent task ID for branching
        estimated_hours: Estimated hours to complete
        
    Returns:
        Dictionary with task_id and success status
    """
    try:
        memory_store = get_memory_store()
        
        # Resolve project
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        if not success:
            return {"success": False, "error": message, "error_type": "ProjectNotFound"}
        
        assert resolved_id is not None
        
        # Check if project exists
        if not memory_store.project_exists(resolved_id):
            return {
                "success": False,
                "error": f"Project {resolved_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        # Validate priority
        valid_priorities = ["critical", "high", "medium", "low"]
        if priority not in valid_priorities:
            priority = "medium"
        
        # Create task
        task = Task(
            id=str(uuid4()),
            title=title,
            description=description,
            project_id=resolved_id,
            requested_agent_id=requested_agent_id,
            priority=priority,
            related_files=related_files or [],
            depends_on=depends_on or [],
            parent_task_id=parent_task_id,
            estimated_hours=estimated_hours
        )
        
        # Save task
        task_id = memory_store.create_task(task)
        
        # If parent task specified, add this as child
        if parent_task_id:
            parent_task = memory_store.get_task(resolved_id, parent_task_id)
            if parent_task:
                parent_task.child_tasks.append(task_id)
                memory_store.update_task(resolved_id, parent_task)
        
        # Log activity
        activity = ActivityFeedItem(
            id=str(uuid4()),
            activity_type="task_created",
            agent_id="system",
            agent_name="System",
            project_id=resolved_id,
            summary=f"Task created: {title}",
            related_entity_id=task_id,
            related_entity_type="task"
        )
        memory_store.log_activity(resolved_id, activity)
        
        logger.info(f"Created task {task_id}: {title}")
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task '{title}' created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_task(
    project_id: str,
    task_id: str
) -> Dict[str, Any]:
    """
    Get task details.
    
    Args:
        project_id: Project ID
        task_id: Task ID
        
    Returns:
        Dictionary with task details
    """
    try:
        memory_store = get_memory_store()
        
        task = memory_store.get_task(project_id, task_id)
        if not task:
            return {
                "success": False,
                "error": f"Task {task_id} not found",
                "error_type": "TaskNotFound"
            }
        
        return {
            "success": True,
            "task": task.model_dump()
        }
        
    except Exception as e:
        logger.error(f"Error getting task: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def assign_task(
    project_id: str,
    task_id: str,
    agent_id: str,
    requested_by_user: bool = False
) -> Dict[str, Any]:
    """
    Assign a task to an agent.
    
    Args:
        project_id: Project ID
        task_id: Task ID
        agent_id: Agent ID to assign to
        requested_by_user: Whether this was explicitly requested by user
        
    Returns:
        Dictionary with success status
    """
    try:
        memory_store = get_memory_store()
        manager = get_context_manager()
        
        # Get task
        task = memory_store.get_task(project_id, task_id)
        if not task:
            return {
                "success": False,
                "error": f"Task {task_id} not found",
                "error_type": "TaskNotFound"
            }
        
        # Check if agent exists
        agent = manager.get_agent(agent_id)
        if not agent:
            return {
                "success": False,
                "error": f"Agent {agent_id} not found",
                "error_type": "AgentNotFound"
            }
        
        # Assign task
        task.assigned_agent_id = agent_id
        if requested_by_user:
            task.requested_agent_id = agent_id
        
        # Update status to in_progress
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        
        # Save task
        memory_store.update_task(project_id, task, agent_id)
        
        # Log activity
        activity = ActivityFeedItem(
            id=str(uuid4()),
            activity_type="task_assigned",
            agent_id=agent_id,
            agent_name=agent.agent_name,
            project_id=project_id,
            summary=f"Task '{task.title}' assigned to {agent.agent_name}",
            related_entity_id=task_id,
            related_entity_type="task"
        )
        memory_store.log_activity(project_id, activity)
        
        logger.info(f"Assigned task {task_id} to agent {agent_id}")
        
        return {
            "success": True,
            "message": f"Task assigned to {agent.agent_name}"
        }
        
    except Exception as e:
        logger.error(f"Error assigning task: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def update_task_status(
    project_id: str,
    task_id: str,
    agent_id: str,
    status: str,
    notes: str = ""
) -> Dict[str, Any]:
    """
    Update task status.
    
    Args:
        project_id: Project ID
        task_id: Task ID
        agent_id: Agent ID making the update
        status: New status (pending, in_progress, blocked, completed, cancelled)
        notes: Optional notes about the status change
        
    Returns:
        Dictionary with success status
    """
    try:
        memory_store = get_memory_store()
        
        # Get task
        task = memory_store.get_task(project_id, task_id)
        if not task:
            return {
                "success": False,
                "error": f"Task {task_id} not found",
                "error_type": "TaskNotFound"
            }
        
        # Validate status
        valid_statuses = ["pending", "in_progress", "blocked", "completed", "cancelled"]
        if status not in valid_statuses:
            return {
                "success": False,
                "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                "error_type": "ValidationError"
            }
        
        # Update status
        old_status = task.status
        task.status = TaskStatus(status)
        
        # Handle status-specific actions
        if status == "completed":
            task.completed_at = datetime.now()
            if task.started_at:
                task.actual_hours = (task.completed_at - task.started_at).total_seconds() / 3600
        elif status == "in_progress" and not task.started_at:
            task.started_at = datetime.now()
        elif status == "blocked" and notes:
            task.metadata["block_reason"] = notes
        
        # Save task
        memory_store.update_task(project_id, task, agent_id)
        
        # Log activity
        activity = ActivityFeedItem(
            id=str(uuid4()),
            activity_type=f"task_{status}",
            agent_id=agent_id,
            agent_name="Agent",  # Would get from agent profile
            project_id=project_id,
            summary=f"Task '{task.title}' moved from {old_status} to {status}",
            related_entity_id=task_id,
            related_entity_type="task"
        )
        memory_store.log_activity(project_id, activity)
        
        logger.info(f"Updated task {task_id} status to {status}")
        
        return {
            "success": True,
            "message": f"Task status updated to {status}"
        }
        
    except Exception as e:
        logger.error(f"Error updating task status: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_project_tasks(
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    status: Optional[str] = None,
    assigned_agent_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get all tasks for a project.
    
    Args:
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name to look up
        workspace_path: Workspace path to look up
        status: Filter by status
        assigned_agent_id: Filter by assigned agent
        
    Returns:
        Dictionary with list of tasks
    """
    try:
        memory_store = get_memory_store()
        
        # Resolve project
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        if not success:
            return {"success": False, "error": message, "error_type": "ProjectNotFound"}
        
        assert resolved_id is not None
        
        # Get tasks
        tasks = memory_store.get_project_tasks(
            resolved_id,
            status=status,
            assigned_agent_id=assigned_agent_id
        )
        
        return {
            "success": True,
            "tasks": [task.model_dump() for task in tasks],
            "count": len(tasks)
        }
        
    except Exception as e:
        logger.error(f"Error getting project tasks: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_my_tasks(
    agent_id: str,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get all tasks assigned to an agent.
    
    Args:
        agent_id: Agent ID
        status: Filter by status
        
    Returns:
        Dictionary with list of tasks
    """
    try:
        memory_store = get_memory_store()
        
        # Get tasks for agent
        tasks = memory_store.get_agent_tasks(agent_id, status=status)
        
        return {
            "success": True,
            "tasks": [task.model_dump() for task in tasks],
            "count": len(tasks)
        }
        
    except Exception as e:
        logger.error(f"Error getting agent tasks: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def complete_task(
    project_id: str,
    task_id: str,
    agent_id: str,
    completion_notes: str = ""
) -> Dict[str, Any]:
    """
    Mark a task as completed.
    
    Args:
        project_id: Project ID
        task_id: Task ID
        agent_id: Agent completing the task
        completion_notes: Notes about completion
        
    Returns:
        Dictionary with success status
    """
    return await update_task_status(
        project_id=project_id,
        task_id=task_id,
        agent_id=agent_id,
        status="completed",
        notes=completion_notes
    )


async def delete_task(
    project_id: str,
    task_id: str,
    agent_id: str,
    reason: str = ""
) -> Dict[str, Any]:
    """
    Delete (soft delete) a task.
    
    Args:
        project_id: Project ID
        task_id: Task ID
        agent_id: Agent deleting the task
        reason: Reason for deletion
        
    Returns:
        Dictionary with success status
    """
    try:
        memory_store = get_memory_store()
        
        # Delete task
        success = memory_store.delete_task(project_id, task_id, agent_id)
        
        if not success:
            return {
                "success": False,
                "error": f"Task {task_id} not found",
                "error_type": "TaskNotFound"
            }
        
        # Log activity
        activity = ActivityFeedItem(
            id=str(uuid4()),
            activity_type="task_deleted",
            agent_id=agent_id,
            agent_name="Agent",
            project_id=project_id,
            summary=f"Task deleted: {reason}" if reason else "Task deleted",
            related_entity_id=task_id,
            related_entity_type="task"
        )
        memory_store.log_activity(project_id, activity)
        
        logger.info(f"Deleted task {task_id}")
        
        return {
            "success": True,
            "message": "Task deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }
