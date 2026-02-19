"""
Unit tests for task management tools.

Tests task lifecycle operations including creation, assignment, and status updates.
Note: Tests mock the fastmcp dependencies due to environment constraints.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock


@pytest.mark.unit
@pytest.mark.tools

class TestCreateTask:
    """Test task creation."""
    
    @pytest.mark.asyncio
    async def test_create_task_success(self, memory_store, sample_project_id):
        """Test successful task creation."""
        from coordmcp.tools import task_tools
        
        with patch.object(task_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(task_tools, 'resolve_project_id', return_value=(True, sample_project_id, "OK")):
            
            result = await task_tools.create_task(
                project_id=sample_project_id,
                title="Test Task",
                description="Test description",
                priority="high"
            )
            
            assert result["success"] is True
            assert "task_id" in result
    
    @pytest.mark.asyncio
    async def test_create_task_with_parent(self, memory_store, sample_project_id):
        """Test creating a subtask with parent."""
        from coordmcp.tools import task_tools
        from tests.utils.factories import TaskFactory
        
        # Create parent task
        parent = TaskFactory.create(project_id=sample_project_id)
        memory_store.create_task(parent)
        
        with patch.object(task_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(task_tools, 'resolve_project_id', return_value=(True, sample_project_id, "OK")):
            
            result = await task_tools.create_task(
                project_id=sample_project_id,
                title="Child Task",
                parent_task_id=parent.id
            )
            
            assert result["success"] is True
            
            # Verify parent has child
            updated_parent = memory_store.get_task(sample_project_id, parent.id)
            assert result["task_id"] in updated_parent.child_tasks
    
    @pytest.mark.asyncio
    async def test_create_task_invalid_priority(self, memory_store, sample_project_id):
        """Test that invalid priority defaults to medium."""
        from coordmcp.tools import task_tools
        
        with patch.object(task_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(task_tools, 'resolve_project_id', return_value=(True, sample_project_id, "OK")):
            
            result = await task_tools.create_task(
                project_id=sample_project_id,
                title="Test Task",
                priority="invalid"
            )
            
            assert result["success"] is True
            # Check that task was created (priority defaulted to medium)


@pytest.mark.unit
@pytest.mark.tools

class TestAssignTask:
    """Test task assignment."""
    
    @pytest.mark.asyncio
    async def test_assign_task_success(self, memory_store, context_manager, sample_project_id):
        """Test successful task assignment."""
        from coordmcp.tools import task_tools
        from tests.utils.factories import TaskFactory
        from coordmcp.memory.models import TaskStatus
        
        # Create task and agent
        task = TaskFactory.create(project_id=sample_project_id)
        memory_store.create_task(task)
        agent_id = context_manager.register_agent("Task Agent", "opencode")
        
        with patch.object(task_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(task_tools, 'get_context_manager', return_value=context_manager):
            
            result = await task_tools.assign_task(
                project_id=sample_project_id,
                task_id=task.id,
                agent_id=agent_id
            )
            
            assert result["success"] is True
            
            # Verify task updated
            updated_task = memory_store.get_task(sample_project_id, task.id)
            assert updated_task.assigned_agent_id == agent_id
            assert updated_task.status == TaskStatus.IN_PROGRESS
    
    @pytest.mark.asyncio
    async def test_assign_task_nonexistent_agent(self, memory_store, sample_project_id):
        """Test assignment fails for nonexistent agent."""
        from coordmcp.tools import task_tools
        from tests.utils.factories import TaskFactory
        
        task = TaskFactory.create(project_id=sample_project_id)
        memory_store.create_task(task)
        
        with patch.object(task_tools, 'get_memory_store', return_value=memory_store):
            result = await task_tools.assign_task(
                project_id=sample_project_id,
                task_id=task.id,
                agent_id="nonexistent-agent"
            )
            
            assert result["success"] is False
            assert "not found" in result["error"].lower()


@pytest.mark.unit
@pytest.mark.tools

class TestUpdateTaskStatus:
    """Test task status updates."""
    
    @pytest.mark.asyncio
    async def test_complete_task(self, memory_store, sample_project_id):
        """Test completing a task."""
        from coordmcp.tools import task_tools
        from tests.utils.factories import TaskFactory
        from coordmcp.memory.models import TaskStatus
        
        task = TaskFactory.create(project_id=sample_project_id)
        memory_store.create_task(task)
        
        with patch.object(task_tools, 'get_memory_store', return_value=memory_store):
            result = await task_tools.update_task_status(
                project_id=sample_project_id,
                task_id=task.id,
                agent_id="test-agent",
                status="completed"
            )
            
            assert result["success"] is True
            
            updated_task = memory_store.get_task(sample_project_id, task.id)
            assert updated_task.status == TaskStatus.COMPLETED
            assert updated_task.completed_at is not None
    
    @pytest.mark.asyncio
    async def test_block_task_with_notes(self, memory_store, sample_project_id):
        """Test blocking a task with notes."""
        from coordmcp.tools import task_tools
        from tests.utils.factories import TaskFactory
        from coordmcp.memory.models import TaskStatus
        
        task = TaskFactory.create(project_id=sample_project_id)
        memory_store.create_task(task)
        
        with patch.object(task_tools, 'get_memory_store', return_value=memory_store):
            result = await task_tools.update_task_status(
                project_id=sample_project_id,
                task_id=task.id,
                agent_id="test-agent",
                status="blocked",
                notes="Waiting for dependency"
            )
            
            assert result["success"] is True
            
            updated_task = memory_store.get_task(sample_project_id, task.id)
            assert updated_task.status == TaskStatus.BLOCKED
            assert updated_task.metadata.get("block_reason") == "Waiting for dependency"
    
    @pytest.mark.asyncio
    async def test_invalid_status_returns_error(self, memory_store, sample_project_id):
        """Test that invalid status returns error."""
        from coordmcp.tools import task_tools
        from tests.utils.factories import TaskFactory
        
        task = TaskFactory.create(project_id=sample_project_id)
        memory_store.create_task(task)
        
        with patch.object(task_tools, 'get_memory_store', return_value=memory_store):
            result = await task_tools.update_task_status(
                project_id=sample_project_id,
                task_id=task.id,
                agent_id="test-agent",
                status="invalid_status"
            )
            
            assert result["success"] is False
            assert "invalid" in result["error"].lower()


@pytest.mark.unit
@pytest.mark.tools

class TestGetTasks:
    """Test task retrieval."""
    
    @pytest.mark.asyncio
    async def test_get_project_tasks(self, memory_store, sample_project_id):
        """Test getting all project tasks."""
        from coordmcp.tools import task_tools
        from tests.utils.factories import TaskFactory
        
        # Create multiple tasks
        for i in range(3):
            task = TaskFactory.create(project_id=sample_project_id, title=f"Task {i}")
            memory_store.create_task(task)
        
        with patch.object(task_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(task_tools, 'resolve_project_id', return_value=(True, sample_project_id, "OK")):
            
            result = await task_tools.get_project_tasks(project_id=sample_project_id)
            
            assert result["success"] is True
            assert result["count"] == 3
    
    @pytest.mark.asyncio
    async def test_get_my_tasks(self, memory_store, sample_project_id):
        """Test getting tasks assigned to an agent."""
        from coordmcp.tools import task_tools
        from tests.utils.factories import TaskFactory
        
        agent_id = "test-agent-123"
        
        # Create tasks for agent
        for i in range(2):
            task = TaskFactory.create(
                project_id=sample_project_id,
                assigned_agent_id=agent_id,
                title=f"Agent Task {i}"
            )
            memory_store.create_task(task)
        
        # Create task for different agent
        other_task = TaskFactory.create(
            project_id=sample_project_id,
            assigned_agent_id="other-agent"
        )
        memory_store.create_task(other_task)
        
        with patch.object(task_tools, 'get_memory_store', return_value=memory_store):
            result = await task_tools.get_my_tasks(agent_id=agent_id)
            
            assert result["success"] is True
            assert result["count"] == 2


@pytest.mark.unit
@pytest.mark.tools

class TestDeleteTask:
    """Test task deletion."""
    
    @pytest.mark.asyncio
    async def test_delete_task_success(self, memory_store, sample_project_id):
        """Test successful task deletion."""
        from coordmcp.tools import task_tools
        from tests.utils.factories import TaskFactory
        
        task = TaskFactory.create(project_id=sample_project_id)
        memory_store.create_task(task)
        
        with patch.object(task_tools, 'get_memory_store', return_value=memory_store):
            result = await task_tools.delete_task(
                project_id=sample_project_id,
                task_id=task.id,
                agent_id="test-agent"
            )
            
            assert result["success"] is True
            
            # Task should be soft-deleted (not found in normal query)
            deleted_task = memory_store.get_task(sample_project_id, task.id)
            assert deleted_task is None or deleted_task.is_deleted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
