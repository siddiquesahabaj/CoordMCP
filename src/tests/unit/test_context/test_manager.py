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
from coordmcp.context.state import (
    AgentContext, AgentProfile, CurrentContext, LockInfo,
    AgentType, Priority, OperationType
)
from coordmcp.errors import AgentNotFoundError
from tests.utils.factories import (
    AgentContextFactory,
    CurrentContextFactory,
    LockInfoFactory,
    AgentProfileFactory
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
