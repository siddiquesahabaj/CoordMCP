"""
Unit tests for ProjectMemoryStore functionality with Pydantic schema.

These tests verify the core memory operations including:
- Project creation and management
- Decision storage and retrieval with soft delete
- Tech stack management
- Change logging with indexing
- File metadata management with indexing
- Relationship tracking
- Schema migration
"""

import pytest
from datetime import datetime, timedelta
from coordmcp.memory.models import (
    Decision, TechStackEntry, Change, FileMetadata,
    DecisionStatus, ChangeType, ArchitectureImpact, FileType, Complexity,
    RelationshipType
)
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
    
    def test_create_project_returns_valid_uuid(self, memory_store, fresh_temp_dir):
        """Test that create_project returns a valid UUID."""
        workspace = fresh_temp_dir / "new_project"
        workspace.mkdir()
        
        project_id = memory_store.create_project(
            project_name="New Project",
            description="A test project",
            workspace_path=str(workspace)
        )
        
        assert_valid_uuid(project_id)
    
    def test_create_project_makes_project_exist(self, memory_store, fresh_temp_dir):
        """Test that created project exists in store."""
        workspace = fresh_temp_dir / "test_project"
        workspace.mkdir()
        
        project_id = memory_store.create_project(
            project_name="Test Project",
            description="Test description",
            workspace_path=str(workspace)
        )
        
        assert_project_exists(memory_store, project_id)
    
    def test_create_project_stores_correct_info(self, memory_store, fresh_temp_dir):
        """Test that project info is stored correctly."""
        workspace = fresh_temp_dir / "my_project"
        workspace.mkdir()
        
        project_id = memory_store.create_project(
            project_name="My Project",
            description="My description",
            workspace_path=str(workspace)
        )
        
        project_info = memory_store.get_project_info(project_id)
        assert project_info.project_name == "My Project"
        assert project_info.description == "My description"
        assert project_info.workspace_path == str(workspace)
        assert project_info.schema_version == "1.2.0"
    
    def test_create_project_stores_workspace_path(self, memory_store, fresh_temp_dir):
        """Test that create_project stores workspace_path correctly."""
        workspace = fresh_temp_dir / "test_workspace"
        workspace.mkdir()
        
        project_id = memory_store.create_project(
            project_name="Test Project",
            description="Test description",
            workspace_path=str(workspace)
        )
        
        project_info = memory_store.get_project_info(project_id)
        assert project_info.workspace_path == str(workspace)


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
        assert retrieved.status == DecisionStatus.ACTIVE
    
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
    
    def test_decision_soft_delete(self, memory_store, sample_project_id):
        """Test that decisions can be soft deleted."""
        decision = DecisionFactory.create(title="To Delete")
        decision_id = memory_store.save_decision(sample_project_id, decision)
        
        # Soft delete
        memory_store.delete_decision(sample_project_id, decision_id, agent_id="test-agent", soft=True)
        
        # Should not appear in normal query
        retrieved = memory_store.get_decision(sample_project_id, decision_id)
        assert retrieved is None
        
        # Should appear with include_deleted
        all_decisions = memory_store.get_all_decisions(sample_project_id, include_deleted=True)
        assert len(all_decisions) == 1
        assert all_decisions[0].is_deleted is True
    
    def test_decision_version_increment(self, memory_store, sample_project_id):
        """Test that decision version increments on update."""
        decision = DecisionFactory.create(title="Version Test")
        decision_id = memory_store.save_decision(sample_project_id, decision, agent_id="agent-1")
        
        # Get and check (touch() incremented version to 2 on first save)
        retrieved = memory_store.get_decision(sample_project_id, decision_id)
        assert retrieved.version == 2
        assert retrieved.updated_by == "agent-1"
        
        # Save again (simulating update)
        retrieved.title = "Updated Title"
        memory_store.save_decision(sample_project_id, retrieved, agent_id="agent-2")
        
        # Check version incremented again
        updated = memory_store.get_decision(sample_project_id, decision_id)
        assert updated.version == 3
        assert updated.updated_by == "agent-2"


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
    """Test change logging operations with indexing."""
    
    def test_log_change_returns_id(self, memory_store, sample_project_id):
        """Test that log_change returns a change ID."""
        change = ChangeFactory.create(file_path="src/main.py")
        
        change_id = memory_store.log_change(sample_project_id, change)
        
        assert change_id is not None
    
    def test_get_recent_changes_returns_changes(self, memory_store, sample_project_id):
        """Test that get_recent_changes returns logged changes."""
        change = ChangeFactory.create(
            file_path="src/main.py",
            change_type=ChangeType.CREATE,
            description="Initial commit"
        )
        memory_store.log_change(sample_project_id, change)
        
        changes = memory_store.get_recent_changes(sample_project_id)
        
        assert len(changes) == 1
        assert changes[0].file_path == "src/main.py"
        assert changes[0].change_type == ChangeType.CREATE
    
    def test_get_recent_changes_respects_limit(self, memory_store, sample_project_id):
        """Test that get_recent_changes respects the limit parameter."""
        # Log 5 changes
        for i in range(5):
            change = ChangeFactory.create(file_path=f"src/file{i}.py")
            memory_store.log_change(sample_project_id, change)
        
        changes = memory_store.get_recent_changes(sample_project_id, limit=3)
        
        assert len(changes) == 3
    
    def test_get_changes_for_file(self, memory_store, sample_project_id):
        """Test that get_changes_for_file uses the index."""
        # Log changes for different files
        change1 = ChangeFactory.create(file_path="src/main.py", description="Change 1")
        change2 = ChangeFactory.create(file_path="src/main.py", description="Change 2")
        change3 = ChangeFactory.create(file_path="src/other.py", description="Change 3")
        
        memory_store.log_change(sample_project_id, change1)
        memory_store.log_change(sample_project_id, change2)
        memory_store.log_change(sample_project_id, change3)
        
        # Get changes for specific file
        changes = memory_store.get_changes_for_file(sample_project_id, "src/main.py")
        
        assert len(changes) == 2
        assert all(c.file_path == "src/main.py" for c in changes)
    
    def test_get_changes_in_date_range(self, memory_store, sample_project_id):
        """Test that get_changes_in_date_range uses the index."""
        from datetime import datetime, timedelta
        
        # Create changes at different times
        change1 = ChangeFactory.create(file_path="src/old.py")
        change1.created_at = datetime.now() - timedelta(days=5)
        
        change2 = ChangeFactory.create(file_path="src/recent.py")
        change2.created_at = datetime.now() - timedelta(days=1)
        
        memory_store.log_change(sample_project_id, change1)
        memory_store.log_change(sample_project_id, change2)
        
        # Query last 3 days
        start = datetime.now() - timedelta(days=3)
        end = datetime.now()
        changes = memory_store.get_changes_in_date_range(sample_project_id, start, end)
        
        assert len(changes) == 1
        assert changes[0].file_path == "src/recent.py"
    
    def test_get_changes_by_agent(self, memory_store, sample_project_id):
        """Test that get_changes_by_agent uses the index."""
        change1 = ChangeFactory.create(file_path="src/agent1.py", agent_id="agent-1")
        change2 = ChangeFactory.create(file_path="src/agent2.py", agent_id="agent-2")
        
        memory_store.log_change(sample_project_id, change1)
        memory_store.log_change(sample_project_id, change2)
        
        changes = memory_store.get_changes_by_agent(sample_project_id, "agent-1")
        
        assert len(changes) == 1
        assert changes[0].agent_id == "agent-1"


@pytest.mark.unit
@pytest.mark.memory
class TestFileMetadata:
    """Test file metadata operations with indexing."""
    
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
    
    def test_get_files_by_module(self, memory_store, sample_project_id):
        """Test that get_files_by_module uses the index."""
        # Store files in different modules
        meta1 = FileMetadataFactory.create(path="src/core/main.py", module="core")
        meta2 = FileMetadataFactory.create(path="src/core/utils.py", module="core")
        meta3 = FileMetadataFactory.create(path="src/api/routes.py", module="api")
        
        memory_store.update_file_metadata(sample_project_id, meta1)
        memory_store.update_file_metadata(sample_project_id, meta2)
        memory_store.update_file_metadata(sample_project_id, meta3)
        
        core_files = memory_store.get_files_by_module(sample_project_id, "core")
        
        assert len(core_files) == 2
        assert all(f.module == "core" for f in core_files)
    
    def test_get_files_by_complexity(self, memory_store, sample_project_id):
        """Test that get_files_by_complexity uses the index."""
        # Store files with different complexity
        meta1 = FileMetadataFactory.create(path="src/simple.py", complexity=Complexity.LOW)
        meta2 = FileMetadataFactory.create(path="src/medium.py", complexity=Complexity.MEDIUM)
        meta3 = FileMetadataFactory.create(path="src/complex.py", complexity=Complexity.HIGH)
        
        memory_store.update_file_metadata(sample_project_id, meta1)
        memory_store.update_file_metadata(sample_project_id, meta2)
        memory_store.update_file_metadata(sample_project_id, meta3)
        
        high_complexity = memory_store.get_files_by_complexity(sample_project_id, "high")
        
        assert len(high_complexity) == 1
        assert high_complexity[0].path == "src/complex.py"
    
    def test_detect_circular_dependencies(self, memory_store, sample_project_id):
        """Test circular dependency detection."""
        # Create files with circular dependency: A -> B -> C -> A
        meta_a = FileMetadataFactory.create(
            path="src/a.py",
            dependencies=["src/b.py"]
        )
        meta_b = FileMetadataFactory.create(
            path="src/b.py",
            dependencies=["src/c.py"]
        )
        meta_c = FileMetadataFactory.create(
            path="src/c.py",
            dependencies=["src/a.py"]
        )
        
        memory_store.update_file_metadata(sample_project_id, meta_a)
        memory_store.update_file_metadata(sample_project_id, meta_b)
        memory_store.update_file_metadata(sample_project_id, meta_c)
        
        cycles = memory_store.detect_circular_dependencies(sample_project_id)
        
        assert len(cycles) == 1
        assert "src/a.py" in cycles[0]
        assert "src/b.py" in cycles[0]
        assert "src/c.py" in cycles[0]


@pytest.mark.unit
@pytest.mark.memory
class TestRelationships:
    """Test relationship tracking between entities."""
    
    def test_create_relationship_via_decision(self, memory_store, sample_project_id):
        """Test that saving a decision creates relationships to files."""
        # Create decision with related files
        decision = DecisionFactory.create(
            title="Test Decision",
            related_files=["src/main.py", "src/utils.py"]
        )
        decision_id = memory_store.save_decision(sample_project_id, decision)
        
        # Get relationships
        relationships = memory_store.get_relationships(sample_project_id)
        
        assert len(relationships) == 2
        assert all(r.source_type == "decision" for r in relationships)
        assert all(r.source_id == decision_id for r in relationships)
        assert all(r.target_type == "file" for r in relationships)
    
    def test_get_related_entities(self, memory_store, sample_project_id):
        """Test getting entities related to a specific entity."""
        # Create decision with related files
        decision = DecisionFactory.create(
            title="Test Decision",
            related_files=["src/main.py"]
        )
        decision_id = memory_store.save_decision(sample_project_id, decision)
        
        # Get related entities
        related = memory_store.get_related_entities(sample_project_id, "decision", decision_id)
        
        assert "files" in related
        assert "src/main.py" in related["files"]


@pytest.mark.unit
@pytest.mark.memory
class TestProjectDeletion:
    """Test project deletion operations."""
    
    def test_soft_delete_project(self, memory_store, fresh_temp_dir):
        """Test that projects can be soft deleted."""
        workspace = fresh_temp_dir / "to_delete"
        workspace.mkdir()
        project_id = memory_store.create_project("To Delete", "Will be deleted", str(workspace))
        
        # Soft delete
        memory_store.delete_project(project_id, agent_id="test-agent", soft=True)
        
        # Should still exist but be marked deleted
        project = memory_store.get_project_info(project_id)
        assert project.is_deleted is True
        assert project.deleted_at is not None
    
    def test_hard_delete_project(self, memory_store, fresh_temp_dir):
        """Test that projects can be hard deleted."""
        workspace = fresh_temp_dir / "to_delete_hard"
        workspace.mkdir()
        project_id = memory_store.create_project("To Delete", "Will be deleted", str(workspace))
        
        # Add some data
        decision = DecisionFactory.create()
        memory_store.save_decision(project_id, decision)
        
        # Hard delete
        memory_store.delete_project(project_id, agent_id="test-agent", soft=False)
        
        # Should no longer exist
        assert memory_store.get_project_info(project_id) is None
        assert not memory_store.project_exists(project_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
