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


def resolve_project_id(
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None
) -> tuple[bool, Optional[str], str]:
    """
    Helper to resolve project_id from flexible identifiers.
    
    Returns: (success, resolved_project_id, message)
    """
    from coordmcp.utils.project_resolver import resolve_project
    
    store = get_memory_store()
    success, project_info, message = resolve_project(
        memory_store=store,
        project_id=project_id,
        project_name=project_name,
        workspace_path=workspace_path
    )
    
    if success:
        return True, project_info.project_id, message
    else:
        return False, None, message


# ==================== Project Tools ====================

async def create_project(
    project_name: str,
    workspace_path: str,
    description: str = ""
) -> Dict[str, Any]:
    """
    Create a new project in the memory system.
    
    This tool creates a new project linked to a specific workspace directory.
    The workspace_path is required and must be an absolute path to an existing directory.
    
    Use Cases:
    - Starting a new project and want to track it in CoordMCP
    - Setting up project memory before writing code
    - Establishing the project workspace for multi-agent coordination
    
    Args:
        project_name: Name of the project (e.g., "Todo App", "API Service")
        workspace_path: Absolute path to project workspace directory (required)
                       Example: "/home/user/projects/myapp" or "C:\\Users\\name\\projects\\myapp"
        description: Project description (optional)
        
    Returns:
        Dictionary with project details:
        {
            "success": True/False,
            "project_id": "proj-uuid-123",
            "project_name": "My App",
            "workspace_path": "/home/user/projects/myapp",
            "message": "Project created successfully"
        }
        
    Example:
        result = await create_project(
            project_name="Todo App",
            workspace_path="/home/user/projects/todo-app",
            description="A task management application"
        )
        # Returns project_id for use in other tools
    """
    try:
        # Validate workspace_path
        from coordmcp.utils.project_resolver import validate_workspace_path
        is_valid, error_msg = validate_workspace_path(workspace_path)
        if not is_valid:
            return {
                "success": False,
                "error": error_msg,
                "error_type": "ValidationError"
            }
        
        # Check if workspace path is already used
        store = get_memory_store()
        from coordmcp.utils.project_resolver import is_workspace_path_unique, normalize_path
        if not is_workspace_path_unique(store, workspace_path):
            return {
                "success": False,
                "error": f"Workspace path '{normalize_path(workspace_path)}' is already associated with another project",
                "error_type": "DuplicateWorkspaceError"
            }
        
        project_id = store.create_project(
            project_name=project_name,
            description=description,
            workspace_path=normalize_path(workspace_path)
        )
        
        return {
            "success": True,
            "project_id": project_id,
            "project_name": project_name,
            "workspace_path": normalize_path(workspace_path),
            "message": f"Project '{project_name}' created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }


async def get_project_info(
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get information about a project by ID, name, or workspace path.
    
    This tool provides flexible project lookup. You can specify any combination
    of identifiers, and it will resolve to the matching project.
    
    Priority: project_id > workspace_path > project_name
    
    Use Cases:
    - Get project details when you know the project_id
    - Find project by its workspace directory path
    - Look up project by name when ID is unknown
    - Validate that multiple identifiers point to the same project
    
    Args:
        project_id: Project ID (e.g., "proj-abc-123")
        project_name: Project name (e.g., "My App")
        workspace_path: Workspace directory path (e.g., "/home/user/projects/myapp")
        
    Returns:
        Dictionary with project details:
        {
            "success": True/False,
            "project": {
                "project_id": "...",
                "project_name": "...",
                "description": "...",
                "workspace_path": "...",
                "created_at": "...",
                "updated_at": "..."
            },
            "message": "Success or error description"
        }
        
    Examples:
        # Get by ID
        await get_project_info(project_id="proj-abc-123")
        
        # Get by name
        await get_project_info(project_name="My App")
        
        # Get by workspace path
        await get_project_info(workspace_path="/home/user/projects/myapp")
    """
    try:
        store = get_memory_store()
        
        # Use project resolver for flexible lookup
        from coordmcp.utils.project_resolver import resolve_project
        success, project_info, message = resolve_project(
            memory_store=store,
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        
        if not success:
            return {
                "success": False,
                "error": message,
                "error_type": "ProjectNotFound"
            }
        
        return {
            "success": True,
            "project": project_info.model_dump(),
            "message": message
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
    title: str,
    description: str,
    rationale: str,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    context: str = "",
    impact: str = "",
    tags: Optional[List[str]] = None,
    related_files: Optional[List[str]] = None,
    author_agent: str = ""
) -> Dict[str, Any]:
    """
    Save a major architectural or technical decision to project memory.
    
    Records important technical choices, architecture patterns, framework selections,
    and other significant decisions. This creates a permanent record of WHY certain
    choices were made, which is invaluable for future development and onboarding.
    
    Use Cases:
    - Documenting framework/library choices (React vs Vue, FastAPI vs Flask)
    - Recording architecture patterns (Microservices vs Monolithic)
    - Tracking database decisions (PostgreSQL vs MongoDB)
    - Noting API design choices (REST vs GraphQL)
    - Capturing security implementation strategies
    
    Args:
        title: Decision title (e.g., "Use PostgreSQL for primary database")
        description: Detailed description of the decision
        rationale: Why this decision was made, including trade-offs considered
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name (optional if project_id or workspace_path provided)
        workspace_path: Workspace directory path (optional if project_id or project_name provided)
        context: Additional context around the decision
        impact: Expected impact on the project
        tags: List of tags for categorization (e.g., ["database", "backend"])
        related_files: List of related file paths affected by this decision
        author_agent: ID of the agent making the decision
        
    Returns:
        Dictionary with decision_id and success status
        
    Examples:
        # Save by project ID
        await save_decision(
            project_id="proj-abc-123",
            title="Use FastAPI",
            description="FastAPI chosen for API framework",
            rationale="Type hints, automatic docs, async support"
        )
        
        # Save by workspace path
        await save_decision(
            workspace_path="/home/user/projects/myapp",
            title="Use PostgreSQL",
            description="Primary database selection",
            rationale="ACID compliance, complex queries, JSON support"
        )
    """
    try:
        store = get_memory_store()
        
        # Resolve project identifier
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        
        if not success:
            return {
                "success": False,
                "error": message,
                "error_type": "ProjectNotFound"
            }
        
        # Check if project exists
        if not store.project_exists(resolved_id):
            return {
                "success": False,
                "error": f"Project {resolved_id} not found",
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
        
        decision_id = store.save_decision(resolved_id, decision)
        
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
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    status: str = "all",
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Retrieve architectural and technical decisions for a project.
    
    This tool fetches all recorded decisions for a project, with optional filtering
    by status (active, archived, superseded) and tags. Use this to understand
    the decision history and rationale behind the current architecture.
    
    Use Cases:
    - Review all decisions made for a project
    - Find active architectural decisions
    - Filter decisions by category using tags (e.g., "database", "api")
    - Check the status of previous decisions
    - Understand the evolution of the architecture
    
    Args:
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name (optional if project_id or workspace_path provided)
        workspace_path: Workspace directory path (optional if project_id or project_name provided)
        status: Filter by status - "active", "archived", "superseded", or "all" (default: "all")
        tags: Optional list of tags to filter decisions (e.g., ["database", "backend"])
        
    Returns:
        Dictionary with list of decisions:
        {
            "success": True/False,
            "decisions": [
                {
                    "id": "...",
                    "title": "Use PostgreSQL",
                    "description": "...",
                    "rationale": "...",
                    "status": "active",
                    "tags": ["database", "backend"],
                    "created_at": "..."
                }
            ],
            "count": 5
        }
        
    Examples:
        # Get all decisions by project ID
        await get_project_decisions(project_id="proj-abc-123")
        
        # Get only active decisions by workspace path
        await get_project_decisions(
            workspace_path="/home/user/projects/myapp",
            status="active"
        )
        
        # Get database-related decisions by project name
        await get_project_decisions(
            project_name="My App",
            tags=["database"]
        )
    """
    try:
        store = get_memory_store()
        
        # Resolve project identifier
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        
        if not success:
            return {
                "success": False,
                "error": message,
                "error_type": "ProjectNotFound"
            }
        
        # Get decisions
        if status == "all":
            decisions = store.get_all_decisions(resolved_id)
        else:
            decisions = store.get_decisions_by_status(resolved_id, status)
        
        # Filter by tags if provided
        if tags:
            decisions = [d for d in decisions if any(tag in d.tags for tag in tags)]
        
        return {
            "success": True,
            "decisions": [d.model_dump() for d in decisions],
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
    query: str,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Search through project decisions by keywords, titles, descriptions, or metadata.
    
    This tool performs full-text search across all decision fields including
    titles, descriptions, rationale, and context. It's useful when you need
    to find specific decisions but don't remember their exact details.
    
    Use Cases:
    - Find decisions related to a specific technology or pattern
    - Search for rationale behind certain architectural choices
    - Locate decisions by partial keywords
    - Research previous decisions before making similar ones
    - Find all decisions mentioning a specific component or service
    
    Args:
        query: Search query string (searches titles, descriptions, rationale)
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name (optional if project_id or workspace_path provided)
        workspace_path: Workspace directory path (optional if project_id or project_name provided)
        tags: Optional list of tags to further filter results
        
    Returns:
        Dictionary with matching decisions:
        {
            "success": True/False,
            "decisions": [...],
            "count": 3
        }
        
    Examples:
        # Search for database-related decisions
        await search_decisions(
            project_id="proj-abc-123",
            query="PostgreSQL"
        )
        
        # Search by workspace and filter by tags
        await search_decisions(
            workspace_path="/home/user/projects/myapp",
            query="authentication",
            tags=["security", "backend"]
        )
    """
    try:
        store = get_memory_store()
        
        # Resolve project identifier
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        
        if not success:
            return {
                "success": False,
                "error": message,
                "error_type": "ProjectNotFound"
            }
        
        decisions = store.search_decisions(resolved_id, query, tags)
        
        return {
            "success": True,
            "decisions": [d.model_dump() for d in decisions],
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
    category: str,
    technology: str,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    version: str = "",
    rationale: str = "",
    decision_ref: str = ""
) -> Dict[str, Any]:
    """
    Update or add technology stack information for a project.
    
    Records the technologies, frameworks, and tools used in different categories
    of the project (backend, frontend, database, infrastructure). This creates
    a living document of the project's technology choices.
    
    Use Cases:
    - Documenting the backend framework choice (FastAPI, Django, Express)
    - Recording frontend technologies (React, Vue, Angular)
    - Tracking database systems (PostgreSQL, MongoDB, Redis)
    - Noting infrastructure tools (Docker, Kubernetes, AWS)
    - Updating versions when upgrades occur
    - Linking tech choices to their underlying decisions
    
    Args:
        category: Technology category - "backend", "frontend", "database", or "infrastructure"
        technology: Technology name (e.g., "FastAPI", "React", "PostgreSQL")
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name (optional if project_id or workspace_path provided)
        workspace_path: Workspace directory path (optional if project_id or project_name provided)
        version: Version string (e.g., "3.11", "18.2.0")
        rationale: Why this technology was chosen (optional but recommended)
        decision_ref: Reference to a related decision ID (optional)
        
    Returns:
        Dictionary with success status:
        {
            "success": True/False,
            "message": "Tech stack updated: backend = FastAPI"
        }
        
    Examples:
        # Update by project ID
        await update_tech_stack(
            project_id="proj-abc-123",
            category="backend",
            technology="FastAPI",
            version="0.104.0",
            rationale="High performance, async support, type hints"
        )
        
        # Update by workspace path
        await update_tech_stack(
            workspace_path="/home/user/projects/myapp",
            category="database",
            technology="PostgreSQL",
            version="15",
            decision_ref="dec-xyz-789"
        )
    """
    try:
        store = get_memory_store()
        
        # Resolve project identifier
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        
        if not success:
            return {
                "success": False,
                "error": message,
                "error_type": "ProjectNotFound"
            }
        
        entry = TechStackEntry(
            category=category,
            technology=technology,
            version=version,
            rationale=rationale,
            decision_ref=decision_ref if decision_ref else None
        )
        
        store.update_tech_stack(resolved_id, entry)
        
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
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the current technology stack for a project.
    
    Retrieves all recorded technologies, frameworks, and tools used in the project.
    Can optionally filter by category to get specific sections (backend, frontend, etc.).
    
    Use Cases:
    - Review all technologies used in the project
    - Check what backend framework is being used
    - Verify database technologies
    - See infrastructure and deployment tools
    - Understand the complete tech landscape
    
    Args:
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name (optional if project_id or workspace_path provided)
        workspace_path: Workspace directory path (optional if project_id or project_name provided)
        category: Optional specific category to retrieve ("backend", "frontend", "database", "infrastructure")
        
    Returns:
        Dictionary with tech stack information:
        {
            "success": True/False,
            "tech_stack": {
                "backend": [{"technology": "FastAPI", "version": "0.104.0", ...}],
                "frontend": [{"technology": "React", "version": "18.2.0", ...}],
                "database": [{"technology": "PostgreSQL", "version": "15", ...}],
                "infrastructure": [...]
            }
        }
        
    Examples:
        # Get full tech stack by project ID
        await get_tech_stack(project_id="proj-abc-123")
        
        # Get only database technologies by workspace
        await get_tech_stack(
            workspace_path="/home/user/projects/myapp",
            category="database"
        )
        
        # Get backend stack by project name
        await get_tech_stack(
            project_name="My App",
            category="backend"
        )
    """
    try:
        store = get_memory_store()
        
        # Resolve project identifier
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        
        if not success:
            return {
                "success": False,
                "error": message,
                "error_type": "ProjectNotFound"
            }
        
        tech_stack = store.get_tech_stack(resolved_id, category)
        
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
    file_path: str,
    change_type: str,
    description: str,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    agent_id: str = "",
    code_summary: str = "",
    architecture_impact: str = "none",
    related_decision: str = ""
) -> Dict[str, Any]:
    """
    Log a change to project files or architecture for tracking and auditing.
    
    Records modifications to the codebase including file creations, updates,
    deletions, and refactors. This creates an audit trail of changes and
    helps track the evolution of the project over time.
    
    Use Cases:
    - Tracking file modifications during development
    - Recording architectural changes with impact assessment
    - Creating an audit trail of who changed what and when
    - Linking changes to architectural decisions
    - Monitoring significant vs minor changes
    
    Args:
        file_path: Path of the file changed (relative to project root)
        change_type: Type of change - "create", "modify", "delete", or "refactor"
        description: Detailed description of what changed and why
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name (optional if project_id or workspace_path provided)
        workspace_path: Workspace directory path (optional if project_id or project_name provided)
        agent_id: ID of the agent making the change (optional)
        code_summary: Brief summary of code changes (optional)
        architecture_impact: Impact level - "none", "minor", or "significant"
        related_decision: ID of related architectural decision (optional)
        
    Returns:
        Dictionary with change_id and success status:
        {
            "success": True/False,
            "change_id": "change-uuid-123",
            "message": "Change logged for src/main.py"
        }
        
    Examples:
        # Log a file creation by project ID
        await log_change(
            project_id="proj-abc-123",
            file_path="src/models/user.py",
            change_type="create",
            description="Added User model with authentication fields",
            agent_id="agent-1",
            architecture_impact="significant"
        )
        
        # Log a modification by workspace path
        await log_change(
            workspace_path="/home/user/projects/myapp",
            file_path="config/database.py",
            change_type="modify",
            description="Updated connection pooling settings",
            architecture_impact="minor"
        )
    """
    try:
        store = get_memory_store()
        
        # Resolve project identifier
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        
        if not success:
            return {
                "success": False,
                "error": message,
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
        
        change_id = store.log_change(resolved_id, change)
        
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
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    limit: int = 20,
    architecture_impact_filter: str = "all"
) -> Dict[str, Any]:
    """
    Get recent changes made to a project.
    
    Retrieves the most recent changes logged for a project, useful for
    understanding recent development activity and tracking the evolution
    of the codebase. Can filter by architectural impact level.
    
    Use Cases:
    - Review recent development activity
    - Find the latest significant architectural changes
    - Track what files were recently modified
    - Monitor development velocity and patterns
    - Identify recent breaking changes
    
    Args:
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name (optional if project_id or workspace_path provided)
        workspace_path: Workspace directory path (optional if project_id or project_name provided)
        limit: Maximum number of changes to return (default: 20)
        architecture_impact_filter: Filter by impact - "all", "none", "minor", or "significant"
        
    Returns:
        Dictionary with list of recent changes:
        {
            "success": True/False,
            "changes": [
                {
                    "id": "...",
                    "file_path": "src/main.py",
                    "change_type": "modify",
                    "description": "...",
                    "timestamp": "...",
                    "architecture_impact": "significant"
                }
            ],
            "count": 10
        }
        
    Examples:
        # Get last 20 changes by project ID
        await get_recent_changes(project_id="proj-abc-123")
        
        # Get only significant changes by workspace
        await get_recent_changes(
            workspace_path="/home/user/projects/myapp",
            limit=10,
            architecture_impact_filter="significant"
        )
        
        # Get recent changes by project name
        await get_recent_changes(
            project_name="My App",
            limit=50
        )
    """
    try:
        store = get_memory_store()
        
        # Resolve project identifier
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        
        if not success:
            return {
                "success": False,
                "error": message,
                "error_type": "ProjectNotFound"
            }
        
        impact_filter = None if architecture_impact_filter == "all" else architecture_impact_filter
        changes = store.get_recent_changes(resolved_id, limit, impact_filter)
        
        return {
            "success": True,
            "changes": [c.model_dump() for c in changes],
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
    file_path: str,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
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
    
    Records detailed information about project files including their purpose,
    dependencies, complexity, and relationships to other files. This helps
    understand the codebase structure and navigate large projects.
    
    Use Cases:
    - Documenting file purposes and responsibilities
    - Tracking file dependencies and relationships
    - Recording code complexity metrics
    - Maintaining module organization
    - Tracking who last modified files
    - Building dependency graphs
    
    Args:
        file_path: File path (relative to project root)
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name (optional if project_id or workspace_path provided)
        workspace_path: Workspace directory path (optional if project_id or project_name provided)
        file_type: File type - "source", "test", "config", or "doc" (default: "source")
        module: Module/component name this file belongs to
        purpose: Description of the file's purpose and responsibilities
        dependencies: List of files this file depends on (imports, includes)
        dependents: List of files that depend on this file
        lines_of_code: Number of lines of code (optional metric)
        complexity: Complexity level - "low", "medium", or "high"
        last_modified_by: ID of agent who last modified the file
        
    Returns:
        Dictionary with success status:
        {
            "success": True/False,
            "message": "File metadata updated for src/models/user.py"
        }
        
    Examples:
        # Update metadata by project ID
        await update_file_metadata(
            project_id="proj-abc-123",
            file_path="src/models/user.py",
            file_type="source",
            module="models",
            purpose="User model with authentication and validation",
            dependencies=["src/database.py", "src/utils/crypto.py"],
            complexity="medium",
            lines_of_code=150
        )
        
        # Update by workspace path
        await update_file_metadata(
            workspace_path="/home/user/projects/myapp",
            file_path="tests/test_api.py",
            file_type="test",
            module="api_tests",
            purpose="API endpoint tests",
            dependents=["src/api/routes.py"]
        )
    """
    try:
        store = get_memory_store()
        
        # Resolve project identifier
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        
        if not success:
            return {
                "success": False,
                "error": message,
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
        
        store.update_file_metadata(resolved_id, metadata)
        
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
    file_path: str,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    direction: str = "dependencies"
) -> Dict[str, Any]:
    """
    Get dependency graph for a file.
    
    Retrieves the dependency relationships for a specific file, showing
    either what files it depends on (dependencies), what files depend on
    it (dependents), or both. Useful for understanding code coupling and
    impact analysis.
    
    Use Cases:
    - Understanding what a file imports or depends on
    - Finding which files would be affected by changes
    - Analyzing code coupling and dependencies
    - Impact analysis before refactoring
    - Navigating complex codebases
    
    Args:
        file_path: File path to analyze (relative to project root)
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name (optional if project_id or workspace_path provided)
        workspace_path: Workspace directory path (optional if project_id or project_name provided)
        direction: Direction to analyze - "dependencies", "dependents", or "both"
        
    Returns:
        Dictionary with file dependencies:
        {
            "success": True/False,
            "file_path": "src/models/user.py",
            "direction": "dependencies",
            "dependencies": [
                "src/database.py",
                "src/utils/crypto.py"
            ]
        }
        
    Examples:
        # Get what a file depends on by project ID
        await get_file_dependencies(
            project_id="proj-abc-123",
            file_path="src/models/user.py",
            direction="dependencies"
        )
        
        # Get what depends on a file by workspace
        await get_file_dependencies(
            workspace_path="/home/user/projects/myapp",
            file_path="src/config.py",
            direction="dependents"
        )
        
        # Get both directions by project name
        await get_file_dependencies(
            project_name="My App",
            file_path="src/api/routes.py",
            direction="both"
        )
    """
    try:
        store = get_memory_store()
        
        # Resolve project identifier
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        
        if not success:
            return {
                "success": False,
                "error": message,
                "error_type": "ProjectNotFound"
            }
        
        deps = store.get_file_dependencies(resolved_id, file_path, direction)
        
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
    module_name: str,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get detailed information about a project module.
    
    Retrieves comprehensive information about a specific module including
    its metadata, purpose, and all files that belong to it. Modules are
    logical groupings of files (e.g., "authentication", "database", "api").
    
    Use Cases:
    - Understanding module boundaries and responsibilities
    - Finding all files in a specific module
    - Analyzing module structure and organization
    - Understanding module dependencies and relationships
    - Getting an overview of a specific component
    
    Args:
        module_name: Name of the module to retrieve information about
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name (optional if project_id or workspace_path provided)
        workspace_path: Workspace directory path (optional if project_id or project_name provided)
        
    Returns:
        Dictionary with module information:
        {
            "success": True/False,
            "module": {
                "name": "authentication",
                "description": "User authentication and authorization",
                "responsibilities": ["login", "logout", "token management"],
                ...
            },
            "files": [
                {"path": "src/auth/login.py", ...},
                {"path": "src/auth/tokens.py", ...}
            ],
            "file_count": 5
        }
        
    Examples:
        # Get module info by project ID
        await get_module_info(
            project_id="proj-abc-123",
            module_name="authentication"
        )
        
        # Get module info by workspace path
        await get_module_info(
            workspace_path="/home/user/projects/myapp",
            module_name="database"
        )
        
        # Get module info by project name
        await get_module_info(
            project_name="My App",
            module_name="api"
        )
    """
    try:
        store = get_memory_store()
        
        # Resolve project identifier
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        
        if not success:
            return {
                "success": False,
                "error": message,
                "error_type": "ProjectNotFound"
            }
        
        module = store.get_architecture_module(resolved_id, module_name)
        files = store.get_files_by_module(resolved_id, module_name)
        
        return {
            "success": True,
            "module": module.model_dump() if module else None,
            "files": [f.model_dump() for f in files],
            "file_count": len(files)
        }
    except Exception as e:
        logger.error(f"Error getting module info: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }
