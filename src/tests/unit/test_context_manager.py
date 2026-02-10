"""
Unit tests for ContextManager
"""

import pytest
import tempfile
from pathlib import Path
from coordmcp.storage.json_adapter import JSONStorageBackend
from coordmcp.context.manager import ContextManager
from coordmcp.context.file_tracker import FileTracker


class TestContextManager:
    """Test suite for ContextManager"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONStorageBackend(Path(tmpdir))
            yield backend
    
    @pytest.fixture
    def context_manager(self, temp_storage):
        """Create context manager with temporary storage"""
        file_tracker = FileTracker(temp_storage)
        return ContextManager(temp_storage, file_tracker)
    
    def test_register_agent(self, context_manager):
        """Test agent registration"""
        agent_id = context_manager.register_agent(
            agent_name="TestAgent",
            agent_type="opencode",
            capabilities=["python", "fastapi"]
        )
        
        assert agent_id is not None
        assert len(agent_id) > 0
        
        # Verify agent exists
        agent = context_manager.get_agent(agent_id)
        assert agent is not None
        assert agent.agent_name == "TestAgent"
        assert agent.agent_type == "opencode"
    
    def test_get_all_agents(self, context_manager):
        """Test listing all agents"""
        # Register multiple agents
        for i in range(3):
            context_manager.register_agent(
                agent_name=f"Agent{i}",
                agent_type="opencode"
            )
        
        agents = context_manager.get_all_agents()
        assert len(agents) == 3
    
    def test_agent_not_found(self, context_manager):
        """Test getting non-existent agent"""
        agent = context_manager.get_agent("non-existent-id")
        assert agent is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
