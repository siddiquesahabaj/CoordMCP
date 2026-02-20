"""
Unit tests for onboarding tools.

Tests the project onboarding functionality including:
- Getting project onboarding context for an agent
- Error handling for missing agent/project
- Building project info, agent context, active agents, recent changes
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from coordmcp.context.state import AgentProfile, ProjectActivity, AgentType
from coordmcp.context.manager import ContextManager
from coordmcp.context.file_tracker import FileTracker
from coordmcp.memory.models import ProjectInfo


@pytest.mark.unit
@pytest.mark.onboarding
class TestGetProjectOnboardingContext:
    """Test getting project onboarding context."""

    @pytest.fixture
    def setup_project(self, memory_store, fresh_temp_dir):
        """Helper to create a test project."""
        def _create(name, workspace_name):
            workspace = fresh_temp_dir / workspace_name
            workspace.mkdir()
            project_id = memory_store.create_project(
                project_name=name,
                workspace_path=str(workspace)
            )
            return project_id, workspace
        return _create

    @pytest.fixture
    def mock_storage(self, storage_backend):
        """Mock get_storage to return test storage."""
        return storage_backend

    @pytest.mark.asyncio
    async def test_onboarding_success_new_agent(self, memory_store, context_manager, fresh_temp_dir):
        """Test onboarding context for a new agent in a project."""
        from coordmcp.tools import onboarding_tools

        workspace = fresh_temp_dir / "test_workspace"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Test Project",
            workspace_path=str(workspace)
        )

        agent_id = context_manager.register_agent("TestAgent", "opencode")

        with patch.object(onboarding_tools, 'get_context_manager', return_value=context_manager), \
             patch.object(onboarding_tools, 'get_memory_store', return_value=memory_store):
            result = await onboarding_tools.get_project_onboarding_context(
                agent_id=agent_id,
                project_id=project_id
            )

            assert result["success"] is True
            assert "project_info" in result
            assert result["project_info"]["project_id"] == project_id
            assert result["project_info"]["project_name"] == "Test Project"
            assert "agent_context" in result
            assert result["agent_context"]["agent_id"] == agent_id
            assert result["agent_context"]["is_returning"] is False

    @pytest.mark.asyncio
    async def test_onboarding_success_returning_agent(self, memory_store, context_manager, fresh_temp_dir):
        """Test onboarding context for a returning agent."""
        from coordmcp.tools import onboarding_tools

        workspace = fresh_temp_dir / "test_workspace"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Test Project",
            workspace_path=str(workspace)
        )

        agent_id = context_manager.register_agent("TestAgent", "opencode")
        context_manager.start_context(
            agent_id=agent_id,
            project_id=project_id,
            objective="First task",
            task_description="Initial work"
        )

        with patch.object(onboarding_tools, 'get_context_manager', return_value=context_manager), \
             patch.object(onboarding_tools, 'get_memory_store', return_value=memory_store):
            result = await onboarding_tools.get_project_onboarding_context(
                agent_id=agent_id,
                project_id=project_id
            )

            assert result["success"] is True
            assert result["agent_context"]["is_returning"] is True

    @pytest.mark.asyncio
    async def test_onboarding_agent_not_found(self, memory_store, context_manager, fresh_temp_dir):
        """Test onboarding returns error when agent not found."""
        from coordmcp.tools import onboarding_tools

        workspace = fresh_temp_dir / "test_workspace"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Test Project",
            workspace_path=str(workspace)
        )

        with patch.object(onboarding_tools, 'get_context_manager', return_value=context_manager), \
             patch.object(onboarding_tools, 'get_memory_store', return_value=memory_store):
            result = await onboarding_tools.get_project_onboarding_context(
                agent_id="nonexistent_agent",
                project_id=project_id
            )

            assert result["success"] is False
            assert result["error_type"] == "AgentNotFound"
            assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_onboarding_project_not_found(self, memory_store, context_manager):
        """Test onboarding returns error when project not found."""
        from coordmcp.tools import onboarding_tools

        agent_id = context_manager.register_agent("TestAgent", "opencode")

        with patch.object(onboarding_tools, 'get_context_manager', return_value=context_manager), \
             patch.object(onboarding_tools, 'get_memory_store', return_value=memory_store):
            result = await onboarding_tools.get_project_onboarding_context(
                agent_id=agent_id,
                project_id="nonexistent_project"
            )

            assert result["success"] is False
            assert result["error_type"] == "ProjectNotFound"
            assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_onboarding_returns_active_agents(self, memory_store, context_manager, fresh_temp_dir):
        """Test that onboarding returns active agents in the project."""
        from coordmcp.tools import onboarding_tools

        workspace = fresh_temp_dir / "test_workspace"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Test Project",
            workspace_path=str(workspace)
        )

        agent_id1 = context_manager.register_agent("Agent1", "opencode")
        agent_id2 = context_manager.register_agent("Agent2", "cursor")

        context_manager.start_context(
            agent_id=agent_id1,
            project_id=project_id,
            objective="Task 1"
        )
        context_manager.start_context(
            agent_id=agent_id2,
            project_id=project_id,
            objective="Task 2"
        )

        with patch.object(onboarding_tools, 'get_context_manager', return_value=context_manager), \
             patch.object(onboarding_tools, 'get_memory_store', return_value=memory_store):
            result = await onboarding_tools.get_project_onboarding_context(
                agent_id=agent_id1,
                project_id=project_id
            )

            assert result["success"] is True
            assert "active_agents" in result
            assert len(result["active_agents"]) >= 2

    @pytest.mark.asyncio
    async def test_onboarding_returns_recent_changes(self, memory_store, context_manager, fresh_temp_dir):
        """Test that onboarding returns recent changes in the project."""
        from coordmcp.tools import onboarding_tools
        from coordmcp.memory.models import Change, ChangeType
        from uuid import uuid4

        workspace = fresh_temp_dir / "test_workspace"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Test Project",
            workspace_path=str(workspace)
        )

        change = Change(
            id=str(uuid4()),
            file_path="src/main.py",
            change_type=ChangeType.MODIFY,
            description="Added new feature",
            agent_id="test_agent"
        )
        memory_store.log_change(project_id, change)

        agent_id = context_manager.register_agent("TestAgent", "opencode")

        with patch.object(onboarding_tools, 'get_context_manager', return_value=context_manager), \
             patch.object(onboarding_tools, 'get_memory_store', return_value=memory_store):
            result = await onboarding_tools.get_project_onboarding_context(
                agent_id=agent_id,
                project_id=project_id
            )

            assert result["success"] is True
            assert "recent_changes" in result

    @pytest.mark.asyncio
    async def test_onboarding_returns_recommended_steps(self, memory_store, context_manager, fresh_temp_dir):
        """Test that onboarding returns recommended next steps."""
        from coordmcp.tools import onboarding_tools

        workspace = fresh_temp_dir / "test_workspace"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Test Project",
            workspace_path=str(workspace)
        )

        agent_id = context_manager.register_agent("TestAgent", "opencode")

        with patch.object(onboarding_tools, 'get_context_manager', return_value=context_manager), \
             patch.object(onboarding_tools, 'get_memory_store', return_value=memory_store):
            result = await onboarding_tools.get_project_onboarding_context(
                agent_id=agent_id,
                project_id=project_id
            )

            assert result["success"] is True
            assert "recommended_next_steps" in result
            assert len(result["recommended_next_steps"]) > 0


@pytest.mark.unit
@pytest.mark.onboarding
class TestBuildProjectInfo:
    """Test project info building functions."""

    def test_build_project_info_with_data(self, memory_store, fresh_temp_dir):
        """Test building project info with complete data."""
        from coordmcp.tools import onboarding_tools

        workspace = fresh_temp_dir / "test_workspace"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Test Project",
            description="A test project",
            workspace_path=str(workspace)
        )

        project_info = memory_store.get_project_info(project_id)

        result = onboarding_tools._build_project_info(project_info, memory_store)

        assert result["project_id"] == project_id
        assert result["project_name"] == "Test Project"
        assert result["description"] == "A test project"

    def test_build_project_info_empty(self):
        """Test building project info with no data."""
        from coordmcp.tools import onboarding_tools

        result = onboarding_tools._build_project_info(None, None)

        assert result == {}


@pytest.mark.unit
@pytest.mark.onboarding
class TestBuildAgentContext:
    """Test agent context building functions."""

    def test_build_agent_context_new_agent(self, context_manager):
        """Test building context for a new agent."""
        from coordmcp.tools import onboarding_tools

        agent_id = context_manager.register_agent("TestAgent", "opencode")
        agent_profile = context_manager.get_agent(agent_id)

        result = onboarding_tools._build_agent_context(agent_profile, "project_123")

        assert result["agent_id"] == agent_id
        assert result["agent_name"] == "TestAgent"
        assert result["is_returning"] is False
        assert result["previous_sessions_in_project"] == 0

    def test_build_agent_context_returning_agent(self, context_manager):
        """Test building context for a returning agent."""
        from coordmcp.tools import onboarding_tools

        agent_id = context_manager.register_agent("TestAgent", "opencode")
        agent_profile = context_manager.get_agent(agent_id)
        agent_profile.projects_involved.append("project_123")

        result = onboarding_tools._build_agent_context(agent_profile, "project_123")

        assert result["is_returning"] is True


@pytest.mark.unit
@pytest.mark.onboarding
class TestGetWorkflowGuidance:
    """Test workflow guidance functionality."""

    @pytest.mark.asyncio
    async def test_get_workflow_guidance_default(self, memory_store, fresh_temp_dir):
        """Test getting default workflow guidance."""
        from coordmcp.tools import onboarding_tools

        with patch.object(onboarding_tools, 'get_memory_store', return_value=memory_store):
            result = await onboarding_tools.get_workflow_guidance()

            assert result["success"] is True
            assert result["workflow_name"] == "default"
            assert result["workflow_display_name"] == "Standard Development Workflow"
            assert "phases" in result
            assert len(result["phases"]) > 0

    @pytest.mark.asyncio
    async def test_get_workflow_guidance_test_first(self, memory_store, fresh_temp_dir):
        """Test getting test-first workflow guidance."""
        from coordmcp.tools import onboarding_tools

        with patch.object(onboarding_tools, 'get_memory_store', return_value=memory_store):
            result = await onboarding_tools.get_workflow_guidance(workflow_name="test-first")

            assert result["success"] is True
            assert result["workflow_name"] == "test-first"
            assert result["workflow_display_name"] == "Test-First Development"

    @pytest.mark.asyncio
    async def test_get_workflow_guidance_feature_branch(self, memory_store, fresh_temp_dir):
        """Test getting feature-branch workflow guidance."""
        from coordmcp.tools import onboarding_tools

        with patch.object(onboarding_tools, 'get_memory_store', return_value=memory_store):
            result = await onboarding_tools.get_workflow_guidance(workflow_name="feature-branch")

            assert result["success"] is True
            assert result["workflow_name"] == "feature-branch"
            assert result["workflow_display_name"] == "Feature Branch Workflow"

    @pytest.mark.asyncio
    async def test_get_workflow_guidance_with_project(self, memory_store, fresh_temp_dir):
        """Test getting workflow guidance with project context."""
        from coordmcp.tools import onboarding_tools

        workspace = fresh_temp_dir / "test_workspace"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Test Project",
            workspace_path=str(workspace),
            recommended_workflows=["test-first", "feature-branch"]
        )

        with patch.object(onboarding_tools, 'get_memory_store', return_value=memory_store):
            result = await onboarding_tools.get_workflow_guidance(project_id=project_id)

            assert result["success"] is True
            assert "project_id" in result
            assert "project_name" in result
            assert result["project_name"] == "Test Project"

    @pytest.mark.asyncio
    async def test_get_workflow_guidance_invalid_name(self, memory_store, fresh_temp_dir):
        """Test that invalid workflow name falls back to default."""
        from coordmcp.tools import onboarding_tools

        with patch.object(onboarding_tools, 'get_memory_store', return_value=memory_store):
            result = await onboarding_tools.get_workflow_guidance(workflow_name="nonexistent_workflow")

            assert result["success"] is True
            assert result["is_default"] is True


@pytest.mark.unit
@pytest.mark.onboarding
class TestValidateWorkflowState:
    """Test workflow state validation functionality."""

    @pytest.mark.asyncio
    async def test_validate_workflow_unregistered(self, context_manager):
        """Test validation for unregistered agent."""
        from coordmcp.tools import onboarding_tools

        with patch.object(onboarding_tools, 'get_context_manager', return_value=context_manager):
            result = await onboarding_tools.validate_workflow_state("nonexistent_agent")

            assert result["success"] is True
            assert result["current_state"] == "unregistered"
            assert len(result["warnings"]) > 0

    @pytest.mark.asyncio
    async def test_validate_workflow_registered_no_context(self, context_manager):
        """Test validation for registered agent without context."""
        from coordmcp.tools import onboarding_tools

        agent_id = context_manager.register_agent("TestAgent", "opencode")

        with patch.object(onboarding_tools, 'get_context_manager', return_value=context_manager):
            result = await onboarding_tools.validate_workflow_state(agent_id)

            assert result["success"] is True
            assert result["has_active_context"] is False
            assert len(result["warnings"]) > 0

    @pytest.mark.asyncio
    async def test_validate_workflow_with_context(self, memory_store, context_manager, fresh_temp_dir):
        """Test validation for agent with active context."""
        from coordmcp.tools import onboarding_tools

        workspace = fresh_temp_dir / "test_workspace"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Test Project",
            workspace_path=str(workspace)
        )

        agent_id = context_manager.register_agent("TestAgent", "opencode")
        context_manager.start_context(
            agent_id=agent_id,
            project_id=project_id,
            objective="Test task"
        )

        with patch.object(onboarding_tools, 'get_context_manager', return_value=context_manager):
            result = await onboarding_tools.validate_workflow_state(agent_id)

            assert result["success"] is True
            assert result["current_state"] == "context_started"
            assert result["has_active_context"] is True
            assert "context_started" in result["completed_steps"]


@pytest.mark.unit
@pytest.mark.onboarding
class TestGetSystemPrompt:
    """Test system prompt functionality."""

    @pytest.mark.asyncio
    async def test_get_system_prompt_returns_content(self):
        """Test that get_system_prompt returns valid content."""
        from coordmcp.tools import onboarding_tools

        result = await onboarding_tools.get_system_prompt()

        assert result["success"] is True
        assert "system_prompt" in result
        assert "version" in result
        assert "MANDATORY WORKFLOW" in result["system_prompt"]
        assert "CoordMCP" in result["system_prompt"]

    @pytest.mark.asyncio
    async def test_get_system_prompt_contains_workflow_steps(self):
        """Test that system prompt contains workflow steps."""
        from coordmcp.tools import onboarding_tools

        result = await onboarding_tools.get_system_prompt()
        prompt = result["system_prompt"]

        assert "discover_project" in prompt or "create_project" in prompt
        assert "register_agent" in prompt
        assert "start_context" in prompt
        assert "lock_files" in prompt
        assert "log_change" in prompt
        assert "unlock_files" in prompt
        assert "end_context" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
