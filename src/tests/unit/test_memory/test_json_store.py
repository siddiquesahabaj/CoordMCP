"""
Unit tests for ProjectMemoryStore functionality.

These tests verify the core memory operations including:
- Project creation and management
- Decision storage and retrieval
- Tech stack management
- Change logging
- File metadata management
"""

import pytest
from coordmcp.memory.models import Decision, TechStackEntry, Change, FileMetadata
from tests.utils.factories import (
    DecisionFactory,
    TechStackEntryFactory,
    ChangeFactory,
    FileMetadataFactory,
)
from tests.utils.assertions import assert_project_exists, assert_valid_uuid


@pytest.mark.unit
@pytest.mark.memory
class TestProjectCreation:
    """Test project creation operations."""
    
    def test_create_project_returns_valid_uuid(self, memory_store):
        """Test that create_project returns a valid UUID."""
        project_id = memory_store.create_project(
            project_name="New Project",
            description="A test project"
        )
        
        assert_valid_uuid(project_id)
    
    def test_create_project_makes_project_exist(self, memory_store):
        """Test that created project exists in store."""
        project_id = memory_store.create_project(
            project_name="Test Project",
            description="Test description"
        )
        
        assert_project_exists(memory_store, project_id)
    
    def test_create_project_stores_correct_info(self, memory_store):
        """Test that project info is stored correctly."""
        project_id = memory_store.create_project(
            project_name="My Project",
            description="My description"
        )
        
        project_info = memory_store.get_project_info(project_id)
        assert project_info.project_name == "My Project"
        assert project_info.description == "My description"


@pytest.mark.unit
@pytest.mark.memory
class TestDecisions:
    """Test decision management operations."""
    
    def test_save_decision_returns_id(self, memory_store, sample_project_id):
        """Test that save_decision returns a decision ID."""
        decision = DecisionFactory.create(title="Test Decision")
        
        decision_id = memory_store.save_decision(sample_project_id, decision)
        
        assert decision_id is not None
        assert_valid_uuid(decision_id)
    
    def test_get_decision_returns_correct_data(self, memory_store, sample_project_id):
        """Test that get_decision returns correct decision data."""
        decision = DecisionFactory.create(
            title="Use FastAPI",
            description="For API layer",
            tags=["backend", "api"]
        )
        decision_id = memory_store.save_decision(sample_project_id, decision)
        
        retrieved = memory_store.get_decision(sample_project_id, decision_id)
        
        assert retrieved.title == "Use FastAPI"
        assert retrieved.description == "For API layer"
        assert retrieved.tags == ["backend", "api"]
    
    def test_get_all_decisions_returns_list(self, memory_store, sample_project_id):
        """Test that get_all_decisions returns all saved decisions."""
        # Save multiple decisions
        for i in range(3):
            decision = DecisionFactory.create(title=f"Decision {i}")
            memory_store.save_decision(sample_project_id, decision)
        
        decisions = memory_store.get_all_decisions(sample_project_id)
        
        assert len(decisions) == 3
    
    def test_search_decisions_finds_by_query(self, memory_store, sample_project_id):
        """Test that search_decisions finds decisions matching query."""
        # Save decisions with different content
        decision1 = DecisionFactory.create(
            title="Use FastAPI",
            description="Fast framework"
        )
        decision2 = DecisionFactory.create(
            title="Use Django",
            description="Full framework"
        )
        memory_store.save_decision(sample_project_id, decision1)
        memory_store.save_decision(sample_project_id, decision2)
        
        results = memory_store.search_decisions(sample_project_id, "FastAPI")
        
        assert len(results) == 1
        assert results[0].title == "Use FastAPI"


@pytest.mark.unit
@pytest.mark.memory
class TestTechStack:
    """Test technology stack management."""
    
    def test_update_tech_stack_stores_entry(self, memory_store, sample_project_id):
        """Test that update_tech_stack stores tech stack entry."""
        entry = TechStackEntryFactory.create(
            category="backend",
            technology="FastAPI",
            version="0.100.0"
        )
        
        memory_store.update_tech_stack(sample_project_id, entry)
        
        tech_stack = memory_store.get_tech_stack(sample_project_id)
        assert "backend" in tech_stack
        assert tech_stack["backend"]["technology"] == "FastAPI"
    
    def test_get_tech_stack_by_category(self, memory_store, sample_project_id):
        """Test that get_tech_stack can filter by category."""
        entry = TechStackEntryFactory.create(category="backend", technology="FastAPI")
        memory_store.update_tech_stack(sample_project_id, entry)
        
        backend = memory_store.get_tech_stack(sample_project_id, "backend")
        
        assert backend["technology"] == "FastAPI"


@pytest.mark.unit
@pytest.mark.memory
class TestChanges:
    """Test change logging operations."""
    
    def test_log_change_returns_id(self, memory_store, sample_project_id):
        """Test that log_change returns a change ID."""
        change = ChangeFactory.create(file_path="src/main.py")
        
        change_id = memory_store.log_change(sample_project_id, change)
        
        assert change_id is not None
    
    def test_get_recent_changes_returns_changes(self, memory_store, sample_project_id):
        """Test that get_recent_changes returns logged changes."""
        change = ChangeFactory.create(
            file_path="src/main.py",
            change_type="create",
            description="Initial commit"
        )
        memory_store.log_change(sample_project_id, change)
        
        changes = memory_store.get_recent_changes(sample_project_id)
        
        assert len(changes) == 1
        assert changes[0].file_path == "src/main.py"
    
    def test_get_recent_changes_respects_limit(self, memory_store, sample_project_id):
        """Test that get_recent_changes respects the limit parameter."""
        # Log 5 changes
        for i in range(5):
            change = ChangeFactory.create(file_path=f"src/file{i}.py")
            memory_store.log_change(sample_project_id, change)
        
        changes = memory_store.get_recent_changes(sample_project_id, limit=3)
        
        assert len(changes) == 3


@pytest.mark.unit
@pytest.mark.memory
class TestFileMetadata:
    """Test file metadata operations."""
    
    def test_update_file_metadata_stores_data(self, memory_store, sample_project_id):
        """Test that update_file_metadata stores file information."""
        metadata = FileMetadataFactory.create(
            path="src/main.py",
            module="core",
            lines_of_code=100
        )
        
        memory_store.update_file_metadata(sample_project_id, metadata)
        
        retrieved = memory_store.get_file_metadata(sample_project_id, "src/main.py")
        assert retrieved.path == "src/main.py"
        assert retrieved.module == "core"
        assert retrieved.lines_of_code == 100
    
    def test_get_all_file_metadata_returns_files(self, memory_store, sample_project_id):
        """Test that get_all_file_metadata returns all stored files."""
        # Store multiple files
        for i in range(3):
            metadata = FileMetadataFactory.create(path=f"src/file{i}.py")
            memory_store.update_file_metadata(sample_project_id, metadata)
        
        files = memory_store.get_all_file_metadata(sample_project_id)
        
        assert len(files) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
