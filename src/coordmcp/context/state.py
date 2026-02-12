"""
Data models for the CoordMCP context management system.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Literal
from enum import Enum
from pydantic import BaseModel, Field, validator


class AgentType(str, Enum):
    """Types of agents that can register with CoordMCP."""
    OPENCODE = "opencode"
    CURSOR = "cursor"
    CLAUDE_CODE = "claude_code"
    CUSTOM = "custom"


class Priority(str, Enum):
    """Priority levels for agent tasks."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OperationType(str, Enum):
    """Types of file operations agents can perform."""
    READ = "read"
    WRITE = "write"
    ANALYZE = "analyze"
    DELETE = "delete"


class CurrentContext(BaseModel):
    """Represents an agent's current working context."""
    project_id: str = Field(..., description="Project ID the agent is working on")
    current_objective: str = Field(..., description="Current objective or goal")
    current_file: str = Field(default="", description="File the agent is currently editing")
    task_description: str = Field(default="", description="Detailed task description")
    priority: Priority = Field(default=Priority.MEDIUM, description="Task priority")
    started_at: datetime = Field(default_factory=datetime.now, description="When this context started")
    estimated_completion: Optional[datetime] = Field(default=None, description="Estimated completion time")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('estimated_completion')
    def validate_estimated_completion(cls, v, values):
        if v and 'started_at' in values and v < values['started_at']:
            raise ValueError("estimated_completion cannot be before started_at")
        return v
    
    def is_overdue(self) -> bool:
        """Check if the estimated completion has passed."""
        if self.estimated_completion:
            return datetime.now() > self.estimated_completion
        return False
    
    def get_duration(self) -> timedelta:
        """Get how long this context has been active."""
        return datetime.now() - self.started_at


class LockInfo(BaseModel):
    """Information about a file lock."""
    file_path: str = Field(..., description="Path of the locked file")
    locked_at: datetime = Field(default_factory=datetime.now, description="When the lock was acquired")
    locked_by: str = Field(..., description="Agent ID that holds the lock")
    reason: str = Field(default="", description="Reason for locking")
    expected_unlock_time: Optional[datetime] = Field(default=None, description="When the lock is expected to be released")
    lock_scope: str = Field(default="file", description="Scope: file, directory, module, or project")
    priority: int = Field(default=0, ge=0, description="Lock priority (higher can preempt lower)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def is_stale(self, timeout_hours: int = 24) -> bool:
        """Check if the lock is stale (older than timeout)."""
        age = datetime.now() - self.locked_at
        return age > timedelta(hours=timeout_hours)
    
    def is_held_by(self, agent_id: str) -> bool:
        """Check if the lock is held by a specific agent."""
        return self.locked_by == agent_id
    
    def can_acquire(self, requesting_agent_id: str, requesting_priority: int = 0) -> bool:
        """Check if requesting agent can acquire this lock."""
        if self.locked_by == requesting_agent_id:
            return True
        if self.priority > 0 and requesting_priority > self.priority:
            return True
        return False
    
    def extend(self, new_expected_time: Optional[datetime] = None, agent_id: str = ""):
        """Extend the lock duration."""
        if agent_id and agent_id != self.locked_by:
            raise ValueError(f"Only the lock owner ({self.locked_by}) can extend the lock")
        self.locked_at = datetime.now()
        if new_expected_time:
            self.expected_unlock_time = new_expected_time


class ContextEntry(BaseModel):
    """Represents a single context entry in the agent's recent context."""
    timestamp: datetime = Field(default_factory=datetime.now)
    file: str = Field(..., description="File that was operated on")
    operation: OperationType = Field(..., description="Type of operation")
    summary: str = Field(default="", description="Brief summary of what was done")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionLogEntry(BaseModel):
    """Represents a session log entry."""
    timestamp: datetime = Field(default_factory=datetime.now)
    event: str = Field(..., description="Event type")
    details: Dict = Field(default_factory=dict, description="Event details")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentContext(BaseModel):
    """Complete context for an agent."""
    agent_id: str = Field(..., description="Unique agent ID")
    agent_name: str = Field(..., description="Human-readable agent name")
    agent_type: AgentType = Field(..., description="Type of agent")
    session_id: str = Field(..., description="Current session ID")
    created_at: datetime = Field(default_factory=datetime.now, description="When this context was created")
    
    current_context: Optional[CurrentContext] = Field(default=None, description="Current working context")
    locked_files: List[LockInfo] = Field(default_factory=list, description="Files currently locked by this agent")
    recent_context: List[ContextEntry] = Field(default_factory=list, description="Recent file operations (last 50)")
    session_log: List[SessionLogEntry] = Field(default_factory=list, description="Session events (last 100)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_context_entry(self, entry: ContextEntry, max_entries: int = 50):
        """Add a context entry, keeping only the last N entries."""
        self.recent_context.append(entry)
        if len(self.recent_context) > max_entries:
            self.recent_context = self.recent_context[-max_entries:]
    
    def add_session_log_entry(self, entry: SessionLogEntry, max_entries: int = 100):
        """Add a session log entry, keeping only the last N entries."""
        self.session_log.append(entry)
        if len(self.session_log) > max_entries:
            self.session_log = self.session_log[-max_entries:]
    
    def lock_file(self, lock_info: LockInfo):
        """Add a file lock, replacing any existing lock for this file."""
        # Remove existing lock for this file if any
        self.locked_files = [l for l in self.locked_files if l.file_path != lock_info.file_path]
        self.locked_files.append(lock_info)
    
    def unlock_file(self, file_path: str) -> bool:
        """Remove a file lock. Returns True if file was locked."""
        original_count = len(self.locked_files)
        self.locked_files = [l for l in self.locked_files if l.file_path != file_path]
        return len(self.locked_files) < original_count
    
    def is_file_locked_by_me(self, file_path: str) -> bool:
        """Check if this agent has locked a specific file."""
        return any(l.file_path == file_path for l in self.locked_files)
    
    def get_locked_file_paths(self) -> List[str]:
        """Get list of file paths locked by this agent."""
        return [l.file_path for l in self.locked_files]
    
    def switch_context(self, new_context: CurrentContext) -> Optional[CurrentContext]:
        """Switch to a new context, returning the previous one."""
        old_context = self.current_context
        self.current_context = new_context
        
        # Log the context switch
        self.add_session_log_entry(SessionLogEntry(
            event="context_switched",
            details={
                "from_project": old_context.project_id if old_context else None,
                "to_project": new_context.project_id,
                "from_objective": old_context.current_objective if old_context else None,
                "to_objective": new_context.current_objective
            }
        ))
        
        return old_context


class AgentProfile(BaseModel):
    """Profile information for an agent (stored in global registry)."""
    agent_id: str = Field(..., description="Unique agent ID")
    agent_name: str = Field(..., description="Human-readable name")
    agent_type: AgentType = Field(..., description="Type of agent")
    version: str = Field(default="1.0.0", description="Agent version")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities/skills")
    last_active: datetime = Field(default_factory=datetime.now, description="Last activity timestamp")
    total_sessions: int = Field(default=0, ge=0, description="Total number of sessions")
    projects_involved: List[str] = Field(default_factory=list, description="Projects this agent has worked on")
    status: Literal["active", "inactive", "suspended"] = Field(default="active")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def mark_active(self):
        """Update last_active timestamp."""
        self.last_active = datetime.now()
    
    def add_project(self, project_id: str):
        """Add a project to the agent's involvement list."""
        if project_id not in self.projects_involved:
            self.projects_involved.append(project_id)
    
    def increment_sessions(self):
        """Increment the session counter."""
        self.total_sessions += 1
    
    def is_active(self) -> bool:
        """Check if the agent is currently active."""
        return self.status == "active"


class LockConflict(BaseModel):
    """Represents a file lock conflict."""
    file_path: str
    locked_by: str
    locked_at: datetime
    reason: str
    expected_unlock_time: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ContextSummary(BaseModel):
    """Summary of agent context for display."""
    agent_id: str
    agent_name: str
    current_project: Optional[str] = None
    current_objective: Optional[str] = None
    files_locked: int = 0
    recent_operations: int = 0
    session_duration_minutes: int = 0
    
    @classmethod
    def from_agent_context(cls, context: AgentContext) -> "ContextSummary":
        """Create a summary from an agent context."""
        duration = datetime.now() - context.created_at
        return cls(
            agent_id=context.agent_id,
            agent_name=context.agent_name,
            current_project=context.current_context.project_id if context.current_context else None,
            current_objective=context.current_context.current_objective if context.current_context else None,
            files_locked=len(context.locked_files),
            recent_operations=len(context.recent_context),
            session_duration_minutes=int(duration.total_seconds() / 60)
        )
