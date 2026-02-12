"""
Data models for the CoordMCP memory system.

Enhanced with schema versioning, indexes, Pydantic validation, and relationship tracking.
"""

from datetime import datetime
from typing import List, Dict, Optional, Literal, Any, Set
from enum import Enum
import re
from pydantic import BaseModel, Field, validator


# Schema Versions - bump when making breaking changes
SCHEMA_VERSION = "1.2.0"


class ChangeType(str, Enum):
    """Types of changes that can be logged."""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    REFACTOR = "refactor"


class ArchitectureImpact(str, Enum):
    """Levels of architectural impact for changes."""
    NONE = "none"
    MINOR = "minor"
    SIGNIFICANT = "significant"


class DecisionStatus(str, Enum):
    """Status of a decision in the system."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"


class FileType(str, Enum):
    """Types of files in the project."""
    SOURCE = "source"
    TEST = "test"
    CONFIG = "config"
    DOC = "doc"


class Complexity(str, Enum):
    """Complexity levels for files."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RelationshipType(str, Enum):
    """Types of relationships between entities."""
    DEPENDS_ON = "depends_on"
    IMPLEMENTS = "implements"
    REFERENCES = "references"
    SUPERSEDES = "supersedes"
    RELATED_TO = "related_to"


def tokenize_text(text: str) -> List[str]:
    """Extract searchable tokens from text."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
    tokens = [word for word in text.split() if len(word) > 2 and word not in stop_words]
    return list(set(tokens))


class BaseEntity(BaseModel):
    """Base class for all entities with common fields."""
    id: str = Field(..., description="Unique identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    created_by: str = Field(default="", description="Agent/entity that created this")
    updated_by: str = Field(default="", description="Agent/entity that last updated this")
    version: int = Field(default=1, ge=1, description="Version number for optimistic locking")
    is_deleted: bool = Field(default=False, description="Soft delete flag")
    deleted_at: Optional[datetime] = Field(default=None, description="When this was soft deleted")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extensible metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def touch(self, agent_id: str = ""):
        """Update timestamps and version."""
        self.updated_at = datetime.now()
        self.updated_by = agent_id
        self.version += 1
    
    def soft_delete(self, agent_id: str = ""):
        """Soft delete this entity."""
        self.is_deleted = True
        self.deleted_at = datetime.now()
        self.touch(agent_id)
    
    def restore(self, agent_id: str = ""):
        """Restore from soft delete."""
        self.is_deleted = False
        self.deleted_at = None
        self.touch(agent_id)


class Relationship(BaseModel):
    """Represents a relationship between two entities."""
    source_type: str = Field(..., description="Type of source entity (decision, file, module, change)")
    source_id: str = Field(..., description="ID of source entity")
    target_type: str = Field(..., description="Type of target entity")
    target_id: str = Field(..., description="ID of target entity")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: str = Field(default="")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Decision(BaseEntity):
    """Represents a major architectural or technical decision."""
    title: str = Field(..., min_length=3, max_length=200, description="Decision title")
    description: str = Field(..., min_length=10, description="Detailed description")
    context: str = Field(default="", description="Context in which decision was made")
    rationale: str = Field(default="", description="Reasoning behind the decision")
    impact: str = Field(default="", description="Impact of this decision")
    status: DecisionStatus = Field(default=DecisionStatus.ACTIVE)
    related_files: List[str] = Field(default_factory=list, description="File paths related to this decision")
    author_agent_id: str = Field(default="", description="Agent that made this decision")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    superseded_by: Optional[str] = Field(default=None, description="ID of decision that superseded this one")
    supersedes: List[str] = Field(default_factory=list, description="IDs of decisions this one supersedes")
    valid_from: datetime = Field(default_factory=datetime.now, description="When this decision becomes effective")
    valid_to: Optional[datetime] = Field(default=None, description="When this decision expires")
    
    @validator('status')
    def validate_superseded(cls, v, values):
        if v == DecisionStatus.SUPERSEDED and not values.get('superseded_by'):
            raise ValueError("Superseded decisions must have superseded_by set")
        return v
    
    def get_search_tokens(self) -> List[str]:
        """Get searchable tokens from this decision."""
        text = f"{self.title} {self.description} {self.context} {self.rationale} {' '.join(self.tags)}"
        return tokenize_text(text)
    
    def is_valid_at(self, timestamp: Optional[datetime] = None) -> bool:
        """Check if decision is valid at a given time."""
        if timestamp is None:
            timestamp = datetime.now()
        return self.valid_from <= timestamp and (
            self.valid_to is None or timestamp <= self.valid_to
        )
    
    def create_new_version(self, changes: Dict[str, Any], agent_id: str) -> "Decision":
        """Create a new version of this decision."""
        new_data = self.dict()
        new_data.update(changes)
        new_data['id'] = f"{self.id}_v{self.version + 1}"
        new_data['previous_version_id'] = self.id
        new_data['version'] = 1
        new_data['created_at'] = datetime.now()
        new_data['created_by'] = agent_id
        new_data['supersedes'] = [self.id]
        
        new_decision = Decision(**new_data)
        self.superseded_by = new_decision.id
        self.status = DecisionStatus.SUPERSEDED
        self.touch(agent_id)
        
        return new_decision


class DecisionIndex(BaseModel):
    """Search index for fast decision lookups."""
    by_tag: Dict[str, List[str]] = Field(default_factory=dict)
    by_author: Dict[str, List[str]] = Field(default_factory=dict)
    by_status: Dict[str, List[str]] = Field(default_factory=dict)
    by_word: Dict[str, List[str]] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_decision(self, decision: Decision):
        """Add a decision to all indexes."""
        for tag in decision.tags:
            if tag not in self.by_tag:
                self.by_tag[tag] = []
            if decision.id not in self.by_tag[tag]:
                self.by_tag[tag].append(decision.id)
        
        if decision.author_agent_id:
            if decision.author_agent_id not in self.by_author:
                self.by_author[decision.author_agent_id] = []
            if decision.id not in self.by_author[decision.author_agent_id]:
                self.by_author[decision.author_agent_id].append(decision.id)
        
        status_key = decision.status.value if isinstance(decision.status, Enum) else decision.status
        if status_key not in self.by_status:
            self.by_status[status_key] = []
        if decision.id not in self.by_status[status_key]:
            self.by_status[status_key].append(decision.id)
        
        for token in decision.get_search_tokens():
            if token not in self.by_word:
                self.by_word[token] = []
            if decision.id not in self.by_word[token]:
                self.by_word[token].append(decision.id)
        
        self.last_updated = datetime.now()
    
    def remove_decision(self, decision: Decision):
        """Remove a decision from all indexes."""
        for tag in decision.tags:
            if tag in self.by_tag and decision.id in self.by_tag[tag]:
                self.by_tag[tag].remove(decision.id)
        
        if decision.author_agent_id in self.by_author:
            if decision.id in self.by_author[decision.author_agent_id]:
                self.by_author[decision.author_agent_id].remove(decision.id)
        
        status_key = decision.status.value if isinstance(decision.status, Enum) else decision.status
        if status_key in self.by_status:
            if decision.id in self.by_status[status_key]:
                self.by_status[status_key].remove(decision.id)
        
        for token in decision.get_search_tokens():
            if token in self.by_word and decision.id in self.by_word[token]:
                self.by_word[token].remove(decision.id)
        
        self.last_updated = datetime.now()
    
    def search(self, query: str, decision_map: Dict[str, Decision]) -> List[Decision]:
        """Search decisions using the index."""
        tokens = tokenize_text(query)
        if not tokens:
            return []
        
        matching_ids = set()
        for token in tokens:
            if token in self.by_word:
                matching_ids.update(self.by_word[token])
        
        results = []
        for decision_id in matching_ids:
            if decision_id in decision_map:
                decision = decision_map[decision_id]
                if not decision.is_deleted:
                    score = sum(1 for token in tokens if token in decision.get_search_tokens())
                    results.append((score, decision))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in results]


class TechStackEntry(BaseModel):
    """Represents a technology stack entry."""
    category: str = Field(..., description="Technology category (backend, frontend, etc.)")
    technology: str = Field(..., description="Technology name")
    version: str = Field(default="", description="Version string")
    rationale: str = Field(default="", description="Why this technology was chosen")
    decision_ref: Optional[str] = Field(default=None, description="Reference to decision ID")
    added_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ArchitectureModule(BaseModel):
    """Represents a module in the project architecture."""
    name: str = Field(..., description="Module name")
    purpose: str = Field(default="", description="What this module does")
    files: List[str] = Field(default_factory=list, description="Files in this module")
    dependencies: List[str] = Field(default_factory=list, description="Other modules this depends on")
    dependents: List[str] = Field(default_factory=list, description="Modules that depend on this")
    responsibilities: List[str] = Field(default_factory=list, description="Key responsibilities")
    
    def get_dependency_graph(self) -> Dict[str, Set[str]]:
        """Get a dependency graph starting from this module."""
        graph = {self.name: set(self.dependencies)}
        return graph


class Change(BaseEntity):
    """Represents a change made to the project."""
    file_path: str = Field(..., description="Path of file that was changed")
    change_type: ChangeType = Field(default=ChangeType.MODIFY)
    description: str = Field(default="", description="What was changed")
    agent_id: str = Field(default="", description="Agent that made the change")
    impact_area: str = Field(default="", description="Area of impact")
    architecture_impact: ArchitectureImpact = Field(default=ArchitectureImpact.NONE)
    related_decision: Optional[str] = Field(default=None, description="Decision this change implements")
    code_summary: str = Field(default="", description="Summary of code changes")
    lines_changed: int = Field(default=0, ge=0, description="Number of lines changed")
    
    def get_search_tokens(self) -> List[str]:
        """Get searchable tokens."""
        return tokenize_text(f"{self.description} {self.code_summary} {self.file_path}")


class ChangeIndex(BaseModel):
    """Index for fast change lookups."""
    by_file: Dict[str, List[str]] = Field(default_factory=dict, description="file_path -> change_ids")
    by_agent: Dict[str, List[str]] = Field(default_factory=dict, description="agent_id -> change_ids")
    by_date: Dict[str, List[str]] = Field(default_factory=dict, description="YYYY-MM-DD -> change_ids")
    by_type: Dict[str, List[str]] = Field(default_factory=dict, description="change_type -> change_ids")
    by_decision: Dict[str, List[str]] = Field(default_factory=dict, description="decision_id -> change_ids")
    last_updated: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_change(self, change: Change):
        """Add a change to all indexes."""
        # Index by file
        if change.file_path not in self.by_file:
            self.by_file[change.file_path] = []
        if change.id not in self.by_file[change.file_path]:
            self.by_file[change.file_path].append(change.id)
        
        # Index by agent
        if change.agent_id:
            if change.agent_id not in self.by_agent:
                self.by_agent[change.agent_id] = []
            if change.id not in self.by_agent[change.agent_id]:
                self.by_agent[change.agent_id].append(change.id)
        
        # Index by date
        date_key = change.created_at.strftime("%Y-%m-%d")
        if date_key not in self.by_date:
            self.by_date[date_key] = []
        if change.id not in self.by_date[date_key]:
            self.by_date[date_key].append(change.id)
        
        # Index by type
        type_key = change.change_type.value if isinstance(change.change_type, Enum) else change.change_type
        if type_key not in self.by_type:
            self.by_type[type_key] = []
        if change.id not in self.by_type[type_key]:
            self.by_type[type_key].append(change.id)
        
        # Index by decision
        if change.related_decision:
            if change.related_decision not in self.by_decision:
                self.by_decision[change.related_decision] = []
            if change.id not in self.by_decision[change.related_decision]:
                self.by_decision[change.related_decision].append(change.id)
        
        self.last_updated = datetime.now()
    
    def remove_change(self, change: Change):
        """Remove a change from all indexes."""
        if change.file_path in self.by_file and change.id in self.by_file[change.file_path]:
            self.by_file[change.file_path].remove(change.id)
        
        if change.agent_id in self.by_agent and change.id in self.by_agent[change.agent_id]:
            self.by_agent[change.agent_id].remove(change.id)
        
        date_key = change.created_at.strftime("%Y-%m-%d")
        if date_key in self.by_date and change.id in self.by_date[date_key]:
            self.by_date[date_key].remove(change.id)
        
        type_key = change.change_type.value if isinstance(change.change_type, Enum) else change.change_type
        if type_key in self.by_type and change.id in self.by_type[type_key]:
            self.by_type[type_key].remove(change.id)
        
        if change.related_decision and change.related_decision in self.by_decision:
            if change.id in self.by_decision[change.related_decision]:
                self.by_decision[change.related_decision].remove(change.id)
        
        self.last_updated = datetime.now()
    
    def get_changes_in_date_range(self, start: datetime, end: datetime) -> List[str]:
        """Get all change IDs in a date range."""
        results = []
        current = start.date()
        end_date = end.date()
        
        while current <= end_date:
            date_key = current.strftime("%Y-%m-%d")
            results.extend(self.by_date.get(date_key, []))
            current = current + __import__('datetime').timedelta(days=1)
        
        return results
    
    def get_changes_by_file(self, file_path: str) -> List[str]:
        """Get all change IDs for a file."""
        return self.by_file.get(file_path, [])
    
    def get_changes_by_agent(self, agent_id: str) -> List[str]:
        """Get all change IDs by an agent."""
        return self.by_agent.get(agent_id, [])


class FileMetadata(BaseEntity):
    """Metadata about a file in the project."""
    path: str = Field(..., description="File path")
    file_type: FileType = Field(default=FileType.SOURCE)
    last_modified: Optional[datetime] = Field(default=None)
    last_modified_by: str = Field(default="")
    module: str = Field(default="", description="Module this file belongs to")
    purpose: str = Field(default="", description="What this file does")
    dependencies: List[str] = Field(default_factory=list, description="Files this depends on")
    dependents: List[str] = Field(default_factory=list, description="Files that depend on this")
    lines_of_code: int = Field(default=0, ge=0)
    complexity: Complexity = Field(default=Complexity.LOW)
    related_decisions: List[str] = Field(default_factory=list)
    related_changes: List[str] = Field(default_factory=list)
    
    def add_related_decision(self, decision_id: str):
        """Add a related decision reference."""
        if decision_id not in self.related_decisions:
            self.related_decisions.append(decision_id)
    
    def add_related_change(self, change_id: str):
        """Add a related change reference."""
        if change_id not in self.related_changes:
            self.related_changes.append(change_id)


class FileMetadataIndex(BaseModel):
    """Index for file metadata."""
    by_module: Dict[str, List[str]] = Field(default_factory=dict)
    by_type: Dict[str, List[str]] = Field(default_factory=dict)
    by_complexity: Dict[str, List[str]] = Field(default_factory=dict)
    dependency_graph: Dict[str, Set[str]] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            set: lambda v: list(v)
        }
    
    def dict(self, **kwargs):
        """Override dict to properly serialize sets."""
        d = super().dict(**kwargs)
        # Convert sets to lists in dependency_graph
        if 'dependency_graph' in d:
            d['dependency_graph'] = {
                k: list(v) if isinstance(v, set) else v 
                for k, v in d['dependency_graph'].items()
            }
        return d
    
    def add_file(self, file_metadata: FileMetadata):
        """Add a file to all indexes."""
        # Index by module
        if file_metadata.module:
            if file_metadata.module not in self.by_module:
                self.by_module[file_metadata.module] = []
            if file_metadata.path not in self.by_module[file_metadata.module]:
                self.by_module[file_metadata.module].append(file_metadata.path)
        
        # Index by type
        type_key = file_metadata.file_type.value if isinstance(file_metadata.file_type, Enum) else file_metadata.file_type
        if type_key not in self.by_type:
            self.by_type[type_key] = []
        if file_metadata.path not in self.by_type[type_key]:
            self.by_type[type_key].append(file_metadata.path)
        
        # Index by complexity
        complexity_key = file_metadata.complexity.value if isinstance(file_metadata.complexity, Enum) else file_metadata.complexity
        if complexity_key not in self.by_complexity:
            self.by_complexity[complexity_key] = []
        if file_metadata.path not in self.by_complexity[complexity_key]:
            self.by_complexity[complexity_key].append(file_metadata.path)
        
        # Update dependency graph
        self.dependency_graph[file_metadata.path] = set(file_metadata.dependencies)
        
        self.last_updated = datetime.now()
    
    def remove_file(self, file_metadata: FileMetadata):
        """Remove a file from all indexes."""
        if file_metadata.module in self.by_module:
            if file_metadata.path in self.by_module[file_metadata.module]:
                self.by_module[file_metadata.module].remove(file_metadata.path)
        
        type_key = file_metadata.file_type.value if isinstance(file_metadata.file_type, Enum) else file_metadata.file_type
        if type_key in self.by_type:
            if file_metadata.path in self.by_type[type_key]:
                self.by_type[type_key].remove(file_metadata.path)
        
        complexity_key = file_metadata.complexity.value if isinstance(file_metadata.complexity, Enum) else file_metadata.complexity
        if complexity_key in self.by_complexity:
            if file_metadata.path in self.by_complexity[complexity_key]:
                self.by_complexity[complexity_key].remove(file_metadata.path)
        
        if file_metadata.path in self.dependency_graph:
            del self.dependency_graph[file_metadata.path]
        
        self.last_updated = datetime.now()
    
    def get_files_by_complexity(self, complexity: Complexity) -> List[str]:
        """Get all files with a specific complexity."""
        key = complexity.value if isinstance(complexity, Enum) else complexity
        return self.by_complexity.get(key, [])
    
    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies in the graph."""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependency_graph.get(node, []):
                if neighbor not in visited:
                    result = dfs(neighbor, path)
                    if result:
                        return result
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:]
            
            path.pop()
            rec_stack.remove(node)
            return None
        
        for node in self.dependency_graph:
            if node not in visited:
                cycle = dfs(node, [])
                if cycle:
                    cycles.append(cycle)
        
        return cycles


class ProjectInfo(BaseEntity):
    """Basic information about a project."""
    project_id: str = Field(..., description="Unique project ID")
    project_name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="")
    schema_version: str = Field(default=SCHEMA_VERSION)


class PaginatedChanges(BaseModel):
    """Container for paginated changes with metadata."""
    changes: List[Change]
    total_count: int
    page: int
    per_page: int
    has_more: bool


class DataContainer(BaseModel):
    """Base container with schema versioning for all data files."""
    schema_version: str = Field(default=SCHEMA_VERSION)
    last_modified: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def migrate_if_needed(self) -> bool:
        """Migrate data if schema version is outdated."""
        if self.schema_version == SCHEMA_VERSION:
            return False
        
        migrations = {
            "1.0.0": self._migrate_1_0_0_to_1_1_0,
            "1.1.0": self._migrate_1_1_0_to_1_2_0,
        }
        
        while self.schema_version in migrations:
            old_version = self.schema_version
            migrations[self.schema_version]()
            if self.schema_version == old_version:
                break
        
        return True
    
    def _migrate_1_0_0_to_1_1_0(self):
        """Migrate from 1.0.0 to 1.1.0."""
        if "decisions" in self.data:
            for decision_id, decision_data in self.data["decisions"].items():
                if "author_agent" in decision_data and "author_agent_id" not in decision_data:
                    decision_data["author_agent_id"] = decision_data.pop("author_agent")
        self.schema_version = "1.1.0"
        self.last_modified = datetime.now()
    
    def _migrate_1_1_0_to_1_2_0(self):
        """Migrate from 1.1.0 to 1.2.0."""
        # Add new fields for all entities
        for entity_type in ["decisions", "changes", "files"]:
            if entity_type in self.data:
                for entity_id, entity_data in self.data[entity_type].items():
                    # Add BaseEntity fields if missing
                    if "version" not in entity_data:
                        entity_data["version"] = 1
                    if "is_deleted" not in entity_data:
                        entity_data["is_deleted"] = False
                    if "metadata" not in entity_data:
                        entity_data["metadata"] = {}
                    if "created_by" not in entity_data:
                        entity_data["created_by"] = entity_data.get("author_agent_id", "")
                    if "updated_by" not in entity_data:
                        entity_data["updated_by"] = entity_data.get("author_agent_id", "")
        
        self.schema_version = "1.2.0"
        self.last_modified = datetime.now()


# Backward compatibility - add from_dict methods for Pydantic models
# These allow loading from legacy dictionary formats
