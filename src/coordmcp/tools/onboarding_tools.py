"""
Smart onboarding tools for CoordMCP.

Provides comprehensive project context when an agent enters a project.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from coordmcp.core.server import get_storage
from coordmcp.context.manager import ContextManager
from coordmcp.context.file_tracker import FileTracker
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.memory.models import SCHEMA_VERSION
from coordmcp.logger import get_logger

logger = get_logger("tools.onboarding")


def get_context_manager() -> ContextManager:
    """Get or create the ContextManager instance."""
    storage = get_storage()
    file_tracker = FileTracker(storage)
    return ContextManager(storage, file_tracker)


def get_memory_store() -> ProjectMemoryStore:
    """Get or create the ProjectMemoryStore instance."""
    storage = get_storage()
    return ProjectMemoryStore(storage)


async def get_project_onboarding_context(
    agent_id: str,
    project_id: str
) -> Dict[str, Any]:
    """
    Get comprehensive onboarding context when an agent enters a project.
    
    Returns a complete 'situation report' including project info, recent activity,
    active agents, key decisions, and agent's own context history.
    
    Args:
        agent_id: Agent ID
        project_id: Project ID
        
    Returns:
        Dictionary with complete onboarding context
    """
    try:
        manager = get_context_manager()
        memory_store = get_memory_store()
        
        # Check if agent exists
        agent_profile = manager.get_agent(agent_id)
        if not agent_profile:
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
        
        project_info = memory_store.get_project_info(project_id)
        
        # Build onboarding context
        onboarding = {
            "success": True,
            "project_info": _build_project_info(project_info, memory_store),
            "agent_context": _build_agent_context(agent_profile, project_id),
            "active_agents": _get_active_agents_in_project(manager, project_id),
            "recent_changes": _get_recent_changes(memory_store, project_id),
            "key_decisions": _get_key_decisions(memory_store, project_id),
            "locked_files": _get_locked_files(project_id),
            "recommended_next_steps": _get_recommended_steps(project_id, agent_id, manager)
        }
        
        logger.info(f"Generated onboarding context for agent {agent_id} in project {project_id}")
        return onboarding
        
    except Exception as e:
        logger.error(f"Error generating onboarding context: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


def _build_project_info(project_info, memory_store) -> Dict[str, Any]:
    """Build project information section."""
    if not project_info:
        return {}
    
    return {
        "project_id": project_info.project_id,
        "project_name": project_info.project_name,
        "description": project_info.description,
        "workspace_path": project_info.workspace_path,
        "project_type": getattr(project_info, 'project_type', ''),
        "tech_stack": _get_tech_stack_summary(memory_store, project_info.project_id),
        "architecture": _get_architecture_summary(memory_store, project_info.project_id),
        "recommended_workflows": getattr(project_info, 'recommended_workflows', [])
    }


def _build_agent_context(agent_profile, project_id: str) -> Dict[str, Any]:
    """Build agent's personal context section."""
    # Check if this is a returning agent to this project
    is_returning = project_id in agent_profile.projects_involved
    
    # Find last session in this project from cross-project history
    last_session_info = None
    for activity in agent_profile.cross_project_history:
        if activity.project_id == project_id:
            last_session_info = activity
            break
    
    return {
        "agent_id": agent_profile.agent_id,
        "agent_name": agent_profile.agent_name,
        "is_returning": is_returning,
        "previous_sessions_in_project": last_session_info.total_sessions if last_session_info else 0,
        "last_session_in_project": last_session_info.last_visited.isoformat() if last_session_info else None,
        "total_sessions_all_projects": agent_profile.total_sessions,
        "capabilities": agent_profile.capabilities,
        "typical_objectives": agent_profile.typical_objectives,
        "last_project_id": agent_profile.last_project_id
    }


def _get_active_agents_in_project(manager, project_id: str) -> List[Dict[str, Any]]:
    """Get all active agents working in the project."""
    active_agents = manager.get_agents_in_project(project_id)
    return active_agents


def _get_recent_changes(memory_store, project_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent changes in the project."""
    try:
        changes = memory_store.get_recent_changes(project_id, limit=limit)
        return [{
            "change_id": c.id,
            "file_path": c.file_path,
            "change_type": c.change_type,
            "description": c.description,
            "agent_id": c.agent_id,
            "created_at": c.created_at.isoformat(),
            "architecture_impact": c.architecture_impact
        } for c in changes]
    except Exception as e:
        logger.warning(f"Could not get recent changes: {e}")
        return []


def _get_key_decisions(memory_store, project_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get key/active decisions for the project."""
    try:
        # Get all decisions and filter for active ones
        decisions_data = memory_store.backend.load(f"memory/{project_id}/decisions")
        if not decisions_data or "decisions" not in decisions_data:
            return []
        
        active_decisions = []
        for decision_id, decision_dict in decisions_data["decisions"].items():
            # Only include active decisions
            status = decision_dict.get("status", "active")
            if status == "active":
                active_decisions.append({
                    "decision_id": decision_id,
                    "title": decision_dict.get("title", ""),
                    "description": decision_dict.get("description", "")[:100] + "...",  # Truncate
                    "tags": decision_dict.get("tags", []),
                    "author_agent_id": decision_dict.get("author_agent_id", "")
                })
        
        # Return top N
        return active_decisions[:limit]
    except Exception as e:
        logger.warning(f"Could not get key decisions: {e}")
        return []


def _get_locked_files(project_id: str) -> List[Dict[str, Any]]:
    """Get currently locked files in the project."""
    try:
        tracker = FileTracker(get_storage())
        result = tracker.get_locked_files(project_id)
        
        if result.get("success"):
            return result.get("locked_files", [])
        return []
    except Exception as e:
        logger.warning(f"Could not get locked files: {e}")
        return []


def _get_tech_stack_summary(memory_store, project_id: str) -> List[Dict[str, Any]]:
    """Get technology stack summary."""
    try:
        tech_stack = memory_store.get_tech_stack(project_id)
        return [{
            "category": entry.category,
            "technology": entry.technology,
            "version": entry.version
        } for entry in tech_stack]
    except Exception as e:
        logger.warning(f"Could not get tech stack: {e}")
        return []


def _get_architecture_summary(memory_store, project_id: str) -> Dict[str, Any]:
    """Get architecture summary."""
    try:
        arch_data = memory_store.backend.load(f"memory/{project_id}/architecture")
        if arch_data and "architecture" in arch_data:
            modules = arch_data["architecture"].get("modules", {})
            return {
                "module_count": len(modules),
                "modules": list(modules.keys())[:5]  # Top 5 modules
            }
        return {"module_count": 0, "modules": []}
    except Exception as e:
        logger.warning(f"Could not get architecture: {e}")
        return {"module_count": 0, "modules": []}


def _get_recommended_steps(project_id: str, agent_id: str, manager) -> List[str]:
    """Generate recommended next steps based on project state."""
    recommendations = []
    
    try:
        # Check if agent has context already
        agent_context = manager.get_context(agent_id)
        if not agent_context or not agent_context.current_context:
            recommendations.append("Start a work context to begin tracking your progress")
        
        # Check for blocked tasks
        # This would require task system - placeholder for now
        recommendations.append("Review recent changes to understand current state")
        
        # Check for locked files
        locked = _get_locked_files(project_id)
        if locked:
            recommendations.append(f"Note: {len(locked)} files are currently locked by other agents")
        
        # Check for active agents
        active = _get_active_agents_in_project(manager, project_id)
        if len(active) > 1:  # More than just this agent
            recommendations.append(f"Coordinate with {len(active)-1} other active agent(s)")
        
    except Exception as e:
        logger.warning(f"Could not generate recommendations: {e}")
    
    return recommendations
