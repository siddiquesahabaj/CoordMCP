"""
Unit tests for FileTracker
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from coordmcp.storage.json_adapter import JSONStorageBackend
from coordmcp.context.file_tracker import FileTracker, FileLockError


class TestFileTracker:
    """Test suite for FileTracker"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONStorageBackend(Path(tmpdir))
            yield backend
    
    @pytest.fixture
    def file_tracker(self, temp_storage):
        """Create file tracker with temporary storage"""
        return FileTracker(temp_storage)
    
    def test_lock_files(self, file_tracker):
        """Test locking files"""
        result = file_tracker.lock_files(
            agent_id="agent-1",
            project_id="proj-1",
            files=["file1.py", "file2.py"],
            reason="Testing"
        )
        
        assert result["success"] is True
        assert len(result["locked_files"]) == 2
    
    def test_unlock_files(self, file_tracker):
        """Test unlocking files"""
        # Lock files first
        file_tracker.lock_files(
            agent_id="agent-1",
            project_id="proj-1",
            files=["file1.py"],
            reason="Testing"
        )
        
        # Unlock files
        result = file_tracker.unlock_files(
            agent_id="agent-1",
            project_id="proj-1",
            files=["file1.py"]
        )
        
        assert result["success"] is True
        assert result["unlocked_count"] == 1
    
    def test_file_lock_conflict(self, file_tracker):
        """Test file lock conflict detection"""
        # Agent 1 locks file
        file_tracker.lock_files(
            agent_id="agent-1",
            project_id="proj-1",
            files=["shared.py"],
            reason="Agent 1 working"
        )
        
        # Agent 2 tries to lock same file
        with pytest.raises(FileLockError):
            file_tracker.lock_files(
                agent_id="agent-2",
                project_id="proj-1",
                files=["shared.py"],
                reason="Agent 2 working"
            )
    
    def test_get_locked_files(self, file_tracker):
        """Test retrieving locked files"""
        file_tracker.lock_files(
            agent_id="agent-1",
            project_id="proj-1",
            files=["file1.py", "file2.py"],
            reason="Testing"
        )
        
        locked = file_tracker.get_locked_files("proj-1")
        assert locked["total_locked"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
