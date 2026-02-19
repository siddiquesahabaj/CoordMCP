"""
Agent messaging tools for CoordMCP.

Provides messaging capabilities between agents working on the same project.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4

from coordmcp.core.server import get_storage
from coordmcp.context.manager import ContextManager
from coordmcp.context.file_tracker import FileTracker
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.memory.models import AgentMessage, MessageType
from coordmcp.logger import get_logger
from coordmcp.tools.memory_tools import resolve_project_id

logger = get_logger("tools.message")


def get_context_manager() -> ContextManager:
    """Get or create the ContextManager instance."""
    storage = get_storage()
    file_tracker = FileTracker(storage)
    return ContextManager(storage, file_tracker)


def get_memory_store() -> ProjectMemoryStore:
    """Get or create the ProjectMemoryStore instance."""
    storage = get_storage()
    return ProjectMemoryStore(storage)


async def send_message(
    from_agent_id: str,
    to_agent_id: str,
    project_id: str,
    content: str,
    message_type: str = "update",
    related_task_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send a message to another agent (or broadcast to all).
    
    Args:
        from_agent_id: Agent ID sending the message
        to_agent_id: Agent ID receiving (use 'broadcast' for all agents)
        project_id: Project ID
        content: Message content
        message_type: Type - request, update, alert, question, review
        related_task_id: Optional related task ID
        
    Returns:
        Dictionary with message_id and success status
    """
    try:
        memory_store = get_memory_store()
        manager = get_context_manager()
        
        # Verify project exists
        if not memory_store.project_exists(project_id):
            return {
                "success": False,
                "error": f"Project {project_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        # Get sender agent info
        from_agent = manager.get_agent(from_agent_id)
        if not from_agent:
            return {
                "success": False,
                "error": f"Sender agent {from_agent_id} not found",
                "error_type": "AgentNotFound"
            }
        
        # Verify recipient if not broadcast
        if to_agent_id != "broadcast":
            to_agent = manager.get_agent(to_agent_id)
            if not to_agent:
                return {
                    "success": False,
                    "error": f"Recipient agent {to_agent_id} not found",
                    "error_type": "AgentNotFound"
                }
        
        # Validate message type
        valid_types = ["request", "update", "alert", "question", "review"]
        if message_type not in valid_types:
            message_type = "update"
        
        # Create message
        message = AgentMessage(
            id=str(uuid4()),
            from_agent_id=from_agent_id,
            from_agent_name=from_agent.agent_name,
            to_agent_id=to_agent_id,
            project_id=project_id,
            message_type=MessageType(message_type),
            content=content,
            related_task_id=related_task_id
        )
        
        # Save message
        message_id = memory_store.send_message(message)
        
        logger.info(f"Message sent from {from_agent_id} to {to_agent_id}")
        
        return {
            "success": True,
            "message_id": message_id,
            "message": f"Message sent to {to_agent_id if to_agent_id != 'broadcast' else 'all agents'}"
        }
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_messages(
    agent_id: str,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    unread_only: bool = False,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get messages for an agent.
    
    Args:
        agent_id: Agent ID to get messages for
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name to look up
        workspace_path: Workspace path to look up
        unread_only: Only get unread messages
        limit: Maximum number of messages
        
    Returns:
        Dictionary with list of messages
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
        
        # Get messages
        messages = memory_store.get_messages(
            resolved_id,
            agent_id,
            unread_only=unread_only,
            limit=limit
        )
        
        return {
            "success": True,
            "messages": [msg.model_dump() for msg in messages],
            "count": len(messages),
            "unread_count": memory_store.get_unread_count(resolved_id, agent_id) if not unread_only else len(messages)
        }
        
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_sent_messages(
    agent_id: str,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get messages sent by an agent.
    
    Args:
        agent_id: Agent ID who sent messages
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name to look up
        workspace_path: Workspace path to look up
        limit: Maximum number of messages
        
    Returns:
        Dictionary with list of sent messages
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
        
        # Get sent messages
        messages = memory_store.get_sent_messages(resolved_id, agent_id, limit=limit)
        
        return {
            "success": True,
            "messages": [msg.model_dump() for msg in messages],
            "count": len(messages)
        }
        
    except Exception as e:
        logger.error(f"Error getting sent messages: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def mark_message_read(
    agent_id: str,
    message_id: str,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Mark a message as read.
    
    Args:
        agent_id: Agent ID marking the message as read
        message_id: Message ID to mark as read
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name to look up
        workspace_path: Workspace path to look up
        
    Returns:
        Dictionary with success status
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
        
        # Mark as read
        result = memory_store.mark_message_read(resolved_id, message_id, agent_id)
        
        if result:
            return {
                "success": True,
                "message": "Message marked as read"
            }
        else:
            return {
                "success": False,
                "error": "Message not found or you are not the recipient",
                "error_type": "MessageNotFound"
            }
        
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def broadcast_message(
    from_agent_id: str,
    project_id: str,
    content: str,
    message_type: str = "update"
) -> Dict[str, Any]:
    """
    Broadcast a message to all agents in a project.
    
    Args:
        from_agent_id: Agent ID sending the message
        project_id: Project ID
        content: Message content
        message_type: Type - request, update, alert, question, review
        
    Returns:
        Dictionary with message_id and success status
    """
    return await send_message(
        from_agent_id=from_agent_id,
        to_agent_id="broadcast",
        project_id=project_id,
        content=content,
        message_type=message_type
    )
