"""
Unit tests for FileTracker functionality.

These tests verify file locking operations including:
- File locking
- File unlocking
- Conflict detection
- Lock retrieval
"""

import pytest
from coordmcp.errors import FileLockError
from tests.utils.assertions import assert_valid_uuid


@pytest.mark.unit
@pytest.mark.context
class TestFileLocking:
    """Test file locking operations."""
    
    def test_lock_files_returns_success(self, file_tracker, sample_project_id):
        """Test that lock_files returns success result."""
        agent_id = "test-agent-uuid"
        
        result = file_tracker.lock_files(
            agent_id=agent_id,
            project_id=sample_project_id,
            files=["src/main.py"],
            reason="Testing"
        )
        
        assert result["success"] is True
        assert len(result["locked_files"]) == 1
    
    def test_lock_files_creates_lock(self, file_tracker, sample_project_id):
        """Test that lock_files actually creates a lock."""
        agent_id = "test-agent-uuid"
        file_tracker.lock_files(
            agent_id=agent_id,
            project_id=sample_project_id,
            files=["src/main.py"],
            reason="Testing"
        )
        
        locked = file_tracker.get_locked_files(sample_project_id)
        assert locked["total_locked"] == 1
        agent_locks = locked["by_agent"].get(agent_id, [])
        assert any(lock["file_path"] == "src/main.py" for lock in agent_locks)
    
    def test_unlock_files_removes_lock(self, file_tracker, sample_project_id):
        """Test that unlock_files removes the lock."""
        agent_id = "test-agent-uuid"
        file_tracker.lock_files(
            agent_id=agent_id,
            project_id=sample_project_id,
            files=["src/main.py"],
            reason="Testing"
        )
        
        result = file_tracker.unlock_files(
            agent_id=agent_id,
            project_id=sample_project_id,
            files=["src/main.py"]
        )
        
        assert result["success"] is True
        locked = file_tracker.get_locked_files(sample_project_id)
        assert locked["total_locked"] == 0


@pytest.mark.unit
@pytest.mark.context
class TestLockConflicts:
    """Test file lock conflict detection."""
    
    def test_cannot_lock_already_locked_file(self, file_tracker, sample_project_id):
        """Test that another agent cannot lock an already locked file."""
        agent1_id = "agent-1-uuid"
        agent2_id = "agent-2-uuid"
        
        # Agent 1 locks file
        file_tracker.lock_files(
            agent_id=agent1_id,
            project_id=sample_project_id,
            files=["src/main.py"],
            reason="Agent 1 working"
        )
        
        # Agent 2 tries to lock same file
        with pytest.raises(FileLockError):
            file_tracker.lock_files(
                agent_id=agent2_id,
                project_id=sample_project_id,
                files=["src/main.py"],
                reason="Agent 2 working"
            )
    
    def test_same_agent_can_lock_multiple_files(self, file_tracker, sample_project_id):
        """Test that same agent can lock multiple files."""
        agent_id = "test-agent-uuid"
        
        result = file_tracker.lock_files(
            agent_id=agent_id,
            project_id=sample_project_id,
            files=["src/main.py", "src/utils.py", "src/models.py"],
            reason="Working on multiple files"
        )
        
        assert result["success"] is True
        assert len(result["locked_files"]) == 3


@pytest.mark.unit
@pytest.mark.context
class TestLockQueries:
    """Test lock query operations."""
    
    def test_get_locked_files_returns_by_agent(self, file_tracker, sample_project_id):
        """Test that get_locked_files groups by agent."""
        agent_id = "test-agent-uuid"
        file_tracker.lock_files(
            agent_id=agent_id,
            project_id=sample_project_id,
            files=["src/file1.py", "src/file2.py"],
            reason="Testing"
        )
        
        locked = file_tracker.get_locked_files(sample_project_id)
        
        assert agent_id in locked["by_agent"]
        assert len(locked["by_agent"][agent_id]) == 2
    
    def test_get_locked_files_counts_total(self, file_tracker, sample_project_id):
        """Test that get_locked_files returns correct total count."""
        file_tracker.lock_files(
            agent_id="agent-1",
            project_id=sample_project_id,
            files=["src/file1.py"],
            reason="Testing"
        )
        file_tracker.lock_files(
            agent_id="agent-2",
            project_id=sample_project_id,
            files=["src/file2.py"],
            reason="Testing"
        )
        
        locked = file_tracker.get_locked_files(sample_project_id)
        
        assert locked["total_locked"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
