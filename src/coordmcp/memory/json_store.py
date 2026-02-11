"""
Project memory store implementation for CoordMCP.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from coordmcp.storage.base import StorageBackend
from coordmcp.memory.models import (
    Decision, TechStackEntry, Change, FileMetadata,
    ProjectInfo, ArchitectureModule, DecisionIndex, PaginatedChanges
)
from coordmcp.logger import get_logger

logger = get_logger("memory.store")


class ProjectMemoryStore:
    """Manages project memory including decisions, tech stack, changes, and file metadata."""
    
    def __init__(self, storage_backend: StorageBackend):
        """
        Initialize the project memory store.
        
        Args:
            storage_backend: Storage backend implementation
        """
        self.backend = storage_backend
        logger.info("ProjectMemoryStore initialized")
    
    def _get_project_key(self, project_id: str) -> str:
        """Get storage key for project info."""
        return f"memory/{project_id}/project_info"
    
    def _get_decisions_key(self, project_id: str) -> str:
        """Get storage key for decisions."""
        return f"memory/{project_id}/decisions"
    
    def _get_decisions_index_key(self, project_id: str) -> str:
        """Get storage key for decisions index."""
        return f"memory/{project_id}/decisions_index"
    
    def _get_tech_stack_key(self, project_id: str) -> str:
        """Get storage key for tech stack."""
        return f"memory/{project_id}/tech_stack"
    
    def _get_changes_key(self, project_id: str) -> str:
        """Get storage key for changes."""
        return f"memory/{project_id}/changes"
    
    def _get_file_metadata_key(self, project_id: str) -> str:
        """Get storage key for file metadata."""
        return f"memory/{project_id}/file_metadata"
    
    def _get_architecture_key(self, project_id: str) -> str:
        """Get storage key for architecture."""
        return f"memory/{project_id}/architecture"
    
    # ==================== Project Management ====================
    
    def create_project(self, project_name: str, description: str = "") -> str:
        """
        Create a new project.
        
        Args:
            project_name: Name of the project
            description: Project description
            
        Returns:
            Project ID
        """
        project_id = str(uuid4())
        project_info = ProjectInfo(
            project_id=project_id,
            project_name=project_name,
            description=description,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        # Save project info
        self.backend.save(
            self._get_project_key(project_id),
            project_info.to_dict()
        )
        
        # Initialize empty collections
        self.backend.save(self._get_decisions_key(project_id), {"decisions": {}})
        self.backend.save(self._get_tech_stack_key(project_id), {"tech_stack": {}})
        self.backend.save(self._get_changes_key(project_id), {"changes": []})
        self.backend.save(self._get_file_metadata_key(project_id), {"files": {}})
        self.backend.save(self._get_architecture_key(project_id), {"architecture": {}})
        
        logger.info(f"Created project '{project_name}' with ID {project_id}")
        return project_id
    
    def project_exists(self, project_id: str) -> bool:
        """Check if a project exists."""
        return self.backend.exists(self._get_project_key(project_id))
    
    def get_project_info(self, project_id: str) -> Optional[ProjectInfo]:
        """Get project information."""
        data = self.backend.load(self._get_project_key(project_id))
        if data:
            return ProjectInfo.from_dict(data)
        return None
    
    def update_project_info(self, project_id: str, **kwargs) -> bool:
        """Update project information."""
        project_info = self.get_project_info(project_id)
        if not project_info:
            return False
        
        for key, value in kwargs.items():
            if hasattr(project_info, key):
                setattr(project_info, key, value)
        
        project_info.last_updated = datetime.now()
        
        self.backend.save(
            self._get_project_key(project_id),
            project_info.to_dict()
        )
        return True
    
    # ==================== Decision Management ====================
    
    def save_decision(self, project_id: str, decision: Decision) -> str:
        """
        Save a decision to project memory.
        
        Args:
            project_id: Project ID
            decision: Decision object to save
            
        Returns:
            Decision ID
        """
        if not self.project_exists(project_id):
            raise ValueError(f"Project {project_id} does not exist")
        
        # Save decision
        key = self._get_decisions_key(project_id)
        data = self.backend.load(key) or {"decisions": {}}
        data["decisions"][decision.id] = decision.to_dict()
        self.backend.save(key, data)
        
        # Update search index
        index = self._get_decisions_index(project_id)
        index.add_decision(decision)
        self._save_decisions_index(project_id, index)
        
        self.update_project_info(project_id)
        
        logger.info(f"Saved decision '{decision.title}' for project {project_id}")
        return decision.id
    
    def _get_decisions_index(self, project_id: str) -> DecisionIndex:
        """Get or create the decisions search index."""
        key = self._get_decisions_index_key(project_id)
        data = self.backend.load(key)
        if data:
            return DecisionIndex.from_dict(data.get("index", {}))
        return DecisionIndex()
    
    def _save_decisions_index(self, project_id: str, index: DecisionIndex) -> None:
        """Save the decisions search index."""
        key = self._get_decisions_index_key(project_id)
        self.backend.save(key, {"index": index.to_dict()})
    
    def get_decision(self, project_id: str, decision_id: str) -> Optional[Decision]:
        """Get a specific decision."""
        key = self._get_decisions_key(project_id)
        data = self.backend.load(key)
        
        if data and decision_id in data.get("decisions", {}):
            return Decision.from_dict(data["decisions"][decision_id])
        return None
    
    def get_all_decisions(self, project_id: str) -> List[Decision]:
        """Get all decisions for a project."""
        key = self._get_decisions_key(project_id)
        data = self.backend.load(key)
        
        if not data:
            return []
        
        decisions = []
        for decision_data in data.get("decisions", {}).values():
            decisions.append(Decision.from_dict(decision_data))
        
        # Sort by timestamp (newest first)
        decisions.sort(key=lambda d: d.timestamp, reverse=True)
        return decisions
    
    def get_decisions_by_status(self, project_id: str, status: str) -> List[Decision]:
        """Get decisions filtered by status."""
        all_decisions = self.get_all_decisions(project_id)
        return [d for d in all_decisions if d.status == status]
    
    def search_decisions(self, project_id: str, query: str, tags: Optional[List[str]] = None) -> List[Decision]:
        """
        Search decisions by query string and optional tags.
        Uses indexed search for fast performance.
        
        Args:
            project_id: Project ID
            query: Search query string
            tags: Optional list of tags to filter by
            
        Returns:
            List of matching decisions
        """
        # Get all decisions as a map for indexed search
        all_decisions = self.get_all_decisions(project_id)
        decisions_map = {d.id: d for d in all_decisions}
        
        # Use index for fast search if we have decisions
        if decisions_map:
            index = self._get_decisions_index(project_id)
            results = index.search(query, decisions_map)
            
            # Filter by tags if provided
            if tags:
                results = [d for d in results if any(tag in d.tags for tag in tags)]
            
            return results
        
        return []
    
    def update_decision_status(self, project_id: str, decision_id: str, status: str) -> bool:
        """Update the status of a decision."""
        decision = self.get_decision(project_id, decision_id)
        if not decision:
            return False
        
        decision.status = status
        self.save_decision(project_id, decision)
        return True
    
    # ==================== Tech Stack Management ====================
    
    def update_tech_stack(self, project_id: str, entry: TechStackEntry) -> None:
        """
        Update or add a tech stack entry.
        
        Args:
            project_id: Project ID
            entry: TechStackEntry to add/update
        """
        if not self.project_exists(project_id):
            raise ValueError(f"Project {project_id} does not exist")
        
        key = self._get_tech_stack_key(project_id)
        data = self.backend.load(key) or {"tech_stack": {}}
        
        # Store by category
        if "tech_stack" not in data:
            data["tech_stack"] = {}
        
        data["tech_stack"][entry.category] = entry.to_dict()
        
        self.backend.save(key, data)
        self.update_project_info(project_id)
        
        logger.info(f"Updated tech stack for project {project_id}: {entry.category} = {entry.technology}")
    
    def get_tech_stack(self, project_id: str, category: Optional[str] = None) -> Dict:
        """
        Get tech stack information.
        
        Args:
            project_id: Project ID
            category: Optional category to get specific entry
            
        Returns:
            Tech stack dictionary or specific entry
        """
        key = self._get_tech_stack_key(project_id)
        data = self.backend.load(key)
        
        if not data:
            return {}
        
        tech_stack = data.get("tech_stack", {})
        
        if category:
            return tech_stack.get(category, {})
        
        return tech_stack
    
    def get_tech_stack_entry(self, project_id: str, category: str) -> Optional[TechStackEntry]:
        """Get a specific tech stack entry."""
        tech_stack = self.get_tech_stack(project_id, category)
        if tech_stack:
            return TechStackEntry.from_dict(category, tech_stack)
        return None
    
    # ==================== Change Log Management ====================
    
    def log_change(self, project_id: str, change: Change) -> str:
        """
        Log a change to the project.
        
        Args:
            project_id: Project ID
            change: Change object to log
            
        Returns:
            Change ID
        """
        if not self.project_exists(project_id):
            raise ValueError(f"Project {project_id} does not exist")
        
        key = self._get_changes_key(project_id)
        data = self.backend.load(key) or {"changes": []}
        
        if "changes" not in data:
            data["changes"] = []
        
        data["changes"].append(change.to_dict())
        
        self.backend.save(key, data)
        self.update_project_info(project_id)
        
        logger.info(f"Logged change '{change.change_type}' for file {change.file_path}")
        return change.id
    
    def get_recent_changes(self, project_id: str, limit: int = 20, 
                          impact_filter: Optional[str] = None) -> List[Change]:
        """
        Get recent changes for a project.
        
        Args:
            project_id: Project ID
            limit: Maximum number of changes to return
            impact_filter: Filter by architecture impact (none, minor, significant)
            
        Returns:
            List of changes (newest first)
        """
        key = self._get_changes_key(project_id)
        data = self.backend.load(key)
        
        if not data:
            return []
        
        changes = []
        for change_data in data.get("changes", []):
            change = Change.from_dict(change_data)
            
            # Apply impact filter if specified
            if impact_filter and impact_filter != "all":
                if change.architecture_impact != impact_filter:
                    continue
            
            changes.append(change)
        
        # Sort by timestamp (newest first)
        changes.sort(key=lambda c: c.timestamp, reverse=True)
        
        return changes[:limit]
    
    def get_changes_for_file(self, project_id: str, file_path: str, limit: int = 10) -> List[Change]:
        """Get changes for a specific file."""
        all_changes = self.get_recent_changes(project_id, limit=1000)
        file_changes = [c for c in all_changes if c.file_path == file_path]
        return file_changes[:limit]
    
    # ==================== File Metadata Management ====================
    
    def update_file_metadata(self, project_id: str, metadata: FileMetadata) -> None:
        """
        Update or add file metadata.
        
        Args:
            project_id: Project ID
            metadata: FileMetadata to add/update
        """
        if not self.project_exists(project_id):
            raise ValueError(f"Project {project_id} does not exist")
        
        key = self._get_file_metadata_key(project_id)
        data = self.backend.load(key) or {"files": {}}
        
        if "files" not in data:
            data["files"] = {}
        
        data["files"][metadata.path] = metadata.to_dict()
        
        self.backend.save(key, data)
        self.update_project_info(project_id)
        
        logger.debug(f"Updated file metadata for {metadata.path}")
    
    def get_file_metadata(self, project_id: str, file_path: str) -> Optional[FileMetadata]:
        """Get metadata for a specific file."""
        key = self._get_file_metadata_key(project_id)
        data = self.backend.load(key)
        
        if data and file_path in data.get("files", {}):
            return FileMetadata.from_dict(file_path, data["files"][file_path])
        return None
    
    def get_all_file_metadata(self, project_id: str) -> List[FileMetadata]:
        """Get metadata for all files in a project."""
        key = self._get_file_metadata_key(project_id)
        data = self.backend.load(key)
        
        if not data:
            return []
        
        files = []
        for file_path, file_data in data.get("files", {}).items():
            files.append(FileMetadata.from_dict(file_path, file_data))
        
        return files
    
    def get_files_by_module(self, project_id: str, module: str) -> List[FileMetadata]:
        """Get all files in a specific module."""
        all_files = self.get_all_file_metadata(project_id)
        return [f for f in all_files if f.module == module]
    
    def get_file_dependencies(self, project_id: str, file_path: str, direction: str = "dependencies") -> List[str]:
        """
        Get file dependencies or dependents.
        
        Args:
            project_id: Project ID
            file_path: File path to check
            direction: "dependencies" (files this file depends on) or 
                      "dependents" (files that depend on this file) or "both"
                      
        Returns:
            List of file paths
        """
        metadata = self.get_file_metadata(project_id, file_path)
        if not metadata:
            return []
        
        if direction == "dependencies":
            return metadata.dependencies
        elif direction == "dependents":
            return metadata.dependents
        elif direction == "both":
            return list(set(metadata.dependencies + metadata.dependents))
        
        return []
    
    # ==================== Architecture Management ====================
    
    def update_architecture(self, project_id: str, architecture_data: Dict) -> None:
        """
        Update project architecture information.
        
        Args:
            project_id: Project ID
            architecture_data: Architecture dictionary
        """
        if not self.project_exists(project_id):
            raise ValueError(f"Project {project_id} does not exist")
        
        key = self._get_architecture_key(project_id)
        self.backend.save(key, {"architecture": architecture_data})
        self.update_project_info(project_id)
        
        logger.info(f"Updated architecture for project {project_id}")
    
    def get_architecture(self, project_id: str) -> Dict:
        """Get project architecture information."""
        key = self._get_architecture_key(project_id)
        data = self.backend.load(key)
        
        if data:
            return data.get("architecture", {})
        return {}
    
    def add_architecture_module(self, project_id: str, module: ArchitectureModule) -> None:
        """Add or update an architecture module."""
        architecture = self.get_architecture(project_id)
        
        if "modules" not in architecture:
            architecture["modules"] = {}
        
        architecture["modules"][module.name] = module.to_dict()
        self.update_architecture(project_id, architecture)
    
    def get_architecture_module(self, project_id: str, module_name: str) -> Optional[ArchitectureModule]:
        """Get a specific architecture module."""
        architecture = self.get_architecture(project_id)
        modules = architecture.get("modules", {})
        
        if module_name in modules:
            return ArchitectureModule.from_dict(module_name, modules[module_name])
        return None
    
    def get_all_modules(self, project_id: str) -> List[ArchitectureModule]:
        """Get all architecture modules."""
        architecture = self.get_architecture(project_id)
        modules_data = architecture.get("modules", {})
        
        modules = []
        for name, data in modules_data.items():
            modules.append(ArchitectureModule.from_dict(name, data))
        
        return modules
