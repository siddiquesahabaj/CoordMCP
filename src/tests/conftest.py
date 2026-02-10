"""
Global pytest configuration and fixtures for CoordMCP tests.

This module provides shared fixtures and configuration used across all tests.
"""

import pytest
import tempfile
from pathlib import Path
from typing import Generator


# Configure test markers
@pytest.fixture(scope="session")
def temp_data_dir() -> Generator[Path, None, None]:
    """
    Provide a temporary data directory for the entire test session.
    
    This directory is created once and shared across all tests in the session,
    then cleaned up after all tests complete.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def fresh_temp_dir() -> Generator[Path, None, None]:
    """
    Provide a fresh temporary directory for each test.
    
    Unlike temp_data_dir, this is created fresh for each test function,
    ensuring complete isolation between tests.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="session")
def test_config(temp_data_dir: Path):
    """
    Provide test configuration with temp data directory.
    
    Returns:
        Config object configured for testing
    """
    from coordmcp.config import Config
    return Config(data_dir=temp_data_dir)
