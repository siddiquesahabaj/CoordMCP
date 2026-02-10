"""
Custom assertions for CoordMCP tests.

Provides reusable assertion helpers for common test scenarios.
"""


def assert_project_exists(store, project_id: str) -> None:
    """
    Assert that a project exists in the store.
    
    Args:
        store: ProjectMemoryStore instance
        project_id: Project ID to check
        
    Raises:
        AssertionError: If project doesn't exist
    """
    assert store.project_exists(project_id), f"Project {project_id} not found"


def assert_decision_has_fields(decision, required_fields: list) -> None:
    """
    Assert that a decision has all required fields.
    
    Args:
        decision: Decision object to check
        required_fields: List of field names that must exist
        
    Raises:
        AssertionError: If any field is missing
    """
    for field in required_fields:
        assert hasattr(decision, field), f"Decision missing field: {field}"


def assert_valid_uuid(uuid_string: str) -> None:
    """
    Assert that a string is a valid UUID format.
    
    Args:
        uuid_string: String to validate
        
    Raises:
        AssertionError: If not a valid UUID
    """
    import re
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    assert uuid_pattern.match(uuid_string), f"Invalid UUID format: {uuid_string}"


def assert_file_locked(file_tracker, project_id: str, file_path: str, agent_id: str) -> None:
    """
    Assert that a file is locked by a specific agent.
    
    Args:
        file_tracker: FileTracker instance
        project_id: Project ID
        file_path: File path to check
        agent_id: Expected agent ID
        
    Raises:
        AssertionError: If file is not locked by agent
    """
    locked = file_tracker.get_locked_files(project_id)
    assert file_path in locked, f"File {file_path} is not locked"
    assert locked[file_path].locked_by == agent_id, f"File locked by wrong agent"


def assert_successful_result(result: dict) -> None:
    """
    Assert that a tool result indicates success.
    
    Args:
        result: Dictionary with 'success' key
        
    Raises:
        AssertionError: If result indicates failure
    """
    assert result.get("success") is True, f"Expected success but got: {result.get('error', 'Unknown error')}"
