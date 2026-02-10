"""
Architecture tools for CoordMCP FastMCP server.
"""

from typing import List, Dict, Any

from coordmcp.core.server import get_storage
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


async def analyze_architecture(project_id: str):
    """Analyze current project architecture."""
    try:
        store = get_memory_store()
        if not store.project_exists(project_id):
            return {"success": False, "error": f"Project {project_id} not found"}
        
        analyzer = get_analyzer()
        return analyzer.analyze_project(project_id)
    except Exception as e:
        logger.error(f"Error analyzing architecture: {e}")
        return {"success": False, "error": str(e)}


async def get_architecture_recommendation(
    project_id: str,
    feature_description: str,
    context: str = "",
    constraints: List[str] = [],
    implementation_style: str = "modular"
):
    """Get architectural recommendation for a new feature or change."""
    try:
        store = get_memory_store()
        if not store.project_exists(project_id):
            return {"success": False, "error": f"Project {project_id} not found"}
        
        recommender = get_recommender()
        return recommender.recommend_structure(
            project_id=project_id,
            feature_description=feature_description,
            context=context,
            constraints=constraints,
            implementation_style=implementation_style
        )
    except Exception as e:
        logger.error(f"Error getting recommendation: {e}")
        return {"success": False, "error": str(e)}


async def validate_code_structure(
    project_id: str,
    file_path: str,
    code_structure: Dict,
    strict_mode: bool = False
):
    """Validate if proposed code structure follows architectural guidelines."""
    try:
        store = get_memory_store()
        if not store.project_exists(project_id):
            return {"success": False, "error": f"Project {project_id} not found"}
        
        validator = CodeStructureValidator()
        return validator.validate(
            project_id=project_id,
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
    project_id: str,
    recommendation_id: str,
    implementation_summary: str,
    actual_files_created: List[str] = [],
    actual_files_modified: List[str] = []
):
    """Update project architecture after implementation."""
    try:
        store = get_memory_store()
        if not store.project_exists(project_id):
            return {"success": False, "error": f"Project {project_id} not found"}
        
        from coordmcp.memory.models import Change
        from datetime import datetime
        from uuid import uuid4
        
        change = Change(
            id=str(uuid4()),
            timestamp=datetime.now(),
            file_path="architecture",
            change_type="modify",
            description=f"Implemented architecture recommendation {recommendation_id}: {implementation_summary}",
            architecture_impact="significant",
            code_summary=f"Files created: {len(actual_files_created)}, Files modified: {len(actual_files_modified)}"
        )
        
        store.log_change(project_id, change)
        
        return {
            "success": True,
            "message": "Architecture updated successfully",
            "files_created": len(actual_files_created),
            "files_modified": len(actual_files_modified)
        }
    except Exception as e:
        logger.error(f"Error updating architecture: {e}")
        return {"success": False, "error": str(e)}
