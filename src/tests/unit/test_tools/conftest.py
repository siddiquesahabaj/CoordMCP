"""
Fixtures for MCP tools tests.
"""

import pytest
from pathlib import Path
from unittest.mock import patch
from coordmcp.storage.json_adapter import JSONStorageBackend
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.context.manager import ContextManager
from coordmcp.context.file_tracker import FileTracker


@pytest.fixture
def storage_backend(fresh_temp_dir: Path):
    """Provide a fresh JSONStorageBackend for each test."""
    return JSONStorageBackend(fresh_temp_dir)


@pytest.fixture
def memory_store(storage_backend):
    """Provide a ProjectMemoryStore with fresh storage."""
    return ProjectMemoryStore(storage_backend)


@pytest.fixture
def sample_project_id(memory_store):
    """Create and return a sample project ID."""
    return memory_store.create_project(
        project_name="Test Project",
        description="Test project for unit tests"
    )


@pytest.fixture
def file_tracker(storage_backend):
    """Provide a FileTracker with fresh storage."""
    return FileTracker(storage_backend)


@pytest.fixture
def context_manager(storage_backend, file_tracker):
    """Provide a ContextManager with fresh storage."""
    return ContextManager(storage_backend, file_tracker)


@pytest.fixture(autouse=True)
def mock_get_storage(storage_backend):
    """Mock get_storage to return the test's storage backend."""
    with patch('coordmcp.tools.memory_tools.get_storage', return_value=storage_backend):
        with patch('coordmcp.tools.context_tools.get_storage', return_value=storage_backend):
            yield storage_backend
