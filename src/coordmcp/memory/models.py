"""
Data models for the CoordMCP memory system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Literal
from enum import Enum


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
    author_agent: str = ""
    tags: List[str] = field(default_factory=list)
    
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
            "author_agent": self.author_agent,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Decision":
        """Create Decision from dictionary."""
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
            author_agent=data.get("author_agent", ""),
            tags=data.get("tags", [])
        )


@dataclass
class TechStackEntry:
    """Represents a technology stack entry."""
    category: str
    technology: str
    version: str = ""
    rationale: str = ""
    decision_ref: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "technology": self.technology,
            "version": self.version,
            "rationale": self.rationale,
            "decision_ref": self.decision_ref
        }
    
    @classmethod
    def from_dict(cls, category: str, data: Dict) -> "TechStackEntry":
        return cls(
            category=category,
            technology=data["technology"],
            version=data.get("version", ""),
            rationale=data.get("rationale", ""),
            decision_ref=data.get("decision_ref")
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
            "code_summary": self.code_summary
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
            code_summary=data.get("code_summary", "")
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
            "complexity": self.complexity
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
            complexity=data.get("complexity", "low")
        )


@dataclass
class ProjectInfo:
    """Basic information about a project."""
    project_id: str
    project_name: str
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ProjectInfo":
        return cls(
            project_id=data["project_id"],
            project_name=data["project_name"],
            description=data.get("description", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"])
        )
