"""
Architecture tools for CoordMCP FastMCP server.
"""

from typing import List, Dict, Any, Optional

from coordmcp.core.server import get_storage
from coordmcp.tools.memory_tools import resolve_project_id
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.architecture.analyzer import ArchitectureAnalyzer
from coordmcp.architecture.recommender import ArchitectureRecommender
from coordmcp.architecture.validators import CodeStructureValidator
from coordmcp.architecture.patterns import (
    get_pattern, get_all_patterns, get_patterns_for_feature
)
from coordmcp.logger import get_logger

logger = get_logger("tools.architecture")


def get_memory_store():
    """Get ProjectMemoryStore instance."""
    storage = get_storage()
    return ProjectMemoryStore(storage)


def get_analyzer():
    """Get ArchitectureAnalyzer instance."""
    return ArchitectureAnalyzer(get_memory_store())


def get_recommender():
    """Get ArchitectureRecommender instance."""
    store = get_memory_store()
    return ArchitectureRecommender(store, ArchitectureAnalyzer(store))


async def analyze_architecture(
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None
):
    """
    Analyze current project architecture.
    
    Args:
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name to look up (alternative to project_id)
        workspace_path: Workspace path to look up (alternative to project_id)
        
    Returns:
        Dictionary with architecture analysis results
        
    Examples:
        # By project ID
        result = await analyze_architecture(project_id="proj-456")
        
        # By project name
        result = await analyze_architecture(project_name="My Project")
        
        # By workspace path
        result = await analyze_architecture(workspace_path="/path/to/project")
    """
    try:
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
        
        store = get_memory_store()
        if not store.project_exists(resolved_id):
            return {"success": False, "error": f"Project {resolved_id} not found"}
        
        analyzer = get_analyzer()
        return analyzer.analyze_project(resolved_id)
    except Exception as e:
        logger.error(f"Error analyzing architecture: {e}")
        return {"success": False, "error": str(e)}


async def get_architecture_recommendation(
    feature_description: str,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    context: str = "",
    constraints: List[str] = [],
    implementation_style: str = "modular"
):
    """
    Get architectural recommendation for a new feature or change.
    
    Args:
        feature_description: Description of the feature to implement
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name to look up (alternative to project_id)
        workspace_path: Workspace path to look up (alternative to project_id)
        context: Additional context for the recommendation
        constraints: List of constraints to consider
        implementation_style: Preferred implementation style
        
    Returns:
        Dictionary with architectural recommendation
        
    Examples:
        # By project ID
        result = await get_architecture_recommendation(
            project_id="proj-456",
            feature_description="Add user authentication"
        )
        
        # By project name
        result = await get_architecture_recommendation(
            project_name="My Project",
            feature_description="Add user authentication"
        )
        
        # By workspace path
        result = await get_architecture_recommendation(
            workspace_path="/path/to/project",
            feature_description="Add user authentication"
        )
    """
    try:
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
        
        store = get_memory_store()
        if not store.project_exists(resolved_id):
            return {"success": False, "error": f"Project {resolved_id} not found"}
        
        recommender = get_recommender()
        return recommender.recommend_structure(
            project_id=resolved_id,
            feature_description=feature_description,
            context=context,
            constraints=constraints,
            implementation_style=implementation_style
        )
    except Exception as e:
        logger.error(f"Error getting recommendation: {e}")
        return {"success": False, "error": str(e)}


async def validate_code_structure(
    file_path: str,
    code_structure: Dict,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    strict_mode: bool = False
):
    """
    Validate if proposed code structure follows architectural guidelines.
    
    Args:
        file_path: Path to the file being validated
        code_structure: The code structure to validate
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name to look up (alternative to project_id)
        workspace_path: Workspace path to look up (alternative to project_id)
        strict_mode: Whether to use strict validation rules
        
    Returns:
        Dictionary with validation results
        
    Examples:
        # By project ID
        result = await validate_code_structure(
            project_id="proj-456",
            file_path="src/main.py",
            code_structure={...}
        )
        
        # By project name
        result = await validate_code_structure(
            project_name="My Project",
            file_path="src/main.py",
            code_structure={...}
        )
        
        # By workspace path
        result = await validate_code_structure(
            workspace_path="/path/to/project",
            file_path="src/main.py",
            code_structure={...}
        )
    """
    try:
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
        
        store = get_memory_store()
        if not store.project_exists(resolved_id):
            return {"success": False, "error": f"Project {resolved_id} not found"}
        
        validator = CodeStructureValidator()
        return validator.validate(
            project_id=resolved_id,
            file_path=file_path,
            code_structure=code_structure,
            strict=strict_mode
        )
    except Exception as e:
        logger.error(f"Error validating code: {e}")
        return {"success": False, "error": str(e)}


async def get_design_patterns():
    """Get all available design patterns."""
    try:
        patterns = get_all_patterns()
        return {
            "success": True,
            "patterns": [
                {"name": name, "description": info["description"], "best_for": info["best_for"]}
                for name, info in patterns.items()
            ],
            "count": len(patterns)
        }
    except Exception as e:
        logger.error(f"Error getting patterns: {e}")
        return {"success": False, "error": str(e)}


async def update_architecture(
    recommendation_id: str,
    implementation_summary: str,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None,
    actual_files_created: List[str] = [],
    actual_files_modified: List[str] = []
):
    """
    Update project architecture after implementation.
    
    Args:
        recommendation_id: ID of the architecture recommendation being implemented
        implementation_summary: Summary of what was implemented
        project_id: Project ID (optional if project_name or workspace_path provided)
        project_name: Project name to look up (alternative to project_id)
        workspace_path: Workspace path to look up (alternative to project_id)
        actual_files_created: List of files that were created
        actual_files_modified: List of files that were modified
        
    Returns:
        Dictionary with update results
        
    Examples:
        # By project ID
        result = await update_architecture(
            project_id="proj-456",
            recommendation_id="rec-789",
            implementation_summary="Added auth module"
        )
        
        # By project name
        result = await update_architecture(
            project_name="My Project",
            recommendation_id="rec-789",
            implementation_summary="Added auth module"
        )
        
        # By workspace path
        result = await update_architecture(
            workspace_path="/path/to/project",
            recommendation_id="rec-789",
            implementation_summary="Added auth module"
        )
    """
    try:
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
        
        store = get_memory_store()
        if not store.project_exists(resolved_id):
            return {"success": False, "error": f"Project {resolved_id} not found"}
        
        from coordmcp.memory.models import Change
        from datetime import datetime
        from uuid import uuid4
        
        from coordmcp.memory.models import ChangeType, ArchitectureImpact
        change = Change(
            id=str(uuid4()),
            file_path="architecture",
            change_type=ChangeType.MODIFY,
            description=f"Implemented architecture recommendation {recommendation_id}: {implementation_summary}",
            architecture_impact=ArchitectureImpact.SIGNIFICANT,
            code_summary=f"Files created: {len(actual_files_created)}, Files modified: {len(actual_files_modified)}"
        )
        
        store.log_change(resolved_id, change)
        
        return {
            "success": True,
            "message": "Architecture updated successfully",
            "files_created": len(actual_files_created),
            "files_modified": len(actual_files_modified)
        }
    except Exception as e:
        logger.error(f"Error updating architecture: {e}")
        return {"success": False, "error": str(e)}
