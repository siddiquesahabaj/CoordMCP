"""
Unit tests for ProjectMemoryStore
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from coordmcp.storage.json_adapter import JSONStorageBackend
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.memory.models import Decision, TechStackEntry, Change, FileMetadata


class TestProjectMemoryStore:
    """Test suite for ProjectMemoryStore"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONStorageBackend(Path(tmpdir))
            yield backend
    
    @pytest.fixture
    def memory_store(self, temp_storage):
        """Create memory store with temporary storage"""
        return ProjectMemoryStore(temp_storage)
    
    @pytest.fixture
    def sample_project_id(self, memory_store):
        """Create a sample project for testing"""
        return memory_store.create_project(
            project_name="Test Project",
            description="Test project for unit tests"
        )
    
    def test_create_project(self, memory_store):
        """Test creating a project"""
        project_id = memory_store.create_project(
            project_name="New Project",
            description="A test project"
        )
        
        assert project_id is not None
        assert len(project_id) > 0
        
        # Verify project exists
        assert memory_store.project_exists(project_id) is True
    
    def test_get_project_info(self, memory_store, sample_project_id):
        """Test retrieving project information"""
        project_info = memory_store.get_project_info(sample_project_id)
        
        assert project_info is not None
        assert project_info.project_name == "Test Project"
        assert project_info.description == "Test project for unit tests"
    
    def test_save_and_get_decision(self, memory_store, sample_project_id):
        """Test saving and retrieving a decision"""
        decision = Decision(
            title="Use FastAPI",
            description="For API layer",
            rationale="Performance",
            impact="All endpoints",
            tags=["backend"]
        )
        
        decision_id = memory_store.save_decision(sample_project_id, decision)
        
        assert decision_id is not None
        assert decision_id == decision.id
        
        # Retrieve decision
        retrieved = memory_store.get_decision(sample_project_id, decision_id)
        assert retrieved is not None
        assert retrieved.title == "Use FastAPI"
        assert retrieved.tags == ["backend"]
    
    def test_list_decisions(self, memory_store, sample_project_id):
        """Test listing all decisions"""
        # Save multiple decisions
        for i in range(3):
            decision = Decision(
                title=f"Decision {i}",
                description=f"Description {i}",
                rationale=f"Rationale {i}"
            )
            memory_store.save_decision(sample_project_id, decision)
        
        decisions = memory_store.get_all_decisions(sample_project_id)
        assert len(decisions) == 3
    
    def test_update_tech_stack(self, memory_store, sample_project_id):
        """Test updating tech stack"""
        entry = TechStackEntry(
            category="backend",
            technology="FastAPI",
            version="0.100.0",
            rationale="High performance"
        )
        
        memory_store.update_tech_stack(sample_project_id, entry)
        
        tech_stack = memory_store.get_tech_stack(sample_project_id)
        assert "backend" in tech_stack
        assert tech_stack["backend"]["technology"] == "FastAPI"
    
    def test_log_change(self, memory_store, sample_project_id):
        """Test logging changes"""
        change = Change(
            file_path="src/main.py",
            change_type="create",
            description="Initial commit",
            architecture_impact="significant"
        )
        
        change_id = memory_store.log_change(sample_project_id, change)
        assert change_id is not None
        
        # Get recent changes
        changes = memory_store.get_recent_changes(sample_project_id)
        assert len(changes) == 1
        assert changes[0].file_path == "src/main.py"
    
    def test_file_metadata(self, memory_store, sample_project_id):
        """Test file metadata operations"""
        metadata = FileMetadata(
            path="src/main.py",
            file_type="source",
            module="core",
            purpose="Main entry point",
            lines_of_code=50,
            complexity="low"
        )
        
        memory_store.update_file_metadata(sample_project_id, metadata)
        
        retrieved = memory_store.get_file_metadata(sample_project_id, "src/main.py")
        assert retrieved is not None
        assert retrieved.path == "src/main.py"
        assert retrieved.module == "core"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
