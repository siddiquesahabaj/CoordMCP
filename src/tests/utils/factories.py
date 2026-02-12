"""
Object factories for creating test data.

Factories provide a convenient way to create test objects with sensible defaults,
while allowing easy customization through keyword arguments.
"""

from datetime import datetime
from uuid import uuid4
from coordmcp.memory.models import (
    Decision, TechStackEntry, Change, FileMetadata,
    DecisionStatus, ChangeType, ArchitectureImpact, FileType, Complexity
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
