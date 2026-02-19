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


@pytest.mark.unit
@pytest.mark.context
class TestLockQueue:
    """Test lock queue operations."""
    
    def test_request_lock_with_queue_acquires_unlocked_file(self, file_tracker, sample_project_id):
        """Test that request_lock_with_queue acquires lock on unlocked file."""
        result = file_tracker.request_lock_with_queue(
            agent_id="agent-1",
            agent_name="Agent One",
            project_id=sample_project_id,
            file_path="src/new_file.py",
            reason="Testing queue"
        )
        
        assert result["success"] is True
        assert result.get("queued") is None or result["queued"] is False
    
    def test_request_lock_with_queue_adds_to_queue_when_locked(self, file_tracker, sample_project_id):
        """Test that request_lock_with_queue queues request when file is locked."""
        # First agent locks file
        file_tracker.lock_files(
            agent_id="agent-1",
            project_id=sample_project_id,
            files=["src/locked.py"],
            reason="First lock"
        )
        
        # Second agent requests lock
        result = file_tracker.request_lock_with_queue(
            agent_id="agent-2",
            agent_name="Agent Two",
            project_id=sample_project_id,
            file_path="src/locked.py",
            reason="Second request"
        )
        
        assert result["success"] is False
        assert result["queued"] is True
        assert result["queue_position"] == 1
        assert "request_id" in result
    
    def test_get_lock_queue_returns_all_requests(self, file_tracker, sample_project_id):
        """Test that get_lock_queue returns queued requests."""
        # Lock file and add to queue
        file_tracker.lock_files(
            agent_id="agent-1",
            project_id=sample_project_id,
            files=["src/queued.py"],
            reason="First"
        )
        file_tracker.request_lock_with_queue(
            agent_id="agent-2",
            agent_name="Agent Two",
            project_id=sample_project_id,
            file_path="src/queued.py",
            reason="Second"
        )
        
        queue = file_tracker.get_lock_queue(sample_project_id)
        
        assert len(queue) == 1
        assert queue[0]["agent_id"] == "agent-2"
    
    def test_get_lock_queue_filters_by_file(self, file_tracker, sample_project_id):
        """Test that get_lock_queue can filter by file."""
        file_tracker.lock_files(
            agent_id="agent-1",
            project_id=sample_project_id,
            files=["src/file1.py", "src/file2.py"],
            reason="First"
        )
        file_tracker.request_lock_with_queue(
            agent_id="agent-2",
            agent_name="Agent Two",
            project_id=sample_project_id,
            file_path="src/file1.py",
            reason="Second"
        )
        file_tracker.request_lock_with_queue(
            agent_id="agent-3",
            agent_name="Agent Three",
            project_id=sample_project_id,
            file_path="src/file2.py",
            reason="Third"
        )
        
        queue = file_tracker.get_lock_queue(sample_project_id, "src/file1.py")
        
        assert len(queue) == 1
        assert queue[0]["agent_id"] == "agent-2"
    
    def test_cancel_lock_request_removes_from_queue(self, file_tracker, sample_project_id):
        """Test that cancel_lock_request removes the request."""
        file_tracker.lock_files(
            agent_id="agent-1",
            project_id=sample_project_id,
            files=["src/cancel.py"],
            reason="First"
        )
        result = file_tracker.request_lock_with_queue(
            agent_id="agent-2",
            agent_name="Agent Two",
            project_id=sample_project_id,
            file_path="src/cancel.py",
            reason="Second"
        )
        
        request_id = result["request_id"]
        
        # Cancel the request
        cancelled = file_tracker.cancel_lock_request(sample_project_id, request_id, "agent-2")
        
        assert cancelled is True
        
        # Verify removed from queue
        queue = file_tracker.get_lock_queue(sample_project_id)
        assert len(queue) == 0
    
    def test_cancel_lock_request_fails_for_wrong_agent(self, file_tracker, sample_project_id):
        """Test that cancel_lock_request fails if agent doesn't own request."""
        file_tracker.lock_files(
            agent_id="agent-1",
            project_id=sample_project_id,
            files=["src/wrong.py"],
            reason="First"
        )
        result = file_tracker.request_lock_with_queue(
            agent_id="agent-2",
            agent_name="Agent Two",
            project_id=sample_project_id,
            file_path="src/wrong.py",
            reason="Second"
        )
        
        request_id = result["request_id"]
        
        # Try to cancel as different agent
        cancelled = file_tracker.cancel_lock_request(sample_project_id, request_id, "agent-3")
        
        assert cancelled is False


@pytest.mark.unit
@pytest.mark.context
class TestLockExtensions:
    """Test lock extension operations."""
    
    def test_extend_lock_success(self, file_tracker, sample_project_id):
        """Test that extend_lock extends a lock."""
        from datetime import datetime, timedelta
        
        file_tracker.lock_files(
            agent_id="agent-1",
            project_id=sample_project_id,
            files=["src/extend.py"],
            reason="Testing"
        )
        
        new_unlock_time = datetime.now() + timedelta(hours=2)
        extended = file_tracker.extend_lock(
            agent_id="agent-1",
            project_id=sample_project_id,
            file_path="src/extend.py",
            new_expected_unlock_time=new_unlock_time
        )
        
        assert extended is True
    
    def test_extend_lock_fails_for_nonexistent(self, file_tracker, sample_project_id):
        """Test that extend_lock fails for nonexistent lock."""
        from datetime import datetime, timedelta
        
        new_unlock_time = datetime.now() + timedelta(hours=2)
        extended = file_tracker.extend_lock(
            agent_id="agent-1",
            project_id=sample_project_id,
            file_path="src/nonexistent.py",
            new_expected_unlock_time=new_unlock_time
        )
        
        assert extended is False


@pytest.mark.unit
@pytest.mark.context
class TestLockHolderQueries:
    """Test lock holder query operations."""
    
    def test_get_lock_holder_returns_agent_id(self, file_tracker, sample_project_id):
        """Test that get_lock_holder returns the locking agent."""
        file_tracker.lock_files(
            agent_id="agent-1",
            project_id=sample_project_id,
            files=["src/holder.py"],
            reason="Testing"
        )
        
        holder = file_tracker.get_lock_holder(sample_project_id, "src/holder.py")
        
        assert holder == "agent-1"
    
    def test_get_lock_holder_returns_none_when_unlocked(self, file_tracker, sample_project_id):
        """Test that get_lock_holder returns None for unlocked file."""
        holder = file_tracker.get_lock_holder(sample_project_id, "src/unlocked.py")
        
        assert holder is None
    
    def test_is_locked_returns_true_when_locked(self, file_tracker, sample_project_id):
        """Test that is_locked returns True for locked file."""
        file_tracker.lock_files(
            agent_id="agent-1",
            project_id=sample_project_id,
            files=["src/locked.py"],
            reason="Testing"
        )
        
        assert file_tracker.is_locked(sample_project_id, "src/locked.py") is True
    
    def test_is_locked_returns_false_when_unlocked(self, file_tracker, sample_project_id):
        """Test that is_locked returns False for unlocked file."""
        assert file_tracker.is_locked(sample_project_id, "src/unlocked.py") is False


@pytest.mark.unit
@pytest.mark.context
class TestForceUnlock:
    """Test force unlock operations."""
    
    def test_unlock_files_force_unlocks_others_lock(self, file_tracker, sample_project_id):
        """Test that force=True unlocks files owned by other agents."""
        file_tracker.lock_files(
            agent_id="agent-1",
            project_id=sample_project_id,
            files=["src/force.py"],
            reason="First"
        )
        
        result = file_tracker.unlock_files(
            agent_id="agent-2",
            project_id=sample_project_id,
            files=["src/force.py"],
            force=True
        )
        
        assert result["success"] is True
        assert "src/force.py" in result["unlocked_files"]
        assert len(result["warnings"]) == 1
    
    def test_unlock_files_without_force_keeps_others_lock(self, file_tracker, sample_project_id):
        """Test that without force, other agent's locks are kept."""
        file_tracker.lock_files(
            agent_id="agent-1",
            project_id=sample_project_id,
            files=["src/no_force.py"],
            reason="First"
        )
        
        result = file_tracker.unlock_files(
            agent_id="agent-2",
            project_id=sample_project_id,
            files=["src/no_force.py"],
            force=False
        )
        
        # File should still be locked by agent-1
        assert file_tracker.is_locked(sample_project_id, "src/no_force.py")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
