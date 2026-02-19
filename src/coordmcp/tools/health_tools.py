"""
Project health dashboard tools for CoordMCP.

Provides comprehensive health monitoring and project status overview.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from coordmcp.core.server import get_storage
from coordmcp.context.manager import ContextManager
from coordmcp.context.file_tracker import FileTracker
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.memory.models import TaskStatus
from coordmcp.logger import get_logger
from coordmcp.tools.memory_tools import resolve_project_id

logger = get_logger("tools.health")


def get_context_manager() -> ContextManager:
    """Get or create the ContextManager instance."""
    storage = get_storage()
    file_tracker = FileTracker(storage)
    return ContextManager(storage, file_tracker)


def get_memory_store() -> ProjectMemoryStore:
    """Get or create the ProjectMemoryStore instance."""
    storage = get_storage()
    return ProjectMemoryStore(storage)


async def get_project_dashboard(
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get comprehensive project health dashboard.
    
    Provides a complete overview of project status including tasks, agents,
    health metrics, and recommendations.
    
    Args:
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name to look up
        workspace_path: Workspace path to look up
        
    Returns:
        Dictionary with complete dashboard data
    """
    try:
        memory_store = get_memory_store()
        manager = get_context_manager()
        
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
        
        # Get project info
        project_info = memory_store.get_project_info(resolved_id)
        project_name_display = project_info.project_name if project_info else "Unknown"
        
        # Build dashboard
        dashboard = {
            "success": True,
            "project_name": project_name_display,
            "project_id": resolved_id,
            "generated_at": datetime.now().isoformat(),
            "overview": _get_overview(memory_store, manager, resolved_id),
            "tasks_summary": _get_tasks_summary(memory_store, resolved_id),
            "agents_summary": _get_agents_summary(manager, resolved_id),
            "locks_summary": _get_locks_summary(resolved_id),
            "recent_activity": _get_recent_activity_summary(memory_store, resolved_id),
            "health_score": 0,
            "health_status": "",
            "recommendations": []
        }
        
        # Calculate health score
        dashboard["health_score"], dashboard["health_status"] = _calculate_health_score(dashboard)
        
        # Generate recommendations
        dashboard["recommendations"] = _generate_recommendations(dashboard)
        
        logger.info(f"Generated dashboard for project {resolved_id}")
        return dashboard
        
    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


def _get_overview(memory_store, manager, project_id: str) -> Dict[str, Any]:
    """Get project overview metrics."""
    # Get project info
    project_info = memory_store.get_project_info(project_id)
    
    # Get all tasks
    all_tasks = memory_store.get_project_tasks(project_id, include_deleted=False)
    
    # Get active agents
    active_agents = manager.get_agents_in_project(project_id)
    
    # Get recent changes (last 24 hours)
    recent_changes = memory_store.get_recent_changes(project_id, limit=100)
    yesterday = datetime.now() - timedelta(days=1)
    changes_today = [c for c in recent_changes if c.created_at > yesterday]
    
    return {
        "total_tasks": len(all_tasks),
        "active_agents": len(active_agents),
        "changes_today": len(changes_today),
        "project_type": getattr(project_info, 'project_type', 'unknown'),
        "workspace_path": getattr(project_info, 'workspace_path', '')
    }


def _get_tasks_summary(memory_store, project_id: str) -> Dict[str, Any]:
    """Get task statistics."""
    all_tasks = memory_store.get_project_tasks(project_id, include_deleted=False)
    
    # Count by status
    by_status = {
        "pending": 0,
        "in_progress": 0,
        "blocked": 0,
        "completed": 0,
        "cancelled": 0
    }
    
    for task in all_tasks:
        status = task.status.value if hasattr(task.status, 'value') else str(task.status)
        if status in by_status:
            by_status[status] += 1
    
    # Get blocked tasks details
    blocked_tasks = []
    for task in all_tasks:
        if task.status == TaskStatus.BLOCKED:
            blocked_tasks.append({
                "task_id": task.id,
                "title": task.title,
                "assigned_agent_id": task.assigned_agent_id,
                "block_reason": task.metadata.get("block_reason", "Unknown")
            })
    
    return {
        "total": len(all_tasks),
        "by_status": by_status,
        "blocked_tasks": blocked_tasks[:5],  # Top 5 blocked
        "completion_rate": _calculate_completion_rate(by_status)
    }


def _get_agents_summary(manager, project_id: str) -> Dict[str, Any]:
    """Get agent activity summary."""
    active_agents = manager.get_agents_in_project(project_id)
    
    agents_data = []
    for agent_info in active_agents:
        agent_id = agent_info.get("agent_id")
        agent_context = manager.get_context(agent_id)
        
        if agent_context and agent_context.current_context:
            agents_data.append({
                "agent_id": agent_id,
                "agent_name": agent_info.get("agent_name"),
                "current_objective": agent_context.current_context.current_objective,
                "locked_files_count": len(agent_context.locked_files),
                "session_duration_minutes": int(agent_context.current_context.get_duration().total_seconds() / 60)
            })
    
    return {
        "active_count": len(agents_data),
        "agents": agents_data
    }


def _get_locks_summary(project_id: str) -> Dict[str, Any]:
    """Get file locks summary."""
    try:
        tracker = FileTracker(get_storage())
        result = tracker.get_locked_files(project_id)
        
        if not result.get("success"):
            return {"total_locked": 0, "stale_locks": 0, "locks_by_agent": {}}
        
        locked_files = result.get("locked_files", [])
        
        # Check for stale locks (older than 24 hours)
        stale_count = 0
        now = datetime.now()
        
        for lock_info in locked_files:
            locked_at = lock_info.get("locked_at")
            if locked_at:
                try:
                    lock_time = datetime.fromisoformat(locked_at)
                    if (now - lock_time) > timedelta(hours=24):
                        stale_count += 1
                except:
                    pass
        
        # Group by agent
        by_agent = {}
        for lock_info in locked_files:
            agent_id = lock_info.get("locked_by", "unknown")
            if agent_id not in by_agent:
                by_agent[agent_id] = []
            by_agent[agent_id].append(lock_info.get("file_path"))
        
        return {
            "total_locked": len(locked_files),
            "stale_locks": stale_count,
            "locks_by_agent": by_agent
        }
        
    except Exception as e:
        logger.warning(f"Could not get locks summary: {e}")
        return {"total_locked": 0, "stale_locks": 0, "locks_by_agent": {}}


def _get_recent_activity_summary(memory_store, project_id: str) -> Dict[str, Any]:
    """Get recent activity summary."""
    try:
        # Get recent activities
        activities = memory_store.get_recent_activities(project_id, limit=20)
        
        # Get recent session summaries
        summaries = memory_store.get_session_summaries(project_id, limit=5)
        
        return {
            "recent_activities_count": len(activities),
            "last_session_summary": summaries[0].summary_text if summaries else None,
            "recent_activities": [
                {
                    "type": a.activity_type,
                    "agent_name": a.agent_name,
                    "summary": a.summary,
                    "timestamp": a.created_at.isoformat() if isinstance(a.created_at, datetime) else a.created_at
                }
                for a in activities[:5]
            ]
        }
    except Exception as e:
        logger.warning(f"Could not get activity summary: {e}")
        return {"recent_activities_count": 0, "recent_activities": []}


def _calculate_completion_rate(by_status: Dict[str, int]) -> float:
    """Calculate task completion rate."""
    total = sum(by_status.values())
    if total == 0:
        return 0.0
    
    completed = by_status.get("completed", 0)
    return round((completed / total) * 100, 1)


def _calculate_health_score(dashboard: Dict) -> tuple:
    """Calculate overall health score (0-100) and status."""
    score = 100
    
    # Deduct for blocked tasks
    blocked_count = dashboard["tasks_summary"]["by_status"].get("blocked", 0)
    score -= blocked_count * 10
    
    # Deduct for stale locks
    stale_locks = dashboard["locks_summary"].get("stale_locks", 0)
    score -= stale_locks * 5
    
    # Bonus for good completion rate
    completion_rate = dashboard["tasks_summary"].get("completion_rate", 0)
    if completion_rate > 50:
        score += 5
    if completion_rate > 80:
        score += 5
    
    # Ensure score is in range
    score = max(0, min(100, score))
    
    # Determine status
    if score >= 80:
        status = "Healthy"
    elif score >= 60:
        status = "Fair"
    elif score >= 40:
        status = "Warning"
    else:
        status = "Critical"
    
    return score, status


def _generate_recommendations(dashboard: Dict) -> List[str]:
    """Generate recommendations based on dashboard data."""
    recommendations = []
    
    # Check for blocked tasks
    blocked_tasks = dashboard["tasks_summary"].get("blocked_tasks", [])
    if blocked_tasks:
        recommendations.append(f"⚠️ {len(blocked_tasks)} task(s) are blocked and need attention")
    
    # Check for stale locks
    stale_locks = dashboard["locks_summary"].get("stale_locks", 0)
    if stale_locks:
        recommendations.append(f"🔓 {stale_locks} file lock(s) are stale (>24h) - consider releasing")
    
    # Check completion rate
    completion_rate = dashboard["tasks_summary"].get("completion_rate", 0)
    if completion_rate < 30 and dashboard["tasks_summary"]["total"] > 5:
        recommendations.append("📊 Low completion rate - consider prioritizing tasks")
    
    # Check active agents
    active_agents = dashboard["agents_summary"].get("active_count", 0)
    if active_agents > 3:
        recommendations.append(f"👥 {active_agents} agents active - ensure good coordination")
    
    # Check recent activity
    changes_today = dashboard["overview"].get("changes_today", 0)
    if changes_today == 0:
        recommendations.append("📅 No changes in last 24 hours - project may be inactive")
    elif changes_today > 20:
        recommendations.append(f"🚀 High activity ({changes_today} changes today) - monitor for conflicts")
    
    # General recommendations
    if not recommendations:
        recommendations.append("✅ Project looks healthy! Keep up the good work.")
    
    return recommendations
