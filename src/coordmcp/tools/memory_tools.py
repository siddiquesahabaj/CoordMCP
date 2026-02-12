"""
Memory management tools for CoordMCP FastMCP server.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4

from coordmcp.core.server import get_storage
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.memory.models import Decision, TechStackEntry, Change, FileMetadata
from coordmcp.logger import get_logger

logger = get_logger("tools.memory")


def get_memory_store() -> ProjectMemoryStore:
    """Get or create the ProjectMemoryStore instance."""
    storage = get_storage()
    return ProjectMemoryStore(storage)


# ==================== Project Tools ====================

async def create_project(project_name: str, description: str = "") -> Dict[str, Any]:
    """
    Create a new project in the memory system.
    
    Args:
        project_name: Name of the project
        description: Project description
        
    Returns:
        Dictionary with project_id and success status
    """
    try:
        store = get_memory_store()
        project_id = store.create_project(project_name, description)
        
        return {
            "success": True,
            "project_id": project_id,
            "message": f"Project '{project_name}' created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_project_info(project_id: str) -> Dict[str, Any]:
    """
    Get information about a project.
    
    Args:
        project_id: Project ID
        
    Returns:
        Project information
    """
    try:
        store = get_memory_store()
        project_info = store.get_project_info(project_id)
        
        if not project_info:
            return {
                "success": False,
                "error": f"Project {project_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        return {
            "success": True,
            "project": project_info.dict()
        }
    except Exception as e:
        logger.error(f"Error getting project info: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


# ==================== Decision Tools ====================

async def save_decision(
    project_id: str,
    title: str,
    description: str,
    rationale: str,
    context: str = "",
    impact: str = "",
    tags: Optional[List[str]] = None,
    related_files: Optional[List[str]] = None,
    author_agent: str = ""
) -> Dict[str, Any]:
    """
    Save a major architectural or technical decision to project memory.
    
    Args:
        project_id: Project ID
        title: Decision title
        description: Detailed description
        rationale: Why this decision was made
        context: Context around the decision
        impact: Expected impact
        tags: List of tags
        related_files: List of related file paths
        author_agent: ID of the agent making the decision
        
    Returns:
        Dictionary with decision_id and success status
    """
    try:
        store = get_memory_store()
        
        # Check if project exists
        if not store.project_exists(project_id):
            return {
                "success": False,
                "error": f"Project {project_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        # Create decision
        from coordmcp.memory.models import DecisionStatus
        decision = Decision(
            id=str(uuid4()),
            title=title,
            description=description,
            context=context,
            rationale=rationale,
            impact=impact,
            status=DecisionStatus.ACTIVE,
            related_files=related_files or [],
            author_agent_id=author_agent,
            tags=tags or []
        )
        
        decision_id = store.save_decision(project_id, decision)
        
        return {
            "success": True,
            "decision_id": decision_id,
            "message": f"Decision '{title}' saved successfully"
        }
    except Exception as e:
        logger.error(f"Error saving decision: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_project_decisions(
    project_id: str,
    status: str = "all",
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Retrieve decisions for a project.
    
    Args:
        project_id: Project ID
        status: Filter by status (active, archived, superseded, all)
        tags: Filter by tags
        
    Returns:
        Dictionary with list of decisions
    """
    try:
        store = get_memory_store()
        
        if not store.project_exists(project_id):
            return {
                "success": False,
                "error": f"Project {project_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        # Get decisions
        if status == "all":
            decisions = store.get_all_decisions(project_id)
        else:
            decisions = store.get_decisions_by_status(project_id, status)
        
        # Filter by tags if provided
        if tags:
            decisions = [d for d in decisions if any(tag in d.tags for tag in tags)]
        
        return {
            "success": True,
            "decisions": [d.dict() for d in decisions],
            "count": len(decisions)
        }
    except Exception as e:
        logger.error(f"Error getting decisions: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def search_decisions(
    project_id: str,
    query: str,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Search through decisions by keywords or metadata.
    
    Args:
        project_id: Project ID
        query: Search query
        tags: Optional tags to filter by
        
    Returns:
        Dictionary with matching decisions
    """
    try:
        store = get_memory_store()
        
        if not store.project_exists(project_id):
            return {
                "success": False,
                "error": f"Project {project_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        decisions = store.search_decisions(project_id, query, tags)
        
        return {
            "success": True,
            "decisions": [d.dict() for d in decisions],
            "count": len(decisions)
        }
    except Exception as e:
        logger.error(f"Error searching decisions: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


# ==================== Tech Stack Tools ====================

async def update_tech_stack(
    project_id: str,
    category: str,
    technology: str,
    version: str = "",
    rationale: str = "",
    decision_ref: str = ""
) -> Dict[str, Any]:
    """
    Update technology stack information for a project.
    
    Args:
        project_id: Project ID
        category: Category (backend, frontend, database, infrastructure)
        technology: Technology name
        version: Version string
        rationale: Why this technology was chosen
        decision_ref: Reference to a decision ID
        
    Returns:
        Dictionary with success status
    """
    try:
        store = get_memory_store()
        
        if not store.project_exists(project_id):
            return {
                "success": False,
                "error": f"Project {project_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        entry = TechStackEntry(
            category=category,
            technology=technology,
            version=version,
            rationale=rationale,
            decision_ref=decision_ref if decision_ref else None
        )
        
        store.update_tech_stack(project_id, entry)
        
        return {
            "success": True,
            "message": f"Tech stack updated: {category} = {technology}"
        }
    except Exception as e:
        logger.error(f"Error updating tech stack: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_tech_stack(
    project_id: str,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get current technology stack for a project.
    
    Args:
        project_id: Project ID
        category: Optional specific category to retrieve
        
    Returns:
        Dictionary with tech stack information
    """
    try:
        store = get_memory_store()
        
        if not store.project_exists(project_id):
            return {
                "success": False,
                "error": f"Project {project_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        tech_stack = store.get_tech_stack(project_id, category)
        
        return {
            "success": True,
            "tech_stack": tech_stack
        }
    except Exception as e:
        logger.error(f"Error getting tech stack: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


# ==================== Change Log Tools ====================

async def log_change(
    project_id: str,
    file_path: str,
    change_type: str,
    description: str,
    agent_id: str = "",
    code_summary: str = "",
    architecture_impact: str = "none",
    related_decision: str = ""
) -> Dict[str, Any]:
    """
    Log a recent change to project structure or architecture.
    
    Args:
        project_id: Project ID
        file_path: Path of the file changed
        change_type: Type of change (create, modify, delete, refactor)
        description: Description of the change
        agent_id: ID of the agent making the change
        code_summary: Brief code summary
        architecture_impact: Impact level (none, minor, significant)
        related_decision: Related decision ID
        
    Returns:
        Dictionary with change_id and success status
    """
    try:
        store = get_memory_store()
        
        if not store.project_exists(project_id):
            return {
                "success": False,
                "error": f"Project {project_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        from coordmcp.memory.models import ChangeType, ArchitectureImpact
        change = Change(
            id=str(uuid4()),
            file_path=file_path,
            change_type=ChangeType(change_type),
            description=description,
            agent_id=agent_id,
            architecture_impact=ArchitectureImpact(architecture_impact),
            related_decision=related_decision if related_decision else None,
            code_summary=code_summary
        )
        
        change_id = store.log_change(project_id, change)
        
        return {
            "success": True,
            "change_id": change_id,
            "message": f"Change logged for {file_path}"
        }
    except Exception as e:
        logger.error(f"Error logging change: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_recent_changes(
    project_id: str,
    limit: int = 20,
    architecture_impact_filter: str = "all"
) -> Dict[str, Any]:
    """
    Get recent changes to a project.
    
    Args:
        project_id: Project ID
        limit: Maximum number of changes to return
        architecture_impact_filter: Filter by impact (all, none, minor, significant)
        
    Returns:
        Dictionary with list of changes
    """
    try:
        store = get_memory_store()
        
        if not store.project_exists(project_id):
            return {
                "success": False,
                "error": f"Project {project_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        impact_filter = None if architecture_impact_filter == "all" else architecture_impact_filter
        changes = store.get_recent_changes(project_id, limit, impact_filter)
        
        return {
            "success": True,
            "changes": [c.dict() for c in changes],
            "count": len(changes)
        }
    except Exception as e:
        logger.error(f"Error getting recent changes: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


# ==================== File Metadata Tools ====================

async def update_file_metadata(
    project_id: str,
    file_path: str,
    file_type: str = "source",
    module: str = "",
    purpose: str = "",
    dependencies: Optional[List[str]] = None,
    dependents: Optional[List[str]] = None,
    lines_of_code: int = 0,
    complexity: str = "low",
    last_modified_by: str = ""
) -> Dict[str, Any]:
    """
    Update metadata for a file in the project.
    
    Args:
        project_id: Project ID
        file_path: File path
        file_type: Type (source, test, config, doc)
        module: Module name
        purpose: Purpose description
        dependencies: Files this file depends on
        dependents: Files that depend on this file
        lines_of_code: Lines of code
        complexity: Complexity level (low, medium, high)
        last_modified_by: Agent who last modified
        
    Returns:
        Dictionary with success status
    """
    try:
        store = get_memory_store()
        
        if not store.project_exists(project_id):
            return {
                "success": False,
                "error": f"Project {project_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        from coordmcp.memory.models import FileType, Complexity
        metadata = FileMetadata(
            id=f"file_{file_path}",
            path=file_path,
            file_type=FileType(file_type),
            last_modified=datetime.now(),
            last_modified_by=last_modified_by,
            module=module,
            purpose=purpose,
            dependencies=dependencies or [],
            dependents=dependents or [],
            lines_of_code=lines_of_code,
            complexity=Complexity(complexity)
        )
        
        store.update_file_metadata(project_id, metadata)
        
        return {
            "success": True,
            "message": f"File metadata updated for {file_path}"
        }
    except Exception as e:
        logger.error(f"Error updating file metadata: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_file_dependencies(
    project_id: str,
    file_path: str,
    direction: str = "dependencies"
) -> Dict[str, Any]:
    """
    Get dependency graph for a file.
    
    Args:
        project_id: Project ID
        file_path: File path
        direction: dependencies, dependents, or both
        
    Returns:
        Dictionary with file dependencies
    """
    try:
        store = get_memory_store()
        
        if not store.project_exists(project_id):
            return {
                "success": False,
                "error": f"Project {project_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        deps = store.get_file_dependencies(project_id, file_path, direction)
        
        return {
            "success": True,
            "file_path": file_path,
            "direction": direction,
            "dependencies": deps
        }
    except Exception as e:
        logger.error(f"Error getting file dependencies: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_module_info(
    project_id: str,
    module_name: str
) -> Dict[str, Any]:
    """
    Get detailed information about a project module.
    
    Args:
        project_id: Project ID
        module_name: Name of the module
        
    Returns:
        Dictionary with module information
    """
    try:
        store = get_memory_store()
        
        if not store.project_exists(project_id):
            return {
                "success": False,
                "error": f"Project {project_id} not found",
                "error_type": "ProjectNotFound"
            }
        
        module = store.get_architecture_module(project_id, module_name)
        files = store.get_files_by_module(project_id, module_name)
        
        return {
            "success": True,
            "module": module.dict() if module else None,
            "files": [f.dict() for f in files],
            "file_count": len(files)
        }
    except Exception as e:
        logger.error(f"Error getting module info: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }
