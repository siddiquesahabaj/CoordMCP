"""
Object factories for creating test data.

Factories provide a convenient way to create test objects with sensible defaults,
while allowing easy customization through keyword arguments.
"""

from datetime import datetime
from uuid import uuid4
from coordmcp.memory.models import Decision, TechStackEntry, Change, FileMetadata


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
            "timestamp": datetime.now(),
            "title": "Test Decision",
            "description": "Test decision description",
            "context": "Test context",
            "rationale": "Test rationale",
            "impact": "Test impact",
            "status": "active",
            "tags": ["test"],
            "related_files": [],
            "author_agent_id": "test-agent"
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
            "decision_ref": None,
            "added_at": datetime.now(),
            "updated_at": datetime.now()
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
            "timestamp": datetime.now(),
            "file_path": "src/main.py",
            "change_type": "create",
            "description": "Test change",
            "code_summary": "Added main function",
            "architecture_impact": "minor",
            "agent_id": "",
            "impact_area": "",
            "related_decision": None
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
        defaults = {
            "path": "src/main.py",
            "file_type": "source",
            "module": "core",
            "purpose": "Main entry point",
            "lines_of_code": 50,
            "complexity": "low"
        }
        defaults.update(overrides)
        return FileMetadata(**defaults)
