"""
Data models for the CoordMCP memory system.

Enhanced with schema versioning, indexes, and relationship tracking for scalability.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Literal, Any
from enum import Enum
import re


# Schema Versions - bump when making breaking changes
SCHEMA_VERSION = "1.1.0"


class ChangeType(Enum):
    """Types of changes that can be logged."""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    REFACTOR = "refactor"


class ArchitectureImpact(Enum):
    """Levels of architectural impact for changes."""
    NONE = "none"
    MINOR = "minor"
    SIGNIFICANT = "significant"


class DecisionStatus(Enum):
    """Status of a decision in the system."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    SUPERSEDED = "superseded"


class FileType(Enum):
    """Types of files in the project."""
    SOURCE = "source"
    TEST = "test"
    CONFIG = "config"
    DOC = "doc"


class Complexity(Enum):
    """Complexity levels for files."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def tokenize_text(text: str) -> List[str]:
    """Extract searchable tokens from text."""
    # Convert to lowercase, remove special chars, split into words
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    # Filter out short words and common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    tokens = [word for word in text.split() if len(word) > 2 and word not in stop_words]
    return list(set(tokens))  # Remove duplicates


@dataclass
class Decision:
    """Represents a major architectural or technical decision."""
    id: str
    timestamp: datetime
    title: str
    description: str
    context: str
    rationale: str
    impact: str
    status: str = "active"  # active, archived, superseded
    related_files: List[str] = field(default_factory=list)
    author_agent_id: str = ""  # Changed from author_agent to author_agent_id for normalization
    tags: List[str] = field(default_factory=list)
    superseded_by: Optional[str] = None  # ID of decision that superseded this one
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "title": self.title,
            "description": self.description,
            "context": self.context,
            "rationale": self.rationale,
            "impact": self.impact,
            "status": self.status,
            "related_files": self.related_files,
            "author_agent_id": self.author_agent_id,
            "tags": self.tags,
            "superseded_by": self.superseded_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Decision":
        """Create Decision from dictionary with migration support."""
        # Handle legacy field name
        author_id = data.get("author_agent_id", data.get("author_agent", ""))
        
        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            title=data["title"],
            description=data["description"],
            context=data.get("context", ""),
            rationale=data["rationale"],
            impact=data.get("impact", ""),
            status=data.get("status", "active"),
            related_files=data.get("related_files", []),
            author_agent_id=author_id,
            tags=data.get("tags", []),
            superseded_by=data.get("superseded_by")
        )
    
    def get_search_tokens(self) -> List[str]:
        """Get searchable tokens from this decision."""
        text = f"{self.title} {self.description} {self.context} {self.rationale}"
        return tokenize_text(text)


@dataclass 
class DecisionIndex:
    """Search index for fast decision lookups."""
    by_tag: Dict[str, List[str]] = field(default_factory=dict)
    by_author: Dict[str, List[str]] = field(default_factory=dict)
    by_status: Dict[str, List[str]] = field(default_factory=dict)
    by_word: Dict[str, List[str]] = field(default_factory=dict)  # Full-text search index
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "by_tag": self.by_tag,
            "by_author": self.by_author,
            "by_status": self.by_status,
            "by_word": self.by_word,
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "DecisionIndex":
        return cls(
            by_tag=data.get("by_tag", {}),
            by_author=data.get("by_author", {}),
            by_status=data.get("by_status", {}),
            by_word=data.get("by_word", {}),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))
        )
    
    def add_decision(self, decision: Decision):
        """Add a decision to all indexes."""
        # Index by tags
        for tag in decision.tags:
            if tag not in self.by_tag:
                self.by_tag[tag] = []
            if decision.id not in self.by_tag[tag]:
                self.by_tag[tag].append(decision.id)
        
        # Index by author
        if decision.author_agent_id:
            if decision.author_agent_id not in self.by_author:
                self.by_author[decision.author_agent_id] = []
            if decision.id not in self.by_author[decision.author_agent_id]:
                self.by_author[decision.author_agent_id].append(decision.id)
        
        # Index by status
        if decision.status not in self.by_status:
            self.by_status[decision.status] = []
        if decision.id not in self.by_status[decision.status]:
            self.by_status[decision.status].append(decision.id)
        
        # Index by searchable words
        for token in decision.get_search_tokens():
            if token not in self.by_word:
                self.by_word[token] = []
            if decision.id not in self.by_word[token]:
                self.by_word[token].append(decision.id)
        
        self.last_updated = datetime.now()
    
    def remove_decision(self, decision: Decision):
        """Remove a decision from all indexes."""
        # Remove from tags
        for tag in decision.tags:
            if tag in self.by_tag and decision.id in self.by_tag[tag]:
                self.by_tag[tag].remove(decision.id)
        
        # Remove from author
        if decision.author_agent_id in self.by_author:
            if decision.id in self.by_author[decision.author_agent_id]:
                self.by_author[decision.author_agent_id].remove(decision.id)
        
        # Remove from status
        if decision.status in self.by_status:
            if decision.id in self.by_status[decision.status]:
                self.by_status[decision.status].remove(decision.id)
        
        # Remove from words
        for token in decision.get_search_tokens():
            if token in self.by_word and decision.id in self.by_word[token]:
                self.by_word[token].remove(decision.id)
        
        self.last_updated = datetime.now()
    
    def search(self, query: str, decision_map: Dict[str, Decision]) -> List[Decision]:
        """Search decisions using the index."""
        tokens = tokenize_text(query)
        if not tokens:
            return []
        
        # Find decisions matching ANY token (OR logic)
        matching_ids = set()
        for token in tokens:
            if token in self.by_word:
                matching_ids.update(self.by_word[token])
        
        # Sort by relevance (number of matching tokens)
        results = []
        for decision_id in matching_ids:
            if decision_id in decision_map:
                decision = decision_map[decision_id]
                score = sum(1 for token in tokens if token in decision.get_search_tokens())
                results.append((score, decision))
        
        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in results]


@dataclass
class TechStackEntry:
    """Represents a technology stack entry."""
    category: str
    technology: str
    version: str = ""
    rationale: str = ""
    decision_ref: Optional[str] = None
    added_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "technology": self.technology,
            "version": self.version,
            "rationale": self.rationale,
            "decision_ref": self.decision_ref,
            "added_at": self.added_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, category: str, data: Dict) -> "TechStackEntry":
        added_at = datetime.now()
        updated_at = datetime.now()
        
        if "added_at" in data:
            added_at = datetime.fromisoformat(data["added_at"])
        if "updated_at" in data:
            updated_at = datetime.fromisoformat(data["updated_at"])
        
        return cls(
            category=category,
            technology=data["technology"],
            version=data.get("version", ""),
            rationale=data.get("rationale", ""),
            decision_ref=data.get("decision_ref"),
            added_at=added_at,
            updated_at=updated_at
        )


@dataclass
class ArchitectureModule:
    """Represents a module in the project architecture."""
    name: str
    purpose: str
    files: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "purpose": self.purpose,
            "files": self.files,
            "dependencies": self.dependencies,
            "responsibilities": self.responsibilities
        }
    
    @classmethod
    def from_dict(cls, name: str, data: Dict) -> "ArchitectureModule":
        return cls(
            name=name,
            purpose=data.get("purpose", ""),
            files=data.get("files", []),
            dependencies=data.get("dependencies", []),
            responsibilities=data.get("responsibilities", [])
        )


@dataclass
class Change:
    """Represents a change made to the project."""
    id: str
    timestamp: datetime
    file_path: str
    change_type: str  # create, modify, delete, refactor
    description: str
    agent_id: str = ""
    impact_area: str = ""
    architecture_impact: str = "none"  # none, minor, significant
    related_decision: Optional[str] = None
    code_summary: str = ""
    lines_changed: int = 0  # New: track lines changed
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "file_path": self.file_path,
            "change_type": self.change_type,
            "description": self.description,
            "agent_id": self.agent_id,
            "impact_area": self.impact_area,
            "architecture_impact": self.architecture_impact,
            "related_decision": self.related_decision,
            "code_summary": self.code_summary,
            "lines_changed": self.lines_changed
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Change":
        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            file_path=data["file_path"],
            change_type=data["change_type"],
            description=data["description"],
            agent_id=data.get("agent_id", ""),
            impact_area=data.get("impact_area", ""),
            architecture_impact=data.get("architecture_impact", "none"),
            related_decision=data.get("related_decision"),
            code_summary=data.get("code_summary", ""),
            lines_changed=data.get("lines_changed", 0)
        )


@dataclass
class FileMetadata:
    """Metadata about a file in the project."""
    path: str
    file_type: str = "source"  # source, test, config, doc
    last_modified: Optional[datetime] = None
    last_modified_by: str = ""
    module: str = ""
    purpose: str = ""
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    lines_of_code: int = 0
    complexity: str = "low"  # low, medium, high
    # New: Reverse relationship tracking
    related_decisions: List[str] = field(default_factory=list)
    related_changes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "path": self.path,
            "type": self.file_type,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "last_modified_by": self.last_modified_by,
            "module": self.module,
            "purpose": self.purpose,
            "dependencies": self.dependencies,
            "dependents": self.dependents,
            "lines_of_code": self.lines_of_code,
            "complexity": self.complexity,
            "related_decisions": self.related_decisions,
            "related_changes": self.related_changes
        }
    
    @classmethod
    def from_dict(cls, path: str, data: Dict) -> "FileMetadata":
        last_modified = None
        if data.get("last_modified"):
            last_modified = datetime.fromisoformat(data["last_modified"])
        
        return cls(
            path=path,
            file_type=data.get("type", "source"),
            last_modified=last_modified,
            last_modified_by=data.get("last_modified_by", ""),
            module=data.get("module", ""),
            purpose=data.get("purpose", ""),
            dependencies=data.get("dependencies", []),
            dependents=data.get("dependents", []),
            lines_of_code=data.get("lines_of_code", 0),
            complexity=data.get("complexity", "low"),
            related_decisions=data.get("related_decisions", []),
            related_changes=data.get("related_changes", [])
        )
    
    def add_related_decision(self, decision_id: str):
        """Add a related decision reference."""
        if decision_id not in self.related_decisions:
            self.related_decisions.append(decision_id)
    
    def add_related_change(self, change_id: str):
        """Add a related change reference."""
        if change_id not in self.related_changes:
            self.related_changes.append(change_id)


@dataclass
class ProjectInfo:
    """Basic information about a project."""
    project_id: str
    project_name: str
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    # New: Cached statistics
    stats: Dict[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION
    
    def to_dict(self) -> Dict:
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "stats": self.stats,
            "schema_version": self.schema_version
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ProjectInfo":
        return cls(
            project_id=data["project_id"],
            project_name=data["project_name"],
            description=data.get("description", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            stats=data.get("stats", {}),
            schema_version=data.get("schema_version", "1.0.0")
        )
    
    def update_stats(self, **kwargs):
        """Update cached statistics."""
        self.stats.update(kwargs)
        self.last_updated = datetime.now()


@dataclass
class PaginatedChanges:
    """Container for paginated changes with metadata."""
    changes: List[Change]
    total_count: int
    page: int
    per_page: int
    has_more: bool
    
    def to_dict(self) -> Dict:
        return {
            "changes": [c.to_dict() for c in self.changes],
            "total_count": self.total_count,
            "page": self.page,
            "per_page": self.per_page,
            "has_more": self.has_more
        }


@dataclass
class DataContainer:
    """Base container with schema versioning for all data files."""
    _schema_version: str = SCHEMA_VERSION
    _last_modified: datetime = field(default_factory=datetime.now)
    _data: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary with schema metadata."""
        return {
            "_schema": {
                "version": self._schema_version,
                "last_modified": self._last_modified.isoformat()
            },
            "data": self._data
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "DataContainer":
        """Create from dictionary with version checking."""
        schema_info = data.get("_schema", {})
        version = schema_info.get("version", "1.0.0")
        last_modified = datetime.now()
        
        if "last_modified" in schema_info:
            last_modified = datetime.fromisoformat(schema_info["last_modified"])
        
        return cls(
            _schema_version=version,
            _last_modified=last_modified,
            _data=data.get("data", {})
        )
    
    def migrate_if_needed(self) -> bool:
        """Migrate data if schema version is outdated."""
        if self._schema_version == SCHEMA_VERSION:
            return False
        
        # Perform migration based on version
        if self._schema_version == "1.0.0" and SCHEMA_VERSION == "1.1.0":
            # Migration from 1.0.0 to 1.1.0
            self._migrate_1_0_0_to_1_1_0()
        
        self._schema_version = SCHEMA_VERSION
        self._last_modified = datetime.now()
        return True
    
    def _migrate_1_0_0_to_1_1_0(self):
        """Migrate data from version 1.0.0 to 1.1.0."""
        # Example: Rename author_agent to author_agent_id in decisions
        if "decisions" in self._data:
            for decision_id, decision_data in self._data["decisions"].items():
                if "author_agent" in decision_data and "author_agent_id" not in decision_data:
                    decision_data["author_agent_id"] = decision_data.pop("author_agent")
