"""
Unit tests for ContextManager with Pydantic schema.

These tests verify:
- Agent registration with Pydantic validation
- Context lifecycle management
- Context switching
- File locking with priorities
- Concurrent agent scenarios
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from coordmcp.context.state import (
    AgentContext, AgentProfile, CurrentContext, LockInfo,
    AgentType, Priority, OperationType, SessionLogEntry
)
from coordmcp.memory.models import Task, TaskStatus, SessionSummary, ActivityFeedItem
from coordmcp.errors import AgentNotFoundError
from tests.utils.factories import (
    AgentContextFactory,
    CurrentContextFactory,
    LockInfoFactory,
    AgentProfileFactory,
    TaskFactory,
    SessionSummaryFactory,
    ActivityFeedItemFactory,
    ProjectInfoFactory
)
from tests.utils.assertions import assert_valid_uuid


@pytest.mark.unit
@pytest.mark.context
class TestAgentRegistration:
    """Test agent registration with Pydantic validation."""
    
    def test_register_agent_returns_valid_uuid(self, context_manager):
        """Test that register_agent returns a valid UUID."""
        agent_id = context_manager.register_agent(
            agent_name="Test Agent",
            agent_type="opencode",
            capabilities=["python", "fastapi"]
        )
        
        assert_valid_uuid(agent_id)
    
    def test_register_agent_stores_profile(self, context_manager):
        """Test that registered agent profile is stored correctly."""
        agent_id = context_manager.register_agent(
            agent_name="Backend Agent",
            agent_type="cursor",
            capabilities=["typescript", "nodejs"],
            version="2.0.0"
        )
        
        profile = context_manager.get_agent(agent_id)
        assert profile is not None
        assert profile.agent_name == "Backend Agent"
        assert profile.agent_type == AgentType.CURSOR
        assert profile.capabilities == ["typescript", "nodejs"]
        assert profile.version == "2.0.0"
        assert profile.status == "active"
    
    def test_register_agent_invalid_type_defaults_to_custom(self, context_manager):
        """Test that invalid agent type defaults to CUSTOM."""
        agent_id = context_manager.register_agent(
            agent_name="Custom Agent",
            agent_type="invalid_type",
            capabilities=[]
        )
        
        profile = context_manager.get_agent(agent_id)
        assert profile.agent_type == AgentType.CUSTOM
    
    def test_get_all_agents_returns_list(self, context_manager):
        """Test that get_all_agents returns all registered agents."""
        # Register multiple agents
        for i in range(3):
            context_manager.register_agent(
                agent_name=f"Agent {i}",
                agent_type="opencode"
            )
        
        agents = context_manager.get_all_agents()
        assert len(agents) == 3
    
    def test_update_agent_status(self, context_manager):
        """Test updating agent status."""
        agent_id = context_manager.register_agent(
            agent_name="Status Test",
            agent_type="opencode"
        )
        
        # Update status
        success = context_manager.update_agent_status(agent_id, "inactive")
        assert success is True
        
        profile = context_manager.get_agent(agent_id)
        assert profile.status == "inactive"
    
    def test_delete_agent_removes_profile(self, context_manager):
        """Test that delete_agent removes the agent."""
        agent_id = context_manager.register_agent(
            agent_name="To Delete",
            agent_type="opencode"
        )
        
        success = context_manager.delete_agent(agent_id)
        assert success is True
        
        profile = context_manager.get_agent(agent_id)
        assert profile is None


@pytest.mark.unit
@pytest.mark.context
class TestContextLifecycle:
    """Test context lifecycle management."""
    
    def test_start_context_creates_context(self, context_manager, sample_project_id):
        """Test that start_context creates a new context."""
        agent_id = context_manager.register_agent("Test Agent", "opencode")
        
        context = context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Implement feature X",
            task_description="Detailed description",
            priority="high"
        )
        
        assert context is not None
        assert context.current_context is not None
        assert context.current_context.current_objective == "Implement feature X"
        assert context.current_context.priority == Priority.HIGH
        assert context.agent_id == agent_id
    
    def test_start_context_raises_for_unregistered_agent(self, context_manager):
        """Test that start_context raises error for unregistered agent."""
        with pytest.raises(AgentNotFoundError):
            context_manager.start_context(
                agent_id="non-existent-id",
                project_id="project-1",
                objective="Test"
            )
    
    def test_end_context_clears_current(self, context_manager, sample_project_id):
        """Test that end_context clears the current context."""
        agent_id = context_manager.register_agent("Test Agent", "opencode")
        
        # Start context
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Test objective"
        )
        
        # End context
        success = context_manager.end_context(agent_id)
        assert success is True
        
        # Verify context cleared
        context = context_manager.get_context(agent_id)
        assert context.current_context is None
    
    def test_end_context_unlocks_files(self, context_manager, file_tracker, sample_project_id):
        """Test that end_context unlocks all files."""
        agent_id = context_manager.register_agent("Test Agent", "opencode")
        
        # Start context and lock files using context_manager (not file_tracker directly)
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Test"
        )
        context_manager.lock_files(agent_id, ["src/main.py"], reason="Testing")
        
        # Verify locked
        assert file_tracker.is_locked(sample_project_id, "src/main.py")
        
        # End context
        context_manager.end_context(agent_id)
        
        # Verify unlocked
        assert not file_tracker.is_locked(sample_project_id, "src/main.py")
    
    def test_get_context_returns_current(self, context_manager, sample_project_id):
        """Test that get_context returns the current context."""
        agent_id = context_manager.register_agent("Test Agent", "opencode")
        
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Test objective"
        )
        
        retrieved = context_manager.get_context(agent_id)
        assert retrieved is not None
        assert retrieved.current_context.current_objective == "Test objective"
    
    def test_get_context_history(self, context_manager, sample_project_id):
        """Test that get_context_history returns recent operations."""
        agent_id = context_manager.register_agent("Test Agent", "opencode")
        
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Test"
        )
        
        # Add some context entries
        for i in range(5):
            context_manager.add_context_entry(
                agent_id=agent_id,
                file=f"src/file{i}.py",
                operation="write",
                summary=f"Edit {i}"
            )
        
        history = context_manager.get_context_history(agent_id, limit=3)
        assert len(history) == 3
        assert history[0].file == "src/file4.py"
    
    def test_get_session_log(self, context_manager, sample_project_id):
        """Test that get_session_log returns session events."""
        agent_id = context_manager.register_agent("Test Agent", "opencode")
        
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Test"
        )
        
        log = context_manager.get_session_log(agent_id)
        assert len(log) >= 1  # Should have context_started event
        assert log[0].event == "context_started"


@pytest.mark.unit
@pytest.mark.context
class TestContextSwitching:
    """Test context switching between projects."""
    
    def test_switch_context_changes_project(self, context_manager, sample_project_id):
        """Test that switch_context changes the current project."""
        agent_id = context_manager.register_agent("Test Agent", "opencode")
        
        # Start in first project
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="First objective"
        )
        
        # Switch to new project
        new_context = context_manager.switch_context(
            agent_id=agent_id,
            new_project_id="new-project-id",
            new_objective="New objective"
        )
        
        assert new_context.current_context.project_id == "new-project-id"
        assert new_context.current_context.current_objective == "New objective"
    
    def test_switch_context_clears_previous_locks(self, context_manager, file_tracker, sample_project_id):
        """Test that switch_context clears locks from previous project."""
        agent_id = context_manager.register_agent("Test Agent", "opencode")
        
        # Start and lock files in first project using context_manager
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="First"
        )
        context_manager.lock_files(agent_id, ["src/main.py"], reason="Testing")
        
        # Verify locked
        assert file_tracker.is_locked(sample_project_id, "src/main.py")
        
        # Switch to new project
        context_manager.switch_context(
            agent_id=agent_id,
            new_project_id="new-project",
            new_objective="New"
        )
        
        # Verify old project files unlocked
        assert not file_tracker.is_locked(sample_project_id, "src/main.py")


@pytest.mark.unit
@pytest.mark.context
class TestAgentReconnection:
    """Test agent reconnection behavior."""
    
    def test_register_agent_reconnects_existing_agent(self, context_manager):
        """Test that register_agent reconnects to existing agent by name."""
        # Register agent first time
        agent_id_1 = context_manager.register_agent(
            agent_name="Reconnect Agent",
            agent_type="opencode",
            capabilities=["python"]
        )
        
        # Register same agent again
        agent_id_2 = context_manager.register_agent(
            agent_name="Reconnect Agent",
            agent_type="opencode",
            capabilities=["python", "javascript"]
        )
        
        # Should return same ID
        assert agent_id_1 == agent_id_2
        
        # Capabilities should be updated
        profile = context_manager.get_agent(agent_id_1)
        assert "javascript" in profile.capabilities
    
    def test_register_agent_updates_last_active_on_reconnect(self, context_manager):
        """Test that last_active is updated on reconnection."""
        agent_id = context_manager.register_agent("Test", "opencode")
        profile_1 = context_manager.get_agent(agent_id)
        first_active = profile_1.last_active
        
        # Small delay and reconnect
        import time
        time.sleep(0.01)
        
        context_manager.register_agent("Test", "opencode")
        profile_2 = context_manager.get_agent(agent_id)
        
        assert profile_2.last_active > first_active
    
    def test_register_agent_creates_new_if_inactive(self, context_manager):
        """Test that a new agent is created if existing is inactive."""
        agent_id_1 = context_manager.register_agent("Inactive Agent", "opencode")
        context_manager.update_agent_status(agent_id_1, "inactive")
        
        # Register with same name
        agent_id_2 = context_manager.register_agent("Inactive Agent", "opencode")
        
        # Should create new agent since old one is inactive
        assert agent_id_1 != agent_id_2


@pytest.mark.unit
@pytest.mark.context
class TestTaskLinking:
    """Test task linking in context management."""
    
    def test_start_context_with_task_id(self, context_manager, memory_store, sample_project_id):
        """Test that start_context links to task when task_id provided."""
        agent_id = context_manager.register_agent("Task Agent", "opencode")
        
        # Create a task
        task = TaskFactory.create(status=TaskStatus.PENDING, project_id=sample_project_id)
        memory_store.create_task(task)
        
        # Start context with task_id
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Work on task",
            task_id=task.id
        )
        
        # Verify task status updated to in_progress
        updated_task = memory_store.get_task(sample_project_id, task.id)
        assert updated_task.status == TaskStatus.IN_PROGRESS
        assert updated_task.assigned_agent_id == agent_id
        assert updated_task.started_at is not None
    
    def test_start_context_skips_completed_task(self, context_manager, memory_store, sample_project_id):
        """Test that linking to completed task doesn't change status."""
        agent_id = context_manager.register_agent("Task Agent", "opencode")
        
        # Create a completed task
        task = TaskFactory.create(status=TaskStatus.COMPLETED, project_id=sample_project_id)
        memory_store.create_task(task)
        
        # Start context with task_id
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Review task",
            task_id=task.id
        )
        
        # Task should remain completed
        updated_task = memory_store.get_task(sample_project_id, task.id)
        assert updated_task.status == TaskStatus.COMPLETED
    
    def test_end_context_completes_linked_task(self, context_manager, memory_store, sample_project_id):
        """Test that ending context completes the linked task."""
        agent_id = context_manager.register_agent("Task Agent", "opencode")
        
        # Create and start a task
        task = TaskFactory.create(status=TaskStatus.PENDING, project_id=sample_project_id)
        memory_store.create_task(task)
        
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Work on task",
            task_id=task.id
        )
        
        # End context
        context_manager.end_context(agent_id)
        
        # Verify task completed
        updated_task = memory_store.get_task(sample_project_id, task.id)
        assert updated_task.status == TaskStatus.COMPLETED
        assert updated_task.completed_at is not None
        assert updated_task.actual_hours is not None
    
    def test_context_stores_task_id(self, context_manager, memory_store, sample_project_id):
        """Test that task_id is stored in current_context."""
        agent_id = context_manager.register_agent("Task Agent", "opencode")
        
        task = TaskFactory.create(status=TaskStatus.PENDING, project_id=sample_project_id)
        memory_store.create_task(task)
        
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Work on task",
            task_id=task.id
        )
        
        context = context_manager.get_context(agent_id)
        assert context.current_context.current_task_id == task.id


@pytest.mark.unit
@pytest.mark.context
class TestSessionSummaryGeneration:
    """Test session summary generation on context end."""
    
    def test_end_context_creates_session_summary(self, context_manager, memory_store, sample_project_id):
        """Test that ending context creates a session summary."""
        agent_id = context_manager.register_agent("Summary Agent", "opencode")
        
        # Start and end context
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Test objective"
        )
        
        # Add some context entries
        context_manager.add_context_entry(agent_id, "src/main.py", "write", "Modified main")
        context_manager.add_context_entry(agent_id, "src/utils.py", "read", "Read utils")
        
        context_manager.end_context(agent_id)
        
        # Check session summary was created
        summaries = memory_store.get_session_summaries(sample_project_id)
        assert len(summaries) == 1
        assert summaries[0].objective == "Test objective"
        assert "src/main.py" in summaries[0].files_modified
    
    def test_end_context_logs_activity(self, context_manager, memory_store, sample_project_id):
        """Test that ending context logs an activity."""
        agent_id = context_manager.register_agent("Activity Agent", "opencode")
        
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Test objective"
        )
        
        context_manager.end_context(agent_id)
        
        # Check activity was logged
        activities = memory_store.get_recent_activities(sample_project_id)
        assert any(a.activity_type == "session_completed" for a in activities)
    
    def test_session_summary_includes_modified_files(self, context_manager, memory_store, sample_project_id):
        """Test that session summary includes files that were written."""
        agent_id = context_manager.register_agent("Files Agent", "opencode")
        
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Modify files"
        )
        
        # Add various operations
        context_manager.add_context_entry(agent_id, "src/main.py", "write", "Modified")
        context_manager.add_context_entry(agent_id, "src/test.py", "write", "Tests")
        context_manager.add_context_entry(agent_id, "src/readme.md", "read", "Read")
        
        context_manager.end_context(agent_id)
        
        summaries = memory_store.get_session_summaries(sample_project_id)
        files_modified = summaries[0].files_modified
        
        assert "src/main.py" in files_modified
        assert "src/test.py" in files_modified
        assert "src/readme.md" not in files_modified


@pytest.mark.unit
@pytest.mark.context
class TestProjectHistory:
    """Test cross-project history updates."""
    
    def test_end_context_updates_project_history(self, context_manager, sample_project_id):
        """Test that ending context updates agent's project history."""
        agent_id = context_manager.register_agent("History Agent", "opencode")
        
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Test"
        )
        context_manager.end_context(agent_id)
        
        profile = context_manager.get_agent(agent_id)
        assert profile.last_project_id == sample_project_id
        
        # Should have project in history
        project_ids = [a.project_id for a in profile.cross_project_history]
        assert sample_project_id in project_ids
    
    def test_multiple_sessions_increment_count(self, context_manager, sample_project_id):
        """Test that multiple sessions increment the session count."""
        agent_id = context_manager.register_agent("Multi Agent", "opencode")
        
        # First session
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="First"
        )
        context_manager.end_context(agent_id)
        
        profile = context_manager.get_agent(agent_id)
        activity = next(a for a in profile.cross_project_history if a.project_id == sample_project_id)
        first_count = activity.total_sessions
        
        # Second session
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Second"
        )
        context_manager.end_context(agent_id)
        
        profile = context_manager.get_agent(agent_id)
        activity = next(a for a in profile.cross_project_history if a.project_id == sample_project_id)
        
        assert activity.total_sessions == first_count + 1


@pytest.mark.unit
@pytest.mark.context
class TestGetAgentsInProject:
    """Test get_agents_in_project functionality."""
    
    def test_get_agents_in_project_returns_active(self, context_manager, sample_project_id):
        """Test that get_agents_in_project returns agents with active contexts."""
        # Register agents
        agent_id_1 = context_manager.register_agent("Agent 1", "opencode")
        agent_id_2 = context_manager.register_agent("Agent 2", "cursor")
        agent_id_3 = context_manager.register_agent("Agent 3", "opencode")
        
        # Start contexts for first two in the project
        context_manager.start_context(
            agent_id=agent_id_1,
            project_id=sample_project_id,
            objective="Work 1"
        )
        context_manager.start_context(
            agent_id=agent_id_2,
            project_id=sample_project_id,
            objective="Work 2"
        )
        context_manager.start_context(
            agent_id=agent_id_3,
            project_id="other-project",
            objective="Other work"
        )
        
        agents = context_manager.get_agents_in_project(sample_project_id)
        
        assert len(agents) == 2
        agent_names = [a["agent_name"] for a in agents]
        assert "Agent 1" in agent_names
        assert "Agent 2" in agent_names
        assert "Agent 3" not in agent_names
    
    def test_get_agents_in_project_includes_lock_info(self, context_manager, sample_project_id):
        """Test that get_agents_in_project includes locked files count."""
        agent_id = context_manager.register_agent("Lock Agent", "opencode")
        
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Lock files"
        )
        context_manager.lock_files(agent_id, ["file1.py", "file2.py"], reason="Testing")
        
        agents = context_manager.get_agents_in_project(sample_project_id)
        
        assert len(agents) == 1
        assert agents[0]["locked_files_count"] == 2
    
    def test_get_agents_in_project_empty_when_none(self, context_manager):
        """Test that get_agents_in_project returns empty list when no agents."""
        agents = context_manager.get_agents_in_project("no-agents-project")
        assert agents == []


@pytest.mark.unit
@pytest.mark.context
class TestGetCurrentContext:
    """Test get_current_context functionality."""
    
    def test_get_current_context_returns_context_info(self, context_manager, sample_project_id):
        """Test that get_current_context returns the CurrentContext object."""
        agent_id = context_manager.register_agent("Context Agent", "opencode")
        
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Current objective"
        )
        
        current = context_manager.get_current_context(agent_id)
        
        assert current is not None
        assert current.project_id == sample_project_id
        assert current.current_objective == "Current objective"
    
    def test_get_current_context_returns_none_when_no_context(self, context_manager):
        """Test that get_current_context returns None when no active context."""
        agent_id = context_manager.register_agent("No Context Agent", "opencode")
        
        current = context_manager.get_current_context(agent_id)
        
        assert current is None
    
    def test_get_current_context_after_end_returns_none(self, context_manager, sample_project_id):
        """Test that get_current_context returns None after context ends."""
        agent_id = context_manager.register_agent("End Agent", "opencode")
        
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="To end"
        )
        
        context_manager.end_context(agent_id)
        
        current = context_manager.get_current_context(agent_id)
        assert current is None


@pytest.mark.unit
@pytest.mark.context
class TestUnlockFiles:
    """Test unlock_files via context_manager."""
    
    def test_unlock_files_via_context_manager(self, context_manager, file_tracker, sample_project_id):
        """Test that unlock_files works through context_manager."""
        agent_id = context_manager.register_agent("Unlock Agent", "opencode")
        
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Lock and unlock"
        )
        
        # Lock files
        context_manager.lock_files(agent_id, ["file1.py", "file2.py"], reason="Testing")
        
        # Unlock one file
        result = context_manager.unlock_files(agent_id, ["file1.py"])
        
        assert result["success"] is True
        assert "file1.py" in result["unlocked_files"]
        assert not file_tracker.is_locked(sample_project_id, "file1.py")
        assert file_tracker.is_locked(sample_project_id, "file2.py")
    
    def test_unlock_files_updates_context(self, context_manager, sample_project_id):
        """Test that unlocking files updates agent context."""
        agent_id = context_manager.register_agent("Unlock Agent", "opencode")
        
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Lock and unlock"
        )
        
        context_manager.lock_files(agent_id, ["file1.py"], reason="Testing")
        
        context_before = context_manager.get_context(agent_id)
        assert len(context_before.locked_files) == 1
        
        context_manager.unlock_files(agent_id, ["file1.py"])
        
        context_after = context_manager.get_context(agent_id)
        assert len(context_after.locked_files) == 0
    
    def test_unlock_files_fails_without_context(self, context_manager):
        """Test that unlock_files fails when agent has no context."""
        agent_id = context_manager.register_agent("No Context Agent", "opencode")
        
        result = context_manager.unlock_files(agent_id, ["file.py"])
        
        assert result["success"] is False
        assert "context not found" in result["error"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
