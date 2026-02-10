"""
Project-related FastMCP resources for CoordMCP.

Resources:
- project://{project_id} - Full project information
- project://{project_id}/decisions - Project decisions
- project://{project_id}/tech-stack - Technology stack
- project://{project_id}/architecture - Architecture overview
- project://{project_id}/recent-changes - Recent changes
- project://{project_id}/modules/{module_name} - Module information
"""

from coordmcp.core.server import get_storage
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.logger import get_logger

logger = get_logger("resources.project")


def get_memory_store():
    """Get ProjectMemoryStore instance."""
    storage = get_storage()
    return ProjectMemoryStore(storage)


async def handle_project_resource(uri: str) -> str:
    """
    Handle project:// resources.
    
    Supported URIs:
    - project://{project_id} - Full project overview
    - project://{project_id}/decisions - All decisions
    - project://{project_id}/tech-stack - Tech stack
    - project://{project_id}/architecture - Architecture
    - project://{project_id}/recent-changes - Recent changes
    - project://{project_id}/modules/{module_name} - Module info
    """
    try:
        # Parse URI
        parts = uri.replace("project://", "").split("/")
        project_id = parts[0]
        resource_type = parts[1] if len(parts) > 1 else "overview"
        
        store = get_memory_store()
        
        # Check if project exists
        if not store.project_exists(project_id):
            return f"# Error\n\nProject not found: {project_id}"
        
        # Get project info
        project_info = store.get_project_info(project_id)
        
        if resource_type == "overview":
            return _format_project_overview(project_info)
        elif resource_type == "decisions":
            return _format_project_decisions(store, project_id)
        elif resource_type == "tech-stack":
            return _format_tech_stack(store, project_id)
        elif resource_type == "architecture":
            return _format_architecture(store, project_id)
        elif resource_type == "recent-changes":
            return _format_recent_changes(store, project_id)
        elif resource_type == "modules":
            module_name = parts[2] if len(parts) > 2 else None
            if module_name:
                return _format_module_info(store, project_id, module_name)
            else:
                return _format_all_modules(store, project_id)
        else:
            return f"# Error\n\nUnknown resource type: {resource_type}"
            
    except Exception as e:
        logger.error(f"Error handling project resource {uri}: {e}")
        return f"# Error\n\nFailed to load resource: {str(e)}"


def _format_project_overview(project_info) -> str:
    """Format project overview as markdown."""
    lines = [
        f"# Project: {project_info.project_name}",
        "",
        f"**Project ID:** {project_info.project_id}",
        f"**Created:** {project_info.created_at}",
        f"**Last Updated:** {project_info.last_updated}",
        "",
        "## Description",
        project_info.description or "No description provided.",
        "",
        "## Quick Stats",
    ]
    
    # Add stats if available
    if hasattr(project_info, 'stats'):
        for key, value in project_info.stats.items():
            lines.append(f"- **{key}:** {value}")
    
    lines.extend([
        "",
        "## Available Resources",
        f"- `project://{project_info.project_id}/decisions` - View all decisions",
        f"- `project://{project_info.project_id}/tech-stack` - View tech stack",
        f"- `project://{project_info.project_id}/architecture` - View architecture",
        f"- `project://{project_info.project_id}/recent-changes` - View recent changes",
        f"- `project://{project_info.project_id}/modules` - View all modules",
    ])
    
    return "\n".join(lines)


def _format_project_decisions(store, project_id: str) -> str:
    """Format project decisions as markdown."""
    decisions = store.get_all_decisions(project_id)
    
    lines = [
        f"# Decisions for Project",
        "",
        f"Total decisions: {len(decisions)}",
        "",
    ]
    
    if not decisions:
        lines.append("*No decisions recorded yet.*")
    else:
        for decision in decisions:
            status_emoji = "✅" if decision.status == "active" else "📦" if decision.status == "archived" else "🔄"
            lines.extend([
                f"## {status_emoji} {decision.title}",
                "",
                f"**ID:** {decision.id}",
                f"**Status:** {decision.status}",
                f"**Date:** {decision.timestamp}",
                f"**Author:** {decision.author_agent or 'Unknown'}",
                "",
                "### Description",
                decision.description or "No description.",
                "",
                "### Rationale",
                decision.rationale or "No rationale provided.",
                "",
            ])
            
            if decision.impact:
                lines.extend([
                    "### Impact",
                    decision.impact,
                    "",
                ])
            
            if decision.tags:
                lines.extend([
                    f"**Tags:** {', '.join(decision.tags)}",
                    "",
                ])
            
            lines.append("---")
            lines.append("")
    
    return "\n".join(lines)


def _format_tech_stack(store, project_id: str) -> str:
    """Format tech stack as markdown."""
    tech_stack = store.get_tech_stack(project_id)
    
    lines = [
        f"# Technology Stack",
        "",
    ]
    
    if not tech_stack:
        lines.append("*No technologies recorded yet.*")
    else:
        for category, entry in tech_stack.items():
            lines.extend([
                f"## {category.capitalize()}",
                "",
                f"**Technology:** {entry.get('technology', 'N/A')}",
            ])
            
            if entry.get('version'):
                lines.append(f"**Version:** {entry['version']}")
            
            if entry.get('rationale'):
                lines.extend([
                    "",
                    "**Rationale:**",
                    entry['rationale'],
                ])
            
            if entry.get('decision_ref'):
                lines.extend([
                    "",
                    f"**Decision Reference:** {entry['decision_ref']}",
                ])
            
            lines.append("")
    
    return "\n".join(lines)


def _format_architecture(store, project_id: str) -> str:
    """Format architecture overview as markdown."""
    architecture = store.get_architecture(project_id)
    modules = store.get_all_architecture_modules(project_id)
    
    lines = [
        f"# Architecture Overview",
        "",
    ]
    
    if architecture and architecture.get('overview'):
        lines.extend([
            "## Overview",
            architecture['overview'],
            "",
        ])
    
    if modules:
        lines.extend([
            f"## Modules ({len(modules)})",
            "",
        ])
        
        for module in modules:
            lines.extend([
                f"### {module.name}",
                "",
                f"**Purpose:** {module.purpose or 'Not specified'}",
                "",
            ])
            
            if module.files:
                lines.append("**Files:**")
                for file in module.files:
                    lines.append(f"- `{file}`")
                lines.append("")
            
            if module.dependencies:
                lines.append(f"**Dependencies:** {', '.join(module.dependencies)}")
                lines.append("")
    else:
        lines.append("*No architecture modules defined yet.*")
    
    return "\n".join(lines)


def _format_recent_changes(store, project_id: str) -> str:
    """Format recent changes as markdown."""
    changes = store.get_recent_changes(project_id, limit=50)
    
    lines = [
        f"# Recent Changes",
        "",
        f"Showing last {len(changes)} changes",
        "",
    ]
    
    if not changes:
        lines.append("*No changes recorded yet.*")
    else:
        for change in changes:
            emoji = {
                "create": "📝",
                "modify": "✏️",
                "delete": "🗑️",
                "refactor": "♻️"
            }.get(change.change_type, "📝")
            
            lines.extend([
                f"## {emoji} {change.change_type.upper()}: {change.file_path}",
                "",
                f"**Date:** {change.timestamp}",
                f"**Agent:** {change.agent_id or 'Unknown'}",
                f"**Impact:** {change.architecture_impact}",
                "",
                "### Description",
                change.description,
                "",
            ])
            
            if change.code_summary:
                lines.extend([
                    "### Code Summary",
                    change.code_summary,
                    "",
                ])
            
            lines.append("---")
            lines.append("")
    
    return "\n".join(lines)


def _format_module_info(store, project_id: str, module_name: str) -> str:
    """Format module information as markdown."""
    module = store.get_architecture_module(project_id, module_name)
    files = store.get_files_by_module(project_id, module_name)
    
    if not module:
        return f"# Module Not Found\n\nModule '{module_name}' not found in project."
    
    lines = [
        f"# Module: {module.name}",
        "",
    ]
    
    if module.purpose:
        lines.extend([
            "## Purpose",
            module.purpose,
            "",
        ])
    
    if module.responsibilities:
        lines.extend([
            "## Responsibilities",
            "",
        ])
        for resp in module.responsibilities:
            lines.append(f"- {resp}")
        lines.append("")
    
    if files:
        lines.extend([
            f"## Files ({len(files)})",
            "",
        ])
        for file_meta in files:
            lines.append(f"- `{file_meta.path}` ({file_meta.file_type})")
        lines.append("")
    
    if module.dependencies:
        lines.extend([
            "## Dependencies",
            "",
        ])
        for dep in module.dependencies:
            lines.append(f"- {dep}")
        lines.append("")
    
    return "\n".join(lines)


def _format_all_modules(store, project_id: str) -> str:
    """Format all modules overview as markdown."""
    modules = store.get_all_architecture_modules(project_id)
    
    lines = [
        f"# All Modules",
        "",
    ]
    
    if not modules:
        lines.append("*No modules defined yet.*")
    else:
        lines.append(f"Total modules: {len(modules)}")
        lines.append("")
        
        for module in modules:
            file_count = len(store.get_files_by_module(project_id, module.name))
            lines.extend([
                f"## {module.name}",
                "",
                f"{module.purpose or 'No purpose specified'}",
                "",
                f"**Files:** {file_count} | **Dependencies:** {len(module.dependencies)}",
                "",
            ])
    
    return "\n".join(lines)
