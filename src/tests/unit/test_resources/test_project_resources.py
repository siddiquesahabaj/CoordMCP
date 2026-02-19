"""
Unit tests for project resources.

Tests project:// resource handling including overview, decisions, tech-stack, etc.
Note: Tests mock the fastmcp dependencies due to environment constraints.
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.unit
@pytest.mark.resources

class TestProjectResources:
    """Test project resource handling."""
    
    @pytest.mark.asyncio
    async def test_project_overview(self, memory_store, sample_project_id):
        """Test project overview resource."""
        from coordmcp.resources import project_resources
        
        with patch.object(project_resources, 'get_memory_store', return_value=memory_store):
            result = await project_resources.handle_project_resource(
                f"project://{sample_project_id}"
            )
            
            assert "Test Project" in result
            assert sample_project_id in result
    
    @pytest.mark.asyncio
    async def test_project_decisions(self, memory_store, sample_project_id):
        """Test project decisions resource."""
        from coordmcp.resources import project_resources
        from tests.utils.factories import DecisionFactory
        
        # Add a decision
        decision = DecisionFactory.create()
        memory_store.save_decision(sample_project_id, decision)
        
        with patch.object(project_resources, 'get_memory_store', return_value=memory_store):
            result = await project_resources.handle_project_resource(
                f"project://{sample_project_id}/decisions"
            )
            
            assert decision.title in result
    
    @pytest.mark.asyncio
    async def test_project_not_found(self, memory_store):
        """Test error handling for non-existent project."""
        from coordmcp.resources import project_resources
        
        with patch.object(project_resources, 'get_memory_store', return_value=memory_store):
            result = await project_resources.handle_project_resource(
                "project://nonexistent-id"
            )
            
            assert "not found" in result.lower()


@pytest.mark.unit
@pytest.mark.resources

class TestTechStackResource:
    """Test tech-stack resource."""
    
    @pytest.mark.asyncio
    async def test_tech_stack_resource(self, memory_store, sample_project_id):
        """Test tech-stack resource formatting."""
        from coordmcp.resources import project_resources
        from tests.utils.factories import TechStackEntryFactory
        
        # Add tech stack entry
        entry = TechStackEntryFactory.create(technology="FastAPI", category="backend")
        memory_store.update_tech_stack(sample_project_id, entry)
        
        with patch.object(project_resources, 'get_memory_store', return_value=memory_store):
            result = await project_resources.handle_project_resource(
                f"project://{sample_project_id}/tech-stack"
            )
            
            assert "FastAPI" in result


@pytest.mark.unit
@pytest.mark.resources

class TestRecentChangesResource:
    """Test recent-changes resource."""
    
    @pytest.mark.asyncio
    async def test_recent_changes_resource(self, memory_store, sample_project_id):
        """Test recent changes resource."""
        from coordmcp.resources import project_resources
        from tests.utils.factories import ChangeFactory
        
        # Log a change
        change = ChangeFactory.create(file_path="src/main.py")
        memory_store.log_change(sample_project_id, change)
        
        with patch.object(project_resources, 'get_memory_store', return_value=memory_store):
            result = await project_resources.handle_project_resource(
                f"project://{sample_project_id}/recent-changes"
            )
            
            assert "src/main.py" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
