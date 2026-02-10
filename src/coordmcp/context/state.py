"""
Data models for the CoordMCP context management system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Literal
from enum import Enum


class AgentType(Enum):
    """Types of agents that can register with CoordMCP."""
    OPENCODE = "opencode"
    CURSOR = "cursor"
    CLAUDE_CODE = "claude_code"
    CUSTOM = "custom"


class Priority(Enum):
    """Priority levels for agent tasks."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OperationType(Enum):
    """Types of file operations agents can perform."""
    READ = "read"
    WRITE = "write"
    ANALYZE = "analyze"
    DELETE = "delete"


@dataclass
class CurrentContext:
    """Represents an agent's current working context."""
    project_id: str
    current_objective: str
    current_file: str = ""
    task_description: str = ""
    priority: str = "medium"
    started_at: datetime = field(default_factory=datetime.now)
    estimated_completion: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "project_id": self.project_id,
            "current_objective": self.current_objective,
            "current_file": self.current_file,
            "task_description": self.task_description,
            "priority": self.priority,
            "started_at": self.started_at.isoformat(),
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CurrentContext":
        """Create CurrentContext from dictionary."""
        started_at = datetime.fromisoformat(data["started_at"])
        estimated_completion = None
        if data.get("estimated_completion"):
            estimated_completion = datetime.fromisoformat(data["estimated_completion"])
        
        return cls(
            project_id=data["project_id"],
            current_objective=data["current_objective"],
            current_file=data.get("current_file", ""),
            task_description=data.get("task_description", ""),
            priority=data.get("priority", "medium"),
            started_at=started_at,
            estimated_completion=estimated_completion
        )


@dataclass
class LockInfo:
    """Information about a file lock."""
    file_path: str
    locked_at: datetime
    locked_by: str
    reason: str
    expected_unlock_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "locked_at": self.locked_at.isoformat(),
            "locked_by": self.locked_by,
            "reason": self.reason,
            "expected_unlock_time": self.expected_unlock_time.isoformat() if self.expected_unlock_time else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "LockInfo":
        """Create LockInfo from dictionary."""
        locked_at = datetime.fromisoformat(data["locked_at"])
        expected_unlock_time = None
        if data.get("expected_unlock_time"):
            expected_unlock_time = datetime.fromisoformat(data["expected_unlock_time"])
        
        return cls(
            file_path=data["file_path"],
            locked_at=locked_at,
            locked_by=data["locked_by"],
            reason=data["reason"],
            expected_unlock_time=expected_unlock_time
        )
    
    def is_stale(self, timeout_hours: int = 24) -> bool:
        """Check if the lock is stale (older than timeout)."""
        from datetime import timedelta
        age = datetime.now() - self.locked_at
        return age > timedelta(hours=timeout_hours)


@dataclass
class ContextEntry:
    """Represents a single context entry in the agent's recent context."""
    timestamp: datetime
    file: str
    operation: str
    summary: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "file": self.file,
            "operation": self.operation,
            "summary": self.summary
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ContextEntry":
        """Create ContextEntry from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            file=data["file"],
            operation=data["operation"],
            summary=data["summary"]
        )


@dataclass
class SessionLogEntry:
    """Represents a session log entry."""
    timestamp: datetime
    event: str
    details: Dict
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "event": self.event,
            "details": self.details
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SessionLogEntry":
        """Create SessionLogEntry from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            event=data["event"],
            details=data.get("details", {})
        )


@dataclass
class AgentContext:
    """Complete context for an agent."""
    agent_id: str
    agent_name: str
    agent_type: str
    session_id: str
    created_at: datetime
    
    current_context: Optional[CurrentContext] = None
    locked_files: List[LockInfo] = field(default_factory=list)
    recent_context: List[ContextEntry] = field(default_factory=list)
    session_log: List[SessionLogEntry] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "current_context": self.current_context.to_dict() if self.current_context else None,
            "locked_files": [lock.to_dict() for lock in self.locked_files],
            "recent_context": [entry.to_dict() for entry in self.recent_context],
            "session_log": [entry.to_dict() for entry in self.session_log]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AgentContext":
        """Create AgentContext from dictionary."""
        current_context = None
        if data.get("current_context"):
            current_context = CurrentContext.from_dict(data["current_context"])
        
        locked_files = []
        for lock_data in data.get("locked_files", []):
            locked_files.append(LockInfo.from_dict(lock_data))
        
        recent_context = []
        for entry_data in data.get("recent_context", []):
            recent_context.append(ContextEntry.from_dict(entry_data))
        
        session_log = []
        for log_data in data.get("session_log", []):
            session_log.append(SessionLogEntry.from_dict(log_data))
        
        return cls(
            agent_id=data["agent_id"],
            agent_name=data["agent_name"],
            agent_type=data["agent_type"],
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            current_context=current_context,
            locked_files=locked_files,
            recent_context=recent_context,
            session_log=session_log
        )
    
    def add_context_entry(self, entry: ContextEntry):
        """Add a context entry, keeping only the last 50."""
        self.recent_context.append(entry)
        # Keep only last 50 entries
        if len(self.recent_context) > 50:
            self.recent_context = self.recent_context[-50:]
    
    def add_session_log_entry(self, entry: SessionLogEntry):
        """Add a session log entry, keeping only the last 100."""
        self.session_log.append(entry)
        # Keep only last 100 entries
        if len(self.session_log) > 100:
            self.session_log = self.session_log[-100:]
    
    def lock_file(self, lock_info: LockInfo):
        """Add a file lock."""
        # Remove existing lock for this file if any
        self.locked_files = [l for l in self.locked_files if l.file_path != lock_info.file_path]
        self.locked_files.append(lock_info)
    
    def unlock_file(self, file_path: str) -> bool:
        """Remove a file lock. Returns True if file was locked."""
        original_count = len(self.locked_files)
        self.locked_files = [l for l in self.locked_files if l.file_path != file_path]
        return len(self.locked_files) < original_count


@dataclass
class AgentProfile:
    """Profile information for an agent (stored in global registry)."""
    agent_id: str
    agent_name: str
    agent_type: str
    version: str = "1.0.0"
    capabilities: List[str] = field(default_factory=list)
    last_active: datetime = field(default_factory=datetime.now)
    total_sessions: int = 0
    projects_involved: List[str] = field(default_factory=list)
    status: str = "active"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "version": self.version,
            "capabilities": self.capabilities,
            "last_active": self.last_active.isoformat(),
            "total_sessions": self.total_sessions,
            "projects_involved": self.projects_involved,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AgentProfile":
        """Create AgentProfile from dictionary."""
        return cls(
            agent_id=data["agent_id"],
            agent_name=data["agent_name"],
            agent_type=data["agent_type"],
            version=data.get("version", "1.0.0"),
            capabilities=data.get("capabilities", []),
            last_active=datetime.fromisoformat(data["last_active"]),
            total_sessions=data.get("total_sessions", 0),
            projects_involved=data.get("projects_involved", []),
            status=data.get("status", "active")
        )
    
    def mark_active(self):
        """Update last_active timestamp."""
        self.last_active = datetime.now()
    
    def add_project(self, project_id: str):
        """Add a project to the agent's involvement list."""
        if project_id not in self.projects_involved:
            self.projects_involved.append(project_id)
