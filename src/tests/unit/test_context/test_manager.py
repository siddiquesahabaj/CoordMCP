"""
Unit tests for ContextManager functionality.

These tests verify agent context management including:
- Agent registration
- Context lifecycle (start, switch, end)
- Session logging
"""

import pytest
from coordmcp.errors import AgentNotFoundError
from tests.utils.assertions import assert_valid_uuid


@pytest.mark.unit
@pytest.mark.context
class TestAgentRegistration:
    """Test agent registration operations."""
    
    def test_register_agent_returns_valid_uuid(self, context_manager):
        """Test that register_agent returns a valid UUID."""
        agent_id = context_manager.register_agent(
            agent_name="TestAgent",
            agent_type="opencode",
            capabilities=["python", "fastapi"]
        )
        
        assert_valid_uuid(agent_id)
    
    def test_register_agent_stores_agent_info(self, context_manager):
        """Test that registered agent info is stored."""
        agent_id = context_manager.register_agent(
            agent_name="MyAgent",
            agent_type="cursor",
            capabilities=["react", "typescript"]
        )
        
        agent = context_manager.get_agent(agent_id)
        assert agent is not None
        assert agent.agent_name == "MyAgent"
        assert agent.agent_type == "cursor"
    
    def test_get_agent_returns_none_for_nonexistent(self, context_manager):
        """Test that get_agent returns None for non-existent agent."""
        agent = context_manager.get_agent("non-existent-uuid")
        
        assert agent is None
    
    def test_get_all_agents_returns_registered_agents(self, context_manager):
        """Test that get_all_agents returns all registered agents."""
        # Register multiple agents
        for i in range(3):
            context_manager.register_agent(
                agent_name=f"Agent{i}",
                agent_type="opencode"
            )
        
        agents = context_manager.get_all_agents()
        
        assert len(agents) == 3


@pytest.mark.unit
@pytest.mark.context
class TestContextLifecycle:
    """Test context lifecycle operations."""
    
    def test_start_context_returns_context(self, context_manager, sample_project_id):
        """Test that start_context returns context object."""
        agent_id = context_manager.register_agent("TestAgent", "opencode")
        
        context = context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Test objective"
        )
        
        assert context is not None
        assert context.current_context.current_objective == "Test objective"
    
    def test_start_context_stores_project_id(self, context_manager, sample_project_id):
        """Test that start_context stores correct project ID."""
        agent_id = context_manager.register_agent("TestAgent", "opencode")
        
        context = context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Test"
        )
        
        assert context.current_context.project_id == sample_project_id
    
    def test_get_agent_context_returns_active_context(self, context_manager, sample_project_id):
        """Test that get_agent_context returns the active context."""
        agent_id = context_manager.register_agent("TestAgent", "opencode")
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Test objective"
        )
        
        context = context_manager.get_agent_context_full(agent_id)
        
        assert context is not None
        assert context.current_context.current_objective == "Test objective"
    
    def test_end_context_clears_active_context(self, context_manager, sample_project_id):
        """Test that end_context clears the active context."""
        agent_id = context_manager.register_agent("TestAgent", "opencode")
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Test"
        )
        
        context_manager.end_context(agent_id)
        
        context = context_manager.get_agent_context_full(agent_id)
        assert context is None or context.current_context is None


@pytest.mark.unit
@pytest.mark.context
class TestContextSwitching:
    """Test context switching operations."""
    
    def test_switch_context_changes_objective(self, context_manager, sample_project_id):
        """Test that switch_context changes the objective."""
        agent_id = context_manager.register_agent("TestAgent", "opencode")
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Original objective"
        )
        
        new_context = context_manager.switch_context(
            agent_id=agent_id,
            to_project_id=sample_project_id,
            to_objective="New objective"
        )
        
        assert new_context.current_context.current_objective == "New objective"
    
    @pytest.mark.skip(reason="Context history tracking not fully implemented")
    def test_switch_context_preserves_history(self, context_manager, sample_project_id):
        """Test that switch_context preserves context history."""
        agent_id = context_manager.register_agent("TestAgent", "opencode")
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="First objective"
        )
        
        context_manager.switch_context(
            agent_id=agent_id,
            to_project_id=sample_project_id,
            to_objective="Second objective"
        )
        
        history = context_manager.get_context_history(agent_id)
        assert len(history) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
