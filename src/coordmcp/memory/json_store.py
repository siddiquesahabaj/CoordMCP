"""
Project memory store implementation for CoordMCP.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

from coordmcp.storage.base import StorageBackend
from coordmcp.memory.models import (
    Decision, TechStackEntry, Change, FileMetadata,
    ProjectInfo, ArchitectureModule, DecisionIndex, PaginatedChanges,
    ChangeIndex, FileMetadataIndex, Relationship, RelationshipType, SCHEMA_VERSION
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
    
    def _get_changes_index_key(self, project_id: str) -> str:
        """Get storage key for changes index."""
        return f"memory/{project_id}/changes_index"
    
    def _get_file_index_key(self, project_id: str) -> str:
        """Get storage key for file metadata index."""
        return f"memory/{project_id}/file_index"
    
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
    
    def _get_relationships_key(self, project_id: str) -> str:
        """Get storage key for relationships."""
        return f"memory/{project_id}/relationships"
    
    # ==================== Project Management ====================
    
    def create_project(self, project_name: str, description: str = "", workspace_path: str = "") -> str:
        """
        Create a new project.
        
        Args:
            project_name: Name of the project
            description: Project description
            workspace_path: Absolute path to the project workspace directory (required)
            
        Returns:
            Project ID
        """
        project_id = str(uuid4())
        project_info = ProjectInfo(
            id=project_id,
            project_id=project_id,
            project_name=project_name,
            description=description,
            workspace_path=workspace_path,
            created_by="system"
        )
        
        # Save project info
        self.backend.save(
            self._get_project_key(project_id),
            project_info.dict()
        )
        
        # Initialize empty collections with schema version
        self.backend.save(self._get_decisions_key(project_id), {"_schema_version": SCHEMA_VERSION, "decisions": {}})
        self.backend.save(self._get_tech_stack_key(project_id), {"_schema_version": SCHEMA_VERSION, "tech_stack": {}})
        self.backend.save(self._get_changes_key(project_id), {"_schema_version": SCHEMA_VERSION, "changes": []})
        self.backend.save(self._get_file_metadata_key(project_id), {"_schema_version": SCHEMA_VERSION, "files": {}})
        self.backend.save(self._get_architecture_key(project_id), {"_schema_version": SCHEMA_VERSION, "architecture": {}})
        self.backend.save(self._get_relationships_key(project_id), {"_schema_version": SCHEMA_VERSION, "relationships": []})
        
        # Initialize indexes
        self.backend.save(self._get_decisions_index_key(project_id), {"_schema_version": SCHEMA_VERSION, "index": DecisionIndex().dict()})
        self.backend.save(self._get_changes_index_key(project_id), {"_schema_version": SCHEMA_VERSION, "index": ChangeIndex().dict()})
        self.backend.save(self._get_file_index_key(project_id), {"_schema_version": SCHEMA_VERSION, "index": FileMetadataIndex().dict()})
        
        logger.info(f"Created project '{project_name}' with ID {project_id}")
        return project_id
    
    def project_exists(self, project_id: str) -> bool:
        """Check if a project exists."""
        return self.backend.exists(self._get_project_key(project_id))
    
    def get_project_info(self, project_id: str) -> Optional[ProjectInfo]:
        """Get project information."""
        data = self.backend.load(self._get_project_key(project_id))
        if data:
            try:
                return ProjectInfo.parse_obj(data)
            except Exception as e:
                logger.warning(f"Failed to parse project info: {e}")
                return None
        return None
    
    def update_project_info(self, project_id: str, agent_id: str = "", **kwargs) -> bool:
        """Update project information."""
        project_info = self.get_project_info(project_id)
        if not project_info:
            return False
        
        for key, value in kwargs.items():
            if hasattr(project_info, key) and key not in ['id', 'project_id', 'created_at', 'created_by']:
                setattr(project_info, key, value)
        
        project_info.touch(agent_id)
        
        self.backend.save(
            self._get_project_key(project_id),
            project_info.dict()
        )
        return True
    
    def delete_project(self, project_id: str, agent_id: str = "", soft: bool = True) -> bool:
        """
        Delete a project (soft or hard delete).
        
        Args:
            project_id: Project ID to delete
            agent_id: Agent performing the deletion
            soft: If True, soft delete; if False, hard delete
            
        Returns:
            True if successful
        """
        project_info = self.get_project_info(project_id)
        if not project_info:
            return False
        
        if soft:
            project_info.soft_delete(agent_id)
            self.backend.save(
                self._get_project_key(project_id),
                project_info.dict()
            )
            logger.info(f"Soft deleted project {project_id}")
        else:
            # Hard delete - remove all project data
            keys_to_delete = [
                self._get_project_key(project_id),
                self._get_decisions_key(project_id),
                self._get_decisions_index_key(project_id),
                self._get_tech_stack_key(project_id),
                self._get_changes_key(project_id),
                self._get_changes_index_key(project_id),
                self._get_file_metadata_key(project_id),
                self._get_file_index_key(project_id),
                self._get_architecture_key(project_id),
                self._get_relationships_key(project_id),
            ]
            for key in keys_to_delete:
                self.backend.delete(key)
            logger.info(f"Hard deleted project {project_id}")
        
        return True
    
    def list_projects(self, include_deleted: bool = False) -> List[ProjectInfo]:
        """List all projects."""
        # This would need to scan the storage backend for all project keys
        # Implementation depends on storage backend capabilities
        # For now, return empty list (to be implemented based on storage)
        return []
    
    # ==================== Decision Management ====================
    
    def save_decision(self, project_id: str, decision: Decision, agent_id: str = "") -> str:
        """
        Save a decision to project memory.
        
        Args:
            project_id: Project ID
            decision: Decision object to save
            agent_id: Agent saving the decision
            
        Returns:
            Decision ID
        """
        if not self.project_exists(project_id):
            raise ValueError(f"Project {project_id} does not exist")
        
        decision.touch(agent_id)
        
        # Save decision
        key = self._get_decisions_key(project_id)
        data = self.backend.load(key) or {"_schema_version": SCHEMA_VERSION, "decisions": {}}
        data["decisions"][decision.id] = decision.dict()
        self.backend.save(key, data)
        
        # Update search index
        index = self._get_decisions_index(project_id)
        index.add_decision(decision)
        self._save_decisions_index(project_id, index)
        
        # Create relationships
        for file_path in decision.related_files:
            self._create_relationship(
                project_id, "decision", decision.id, 
                "file", file_path, RelationshipType("references")
            )
        
        self.update_project_info(project_id, agent_id)
        
        logger.info(f"Saved decision '{decision.title}' for project {project_id}")
        return decision.id
    
    def _get_decisions_index(self, project_id: str) -> DecisionIndex:
        """Get or create the decisions search index."""
        key = self._get_decisions_index_key(project_id)
        data = self.backend.load(key)
        if data and "index" in data:
            try:
                return DecisionIndex.parse_obj(data["index"])
            except Exception as e:
                logger.warning(f"Failed to parse decisions index: {e}")
        return DecisionIndex()
    
    def _save_decisions_index(self, project_id: str, index: DecisionIndex) -> None:
        """Save the decisions search index."""
        key = self._get_decisions_index_key(project_id)
        self.backend.save(key, {"_schema_version": SCHEMA_VERSION, "index": index.dict()})
    
    def get_decision(self, project_id: str, decision_id: str) -> Optional[Decision]:
        """Get a specific decision."""
        key = self._get_decisions_key(project_id)
        data = self.backend.load(key)
        
        if data and decision_id in data.get("decisions", {}):
            try:
                decision = Decision.parse_obj(data["decisions"][decision_id])
                return decision if not decision.is_deleted else None
            except Exception as e:
                logger.warning(f"Failed to parse decision: {e}")
        return None
    
    def get_all_decisions(self, project_id: str, include_deleted: bool = False) -> List[Decision]:
        """Get all decisions for a project."""
        key = self._get_decisions_key(project_id)
        data = self.backend.load(key)
        
        if not data:
            return []
        
        decisions = []
        for decision_data in data.get("decisions", {}).values():
            try:
                decision = Decision.parse_obj(decision_data)
                if include_deleted or not decision.is_deleted:
                    decisions.append(decision)
            except Exception as e:
                logger.warning(f"Failed to parse decision: {e}")
        
        # Sort by timestamp (newest first)
        decisions.sort(key=lambda d: d.created_at, reverse=True)
        return decisions
    
    def get_decisions_by_status(self, project_id: str, status: str) -> List[Decision]:
        """Get decisions filtered by status."""
        all_decisions = self.get_all_decisions(project_id)
        return [d for d in all_decisions if d.status.value == status]
    
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
        all_decisions = self.get_all_decisions(project_id)
        decisions_map = {d.id: d for d in all_decisions}
        
        if decisions_map:
            index = self._get_decisions_index(project_id)
            results = index.search(query, decisions_map)
            
            # Filter by tags if provided
            if tags:
                results = [d for d in results if any(tag in d.tags for tag in tags)]
            
            return results
        
        return []
    
    def update_decision_status(self, project_id: str, decision_id: str, status: str, agent_id: str = "") -> bool:
        """Update the status of a decision."""
        from coordmcp.memory.models import DecisionStatus
        
        decision = self.get_decision(project_id, decision_id)
        if not decision:
            return False
        
        decision.status = DecisionStatus(status)
        self.save_decision(project_id, decision, agent_id)
        return True
    
    def supersede_decision(self, project_id: str, old_decision_id: str, new_decision: Decision, agent_id: str = "") -> bool:
        """Supersede an old decision with a new one."""
        from coordmcp.memory.models import DecisionStatus
        
        old_decision = self.get_decision(project_id, old_decision_id)
        if not old_decision:
            return False
        
        # Create new version
        updated_new_decision = new_decision.create_new_version({
            'supersedes': [old_decision_id]
        }, agent_id)
        
        # Save new decision
        self.save_decision(project_id, updated_new_decision, agent_id)
        
        # Update old decision
        old_decision.superseded_by = updated_new_decision.id
        old_decision.status = DecisionStatus.SUPERSEDED
        old_decision.touch(agent_id)
        
        self.save_decision(project_id, old_decision, agent_id)
        
        logger.info(f"Decision {old_decision_id} superseded by {updated_new_decision.id}")
        return True
    
    def delete_decision(self, project_id: str, decision_id: str, agent_id: str = "", soft: bool = True) -> bool:
        """Delete a decision (soft or hard)."""
        decision = self.get_decision(project_id, decision_id)
        if not decision:
            return False
        
        if soft:
            decision.soft_delete(agent_id)
            self.save_decision(project_id, decision, agent_id)
        else:
            # Hard delete
            key = self._get_decisions_key(project_id)
            data = self.backend.load(key)
            if data and decision_id in data.get("decisions", {}):
                del data["decisions"][decision_id]
                self.backend.save(key, data)
            
            # Remove from index
            index = self._get_decisions_index(project_id)
            index.remove_decision(decision)
            self._save_decisions_index(project_id, index)
        
        return True
    
    # ==================== Tech Stack Management ====================
    
    def update_tech_stack(self, project_id: str, entry: TechStackEntry, agent_id: str = "") -> None:
        """
        Update or add a tech stack entry.
        
        Args:
            project_id: Project ID
            entry: TechStackEntry to add/update
            agent_id: Agent making the update
        """
        if not self.project_exists(project_id):
            raise ValueError(f"Project {project_id} does not exist")
        
        entry.updated_at = datetime.now()
        
        key = self._get_tech_stack_key(project_id)
        data = self.backend.load(key) or {"_schema_version": SCHEMA_VERSION, "tech_stack": {}}
        
        if "tech_stack" not in data:
            data["tech_stack"] = {}
        
        data["tech_stack"][entry.category] = entry.dict()
        
        self.backend.save(key, data)
        self.update_project_info(project_id, agent_id)
        
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
            try:
                return TechStackEntry.parse_obj({**tech_stack, "category": category})
            except Exception as e:
                logger.warning(f"Failed to parse tech stack entry: {e}")
        return None
    
    # ==================== Change Log Management ====================
    
    def log_change(self, project_id: str, change: Change, agent_id: str = "") -> str:
        """
        Log a change to the project.
        
        Args:
            project_id: Project ID
            change: Change object to log
            agent_id: Agent making the change
            
        Returns:
            Change ID
        """
        if not self.project_exists(project_id):
            raise ValueError(f"Project {project_id} does not exist")
        
        change.created_by = agent_id
        change.updated_by = agent_id
        
        key = self._get_changes_key(project_id)
        data = self.backend.load(key) or {"_schema_version": SCHEMA_VERSION, "changes": []}
        
        if "changes" not in data:
            data["changes"] = []
        
        data["changes"].append(change.dict())
        
        self.backend.save(key, data)
        
        # Update change index
        index = self._get_changes_index(project_id)
        index.add_change(change)
        self._save_changes_index(project_id, index)
        
        self.update_project_info(project_id, agent_id)
        
        logger.info(f"Logged change '{change.change_type}' for file {change.file_path}")
        return change.id
    
    def _get_changes_index(self, project_id: str) -> ChangeIndex:
        """Get or create the changes index."""
        key = self._get_changes_index_key(project_id)
        data = self.backend.load(key)
        if data and "index" in data:
            try:
                return ChangeIndex.parse_obj(data["index"])
            except Exception as e:
                logger.warning(f"Failed to parse changes index: {e}")
        return ChangeIndex()
    
    def _save_changes_index(self, project_id: str, index: ChangeIndex) -> None:
        """Save the changes index."""
        key = self._get_changes_index_key(project_id)
        self.backend.save(key, {"_schema_version": SCHEMA_VERSION, "index": index.dict()})
    
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
            try:
                change = Change.parse_obj(change_data)
                
                # Apply impact filter if specified
                if impact_filter and impact_filter != "all":
                    if change.architecture_impact.value != impact_filter:
                        continue
                
                # Skip deleted changes
                if not change.is_deleted:
                    changes.append(change)
            except Exception as e:
                logger.warning(f"Failed to parse change: {e}")
        
        # Sort by timestamp (newest first)
        changes.sort(key=lambda c: c.created_at, reverse=True)
        
        return changes[:limit]
    
    def get_changes_for_file(self, project_id: str, file_path: str, limit: int = 10) -> List[Change]:
        """Get changes for a specific file using the index."""
        index = self._get_changes_index(project_id)
        change_ids = index.get_changes_by_file(file_path)
        
        changes = []
        for change_id in change_ids[:limit]:
            # Find the change in the changes list
            key = self._get_changes_key(project_id)
            data = self.backend.load(key)
            if data:
                for change_data in data.get("changes", []):
                    if change_data.get("id") == change_id:
                        try:
                            change = Change.parse_obj(change_data)
                            if not change.is_deleted:
                                changes.append(change)
                        except Exception:
                            pass
                        break
        
        return changes
    
    def get_changes_in_date_range(self, project_id: str, start: datetime, end: datetime) -> List[Change]:
        """Get all changes in a date range using the index."""
        index = self._get_changes_index(project_id)
        change_ids = index.get_changes_in_date_range(start, end)
        
        changes = []
        key = self._get_changes_key(project_id)
        data = self.backend.load(key)
        
        if data:
            changes_data = {c.get("id"): c for c in data.get("changes", [])}
            for change_id in change_ids:
                if change_id in changes_data:
                    try:
                        change = Change.parse_obj(changes_data[change_id])
                        if not change.is_deleted:
                            changes.append(change)
                    except Exception:
                        pass
        
        return changes
    
    def get_changes_by_agent(self, project_id: str, agent_id: str, limit: int = 20) -> List[Change]:
        """Get changes made by a specific agent using the index."""
        index = self._get_changes_index(project_id)
        change_ids = index.get_changes_by_agent(agent_id)
        
        changes = []
        key = self._get_changes_key(project_id)
        data = self.backend.load(key)
        
        if data:
            changes_data = {c.get("id"): c for c in data.get("changes", [])}
            for change_id in change_ids[:limit]:
                if change_id in changes_data:
                    try:
                        change = Change.parse_obj(changes_data[change_id])
                        if not change.is_deleted:
                            changes.append(change)
                    except Exception:
                        pass
        
        return changes
    
    def delete_change(self, project_id: str, change_id: str, agent_id: str = "", soft: bool = True) -> bool:
        """Delete a change log entry."""
        key = self._get_changes_key(project_id)
        data = self.backend.load(key)
        
        if not data:
            return False
        
        for i, change_data in enumerate(data.get("changes", [])):
            if change_data.get("id") == change_id:
                if soft:
                    change_data["is_deleted"] = True
                    change_data["deleted_at"] = datetime.now().isoformat()
                    change_data["updated_by"] = agent_id
                    data["changes"][i] = change_data
                else:
                    data["changes"].pop(i)
                
                self.backend.save(key, data)
                
                # Update index
                try:
                    change = Change.parse_obj(change_data)
                    index = self._get_changes_index(project_id)
                    index.remove_change(change)
                    self._save_changes_index(project_id, index)
                except Exception:
                    pass
                
                return True
        
        return False
    
    # ==================== File Metadata Management ====================
    
    def update_file_metadata(self, project_id: str, metadata: FileMetadata, agent_id: str = "") -> None:
        """
        Update or add file metadata.
        
        Args:
            project_id: Project ID
            metadata: FileMetadata to add/update
            agent_id: Agent making the update
        """
        if not self.project_exists(project_id):
            raise ValueError(f"Project {project_id} does not exist")
        
        metadata.touch(agent_id)
        metadata.last_modified = datetime.now()
        metadata.last_modified_by = agent_id
        
        key = self._get_file_metadata_key(project_id)
        data = self.backend.load(key) or {"_schema_version": SCHEMA_VERSION, "files": {}}
        
        if "files" not in data:
            data["files"] = {}
        
        data["files"][metadata.path] = metadata.dict()
        
        self.backend.save(key, data)
        
        # Update file index
        index = self._get_file_index(project_id)
        index.add_file(metadata)
        self._save_file_index(project_id, index)
        
        self.update_project_info(project_id, agent_id)
        
        logger.debug(f"Updated file metadata for {metadata.path}")
    
    def _get_file_index(self, project_id: str) -> FileMetadataIndex:
        """Get or create the file metadata index."""
        key = self._get_file_index_key(project_id)
        data = self.backend.load(key)
        if data and "index" in data:
            try:
                return FileMetadataIndex.parse_obj(data["index"])
            except Exception as e:
                logger.warning(f"Failed to parse file index: {e}")
        return FileMetadataIndex()
    
    def _save_file_index(self, project_id: str, index: FileMetadataIndex) -> None:
        """Save the file metadata index."""
        key = self._get_file_index_key(project_id)
        self.backend.save(key, {"_schema_version": SCHEMA_VERSION, "index": index.dict()})
    
    def get_file_metadata(self, project_id: str, file_path: str) -> Optional[FileMetadata]:
        """Get metadata for a specific file."""
        key = self._get_file_metadata_key(project_id)
        data = self.backend.load(key)
        
        if data and file_path in data.get("files", {}):
            try:
                file_data = data["files"][file_path]
                file_data["path"] = file_path
                metadata = FileMetadata.parse_obj(file_data)
                return metadata if not metadata.is_deleted else None
            except Exception as e:
                logger.warning(f"Failed to parse file metadata: {e}")
        return None
    
    def get_all_file_metadata(self, project_id: str, include_deleted: bool = False) -> List[FileMetadata]:
        """Get metadata for all files in a project."""
        key = self._get_file_metadata_key(project_id)
        data = self.backend.load(key)
        
        if not data:
            return []
        
        files = []
        for file_path, file_data in data.get("files", {}).items():
            try:
                file_data["path"] = file_path
                metadata = FileMetadata.parse_obj(file_data)
                if include_deleted or not metadata.is_deleted:
                    files.append(metadata)
            except Exception as e:
                logger.warning(f"Failed to parse file metadata: {e}")
        
        return files
    
    def get_files_by_module(self, project_id: str, module: str) -> List[FileMetadata]:
        """Get all files in a specific module using the index."""
        index = self._get_file_index(project_id)
        file_paths = index.by_module.get(module, [])
        
        files = []
        for file_path in file_paths:
            metadata = self.get_file_metadata(project_id, file_path)
            if metadata:
                files.append(metadata)
        
        return files
    
    def get_files_by_complexity(self, project_id: str, complexity: str) -> List[FileMetadata]:
        """Get all files with a specific complexity level."""
        index = self._get_file_index(project_id)
        file_paths = index.by_complexity.get(complexity, [])
        
        files = []
        for file_path in file_paths:
            metadata = self.get_file_metadata(project_id, file_path)
            if metadata:
                files.append(metadata)
        
        return files
    
    def detect_circular_dependencies(self, project_id: str) -> List[List[str]]:
        """Detect circular dependencies in the project."""
        index = self._get_file_index(project_id)
        return index.detect_cycles()
    
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
    
    def delete_file_metadata(self, project_id: str, file_path: str, agent_id: str = "", soft: bool = True) -> bool:
        """Delete file metadata."""
        metadata = self.get_file_metadata(project_id, file_path)
        if not metadata:
            return False
        
        if soft:
            metadata.soft_delete(agent_id)
            self.update_file_metadata(project_id, metadata, agent_id)
        else:
            key = self._get_file_metadata_key(project_id)
            data = self.backend.load(key)
            if data and file_path in data.get("files", {}):
                del data["files"][file_path]
                self.backend.save(key, data)
            
            # Remove from index
            index = self._get_file_index(project_id)
            index.remove_file(metadata)
            self._save_file_index(project_id, index)
        
        return True
    
    # ==================== Architecture Management ====================
    
    def update_architecture(self, project_id: str, architecture_data: Dict, agent_id: str = "") -> None:
        """
        Update project architecture information.
        
        Args:
            project_id: Project ID
            architecture_data: Architecture dictionary
            agent_id: Agent making the update
        """
        if not self.project_exists(project_id):
            raise ValueError(f"Project {project_id} does not exist")
        
        key = self._get_architecture_key(project_id)
        self.backend.save(key, {"_schema_version": SCHEMA_VERSION, "architecture": architecture_data})
        self.update_project_info(project_id, agent_id)
        
        logger.info(f"Updated architecture for project {project_id}")
    
    def get_architecture(self, project_id: str) -> Dict:
        """Get project architecture information."""
        key = self._get_architecture_key(project_id)
        data = self.backend.load(key)
        
        if data:
            return data.get("architecture", {})
        return {}
    
    def add_architecture_module(self, project_id: str, module: ArchitectureModule, agent_id: str = "") -> None:
        """Add or update an architecture module."""
        architecture = self.get_architecture(project_id)
        
        if "modules" not in architecture:
            architecture["modules"] = {}
        
        architecture["modules"][module.name] = module.dict()
        self.update_architecture(project_id, architecture, agent_id)
    
    def get_architecture_module(self, project_id: str, module_name: str) -> Optional[ArchitectureModule]:
        """Get a specific architecture module."""
        architecture = self.get_architecture(project_id)
        modules = architecture.get("modules", {})
        
        if module_name in modules:
            try:
                return ArchitectureModule.parse_obj(modules[module_name])
            except Exception as e:
                logger.warning(f"Failed to parse architecture module: {e}")
        return None
    
    def get_all_modules(self, project_id: str) -> List[ArchitectureModule]:
        """Get all architecture modules."""
        architecture = self.get_architecture(project_id)
        modules_data = architecture.get("modules", {})
        
        modules = []
        for name, data in modules_data.items():
            try:
                module = ArchitectureModule.parse_obj(data)
                modules.append(module)
            except Exception as e:
                logger.warning(f"Failed to parse architecture module: {e}")
        
        return modules
    
    # ==================== Relationship Management ====================
    
    def _create_relationship(self, project_id: str, source_type: str, source_id: str,
                            target_type: str, target_id: str, relationship_type: RelationshipType,
                            agent_id: str = "") -> None:
        """Create a relationship between two entities."""
        relationship = Relationship(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            relationship_type=relationship_type,
            created_by=agent_id
        )
        
        key = self._get_relationships_key(project_id)
        data = self.backend.load(key) or {"_schema_version": SCHEMA_VERSION, "relationships": []}
        
        if "relationships" not in data:
            data["relationships"] = []
        
        data["relationships"].append(relationship.dict())
        self.backend.save(key, data)
    
    def get_relationships(self, project_id: str, entity_type: Optional[str] = None,
                         entity_id: Optional[str] = None) -> List[Relationship]:
        """Get relationships for a project, optionally filtered by entity."""
        key = self._get_relationships_key(project_id)
        data = self.backend.load(key)
        
        if not data:
            return []
        
        relationships = []
        for rel_data in data.get("relationships", []):
            try:
                relationship = Relationship.parse_obj(rel_data)
                
                # Filter if specified
                if entity_type and entity_id:
                    if (relationship.source_type == entity_type and relationship.source_id == entity_id) or \
                       (relationship.target_type == entity_type and relationship.target_id == entity_id):
                        relationships.append(relationship)
                else:
                    relationships.append(relationship)
            except Exception as e:
                logger.warning(f"Failed to parse relationship: {e}")
        
        return relationships
    
    def get_related_entities(self, project_id: str, entity_type: str, entity_id: str) -> Dict[str, List[str]]:
        """Get all entities related to a specific entity."""
        relationships = self.get_relationships(project_id, entity_type, entity_id)
        
        related = {}
        for rel in relationships:
            if rel.source_type == entity_type and rel.source_id == entity_id:
                key = f"{rel.target_type}s"
                if key not in related:
                    related[key] = []
                related[key].append(rel.target_id)
            elif rel.target_type == entity_type and rel.target_id == entity_id:
                key = f"{rel.source_type}s"
                if key not in related:
                    related[key] = []
                related[key].append(rel.source_id)
        
        return related
