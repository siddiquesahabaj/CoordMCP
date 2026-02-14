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


@pytest.mark.unit
@pytest.mark.discovery
@pytest.mark.skip(reason="Discovery tools use global storage - needs refactoring for testability")
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
    
    @pytest.mark.asyncio
    async def test_discover_exact_match(self, setup_project):
        """Test discovering project with exact path match."""
        from coordmcp.tools.discovery_tools import discover_project
        
        project_id, workspace = setup_project("Test Project", "test_workspace")
        
        result = await discover_project(path=str(workspace))
        
        assert result["success"]
        assert result["found"]
        assert result["project"]["project_id"] == project_id
        assert result["distance"] == 0
    
    @pytest.mark.asyncio
    async def test_discover_from_subdirectory(self, setup_project):
        """Test discovering project from subdirectory."""
        from coordmcp.tools.discovery_tools import discover_project
        
        project_id, workspace = setup_project("Parent Project", "parent")
        subdir = workspace / "src" / "components"
        subdir.mkdir(parents=True)
        
        result = await discover_project(path=str(subdir))
        
        assert result["success"]
        assert result["found"]
        assert result["project"]["project_id"] == project_id
        assert result["distance"] > 0
    
    @pytest.mark.asyncio
    async def test_discover_not_found(self, memory_store, fresh_temp_dir):
        """Test discovering when no project exists."""
        from coordmcp.tools.discovery_tools import discover_project
        
        orphan_dir = fresh_temp_dir / "orphan"
        orphan_dir.mkdir()
        
        result = await discover_project(path=str(orphan_dir))
        
        assert result["success"]
        assert not result["found"]
        assert result["project"] is None
        assert result["distance"] == -1
    
    @pytest.mark.asyncio
    async def test_discover_uses_current_directory(self, setup_project, fresh_temp_dir):
        """Test that discover uses current directory when path not provided."""
        from coordmcp.tools.discovery_tools import discover_project
        
        project_id, workspace = setup_project("CWD Project", "cwd_project")
        original_cwd = os.getcwd()
        
        try:
            os.chdir(workspace)
            result = await discover_project()
            
            assert result["success"]
            assert result["found"]
            assert result["project"]["project_id"] == project_id
        finally:
            os.chdir(original_cwd)
    
    @pytest.mark.asyncio
    async def test_discover_respects_max_levels(self, setup_project):
        """Test that max_parent_levels is respected."""
        from coordmcp.tools.discovery_tools import discover_project
        
        project_id, workspace = setup_project("Deep Project", "deep")
        # Create a very deep subdirectory
        deep_dir = workspace
        for i in range(5):
            deep_dir = deep_dir / f"level{i}"
            deep_dir.mkdir()
        
        # Should not find with max_parent_levels=2
        result = await discover_project(path=str(deep_dir), max_parent_levels=2)
        assert not result["found"]
        
        # Should find with max_parent_levels=5
        result = await discover_project(path=str(deep_dir), max_parent_levels=6)
        assert result["found"]


@pytest.mark.unit
@pytest.mark.discovery
@pytest.mark.skip(reason="Discovery tools use global storage - needs refactoring for testability")
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
        from coordmcp.tools.discovery_tools import get_project
        
        project_id, workspace = setup_project("By ID", "by_id")
        
        result = await get_project(project_id=project_id)
        
        assert result["success"]
        assert result["project"]["project_id"] == project_id
    
    @pytest.mark.asyncio
    async def test_get_by_project_name(self, setup_project):
        """Test getting project by name."""
        from coordmcp.tools.discovery_tools import get_project
        
        project_id, workspace = setup_project("Unique Name", "unique_name")
        
        result = await get_project(project_name="Unique Name")
        
        assert result["success"]
        assert result["project"]["project_name"] == "Unique Name"
    
    @pytest.mark.asyncio
    async def test_get_by_workspace_path(self, setup_project):
        """Test getting project by workspace path."""
        from coordmcp.tools.discovery_tools import get_project
        
        project_id, workspace = setup_project("By Path", "by_path")
        
        result = await get_project(workspace_path=str(workspace))
        
        assert result["success"]
        assert result["project"]["workspace_path"] == str(workspace)
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_project(self, memory_store):
        """Test getting non-existent project."""
        from coordmcp.tools.discovery_tools import get_project
        
        result = await get_project(project_id="nonexistent")
        
        assert not result["success"]
        assert "not found" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_get_ambiguous_name(self, setup_project):
        """Test error when multiple projects have same name."""
        from coordmcp.tools.discovery_tools import get_project
        
        # Create two projects with same name
        setup_project("Same Name", "same1")
        setup_project("Same Name", "same2")
        
        result = await get_project(project_name="Same Name")
        
        assert not result["success"]
        assert "multiple" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_get_mismatched_identifiers(self, setup_project):
        """Test error when identifiers point to different projects."""
        from coordmcp.tools.discovery_tools import get_project
        
        project_id1, _ = setup_project("Project 1", "proj1")
        _, workspace2 = setup_project("Project 2", "proj2")
        
        result = await get_project(
            project_id=project_id1,
            workspace_path=str(workspace2)
        )
        
        assert not result["success"]
        assert "different" in result["error"].lower()


@pytest.mark.unit
@pytest.mark.discovery
@pytest.mark.skip(reason="Discovery tools use global storage - needs refactoring for testability")
class TestListProjects:
    """Test project listing functionality."""
    
    @pytest.fixture
    def setup_projects(self, memory_store, fresh_temp_dir):
        """Helper to create multiple test projects."""
        def _create(count, prefix="Project"):
            projects = []
            for i in range(count):
                workspace = fresh_temp_dir / f"{prefix.lower()}_{i}"
                workspace.mkdir()
                project_id = memory_store.create_project(
                    project_name=f"{prefix} {i}",
                    workspace_path=str(workspace)
                )
                projects.append(project_id)
            return projects
        return _create
    
    @pytest.mark.asyncio
    async def test_list_all_projects(self, setup_projects):
        """Test listing all projects."""
        from coordmcp.tools.discovery_tools import list_projects
        
        setup_projects(3)
        
        result = await list_projects()
        
        assert result["success"]
        assert result["total_count"] == 3
        assert len(result["projects"]) == 3
    
    @pytest.mark.asyncio
    async def test_list_with_workspace_base(self, setup_projects, fresh_temp_dir):
        """Test listing projects filtered by workspace base."""
        from coordmcp.tools.discovery_tools import list_projects
        
        # Create projects in different locations
        base1 = fresh_temp_dir / "workspace1"
        base1.mkdir()
        base2 = fresh_temp_dir / "workspace2"
        base2.mkdir()
        
        for i in range(2):
            proj_dir = base1 / f"proj{i}"
            proj_dir.mkdir()
            memory_store = setup_projects.__self__  # Hack to get memory_store
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
        
        result = await list_projects(workspace_base=str(base1))
        
        assert result["total_count"] == 2
        for proj in result["projects"]:
            assert "Base1" in proj["project_name"]
    
    @pytest.mark.asyncio
    async def test_list_returns_workspace_paths(self, setup_projects):
        """Test that listed projects include workspace paths."""
        from coordmcp.tools.discovery_tools import list_projects
        
        setup_projects(2)
        
        result = await list_projects()
        
        for proj in result["projects"]:
            assert "workspace_path" in proj
            assert proj["workspace_path"] is not None


@pytest.mark.unit
@pytest.mark.discovery
@pytest.mark.skip(reason="Discovery tools use global storage - needs refactoring for testability")
class TestGetActiveAgents:
    """Test active agents retrieval."""
    
    @pytest.mark.asyncio
    async def test_get_all_active_agents(self, context_manager):
        """Test getting all active agents."""
        from coordmcp.tools.discovery_tools import get_active_agents
        
        # Register some agents
        agent_id1 = context_manager.register_agent("Agent1", "opencode")
        agent_id2 = context_manager.register_agent("Agent2", "cursor")
        
        result = await get_active_agents()
        
        assert result["success"]
        assert result["total_count"] >= 2
        agent_names = {a["agent_name"] for a in result["agents"]}
        assert "Agent1" in agent_names
        assert "Agent2" in agent_names
    
    @pytest.mark.asyncio
    async def test_get_agents_by_project(self, context_manager, memory_store, fresh_temp_dir):
        """Test getting agents filtered by project."""
        from coordmcp.tools.discovery_tools import get_active_agents
        
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
        
        result = await get_active_agents(project_id=project_id)
        
        assert result["success"]
        assert result["total_count"] == 1
        assert result["agents"][0]["current_project"] == "Test Project"
    
    @pytest.mark.asyncio
    async def test_get_agents_by_workspace_path(self, context_manager, memory_store, fresh_temp_dir):
        """Test getting agents by workspace path."""
        from coordmcp.tools.discovery_tools import get_active_agents
        
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
        
        result = await get_active_agents(workspace_path=str(workspace))
        
        assert result["success"]
        assert result["total_count"] == 1
    
    @pytest.mark.asyncio
    async def test_nonexistent_project_returns_error(self):
        """Test that non-existent project returns error."""
        from coordmcp.tools.discovery_tools import get_active_agents
        
        result = await get_active_agents(project_id="nonexistent")
        
        assert not result["success"]
        assert "not found" in result["error"].lower()
