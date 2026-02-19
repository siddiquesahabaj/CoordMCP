"""
Agent-related FastMCP resources for CoordMCP.

Resources:
- agent://{agent_id} - Agent profile and capabilities
- agent://{agent_id}/context - Current working context
- agent://{agent_id}/locked-files - Files locked by agent
- agent://{agent_id}/session-log - Agent session activity log
- agent://registry - Global agent registry
"""

from coordmcp.core.server import get_storage
from coordmcp.context.manager import ContextManager
from coordmcp.context.file_tracker import FileTracker
from coordmcp.logger import get_logger

logger = get_logger("resources.agent")


def get_context_manager():
    """Get ContextManager instance."""
    storage = get_storage()
    file_tracker = FileTracker(storage)
    return ContextManager(storage, file_tracker)


async def handle_agent_resource(uri: str) -> str:
    """
    Handle agent:// resources.
    
    Supported URIs:
    - agent://{agent_id} - Agent profile
    - agent://{agent_id}/context - Current context
    - agent://{agent_id}/locked-files - Locked files
    - agent://{agent_id}/session-log - Session log
    - agent://registry - All agents
    """
    try:
        # Parse URI
        parts = uri.replace("agent://", "").split("/")
        
        if parts[0] == "registry":
            return _format_agent_registry()
        
        agent_id = parts[0]
        resource_type = parts[1] if len(parts) > 1 else "profile"
        
        manager = get_context_manager()
        
        # Check if agent exists
        agent = manager.get_agent(agent_id)
        if not agent:
            return f"# Error\n\nAgent not found: {agent_id}"
        
        if resource_type == "profile":
            return _format_agent_profile(agent)
        elif resource_type == "context":
            return _format_agent_context(manager, agent_id)
        elif resource_type == "locked-files":
            return _format_locked_files(manager, agent_id)
        elif resource_type == "session-log":
            return _format_session_log(manager, agent_id)
        else:
            return f"# Error\n\nUnknown resource type: {resource_type}"
            
    except Exception as e:
        logger.error(f"Error handling agent resource {uri}: {e}")
        return f"# Error\n\nFailed to load resource: {str(e)}"


def _format_agent_profile(agent) -> str:
    """Format agent profile as markdown."""
    lines = [
        f"# Agent: {agent.agent_name}",
        "",
        f"**Agent ID:** {agent.agent_id}",
        f"**Type:** {agent.agent_type}",
        f"**Version:** {agent.version}",
        f"**Status:** {agent.status}",
        "",
    ]
    
    if agent.capabilities:
        lines.extend([
            "## Capabilities",
            "",
        ])
        for cap in agent.capabilities:
            lines.append(f"- {cap}")
        lines.append("")
    
    lines.extend([
        "## Activity",
        "",
        f"**Total Sessions:** {agent.total_sessions}",
        f"**Last Active:** {agent.last_active}",
        "",
    ])
    
    if agent.projects_involved:
        lines.extend([
            "## Projects Involved",
            "",
        ])
        for project_id in agent.projects_involved:
            lines.append(f"- {project_id}")
        lines.append("")
    
    lines.extend([
        "## Available Resources",
        f"- `agent://{agent.agent_id}/context` - View current context",
        f"- `agent://{agent.agent_id}/locked-files` - View locked files",
        f"- `agent://{agent.agent_id}/session-log` - View session log",
    ])
    
    return "\n".join(lines)


def _format_agent_context(manager, agent_id: str) -> str:
    """Format agent context as markdown."""
    context = manager.get_context(agent_id)
    
    if not context:
        return f"# Agent Context\n\n*No active context for this agent.*"
    
    lines = [
        f"# Current Context for Agent",
        "",
    ]
    
    current = context.current_context
    if current:
        lines.extend([
            "## Current Objective",
            f"**{current.current_objective}**",
            "",
            f"**Project:** {current.project_id}",
            f"**Priority:** {current.priority}",
            f"**Started:** {current.started_at}",
        ])
        
        if hasattr(current, 'task_description') and current.task_description:
            lines.extend([
                "",
                "### Task Description",
                current.task_description,
            ])
        
        if current.current_file:
            lines.extend([
                "",
                f"**Current File:** `{current.current_file}`",
            ])
        
        lines.append("")
    
    if context.locked_files:
        lines.extend([
            f"## Locked Files ({len(context.locked_files)})",
            "",
        ])
        for lock in context.locked_files:
            lines.extend([
                f"- `{lock.file_path}`",
                f"  - Locked at: {lock.locked_at}",
                f"  - Reason: {lock.reason}",
            ])
            if lock.expected_unlock_time:
                lines.append(f"  - Expected unlock: {lock.expected_unlock_time}")
        lines.append("")
    
    if context.recent_context:
        lines.extend([
            f"## Recent Activity ({len(context.recent_context)} entries)",
            "",
        ])
        for entry in context.recent_context[:10]:
            lines.append(f"- {entry.timestamp}: {entry.operation} on `{entry.file}`")
        lines.append("")
    
    return "\n".join(lines)


def _format_locked_files(manager, agent_id: str) -> str:
    """Format locked files as markdown."""
    storage = get_storage()
    file_tracker = FileTracker(storage)
    
    # Get agent info
    agent = manager.get_agent(agent_id)
    
    # Get all locked files across all projects
    all_locked = []
    # We need to check the file_tracker for this agent's locks
    # For now, get from agent context
    context = manager.get_context(agent_id)
    
    lines = [
        f"# Locked Files for {agent.agent_name if agent else agent_id}",
        "",
    ]
    
    if context and context.locked_files:
        lines.append(f"Total locked files: {len(context.locked_files)}")
        lines.append("")
        
        for lock in context.locked_files:
            lines.extend([
                f"## {lock.file_path}",
                "",
                f"**Locked at:** {lock.locked_at}",
                f"**Reason:** {lock.reason}",
            ])
            if lock.expected_unlock_time:
                lines.extend([
                    "",
                    f"**Expected unlock:** {lock.expected_unlock_time}",
                ])
            lines.append("")
    else:
        lines.append("*No files currently locked by this agent.*")
    
    return "\n".join(lines)


def _format_session_log(manager, agent_id: str) -> str:
    """Format session log as markdown."""
    entries = manager.get_session_log(agent_id, limit=50)
    
    agent = manager.get_agent(agent_id)
    agent_name = agent.agent_name if agent else agent_id
    
    lines = [
        f"# Session Log for {agent_name}",
        "",
        f"Showing last {len(entries)} entries",
        "",
    ]
    
    if not entries:
        lines.append("*No session log entries yet.*")
    else:
        for entry in entries:
            emoji = {
                "context_started": "🚀",
                "context_ended": "🏁",
                "context_switched": "🔄",
                "files_locked": "🔒",
                "files_unlocked": "🔓",
                "decision_saved": "📝",
                "change_logged": "✏️",
                "error": "⚠️"
            }.get(entry.event, "📌")
            
            lines.append(f"## {emoji} {entry.event}")
            lines.append("")
            lines.append(f"**Time:** {entry.timestamp}")
            lines.append("")
            
            if entry.details:
                lines.append("**Details:**")
                for key, value in entry.details.items():
                    if isinstance(value, list):
                        lines.append(f"- {key}: {', '.join(str(v) for v in value)}")
                    else:
                        lines.append(f"- {key}: {value}")
            
            lines.append("")
            lines.append("---")
            lines.append("")
    
    return "\n".join(lines)


def _format_agent_registry() -> str:
    """Format agent registry as markdown."""
    manager = get_context_manager()
    agents = manager.get_all_agents()
    
    lines = [
        f"# Agent Registry",
        "",
        f"Total registered agents: {len(agents)}",
        "",
    ]
    
    if not agents:
        lines.append("*No agents registered yet.*")
    else:
        # Group by status
        active_agents = [a for a in agents if a.status == "active"]
        inactive_agents = [a for a in agents if a.status == "inactive"]
        deprecated_agents = [a for a in agents if a.status == "deprecated"]
        
        if active_agents:
            lines.extend([
                "## Active Agents",
                "",
            ])
            for agent in active_agents:
                lines.append(f"- **{agent.agent_name}** ({agent.agent_type}) - {agent.total_sessions} sessions")
            lines.append("")
        
        if inactive_agents:
            lines.extend([
                "## Inactive Agents",
                "",
            ])
            for agent in inactive_agents:
                lines.append(f"- **{agent.agent_name}** ({agent.agent_type})")
            lines.append("")
        
        if deprecated_agents:
            lines.extend([
                "## Deprecated Agents",
                "",
            ])
            for agent in deprecated_agents:
                lines.append(f"- **{agent.agent_name}** ({agent.agent_type})")
            lines.append("")
        
        lines.extend([
            "## Agent Details",
            "",
        ])
        for agent in agents:
            lines.extend([
                f"### {agent.agent_name}",
                "",
                f"- **ID:** {agent.agent_id}",
                f"- **Type:** {agent.agent_type}",
                f"- **Version:** {agent.version}",
                f"- **Capabilities:** {', '.join(agent.capabilities) if agent.capabilities else 'None'}",
                f"- **Last Active:** {agent.last_active}",
                "",
            ])
    
    return "\n".join(lines)
