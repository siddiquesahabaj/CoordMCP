"""
Unit tests for Pydantic models in CoordMCP.

Tests cover:
- BaseEntity functionality (touch, soft_delete, restore)
- Decision model and index
- Change model and index
- FileMetadata model and index
- Task model
- AgentMessage model
- SessionSummary model
- ActivityFeedItem model
- ProjectInfo model
- DataContainer migrations
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from coordmcp.memory.models import (
    BaseEntity, Decision, DecisionIndex, DecisionStatus,
    Change, ChangeIndex, ChangeType, ArchitectureImpact,
    FileMetadata, FileMetadataIndex, FileType, Complexity,
    Task, TaskStatus, AgentMessage, MessageType,
    SessionSummary, ActivityFeedItem, ProjectInfo,
    ArchitectureModule, Relationship, RelationshipType,
    DataContainer, SCHEMA_VERSION
)


@pytest.mark.unit
@pytest.mark.models
class TestBaseEntity:
    """Test BaseEntity functionality."""
    
    def test_touch_updates_timestamp(self):
        """Test that touch updates timestamps."""
        entity = BaseEntity(id=str(uuid4()))
        old_updated = entity.updated_at
        
        entity.touch("test-agent")
        
        assert entity.updated_at > old_updated
        assert entity.updated_by == "test-agent"
    
    def test_touch_increments_version(self):
        """Test that touch increments version."""
        entity = BaseEntity(id=str(uuid4()), version=1)
        
        entity.touch()
        
        assert entity.version == 2
    
    def test_soft_delete_sets_flags(self):
        """Test that soft_delete sets appropriate flags."""
        entity = BaseEntity(id=str(uuid4()))
        
        entity.soft_delete("test-agent")
        
        assert entity.is_deleted is True
        assert entity.deleted_at is not None
        assert entity.updated_by == "test-agent"
    
    def test_restore_clears_flags(self):
        """Test that restore clears delete flags."""
        entity = BaseEntity(id=str(uuid4()))
        entity.soft_delete()
        
        entity.restore("test-agent")
        
        assert entity.is_deleted is False
        assert entity.deleted_at is None


@pytest.mark.unit
@pytest.mark.models
class TestDecision:
    """Test Decision model."""
    
    def test_create_decision_with_required_fields(self):
        """Test creating a decision with required fields."""
        decision = Decision(
            id=str(uuid4()),
            title="Test Decision",
            description="Test description"
        )
        
        assert decision.title == "Test Decision"
        assert decision.status == DecisionStatus.ACTIVE
    
    def test_decision_validation_min_title_length(self):
        """Test that title must be at least 3 characters."""
        with pytest.raises(Exception):
            Decision(id=str(uuid4()), title="AB", description="Test")
    
    def test_decision_validation_min_description_length(self):
        """Test that description must be at least 10 characters."""
        with pytest.raises(Exception):
            Decision(id=str(uuid4()), title="Test Decision", description="Too short")
    
    def test_get_search_tokens(self):
        """Test that get_search_tokens extracts meaningful words."""
        decision = Decision(
            id=str(uuid4()),
            title="Use FastAPI Framework",
            description="We decided to use FastAPI for our REST API",
            tags=["backend", "api"]
        )
        
        tokens = decision.get_search_tokens()
        
        assert "fastapi" in tokens
        assert "framework" in tokens
        assert "backend" in tokens
    
    def test_is_valid_at(self):
        """Test decision validity at different times."""
        now = datetime.now()
        decision = Decision(
            id=str(uuid4()),
            title="Test",
            description="Test description",
            valid_from=now - timedelta(days=1),
            valid_to=now + timedelta(days=1)
        )
        
        assert decision.is_valid_at(now) is True
        assert decision.is_valid_at(now + timedelta(days=2)) is False
    
    def test_create_new_version(self):
        """Test creating a new version of a decision."""
        original = Decision(
            id="decision-1",
            title="Original",
            description="Original description",
            version=1
        )
        
        new_version = original.create_new_version(
            {"title": "Updated", "description": "Updated description"},
            "test-agent"
        )
        
        assert original.status == DecisionStatus.SUPERSEDED
        assert original.superseded_by == new_version.id
        assert new_version.supersedes == ["decision-1"]


@pytest.mark.unit
@pytest.mark.models
class TestDecisionIndex:
    """Test DecisionIndex functionality."""
    
    def test_add_decision_to_index(self):
        """Test adding a decision to the index."""
        index = DecisionIndex()
        decision = Decision(
            id="dec-1",
            title="Use Python",
            description="We chose Python for backend",
            tags=["backend"],
            author_agent_id="agent-1"
        )
        
        index.add_decision(decision)
        
        assert "backend" in index.by_tag
        assert "dec-1" in index.by_tag["backend"]
        assert "agent-1" in index.by_author
        assert "dec-1" in index.by_author["agent-1"]
    
    def test_remove_decision_from_index(self):
        """Test removing a decision from the index."""
        index = DecisionIndex()
        decision = Decision(
            id="dec-1",
            title="Test",
            description="Test description",
            tags=["test"],
            author_agent_id="agent-1"
        )
        index.add_decision(decision)
        
        index.remove_decision(decision)
        
        assert "dec-1" not in index.by_tag.get("test", [])
    
    def test_search_by_query(self):
        """Test searching decisions by query."""
        index = DecisionIndex()
        decisions = {
            "dec-1": Decision(id="dec-1", title="Use FastAPI", description="Fast framework"),
            "dec-2": Decision(id="dec-2", title="Use Django", description="Full framework")
        }
        for d in decisions.values():
            index.add_decision(d)
        
        results = index.search("FastAPI", decisions)
        
        assert len(results) == 1
        assert results[0].id == "dec-1"


@pytest.mark.unit
@pytest.mark.models
class TestChange:
    """Test Change model."""
    
    def test_create_change(self):
        """Test creating a change."""
        change = Change(
            id=str(uuid4()),
            file_path="src/main.py",
            change_type=ChangeType.CREATE,
            description="Created main file"
        )
        
        assert change.change_type == ChangeType.CREATE
        assert change.architecture_impact == ArchitectureImpact.NONE
    
    def test_get_search_tokens(self):
        """Test change search tokens."""
        change = Change(
            id=str(uuid4()),
            file_path="src/auth/login.py",
            description="Added user authentication",
            code_summary="Implemented JWT login"
        )
        
        tokens = change.get_search_tokens()
        
        assert "authentication" in tokens
        assert "jwt" in tokens


@pytest.mark.unit
@pytest.mark.models
class TestChangeIndex:
    """Test ChangeIndex functionality."""
    
    def test_add_change_to_index(self):
        """Test adding a change to the index."""
        index = ChangeIndex()
        change = Change(
            id="change-1",
            file_path="src/main.py",
            change_type=ChangeType.CREATE,
            agent_id="agent-1"
        )
        
        index.add_change(change)
        
        assert "src/main.py" in index.by_file
        assert "change-1" in index.by_file["src/main.py"]
        assert "agent-1" in index.by_agent
    
    def test_get_changes_in_date_range(self):
        """Test getting changes in a date range."""
        index = ChangeIndex()
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        change = Change(
            id="change-1",
            file_path="src/main.py",
            change_type=ChangeType.CREATE,
            created_at=now
        )
        index.add_change(change)
        
        results = index.get_changes_in_date_range(yesterday, now + timedelta(days=1))
        
        assert "change-1" in results


@pytest.mark.unit
@pytest.mark.models
class TestFileMetadata:
    """Test FileMetadata model."""
    
    def test_create_file_metadata(self):
        """Test creating file metadata."""
        metadata = FileMetadata(
            id=str(uuid4()),
            path="src/main.py",
            file_type=FileType.SOURCE,
            complexity=Complexity.LOW
        )
        
        assert metadata.file_type == FileType.SOURCE
        assert metadata.complexity == Complexity.LOW
    
    def test_add_related_decision(self):
        """Test adding related decision."""
        metadata = FileMetadata(id=str(uuid4()), path="src/main.py")
        
        metadata.add_related_decision("decision-1")
        
        assert "decision-1" in metadata.related_decisions
    
    def test_no_duplicate_related_decisions(self):
        """Test that duplicate related decisions are not added."""
        metadata = FileMetadata(id=str(uuid4()), path="src/main.py")
        
        metadata.add_related_decision("decision-1")
        metadata.add_related_decision("decision-1")
        
        assert len(metadata.related_decisions) == 1


@pytest.mark.unit
@pytest.mark.models
class TestFileMetadataIndex:
    """Test FileMetadataIndex functionality."""
    
    def test_add_file_to_index(self):
        """Test adding a file to the index."""
        index = FileMetadataIndex()
        metadata = FileMetadata(
            id=str(uuid4()),
            path="src/core/main.py",
            module="core",
            complexity=Complexity.MEDIUM
        )
        
        index.add_file(metadata)
        
        assert "core" in index.by_module
        assert "medium" in index.by_complexity
    
    def test_detect_cycles(self):
        """Test cycle detection in dependencies."""
        index = FileMetadataIndex()
        index.dependency_graph = {
            "a.py": {"b.py"},
            "b.py": {"c.py"},
            "c.py": {"a.py"}
        }
        
        cycles = index.detect_cycles()
        
        assert len(cycles) > 0


@pytest.mark.unit
@pytest.mark.models
class TestTask:
    """Test Task model."""
    
    def test_create_task(self):
        """Test creating a task."""
        task = Task(
            id=str(uuid4()),
            title="Implement feature",
            project_id="proj-1"
        )
        
        assert task.status == TaskStatus.PENDING
        assert task.priority == "medium"
    
    def test_task_start(self):
        """Test starting a task."""
        task = Task(id=str(uuid4()), title="Test", project_id="proj-1")
        
        task.start("agent-1")
        
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.assigned_agent_id == "agent-1"
        assert task.started_at is not None
    
    def test_task_complete(self):
        """Test completing a task."""
        task = Task(id=str(uuid4()), title="Test", project_id="proj-1")
        task.start("agent-1")
        
        task.complete("agent-1")
        
        assert task.status == TaskStatus.COMPLETED
        assert task.completed_at is not None
        assert task.actual_hours > 0
    
    def test_task_block(self):
        """Test blocking a task."""
        task = Task(id=str(uuid4()), title="Test", project_id="proj-1")
        
        task.block("agent-1", "Waiting for API")
        
        assert task.status == TaskStatus.BLOCKED
        assert task.metadata.get("block_reason") == "Waiting for API"
    
    def test_is_blocked(self):
        """Test is_blocked check."""
        task = Task(id=str(uuid4()), title="Test", project_id="proj-1")
        
        assert task.is_blocked() is False
        task.block("agent-1")
        assert task.is_blocked() is True
    
    def test_is_completed(self):
        """Test is_completed check."""
        task = Task(id=str(uuid4()), title="Test", project_id="proj-1")
        
        assert task.is_completed() is False
        task.complete("agent-1")
        assert task.is_completed() is True


@pytest.mark.unit
@pytest.mark.models
class TestAgentMessage:
    """Test AgentMessage model."""
    
    def test_create_message(self):
        """Test creating a message."""
        msg = AgentMessage(
            id=str(uuid4()),
            from_agent_id="agent-1",
            from_agent_name="Agent One",
            to_agent_id="agent-2",
            project_id="proj-1",
            message_type=MessageType.UPDATE,
            content="Progress update"
        )
        
        assert msg.read is False
        assert msg.message_type == MessageType.UPDATE
    
    def test_mark_read(self):
        """Test marking message as read."""
        msg = AgentMessage(
            id=str(uuid4()),
            from_agent_id="agent-1",
            from_agent_name="Agent One",
            to_agent_id="agent-2",
            project_id="proj-1",
            message_type=MessageType.UPDATE,
            content="Test"
        )
        
        msg.mark_read()
        
        assert msg.read is True
        assert msg.read_at is not None


@pytest.mark.unit
@pytest.mark.models
class TestSessionSummary:
    """Test SessionSummary model."""
    
    def test_create_session_summary(self):
        """Test creating a session summary."""
        summary = SessionSummary(
            id=str(uuid4()),
            agent_id="agent-1",
            project_id="proj-1",
            session_id="session-1",
            duration_minutes=60,
            objective="Build feature"
        )
        
        assert summary.duration_minutes == 60
        assert len(summary.files_modified) == 0
    
    def test_generate_summary_text(self):
        """Test generating summary text."""
        summary = SessionSummary(
            id=str(uuid4()),
            agent_id="agent-1",
            project_id="proj-1",
            session_id="session-1",
            duration_minutes=60,
            objective="Build feature",
            files_modified=["file1.py", "file2.py"],
            key_decisions_made=["dec-1"]
        )
        
        text = summary.generate_summary_text("TestAgent", "TestProject")
        
        assert "TestAgent" in text
        assert "TestProject" in text
        assert "60" in text
        assert "2 file" in text


@pytest.mark.unit
@pytest.mark.models
class TestActivityFeedItem:
    """Test ActivityFeedItem model."""
    
    def test_create_activity(self):
        """Test creating an activity feed item."""
        activity = ActivityFeedItem(
            id=str(uuid4()),
            activity_type="task_created",
            agent_id="agent-1",
            agent_name="Test Agent",
            project_id="proj-1",
            summary="Created task XYZ"
        )
        
        assert activity.activity_type == "task_created"
        assert activity.is_deleted is False


@pytest.mark.unit
@pytest.mark.models
class TestProjectInfo:
    """Test ProjectInfo model."""
    
    def test_create_project_info(self, fresh_temp_dir):
        """Test creating project info."""
        workspace = fresh_temp_dir / "test_project"
        workspace.mkdir()
        
        project = ProjectInfo(
            id=str(uuid4()),
            project_id="proj-1",
            project_name="Test Project",
            workspace_path=str(workspace)
        )
        
        assert project.project_name == "Test Project"
        assert project.schema_version == SCHEMA_VERSION
    
    def test_workspace_path_validation(self):
        """Test that workspace_path must be absolute."""
        with pytest.raises(Exception):
            ProjectInfo(
                id=str(uuid4()),
                project_id="proj-1",
                project_name="Test",
                workspace_path="relative/path"
            )


@pytest.mark.unit
@pytest.mark.models
class TestArchitectureModule:
    """Test ArchitectureModule model."""
    
    def test_create_module(self):
        """Test creating an architecture module."""
        module = ArchitectureModule(
            name="auth",
            purpose="Authentication module",
            files=["auth/login.py", "auth/logout.py"],
            dependencies=["core", "database"]
        )
        
        assert module.name == "auth"
        assert len(module.files) == 2
    
    def test_get_dependency_graph(self):
        """Test getting dependency graph."""
        module = ArchitectureModule(
            name="auth",
            purpose="Auth",
            dependencies=["core", "database"]
        )
        
        graph = module.get_dependency_graph()
        
        assert "auth" in graph
        assert "core" in graph["auth"]


@pytest.mark.unit
@pytest.mark.models
class TestRelationship:
    """Test Relationship model."""
    
    def test_create_relationship(self):
        """Test creating a relationship."""
        rel = Relationship(
            source_type="decision",
            source_id="dec-1",
            target_type="file",
            target_id="src/main.py",
            relationship_type=RelationshipType.REFERENCES
        )
        
        assert rel.relationship_type == RelationshipType.REFERENCES


@pytest.mark.unit
@pytest.mark.models
class TestDataContainer:
    """Test DataContainer migrations."""
    
    def test_create_data_container(self):
        """Test creating a data container."""
        container = DataContainer(data={"test": "value"})
        
        assert container.schema_version == SCHEMA_VERSION
        assert container.data["test"] == "value"
    
    def test_migrate_if_needed_same_version(self):
        """Test that migration doesn't run for current version."""
        container = DataContainer(schema_version=SCHEMA_VERSION)
        
        result = container.migrate_if_needed()
        
        assert result is False
    
    def test_migrate_1_0_0_to_current(self):
        """Test migration from 1.0.0 to current version."""
        container = DataContainer(
            schema_version="1.0.0",
            data={
                "decisions": {
                    "dec-1": {
                        "author_agent": "agent-1"
                    }
                }
            }
        )
        
        container.migrate_if_needed()
        
        assert container.schema_version == SCHEMA_VERSION
        assert "author_agent_id" in container.data["decisions"]["dec-1"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
