"""
Unit tests for project resolver utilities.

Tests the flexible project lookup functionality including:
- Project resolution by ID, name, and workspace path
- Path normalization and validation
- Project discovery by directory
- Workspace path uniqueness checks
"""

import pytest
import os
from pathlib import Path
from coordmcp.utils.project_resolver import (
    normalize_path,
    validate_workspace_path,
    resolve_project,
    discover_project_by_path,
    get_projects_by_path,
    is_workspace_path_unique
)


@pytest.mark.unit
class TestNormalizePath:
    """Test path normalization."""
    
    def test_normalize_converts_to_absolute(self, fresh_temp_dir):
        """Test that normalize_path converts to absolute path."""
        relative = "some/relative/path"
        normalized = normalize_path(relative)
        assert os.path.isabs(normalized)
    
    def test_normalize_handles_trailing_slashes(self, fresh_temp_dir):
        """Test that normalize_path removes trailing slashes."""
        path_with_slash = str(fresh_temp_dir) + "/"
        normalized = normalize_path(path_with_slash)
        assert not normalized.endswith("/")
    
    def test_normalize_resolves_dot_directories(self, fresh_temp_dir):
        """Test that normalize_path resolves . and .. directories."""
        path_with_dot = str(fresh_temp_dir / "subdir" / ".." / "file.txt")
        normalized = normalize_path(path_with_dot)
        assert ".." not in normalized


@pytest.mark.unit
class TestValidateWorkspacePath:
    """Test workspace path validation."""
    
    def test_validate_empty_path_fails(self):
        """Test that empty path fails validation."""
        is_valid, error = validate_workspace_path("")
        assert not is_valid
        assert "required" in error.lower()
    
    def test_validate_relative_path_fails(self):
        """Test that relative path fails validation."""
        is_valid, error = validate_workspace_path("relative/path")
        # On Windows, relative paths that don't exist will fail the existence check
        # before or along with the absolute path check
        assert not is_valid
        assert "absolute" in error.lower() or "does not exist" in error.lower()
    
    def test_validate_nonexistent_path_fails(self, fresh_temp_dir):
        """Test that non-existent path fails validation."""
        nonexistent = fresh_temp_dir / "does_not_exist"
        is_valid, error = validate_workspace_path(str(nonexistent))
        assert not is_valid
        assert "does not exist" in error.lower()
    
    def test_validate_file_path_fails(self, fresh_temp_dir):
        """Test that file path (not directory) fails validation."""
        file_path = fresh_temp_dir / "test_file.txt"
        file_path.touch()
        is_valid, error = validate_workspace_path(str(file_path))
        assert not is_valid
        assert "directory" in error.lower()
    
    def test_validate_valid_directory_passes(self, fresh_temp_dir):
        """Test that valid directory passes validation."""
        test_dir = fresh_temp_dir / "valid_project"
        test_dir.mkdir()
        is_valid, error = validate_workspace_path(str(test_dir))
        assert is_valid
        assert error == ""


@pytest.mark.unit
class TestResolveProject:
    """Test project resolution by various identifiers."""
    
    def test_resolve_by_project_id(self, memory_store, fresh_temp_dir):
        """Test resolving project by ID."""
        workspace = fresh_temp_dir / "project1"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Project One",
            workspace_path=str(workspace)
        )
        
        success, project, message = resolve_project(
            memory_store=memory_store,
            project_id=project_id
        )
        
        assert success
        assert project.project_id == project_id
        assert project.project_name == "Project One"
    
    def test_resolve_by_project_name(self, memory_store, fresh_temp_dir):
        """Test resolving project by name."""
        workspace = fresh_temp_dir / "project2"
        workspace.mkdir()
        memory_store.create_project(
            project_name="Unique Project Name",
            workspace_path=str(workspace)
        )
        
        success, project, message = resolve_project(
            memory_store=memory_store,
            project_name="Unique Project Name"
        )
        
        assert success
        assert project.project_name == "Unique Project Name"
    
    def test_resolve_by_workspace_path(self, memory_store, fresh_temp_dir):
        """Test resolving project by workspace path."""
        workspace = fresh_temp_dir / "project3"
        workspace.mkdir()
        memory_store.create_project(
            project_name="Project Three",
            workspace_path=str(workspace)
        )
        
        success, project, message = resolve_project(
            memory_store=memory_store,
            workspace_path=str(workspace)
        )
        
        assert success
        assert project.workspace_path == str(workspace)
    
    def test_resolve_priority_id_over_name(self, memory_store, fresh_temp_dir):
        """Test that project_id takes priority over name."""
        workspace1 = fresh_temp_dir / "project_a"
        workspace1.mkdir()
        project_id = memory_store.create_project(
            project_name="Same Name",
            workspace_path=str(workspace1)
        )
        
        workspace2 = fresh_temp_dir / "project_b"
        workspace2.mkdir()
        memory_store.create_project(
            project_name="Same Name",
            workspace_path=str(workspace2)
        )
        
        # Should resolve by ID even though name is ambiguous
        success, project, message = resolve_project(
            memory_store=memory_store,
            project_id=project_id,
            project_name="Same Name"
        )
        
        assert success
        assert project.project_id == project_id
    
    def test_resolve_validates_matching_identifiers(self, memory_store, fresh_temp_dir):
        """Test that mismatched identifiers return error."""
        workspace1 = fresh_temp_dir / "project_c"
        workspace1.mkdir()
        project_id1 = memory_store.create_project(
            project_name="Project C",
            workspace_path=str(workspace1)
        )
        
        workspace2 = fresh_temp_dir / "project_d"
        workspace2.mkdir()
        memory_store.create_project(
            project_name="Project D",
            workspace_path=str(workspace2)
        )
        
        # Mixing identifiers from different projects
        success, project, message = resolve_project(
            memory_store=memory_store,
            project_id=project_id1,
            project_name="Project D"
        )
        
        assert not success
        assert "different projects" in message.lower()
    
    def test_resolve_no_identifiers_fails(self, memory_store):
        """Test that no identifiers provided returns error."""
        success, project, message = resolve_project(
            memory_store=memory_store
        )
        
        assert not success
        assert "at least one" in message.lower()
    
    def test_resolve_nonexistent_project_fails(self, memory_store):
        """Test that non-existent project returns error."""
        success, project, message = resolve_project(
            memory_store=memory_store,
            project_id="nonexistent-id"
        )
        
        assert not success
        assert "not found" in message.lower()


@pytest.mark.unit
class TestDiscoverProjectByPath:
    """Test project discovery by directory path."""
    
    def test_discover_exact_match(self, memory_store, fresh_temp_dir):
        """Test discovering project with exact path match."""
        workspace = fresh_temp_dir / "exact_match"
        workspace.mkdir()
        memory_store.create_project(
            project_name="Exact Match Project",
            workspace_path=str(workspace)
        )
        
        found, project, message, distance = discover_project_by_path(
            memory_store=memory_store,
            path=str(workspace)
        )
        
        assert found
        assert distance == 0
        assert "exact" in message.lower()
    
    def test_discover_parent_directory(self, memory_store, fresh_temp_dir):
        """Test discovering project from subdirectory."""
        workspace = fresh_temp_dir / "parent_project"
        workspace.mkdir()
        subdir = workspace / "src" / "components"
        subdir.mkdir(parents=True)
        
        memory_store.create_project(
            project_name="Parent Project",
            workspace_path=str(workspace)
        )
        
        found, project, message, distance = discover_project_by_path(
            memory_store=memory_store,
            path=str(subdir)
        )
        
        assert found
        assert distance == 2  # src/components is 2 levels down
        assert "parent" in message.lower()
    
    def test_discover_not_found(self, memory_store, fresh_temp_dir):
        """Test discovering when no project exists."""
        orphan_dir = fresh_temp_dir / "orphan"
        orphan_dir.mkdir()
        
        found, project, message, distance = discover_project_by_path(
            memory_store=memory_store,
            path=str(orphan_dir)
        )
        
        assert not found
        assert distance == -1
        assert "no project found" in message.lower()
    
    def test_discover_uses_current_directory_by_default(self, memory_store, fresh_temp_dir):
        """Test that discover uses current directory when path not provided."""
        original_cwd = os.getcwd()
        try:
            workspace = fresh_temp_dir / "cwd_project"
            workspace.mkdir()
            os.chdir(workspace)
            
            memory_store.create_project(
                project_name="CWD Project",
                workspace_path=str(workspace)
            )
            
            found, project, message, distance = discover_project_by_path(
                memory_store=memory_store
            )
            
            assert found
            assert project.project_name == "CWD Project"
        finally:
            os.chdir(original_cwd)


@pytest.mark.unit
class TestGetProjectsByPath:
    """Test getting projects under a base path."""
    
    def test_get_projects_recursive(self, memory_store, fresh_temp_dir):
        """Test getting all projects recursively."""
        base = fresh_temp_dir / "workspace"
        base.mkdir()
        
        # Create multiple projects at different levels
        for i in range(3):
            proj_dir = base / f"project{i}"
            proj_dir.mkdir()
            memory_store.create_project(
                project_name=f"Project {i}",
                workspace_path=str(proj_dir)
            )
        
        projects = get_projects_by_path(
            memory_store=memory_store,
            base_path=str(base),
            recursive=True
        )
        
        assert len(projects) == 3
        project_names = {p.project_name for p in projects}
        assert project_names == {"Project 0", "Project 1", "Project 2"}
    
    def test_get_projects_non_recursive(self, memory_store, fresh_temp_dir):
        """Test getting only direct child projects."""
        base = fresh_temp_dir / "workspace"
        base.mkdir()
        
        # Create project at base level
        proj1 = base / "project1"
        proj1.mkdir()
        memory_store.create_project(
            project_name="Project 1",
            workspace_path=str(proj1)
        )
        
        # Create project in subdirectory
        subdir = base / "subdir"
        subdir.mkdir()
        proj2 = subdir / "project2"
        proj2.mkdir()
        memory_store.create_project(
            project_name="Project 2",
            workspace_path=str(proj2)
        )
        
        projects = get_projects_by_path(
            memory_store=memory_store,
            base_path=str(base),
            recursive=False
        )
        
        assert len(projects) == 1
        assert projects[0].project_name == "Project 1"
    
    def test_get_projects_returns_sorted(self, memory_store, fresh_temp_dir):
        """Test that projects are returned sorted by name."""
        base = fresh_temp_dir / "workspace"
        base.mkdir()
        
        # Create projects in non-alphabetical order
        for name in ["Charlie", "Alpha", "Bravo"]:
            proj_dir = base / name.lower()
            proj_dir.mkdir()
            memory_store.create_project(
                project_name=name,
                workspace_path=str(proj_dir)
            )
        
        projects = get_projects_by_path(
            memory_store=memory_store,
            base_path=str(base)
        )
        
        project_names = [p.project_name for p in projects]
        assert project_names == ["Alpha", "Bravo", "Charlie"]


@pytest.mark.unit
class TestIsWorkspacePathUnique:
    """Test workspace path uniqueness checking."""
    
    def test_unique_path_returns_true(self, memory_store, fresh_temp_dir):
        """Test that unused path is considered unique."""
        workspace = fresh_temp_dir / "unique"
        workspace.mkdir()
        
        is_unique = is_workspace_path_unique(
            memory_store=memory_store,
            workspace_path=str(workspace)
        )
        
        assert is_unique
    
    def test_duplicate_path_returns_false(self, memory_store, fresh_temp_dir):
        """Test that used path is not unique."""
        workspace = fresh_temp_dir / "duplicate"
        workspace.mkdir()
        memory_store.create_project(
            project_name="First Project",
            workspace_path=str(workspace)
        )
        
        is_unique = is_workspace_path_unique(
            memory_store=memory_store,
            workspace_path=str(workspace)
        )
        
        assert not is_unique
    
    def test_can_exclude_own_project(self, memory_store, fresh_temp_dir):
        """Test that we can exclude a project when checking uniqueness."""
        workspace = fresh_temp_dir / "update_project"
        workspace.mkdir()
        project_id = memory_store.create_project(
            project_name="Update Project",
            workspace_path=str(workspace)
        )
        
        # Should be unique when excluding itself
        is_unique = is_workspace_path_unique(
            memory_store=memory_store,
            workspace_path=str(workspace),
            exclude_project_id=project_id
        )
        
        assert is_unique
