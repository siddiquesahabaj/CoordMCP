"""
Unit test fixtures for CoordMCP.

Provides fixtures for isolated unit testing of individual components.
"""

import pytest
from pathlib import Path


@pytest.fixture
def storage_backend(fresh_temp_dir: Path):
    """
    Provide a fresh JSONStorageBackend for each test.
    
    Returns:
        JSONStorageBackend instance with temp directory
    """
    from coordmcp.storage.json_adapter import JSONStorageBackend
    return JSONStorageBackend(fresh_temp_dir)


@pytest.fixture
def memory_store(storage_backend):
    """
    Provide a ProjectMemoryStore with fresh storage.
    
    Returns:
        ProjectMemoryStore instance
    """
    from coordmcp.memory.json_store import ProjectMemoryStore
    return ProjectMemoryStore(storage_backend)


@pytest.fixture
def sample_project_id(memory_store):
    """
    Create and return a sample project ID.
    
    Returns:
        str: Project ID of created test project
    """
    return memory_store.create_project(
        project_name="Test Project",
        description="Test project for unit tests"
    )


@pytest.fixture
def context_manager(storage_backend):
    """
    Provide a ContextManager with fresh storage.
    
    Returns:
        ContextManager instance
    """
    from coordmcp.context.manager import ContextManager
    from coordmcp.context.file_tracker import FileTracker
    file_tracker = FileTracker(storage_backend)
    return ContextManager(storage_backend, file_tracker)


@pytest.fixture
def file_tracker(storage_backend):
    """
    Provide a FileTracker with fresh storage.
    
    Returns:
        FileTracker instance
    """
    from coordmcp.context.file_tracker import FileTracker
    return FileTracker(storage_backend)


@pytest.fixture
def analyzer(memory_store):
    """
    Provide an ArchitectureAnalyzer with fresh memory store.
    
    Returns:
        ArchitectureAnalyzer instance
    """
    from coordmcp.architecture.analyzer import ArchitectureAnalyzer
    return ArchitectureAnalyzer(memory_store)
