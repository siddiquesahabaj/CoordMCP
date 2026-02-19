"""
Object factories for creating test data.

Factories provide a convenient way to create test objects with sensible defaults,
while allowing easy customization through keyword arguments.
"""

from datetime import datetime
from uuid import uuid4
from coordmcp.memory.models import (
    Decision, TechStackEntry, Change, FileMetadata,
    DecisionStatus, ChangeType, ArchitectureImpact, FileType, Complexity,
    Task, AgentMessage, MessageType, SessionSummary, ActivityFeedItem
)


class DecisionFactory:
    """Factory for creating Decision objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create a Decision with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            Decision instance
        """
        defaults = {
            "id": str(uuid4()),
            "title": "Test Decision",
            "description": "Test decision description",
            "context": "Test context",
            "rationale": "Test rationale",
            "impact": "Test impact",
            "status": DecisionStatus.ACTIVE,
            "tags": ["test"],
            "related_files": [],
            "author_agent_id": "test-agent",
            "version": 1,
            "is_deleted": False
        }
        defaults.update(overrides)
        return Decision(**defaults)


class TechStackEntryFactory:
    """Factory for creating TechStackEntry objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create a TechStackEntry with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            TechStackEntry instance
        """
        defaults = {
            "category": "backend",
            "technology": "FastAPI",
            "version": "0.100.0",
            "rationale": "High performance framework",
            "decision_ref": None
        }
        defaults.update(overrides)
        return TechStackEntry(**defaults)


class ChangeFactory:
    """Factory for creating Change objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create a Change with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            Change instance
        """
        defaults = {
            "id": str(uuid4()),
            "file_path": "src/main.py",
            "change_type": ChangeType.CREATE,
            "description": "Test change",
            "code_summary": "Added main function",
            "architecture_impact": ArchitectureImpact.MINOR,
            "agent_id": "",
            "impact_area": "",
            "related_decision": None,
            "version": 1,
            "is_deleted": False
        }
        defaults.update(overrides)
        return Change(**defaults)


class FileMetadataFactory:
    """Factory for creating FileMetadata objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create a FileMetadata with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            FileMetadata instance
        """
        path = overrides.get("path", "src/main.py")
        defaults = {
            "id": f"file_{path}",
            "path": path,
            "file_type": FileType.SOURCE,
            "module": "core",
            "purpose": "Main entry point",
            "lines_of_code": 50,
            "complexity": Complexity.LOW,
            "version": 1,
            "is_deleted": False
        }
        defaults.update(overrides)
        return FileMetadata(**defaults)


class AgentContextFactory:
    """Factory for creating AgentContext objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create an AgentContext with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            AgentContext instance
        """
        from coordmcp.context.state import AgentContext, AgentType
        
        defaults = {
            "agent_id": str(uuid4()),
            "agent_name": "Test Agent",
            "agent_type": AgentType.OPENCODE,
            "session_id": str(uuid4())
        }
        defaults.update(overrides)
        return AgentContext(**defaults)


class CurrentContextFactory:
    """Factory for creating CurrentContext objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create a CurrentContext with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            CurrentContext instance
        """
        from coordmcp.context.state import CurrentContext, Priority
        
        defaults = {
            "project_id": str(uuid4()),
            "current_objective": "Test objective",
            "task_description": "Test task description",
            "priority": Priority.MEDIUM,
            "current_file": ""
        }
        defaults.update(overrides)
        return CurrentContext(**defaults)


class LockInfoFactory:
    """Factory for creating LockInfo objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create a LockInfo with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            LockInfo instance
        """
        from coordmcp.context.state import LockInfo
        
        defaults = {
            "file_path": "src/main.py",
            "locked_by": "agent-1",
            "reason": "Testing",
            "priority": 0
        }
        defaults.update(overrides)
        return LockInfo(**defaults)


class AgentProfileFactory:
    """Factory for creating AgentProfile objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create an AgentProfile with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            AgentProfile instance
        """
        from coordmcp.context.state import AgentProfile, AgentType
        
        defaults = {
            "agent_id": str(uuid4()),
            "agent_name": "Test Agent",
            "agent_type": AgentType.OPENCODE,
            "capabilities": ["python", "fastapi"],
            "version": "1.0.0"
        }
        defaults.update(overrides)
        return AgentProfile(**defaults)


class TaskFactory:
    """Factory for creating Task objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create a Task with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            Task instance
        """
        from coordmcp.memory.models import Task, TaskStatus
        
        defaults = {
            "id": str(uuid4()),
            "title": "Test Task",
            "description": "Test task description",
            "status": TaskStatus.PENDING,
            "project_id": str(uuid4()),
            "priority": "medium",
            "related_files": [],
            "depends_on": [],
            "child_tasks": [],
            "version": 1,
            "is_deleted": False
        }
        defaults.update(overrides)
        return Task(**defaults)


class AgentMessageFactory:
    """Factory for creating AgentMessage objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create an AgentMessage with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            AgentMessage instance
        """
        from coordmcp.memory.models import AgentMessage, MessageType
        
        defaults = {
            "id": str(uuid4()),
            "from_agent_id": str(uuid4()),
            "from_agent_name": "Sender Agent",
            "to_agent_id": str(uuid4()),
            "project_id": str(uuid4()),
            "message_type": MessageType.UPDATE,
            "content": "Test message content",
            "read": False,
            "version": 1,
            "is_deleted": False
        }
        defaults.update(overrides)
        return AgentMessage(**defaults)


class SessionSummaryFactory:
    """Factory for creating SessionSummary objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create a SessionSummary with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            SessionSummary instance
        """
        defaults = {
            "id": str(uuid4()),
            "agent_id": str(uuid4()),
            "project_id": str(uuid4()),
            "session_id": str(uuid4()),
            "duration_minutes": 30,
            "objective": "Test objective",
            "objectives_completed": [],
            "files_modified": [],
            "key_decisions_made": [],
            "blockers_encountered": [],
            "summary_text": "Test session summary"
        }
        defaults.update(overrides)
        return SessionSummary(**defaults)


class ActivityFeedItemFactory:
    """Factory for creating ActivityFeedItem objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create an ActivityFeedItem with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            ActivityFeedItem instance
        """
        defaults = {
            "id": str(uuid4()),
            "activity_type": "task_created",
            "agent_id": str(uuid4()),
            "agent_name": "Test Agent",
            "project_id": str(uuid4()),
            "summary": "Test activity summary",
            "related_entity_id": None,
            "related_entity_type": None,
            "version": 1,
            "is_deleted": False
        }
        defaults.update(overrides)
        return ActivityFeedItem(**defaults)


class LockRequestFactory:
    """Factory for creating LockRequest objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create a LockRequest with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            LockRequest instance
        """
        from coordmcp.context.state import LockRequest
        
        defaults = {
            "id": str(uuid4()),
            "file_path": "src/main.py",
            "agent_id": str(uuid4()),
            "agent_name": "Test Agent",
            "reason": "Testing",
            "priority": 0,
            "project_id": str(uuid4())
        }
        defaults.update(overrides)
        return LockRequest(**defaults)


class ProjectInfoFactory:
    """Factory for creating ProjectInfo objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create a ProjectInfo with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            ProjectInfo instance
        """
        from coordmcp.memory.models import ProjectInfo
        import tempfile
        import os
        
        tmpdir = tempfile.gettempdir()
        workspace = os.path.join(tmpdir, f"test_project_{uuid4().hex[:8]}")
        
        defaults = {
            "id": str(uuid4()),
            "project_id": str(uuid4()),
            "project_name": "Test Project",
            "description": "Test project description",
            "workspace_path": workspace,
            "version": 1,
            "is_deleted": False
        }
        defaults.update(overrides)
        return ProjectInfo(**defaults)


class ArchitectureModuleFactory:
    """Factory for creating ArchitectureModule objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create an ArchitectureModule with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            ArchitectureModule instance
        """
        from coordmcp.memory.models import ArchitectureModule
        
        defaults = {
            "name": "core",
            "purpose": "Core functionality",
            "files": ["src/core/main.py"],
            "dependencies": [],
            "dependents": [],
            "responsibilities": ["Handle core logic"]
        }
        defaults.update(overrides)
        return ArchitectureModule(**defaults)


class RelationshipFactory:
    """Factory for creating Relationship objects for tests."""
    
    @staticmethod
    def create(**overrides):
        """
        Create a Relationship with default values.
        
        Args:
            **overrides: Field values to override defaults
            
        Returns:
            Relationship instance
        """
        from coordmcp.memory.models import Relationship, RelationshipType
        
        defaults = {
            "source_type": "decision",
            "source_id": str(uuid4()),
            "target_type": "file",
            "target_id": "src/main.py",
            "relationship_type": RelationshipType.REFERENCES,
            "created_by": "test-agent"
        }
        defaults.update(overrides)
        return Relationship(**defaults)
