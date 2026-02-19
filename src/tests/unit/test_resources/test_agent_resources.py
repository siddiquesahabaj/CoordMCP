"""
Unit tests for agent resources.

Tests agent:// resource handling including profiles, contexts, and activity.
Note: Tests mock the fastmcp dependencies due to environment constraints.
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.unit
@pytest.mark.resources

class TestAgentResources:
    """Test agent resource handling."""
    
    @pytest.mark.asyncio
    async def test_agent_profile(self, context_manager):
        """Test agent profile resource."""
        from coordmcp.resources import agent_resources
        
        agent_id = context_manager.register_agent("Test Agent", "opencode")
        
        with patch.object(agent_resources, 'get_context_manager', return_value=context_manager):
            result = await agent_resources.handle_agent_resource(
                f"agent://{agent_id}"
            )
            
            assert "Test Agent" in result
            assert agent_id in result
    
    @pytest.mark.asyncio
    async def test_agent_context(self, context_manager, sample_project_id):
        """Test agent context resource."""
        from coordmcp.resources import agent_resources
        
        agent_id = context_manager.register_agent("Context Agent", "opencode")
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Testing context resource"
        )
        
        with patch.object(agent_resources, 'get_context_manager', return_value=context_manager):
            result = await agent_resources.handle_agent_resource(
                f"agent://{agent_id}/context"
            )
            
            assert "Testing context resource" in result
    
    @pytest.mark.asyncio
    async def test_agent_not_found(self, context_manager):
        """Test error handling for non-existent agent."""
        from coordmcp.resources import agent_resources
        
        with patch.object(agent_resources, 'get_context_manager', return_value=context_manager):
            result = await agent_resources.handle_agent_resource(
                "agent://nonexistent-id"
            )
            
            assert "not found" in result.lower()


@pytest.mark.unit
@pytest.mark.resources

class TestAgentActivityResource:
    """Test agent activity resource."""
    
    @pytest.mark.asyncio
    async def test_agent_session_log(self, context_manager, sample_project_id):
        """Test agent session log resource."""
        from coordmcp.resources import agent_resources
        
        agent_id = context_manager.register_agent("Activity Agent", "opencode")
        context_manager.start_context(
            agent_id=agent_id,
            project_id=sample_project_id,
            objective="Testing"
        )
        context_manager.add_context_entry(
            agent_id=agent_id,
            file="src/test.py",
            operation="write",
            summary="Test edit"
        )
        
        with patch.object(agent_resources, 'get_context_manager', return_value=context_manager):
            result = await agent_resources.handle_agent_resource(
                f"agent://{agent_id}/session-log"
            )
            
            # Should contain session information
            assert "Session" in result or "session" in result.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
