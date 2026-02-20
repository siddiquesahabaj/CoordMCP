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
        try:
            memory_store = get_memory_store()
            from coordmcp.memory.models import TaskStatus
            blocked_tasks = memory_store.get_project_tasks(project_id, status=TaskStatus.BLOCKED)
            if blocked_tasks:
                recommendations.append(f"⚠️ {len(blocked_tasks)} task(s) are BLOCKED - check dependencies before starting new work")
        except Exception as e:
            logger.warning(f"Could not check blocked tasks: {e}")
        
        recommendations.append("Review recent changes to understand current state")
        
        # Check for pending tasks that could be worked on
        try:
            memory_store = get_memory_store()
            from coordmcp.memory.models import TaskStatus
            pending_tasks = memory_store.get_project_tasks(project_id, status=TaskStatus.PENDING)
            if pending_tasks:
                recommendations.append(f"There are {len(pending_tasks)} pending task(s) available to work on")
        except Exception as e:
            logger.warning(f"Could not check pending tasks: {e}")
        
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


WORKFLOW_TEMPLATES = {
    "test-first": {
        "name": "Test-First Development",
        "description": "Write tests before implementing code",
        "phases": [
            {"step": 1, "action": "register_agent", "tool": "register_agent", "description": "Register your agent identity"},
            {"step": 2, "action": "start_context", "tool": "start_context", "description": "Start a work context for this project"},
            {"step": 3, "action": "create_task", "tool": "create_task", "description": "Create a task for the feature"},
            {"step": 4, "action": "write_test", "tool": "N/A", "description": "Write failing test first"},
            {"step": 5, "action": "implement", "tool": "N/A", "description": "Implement code to pass test"},
            {"step": 6, "action": "lock_files", "tool": "lock_files", "description": "Lock files before editing"},
            {"step": 7, "action": "log_change", "tool": "log_change", "description": "Log the change with description"},
            {"step": 8, "action": "unlock_files", "tool": "unlock_files", "description": "Unlock files after editing"},
            {"step": 9, "action": "complete_task", "tool": "update_task", "description": "Mark task as completed"},
            {"step": 10, "action": "end_context", "tool": "end_context", "description": "End work context"}
        ]
    },
    "feature-branch": {
        "name": "Feature Branch Workflow",
        "description": "Work on feature branches with code review",
        "phases": [
            {"step": 1, "action": "register_agent", "tool": "register_agent", "description": "Register your agent identity"},
            {"step": 2, "action": "start_context", "tool": "start_context", "description": "Start a work context"},
            {"step": 3, "action": "create_task", "tool": "create_task", "description": "Create task for the feature"},
            {"step": 4, "action": "lock_files", "tool": "lock_files", "description": "Lock files you'll modify"},
            {"step": 5, "action": "implement", "tool": "N/A", "description": "Implement the feature"},
            {"step": 6, "action": "log_change", "tool": "log_change", "description": "Document the change"},
            {"step": 7, "action": "unlock_files", "tool": "unlock_files", "description": "Unlock files"},
            {"step": 8, "action": "save_decision", "tool": "save_decision", "description": "Save architectural decision if needed"},
            {"step": 9, "action": "end_context", "tool": "end_context", "description": "End work context"}
        ]
    },
    "review-then-commit": {
        "name": "Review Then Commit",
        "description": "Peer review before committing changes",
        "phases": [
            {"step": 1, "action": "register_agent", "tool": "register_agent", "description": "Register agent"},
            {"step": 2, "action": "start_context", "tool": "start_context", "description": "Start context"},
            {"step": 3, "action": "check_active", "tool": "get_active_agents", "description": "Check who's working on this project"},
            {"step": 4, "action": "lock_files", "tool": "lock_files", "description": "Lock files to work on"},
            {"step": 5, "action": "implement", "tool": "N/A", "description": "Make your changes"},
            {"step": 6, "action": "log_change", "tool": "log_change", "description": "Log all changes"},
            {"step": 7, "action": "unlock_files", "tool": "unlock_files", "description": "Unlock files"},
            {"step": 8, "action": "send_message", "tool": "send_agent_message", "description": "Request review from other agent"},
            {"step": 9, "action": "end_context", "tool": "end_context", "description": "End context"}
        ]
    },
    "default": {
        "name": "Standard Development Workflow",
        "description": "Basic workflow for any development task",
        "phases": [
            {"step": 1, "action": "register_agent", "tool": "register_agent", "description": "Register your agent (REQUIRED first step)"},
            {"step": 2, "action": "start_context", "tool": "start_context", "description": "Start work context with project and objective"},
            {"step": 3, "action": "lock_files", "tool": "lock_files", "description": "Lock files before editing (prevents conflicts)"},
            {"step": 4, "action": "implement", "tool": "N/A", "description": "Make your code changes"},
            {"step": 5, "action": "log_change", "tool": "log_change", "description": "Log each change with description"},
            {"step": 6, "action": "unlock_files", "tool": "unlock_files", "description": "Unlock files when done"},
            {"step": 7, "action": "end_context", "tool": "end_context", "description": "End context to save session summary"}
        ]
    }
}


async def get_workflow_guidance(
    project_id: Optional[str] = None,
    workflow_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get phase-by-phase workflow guidance for agents.
    
    This tool provides structured, step-by-step instructions for working on a project.
    It combines project-specific workflows with the standardCoordMCP workflow.
    
    Args:
        project_id: Optional project ID to get project-specific workflows
        workflow_name: Optional specific workflow to use (e.g., "test-first", "feature-branch")
        
    Returns:
        Dictionary with workflow guidance including phases and steps
    """
    try:
        memory_store = get_memory_store()
        
        # Determine which workflow to use
        selected_workflow = "default"
        project_workflows = []
        
        if project_id:
            if memory_store.project_exists(project_id):
                project_info = memory_store.get_project_info(project_id)
                if project_info:
                    project_workflows = project_info.recommended_workflows or []
                    if not workflow_name and project_workflows:
                        selected_workflow = project_workflows[0]
        
        if workflow_name:
            selected_workflow = workflow_name
        
        # Get workflow template
        if selected_workflow in WORKFLOW_TEMPLATES:
            workflow = WORKFLOW_TEMPLATES[selected_workflow]
        else:
            workflow = WORKFLOW_TEMPLATES["default"]
            selected_workflow = "default"
        
        # Build response
        result = {
            "success": True,
            "workflow_name": selected_workflow,
            "workflow_display_name": workflow["name"],
            "description": workflow["description"],
            "phases": workflow["phases"],
            "project_workflows_available": project_workflows,
            "is_default": selected_workflow == "default"
        }
        
        # Add project context if available
        if project_id and memory_store.project_exists(project_id):
            result["project_id"] = project_id
            project_info = memory_store.get_project_info(project_id)
            if project_info:
                result["project_name"] = project_info.project_name
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting workflow guidance: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def validate_workflow_state(agent_id: str) -> Dict[str, Any]:
    """
    Validate agent's workflow state and return warnings for missing steps.
    
    This tool checks the agent's current workflow state and provides warnings
    about any steps they may have missed (e.g., forgot to lock files, 
    didn't log changes, etc.).
    
    Args:
        agent_id: The agent's ID
        
    Returns:
        Dictionary with workflow validation results including:
        - current_state: Current workflow state
        - warnings: List of warnings about missing steps
        - completed_steps: List of steps completed
        - missing_steps: List of steps that should be completed
    """
    try:
        manager = get_context_manager()
        agent_context = manager.get_context(agent_id)
        agent_profile = manager.get_agent(agent_id)
        
        if not agent_context:
            if agent_profile:
                return {
                    "success": True,
                    "current_state": "registered",
                    "warnings": ["No active context - call start_context() to begin working"],
                    "completed_steps": ["register_agent"],
                    "missing_steps": ["start_context", "lock_files", "make_changes", "log_change", "unlock_files", "end_context"],
                    "has_active_context": False
                }
            return {
                "success": True,
                "current_state": "unregistered",
                "warnings": ["You have not registered with CoordMCP. Call register_agent() first."],
                "completed_steps": [],
                "missing_steps": ["register_agent"]
            }
        
        # Define required workflow steps in order
        required_steps = [
            "register_agent",
            "start_context", 
            "lock_files",
            "make_changes",
            "log_change",
            "unlock_files",
            "end_context"
        ]
        
        completed = agent_context.workflow_progress or []
        current_state = agent_context.workflow_state.value if agent_context.workflow_state else "unregistered"
        
        # Determine missing steps based on current state
        missing = []
        if current_state == "unregistered":
            missing = required_steps
        elif current_state == "registered" or not agent_context.current_context:
            missing = required_steps[1:]  # Skip register_agent
        else:
            # Find where we are in the workflow
            state_to_step = {
                "context_started": "start_context",
                "files_locked": "lock_files", 
                "working": "make_changes",
                "changes_logged": "log_change",
                "files_unlocked": "unlock_files",
                "context_ended": "end_context"
            }
            
            current_step = state_to_step.get(current_state, "start_context")
            step_idx = required_steps.index(current_step) if current_step in required_steps else 0
            missing = required_steps[step_idx + 1:]
        
        # Generate warnings
        warnings = []
        
        if not agent_context.current_context:
            warnings.append("⚠️ No active context - call start_context() to begin working")
        else:
            if current_state in ["context_started", "registered"]:
                warnings.append("⚠️ You haven't locked any files - lock_files() should be called before editing")
            
            if "lock_files" in completed and "unlock_files" not in completed:
                locked_files = agent_context.get_locked_file_paths() if hasattr(agent_context, 'get_locked_file_paths') else []
                if locked_files:
                    warnings.append(f"⚠️ You have {len(locked_files)} locked file(s) - unlock them when done")
            
            # Check if agent has made changes but not logged them
            recent_context = agent_context.recent_context if hasattr(agent_context, 'recent_context') else []
            if recent_context and "log_change" not in completed:
                warnings.append("⚠️ You have recent file operations - call log_change() to document them")
        
        if current_state == "context_ended":
            warnings.append("✅ Context ended - call register_agent() to start a new session")
        
        return {
            "success": True,
            "current_state": current_state,
            "workflow_progress": completed,
            "warnings": warnings,
            "completed_steps": completed,
            "missing_steps": missing,
            "has_active_context": agent_context.current_context is not None
        }
        
    except Exception as e:
        logger.error(f"Error validating workflow state: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_system_prompt() -> Dict[str, Any]:
    """
    Get the CoordMCP system prompt with mandatory workflow instructions.
    
    This tool returns the complete system prompt that agents should use
    as their system prompt for proper CoordMCP integration.
    
    Returns:
        Dictionary with the system prompt content
    """
    system_prompt = """# CoordMCP System Prompt

You are an intelligent coding assistant integrated with **CoordMCP** - a multi-agent coordination system providing shared memory, context management, task tracking, agent messaging, and architectural guidance.

**Using CoordMCP is MANDATORY for all work.** It prevents conflicts, maintains context across sessions, and enables smooth multi-agent collaboration.

---

## MANDATORY WORKFLOW (Always Follow This Order)

### 1. Start: Discover or Create Project
```python
# First, discover if project exists in current directory
discovery = await discover_project(path=os.getcwd())

if discovery["found"]:
    project_id = discovery["project"]["project_id"]
else:
    result = await create_project(
        project_name="Your Project Name",
        workspace_path=os.getcwd(),
        description="What this project does"
    )
    project_id = result["project_id"]
```

### 2. Register: Identify Yourself
```python
agent = await register_agent(
    agent_name="YourName",  # Use consistent name across sessions
    agent_type="opencode",  # or "cursor", "claude_code", "custom"
    capabilities=["python", "react"]  # Your skills
)
agent_id = agent["agent_id"]
```

### 3. Check: Understand Current State
```python
# See who's working and what's happening
agents = await get_active_agents(project_id=project_id)
locked = await get_locked_files(project_id=project_id)
decisions = await get_project_decisions(project_id=project_id)
```

### 4. Begin: Start Your Context
```python
await start_context(
    agent_id=agent_id,
    project_id=project_id,
    objective="What you're working on",
    priority="high"  # critical, high, medium, low
)
```

---

## COORDINATION TOOLS (Use These Before/During Work)

### File Locking - PREVENT CONFLICTS
**When:** Before editing ANY file
```python
# Lock BEFORE making changes
await lock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["src/auth.py", "src/models/user.py"],
    reason="Implementing JWT authentication",
    expected_duration_minutes=60
)

# If files are locked by others, coordinate with them first
locked = await get_locked_files(project_id=project_id)

# Unlock when DONE
await unlock_files(agent_id=agent_id, project_id=project_id, files=[...])
```

---

## QUICK REFERENCE

| When | Tool |
|------|------|
| Start work | `discover_project` → `register_agent` → `start_context` |
| Before editing | `lock_files` |
| After editing | `log_change` → `unlock_files` |
| Need guidance | `get_workflow_guidance_tool()` |
| Check status | `validate_workflow_state_tool(agent_id)` |
| End work | `end_context` |

---

## BEST PRACTICES

✅ ALWAYS discover/create project first  
✅ ALWAYS register yourself before work  
✅ ALWAYS lock files before editing  
✅ ALWAYS log changes after completing work  
✅ ALWAYS unlock files when done  
✅ Call get_workflow_guidance_tool() for step-by-step instructions  
✅ Call validate_workflow_state_tool(agent_id) to check your progress  

❌ NEVER skip workflow steps  
❌ NEVER edit without locking first  
❌ NEVER leave files locked  

**CoordMCP enables smooth vibe coding. Use it for every project.**
"""
    return {
        "success": True,
        "system_prompt": system_prompt,
        "version": "1.0.0"
    }
