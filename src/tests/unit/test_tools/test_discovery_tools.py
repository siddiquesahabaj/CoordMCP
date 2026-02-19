"""
Unit tests for discovery tools.

Tests the project and agent discovery functionality including:
- Project discovery by directory path
- Flexible project lookup
- Project listing and filtering
- Active agents retrieval
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.mark.unit
@pytest.mark.discovery
class TestDiscoverProject:
    """Test project discovery by path."""
    
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
    def mock_storage(self, storage_backend, memory_store, context_manager):
        """Mock get_storage to return test storage."""
        def _mock_get_storage():
            mock = MagicMock()
            mock.return_value = storage_backend
            return storage_backend
        return _mock_get_storage
    
    @pytest.mark.asyncio
    async def test_discover_exact_match(self, memory_store, fresh_temp_dir, storage_backend):
        """Test discovering project with exact path match."""
        from coordmcp.tools import discovery_tools
        
        workspace = fresh_temp_dir / "test_workspace"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Test Project",
            workspace_path=str(workspace)
        )
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store):
            result = await discovery_tools.discover_project(path=str(workspace))
            
            assert result["success"]
            assert result["found"]
            assert result["project"]["project_id"] == project_id
            assert result["distance"] == 0
    
    @pytest.mark.asyncio
    async def test_discover_from_subdirectory(self, memory_store, fresh_temp_dir):
        """Test discovering project from subdirectory."""
        from coordmcp.tools import discovery_tools
        
        workspace = fresh_temp_dir / "parent"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Parent Project",
            workspace_path=str(workspace)
        )
        
        subdir = workspace / "src" / "components"
        subdir.mkdir(parents=True)
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store):
            result = await discovery_tools.discover_project(path=str(subdir))
            
            assert result["success"]
            assert result["found"]
            assert result["project"]["project_id"] == project_id
            assert result["distance"] > 0
    
    @pytest.mark.asyncio
    async def test_discover_not_found(self, memory_store, fresh_temp_dir):
        """Test discovering when no project exists."""
        from coordmcp.tools import discovery_tools
        
        orphan_dir = fresh_temp_dir / "orphan"
        orphan_dir.mkdir()
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store):
            result = await discovery_tools.discover_project(path=str(orphan_dir))
            
            assert result["success"]
            assert not result["found"]
            assert result["project"] is None
            assert result["distance"] == -1
    
    @pytest.mark.asyncio
    async def test_discover_uses_current_directory(self, memory_store, fresh_temp_dir):
        """Test that discover uses current directory when path not provided."""
        from coordmcp.tools import discovery_tools
        
        workspace = fresh_temp_dir / "cwd_project"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="CWD Project",
            workspace_path=str(workspace)
        )
        original_cwd = os.getcwd()
        
        try:
            os.chdir(workspace)
            with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store):
                result = await discovery_tools.discover_project()
                
                assert result["success"]
                assert result["found"]
                assert result["project"]["project_id"] == project_id
        finally:
            os.chdir(original_cwd)
    
    @pytest.mark.asyncio
    async def test_discover_respects_max_levels(self, memory_store, fresh_temp_dir):
        """Test that max_parent_levels is respected."""
        from coordmcp.tools import discovery_tools
        
        workspace = fresh_temp_dir / "deep"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Deep Project",
            workspace_path=str(workspace)
        )
        
        # Create a very deep subdirectory
        deep_dir = workspace
        for i in range(5):
            deep_dir = deep_dir / f"level{i}"
            deep_dir.mkdir()
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store):
            # Should not find with max_parent_levels=2
            result = await discovery_tools.discover_project(path=str(deep_dir), max_parent_levels=2)
            assert not result["found"]
            
            # Should find with max_parent_levels=5
            result = await discovery_tools.discover_project(path=str(deep_dir), max_parent_levels=6)
            assert result["found"]


@pytest.mark.unit
@pytest.mark.discovery
@pytest.mark.skip(reason="Requires pywin32 - environment-specific dependency issue on Windows")
class TestGetProject:
    """Test flexible project lookup."""
    
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
    
    @pytest.mark.asyncio
    async def test_get_by_project_id(self, setup_project):
        """Test getting project by ID."""
        from coordmcp.tools import discovery_tools
        
        memory_store = setup_project.__self__['memory_store']
        project_id, workspace = setup_project("By ID", "by_id")
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store):
            result = await discovery_tools.get_project(project_id=project_id)
            
            assert result["success"]
            assert result["project"]["project_id"] == project_id
    
    @pytest.mark.asyncio
    async def test_get_by_project_name(self, setup_project):
        """Test getting project by name."""
        from coordmcp.tools import discovery_tools
        
        memory_store = setup_project.__self__['memory_store']
        project_id, workspace = setup_project("Unique Name", "unique_name")
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store):
            result = await discovery_tools.get_project(project_name="Unique Name")
            
            assert result["success"]
            assert result["project"]["project_name"] == "Unique Name"
    
    @pytest.mark.asyncio
    async def test_get_by_workspace_path(self, setup_project):
        """Test getting project by workspace path."""
        from coordmcp.tools import discovery_tools
        
        memory_store = setup_project.__self__['memory_store']
        project_id, workspace = setup_project("By Path", "by_path")
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store):
            result = await discovery_tools.get_project(workspace_path=str(workspace))
            
            assert result["success"]
            assert result["project"]["workspace_path"] == str(workspace)
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_project(self, memory_store):
        """Test getting non-existent project."""
        from coordmcp.tools import discovery_tools
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store):
            result = await discovery_tools.get_project(project_id="nonexistent")
            
            assert not result["success"]
            assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_get_ambiguous_name(self, memory_store, fresh_temp_dir):
        """Test error when multiple projects have same name."""
        from coordmcp.tools import discovery_tools
        
        # Create two projects with same name
        for i, suffix in enumerate(["same1", "same2"]):
            workspace = fresh_temp_dir / suffix
            workspace.mkdir()
            memory_store.create_project(
                project_name="Same Name",
                workspace_path=str(workspace)
            )
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store):
            result = await discovery_tools.get_project(project_name="Same Name")
            
            assert not result["success"]
            assert "multiple" in result["error"].lower()


@pytest.mark.unit
@pytest.mark.discovery
@pytest.mark.skip(reason="Requires pywin32 - environment-specific dependency issue on Windows")
class TestListProjects:
    """Test project listing functionality."""
    
    @pytest.mark.asyncio
    async def test_list_all_projects(self, memory_store, fresh_temp_dir):
        """Test listing all projects."""
        from coordmcp.tools import discovery_tools
        
        # Create multiple projects
        for i in range(3):
            workspace = fresh_temp_dir / f"project_{i}"
            workspace.mkdir()
            memory_store.create_project(
                project_name=f"Project {i}",
                workspace_path=str(workspace)
            )
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store):
            result = await discovery_tools.list_projects()
            
            assert result["success"]
            assert result["total_count"] == 3
            assert len(result["projects"]) == 3
    
    @pytest.mark.asyncio
    async def test_list_with_workspace_base(self, memory_store, fresh_temp_dir):
        """Test listing projects filtered by workspace base."""
        from coordmcp.tools import discovery_tools
        
        # Create projects in different locations
        base1 = fresh_temp_dir / "workspace1"
        base1.mkdir()
        base2 = fresh_temp_dir / "workspace2"
        base2.mkdir()
        
        for i in range(2):
            proj_dir = base1 / f"proj{i}"
            proj_dir.mkdir()
            memory_store.create_project(
                project_name=f"Base1 Proj {i}",
                workspace_path=str(proj_dir)
            )
        
        for i in range(3):
            proj_dir = base2 / f"proj{i}"
            proj_dir.mkdir()
            memory_store.create_project(
                project_name=f"Base2 Proj {i}",
                workspace_path=str(proj_dir)
            )
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store):
            result = await discovery_tools.list_projects(workspace_base=str(base1))
            
            assert result["total_count"] == 2
            for proj in result["projects"]:
                assert "Base1" in proj["project_name"]
    
    @pytest.mark.asyncio
    async def test_list_returns_workspace_paths(self, memory_store, fresh_temp_dir):
        """Test that listed projects include workspace paths."""
        from coordmcp.tools import discovery_tools
        
        for i in range(2):
            workspace = fresh_temp_dir / f"proj_{i}"
            workspace.mkdir()
            memory_store.create_project(
                project_name=f"Project {i}",
                workspace_path=str(workspace)
            )
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store):
            result = await discovery_tools.list_projects()
            
            for proj in result["projects"]:
                assert "workspace_path" in proj
                assert proj["workspace_path"] is not None


@pytest.mark.unit
@pytest.mark.discovery
@pytest.mark.skip(reason="Requires pywin32 - environment-specific dependency issue on Windows")
class TestGetActiveAgents:
    """Test active agents retrieval."""
    
    @pytest.mark.asyncio
    async def test_get_all_active_agents(self, memory_store, context_manager):
        """Test getting all active agents."""
        from coordmcp.tools import discovery_tools
        
        # Register some agents
        agent_id1 = context_manager.register_agent("Agent1", "opencode")
        agent_id2 = context_manager.register_agent("Agent2", "cursor")
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(discovery_tools, 'get_context_manager', return_value=context_manager):
            result = await discovery_tools.get_active_agents()
            
            assert result["success"]
            assert result["total_count"] >= 2
            agent_names = {a["agent_name"] for a in result["agents"]}
            assert "Agent1" in agent_names
            assert "Agent2" in agent_names
    
    @pytest.mark.asyncio
    async def test_get_agents_by_project(self, memory_store, context_manager, fresh_temp_dir):
        """Test getting agents filtered by project."""
        from coordmcp.tools import discovery_tools
        
        # Create project
        workspace = fresh_temp_dir / "test_project"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Test Project",
            workspace_path=str(workspace)
        )
        
        # Register agent and set context
        agent_id = context_manager.register_agent("ProjectAgent", "opencode")
        context_manager.start_context(
            agent_id=agent_id,
            project_id=project_id,
            objective="Testing",
            task_description="Test task"
        )
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(discovery_tools, 'get_context_manager', return_value=context_manager):
            result = await discovery_tools.get_active_agents(project_id=project_id)
            
            assert result["success"]
            assert result["total_count"] == 1
            assert result["agents"][0]["current_project"] == "Test Project"
    
    @pytest.mark.asyncio
    async def test_get_agents_by_workspace_path(self, memory_store, context_manager, fresh_temp_dir):
        """Test getting agents by workspace path."""
        from coordmcp.tools import discovery_tools
        
        workspace = fresh_temp_dir / "path_project"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Path Project",
            workspace_path=str(workspace)
        )
        
        agent_id = context_manager.register_agent("PathAgent", "opencode")
        context_manager.start_context(
            agent_id=agent_id,
            project_id=project_id,
            objective="Testing"
        )
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(discovery_tools, 'get_context_manager', return_value=context_manager):
            result = await discovery_tools.get_active_agents(workspace_path=str(workspace))
            
            assert result["success"]
            assert result["total_count"] == 1
    
    @pytest.mark.asyncio
    async def test_nonexistent_project_returns_error(self, memory_store, context_manager):
        """Test that non-existent project returns error."""
        from coordmcp.tools import discovery_tools
        
        with patch.object(discovery_tools, 'get_memory_store', return_value=memory_store), \
             patch.object(discovery_tools, 'get_context_manager', return_value=context_manager):
            result = await discovery_tools.get_active_agents(project_id="nonexistent")
            
            assert not result["success"]
            assert "not found" in result["error"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
