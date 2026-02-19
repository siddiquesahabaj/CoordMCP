"""
Unit tests for context state models in CoordMCP.

Tests cover:
- AgentContext: context management, locking, session logs
- AgentProfile: activity tracking, project history
- CurrentContext: duration, overdue detection
- LockInfo: stale detection, acquisition rules
- ContextEntry/SessionLogEntry: model validation
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from coordmcp.context.state import (
    AgentContext, AgentProfile, CurrentContext, LockInfo,
    AgentType, Priority, OperationType, ContextEntry, SessionLogEntry,
    LockRequest, ProjectActivity, ContextSummary
)


@pytest.mark.unit
@pytest.mark.context
class TestAgentContext:
    """Test AgentContext functionality."""
    
    def test_create_agent_context(self):
        """Test creating an agent context."""
        context = AgentContext(
            agent_id=str(uuid4()),
            agent_name="Test Agent",
            agent_type=AgentType.OPENCODE,
            session_id=str(uuid4())
        )
        
        assert context.agent_name == "Test Agent"
        assert context.current_context is None
        assert len(context.locked_files) == 0
    
    def test_add_context_entry(self):
        """Test adding context entries."""
        context = AgentContext(
            agent_id=str(uuid4()),
            agent_name="Test",
            agent_type=AgentType.OPENCODE,
            session_id=str(uuid4())
        )
        
        entry = ContextEntry(
            file="src/main.py",
            operation=OperationType.READ,
            summary="Read configuration"
        )
        context.add_context_entry(entry)
        
        assert len(context.recent_context) == 1
        assert context.recent_context[0].file == "src/main.py"
    
    def test_add_context_entry_max_entries(self):
        """Test that context entries are limited to max."""
        context = AgentContext(
            agent_id=str(uuid4()),
            agent_name="Test",
            agent_type=AgentType.OPENCODE,
            session_id=str(uuid4())
        )
        
        # Add more than max
        for i in range(60):
            entry = ContextEntry(file=f"file{i}.py", operation=OperationType.READ)
            context.add_context_entry(entry)
        
        assert len(context.recent_context) == 50  # Default max
    
    def test_add_session_log_entry(self):
        """Test adding session log entries."""
        context = AgentContext(
            agent_id=str(uuid4()),
            agent_name="Test",
            agent_type=AgentType.OPENCODE,
            session_id=str(uuid4())
        )
        
        entry = SessionLogEntry(event="context_started", details={"project": "proj-1"})
        context.add_session_log_entry(entry)
        
        assert len(context.session_log) == 1
    
    def test_lock_file(self):
        """Test locking a file."""
        context = AgentContext(
            agent_id=str(uuid4()),
            agent_name="Test",
            agent_type=AgentType.OPENCODE,
            session_id=str(uuid4())
        )
        
        lock = LockInfo(file_path="src/main.py", locked_by="agent-1", reason="Editing")
        context.lock_file(lock)
        
        assert len(context.locked_files) == 1
        assert context.is_file_locked_by_me("src/main.py")
    
    def test_lock_file_replaces_existing(self):
        """Test that locking same file replaces old lock."""
        context = AgentContext(
            agent_id=str(uuid4()),
            agent_name="Test",
            agent_type=AgentType.OPENCODE,
            session_id=str(uuid4())
        )
        
        lock1 = LockInfo(file_path="src/main.py", locked_by="agent-1", reason="First")
        lock2 = LockInfo(file_path="src/main.py", locked_by="agent-1", reason="Second")
        
        context.lock_file(lock1)
        context.lock_file(lock2)
        
        assert len(context.locked_files) == 1
        assert context.locked_files[0].reason == "Second"
    
    def test_unlock_file(self):
        """Test unlocking a file."""
        context = AgentContext(
            agent_id=str(uuid4()),
            agent_name="Test",
            agent_type=AgentType.OPENCODE,
            session_id=str(uuid4())
        )
        
        lock = LockInfo(file_path="src/main.py", locked_by="agent-1")
        context.lock_file(lock)
        
        result = context.unlock_file("src/main.py")
        
        assert result is True
        assert len(context.locked_files) == 0
    
    def test_unlock_file_not_locked(self):
        """Test unlocking a file that isn't locked."""
        context = AgentContext(
            agent_id=str(uuid4()),
            agent_name="Test",
            agent_type=AgentType.OPENCODE,
            session_id=str(uuid4())
        )
        
        result = context.unlock_file("src/main.py")
        
        assert result is False
    
    def test_get_locked_file_paths(self):
        """Test getting list of locked file paths."""
        context = AgentContext(
            agent_id=str(uuid4()),
            agent_name="Test",
            agent_type=AgentType.OPENCODE,
            session_id=str(uuid4())
        )
        
        context.lock_file(LockInfo(file_path="file1.py", locked_by="agent-1"))
        context.lock_file(LockInfo(file_path="file2.py", locked_by="agent-1"))
        
        paths = context.get_locked_file_paths()
        
        assert len(paths) == 2
        assert "file1.py" in paths
        assert "file2.py" in paths
    
    def test_switch_context(self):
        """Test switching contexts."""
        context = AgentContext(
            agent_id=str(uuid4()),
            agent_name="Test",
            agent_type=AgentType.OPENCODE,
            session_id=str(uuid4())
        )
        
        old_context = CurrentContext(
            project_id="proj-1",
            current_objective="Old objective"
        )
        context.current_context = old_context
        
        new_context = CurrentContext(
            project_id="proj-2",
            current_objective="New objective"
        )
        
        returned = context.switch_context(new_context)
        
        assert returned.project_id == "proj-1"
        assert context.current_context.project_id == "proj-2"
        assert len(context.session_log) == 1


@pytest.mark.unit
@pytest.mark.context
class TestAgentProfile:
    """Test AgentProfile functionality."""
    
    def test_create_agent_profile(self):
        """Test creating an agent profile."""
        profile = AgentProfile(
            agent_id=str(uuid4()),
            agent_name="Test Agent",
            agent_type=AgentType.OPENCODE
        )
        
        assert profile.agent_name == "Test Agent"
        assert profile.status == "active"
        assert profile.total_sessions == 0
    
    def test_mark_active(self):
        """Test marking agent as active."""
        profile = AgentProfile(
            agent_id=str(uuid4()),
            agent_name="Test",
            agent_type=AgentType.OPENCODE
        )
        old_time = profile.last_active
        
        profile.mark_active()
        
        assert profile.last_active > old_time
    
    def test_add_project(self):
        """Test adding a project to agent's list."""
        profile = AgentProfile(
            agent_id=str(uuid4()),
            agent_name="Test",
            agent_type=AgentType.OPENCODE
        )
        
        profile.add_project("proj-1")
        
        assert "proj-1" in profile.projects_involved
    
    def test_add_project_no_duplicates(self):
        """Test that duplicate projects aren't added."""
        profile = AgentProfile(
            agent_id=str(uuid4()),
            agent_name="Test",
            agent_type=AgentType.OPENCODE
        )
        
        profile.add_project("proj-1")
        profile.add_project("proj-1")
        
        assert len(profile.projects_involved) == 1
    
    def test_increment_sessions(self):
        """Test incrementing session count."""
        profile = AgentProfile(
            agent_id=str(uuid4()),
            agent_name="Test",
            agent_type=AgentType.OPENCODE
        )
        
        profile.increment_sessions()
        profile.increment_sessions()
        
        assert profile.total_sessions == 2
    
    def test_is_active(self):
        """Test is_active check."""
        profile = AgentProfile(
            agent_id=str(uuid4()),
            agent_name="Test",
            agent_type=AgentType.OPENCODE,
            status="active"
        )
        
        assert profile.is_active() is True
        
        profile.status = "inactive"
        assert profile.is_active() is False


@pytest.mark.unit
@pytest.mark.context
class TestCurrentContext:
    """Test CurrentContext functionality."""
    
    def test_create_current_context(self):
        """Test creating a current context."""
        context = CurrentContext(
            project_id="proj-1",
            current_objective="Build feature",
            priority=Priority.HIGH
        )
        
        assert context.project_id == "proj-1"
        assert context.priority == Priority.HIGH
    
    def test_is_overdue(self):
        """Test overdue detection."""
        context = CurrentContext(
            project_id="proj-1",
            current_objective="Test",
            started_at=datetime.now() - timedelta(hours=2),
            estimated_completion=datetime.now() - timedelta(hours=1)
        )
        
        assert context.is_overdue() is True
    
    def test_is_not_overdue(self):
        """Test when not overdue."""
        context = CurrentContext(
            project_id="proj-1",
            current_objective="Test",
            estimated_completion=datetime.now() + timedelta(hours=1)
        )
        
        assert context.is_overdue() is False
    
    def test_get_duration(self):
        """Test getting context duration."""
        context = CurrentContext(
            project_id="proj-1",
            current_objective="Test",
            started_at=datetime.now() - timedelta(minutes=30)
        )
        
        duration = context.get_duration()
        
        assert duration >= timedelta(minutes=30)
    
    def test_validation_estimated_before_started(self):
        """Test that estimated completion can't be before start."""
        with pytest.raises(Exception):
            CurrentContext(
                project_id="proj-1",
                current_objective="Test",
                started_at=datetime.now(),
                estimated_completion=datetime.now() - timedelta(hours=1)
            )


@pytest.mark.unit
@pytest.mark.context
class TestLockInfo:
    """Test LockInfo functionality."""
    
    def test_create_lock_info(self):
        """Test creating lock info."""
        lock = LockInfo(
            file_path="src/main.py",
            locked_by="agent-1",
            reason="Editing"
        )
        
        assert lock.file_path == "src/main.py"
        assert lock.lock_scope == "file"  # Default
    
    def test_is_stale(self):
        """Test stale lock detection."""
        lock = LockInfo(
            file_path="src/main.py",
            locked_by="agent-1",
            locked_at=datetime.now() - timedelta(hours=25)
        )
        
        assert lock.is_stale(timeout_hours=24) is True
    
    def test_is_not_stale(self):
        """Test when lock is not stale."""
        lock = LockInfo(
            file_path="src/main.py",
            locked_by="agent-1",
            locked_at=datetime.now() - timedelta(hours=12)
        )
        
        assert lock.is_stale(timeout_hours=24) is False
    
    def test_is_held_by(self):
        """Test checking lock holder."""
        lock = LockInfo(
            file_path="src/main.py",
            locked_by="agent-1"
        )
        
        assert lock.is_held_by("agent-1") is True
        assert lock.is_held_by("agent-2") is False
    
    def test_can_acquire_same_agent(self):
        """Test that same agent can always acquire."""
        lock = LockInfo(
            file_path="src/main.py",
            locked_by="agent-1",
            priority=0
        )
        
        assert lock.can_acquire("agent-1", 0) is True
    
    def test_can_acquire_higher_priority(self):
        """Test that higher priority can acquire."""
        lock = LockInfo(
            file_path="src/main.py",
            locked_by="agent-1",
            priority=1
        )
        
        assert lock.can_acquire("agent-2", 2) is True
    
    def test_cannot_acquire_lower_priority(self):
        """Test that lower priority cannot acquire."""
        lock = LockInfo(
            file_path="src/main.py",
            locked_by="agent-1",
            priority=2
        )
        
        assert lock.can_acquire("agent-2", 1) is False
    
    def test_extend(self):
        """Test extending a lock."""
        lock = LockInfo(
            file_path="src/main.py",
            locked_by="agent-1"
        )
        old_time = lock.locked_at
        
        lock.extend(new_expected_time=datetime.now() + timedelta(hours=1))
        
        assert lock.locked_at > old_time
        assert lock.expected_unlock_time is not None
    
    def test_extend_wrong_agent(self):
        """Test that only lock owner can extend."""
        lock = LockInfo(
            file_path="src/main.py",
            locked_by="agent-1"
        )
        
        with pytest.raises(ValueError):
            lock.extend(agent_id="agent-2")


@pytest.mark.unit
@pytest.mark.context
class TestLockRequest:
    """Test LockRequest model."""
    
    def test_create_lock_request(self):
        """Test creating a lock request."""
        request = LockRequest(
            id=str(uuid4()),
            file_path="src/main.py",
            agent_id="agent-1",
            agent_name="Test Agent",
            project_id="proj-1"
        )
        
        assert request.file_path == "src/main.py"
        assert request.priority == 0


@pytest.mark.unit
@pytest.mark.context
class TestProjectActivity:
    """Test ProjectActivity model."""
    
    def test_create_project_activity(self):
        """Test creating a project activity."""
        activity = ProjectActivity(
            project_id="proj-1",
            project_name="Test Project",
            total_sessions=5
        )
        
        assert activity.project_name == "Test Project"
        assert activity.total_sessions == 5


@pytest.mark.unit
@pytest.mark.context
class TestContextSummary:
    """Test ContextSummary model."""
    
    def test_from_agent_context(self):
        """Test creating summary from agent context."""
        context = AgentContext(
            agent_id="agent-1",
            agent_name="Test Agent",
            agent_type=AgentType.OPENCODE,
            session_id="session-1"
        )
        context.current_context = CurrentContext(
            project_id="proj-1",
            current_objective="Build feature"
        )
        context.locked_files = [
            LockInfo(file_path="file1.py", locked_by="agent-1"),
            LockInfo(file_path="file2.py", locked_by="agent-1")
        ]
        
        summary = ContextSummary.from_agent_context(context)
        
        assert summary.agent_id == "agent-1"
        assert summary.agent_name == "Test Agent"
        assert summary.current_project == "proj-1"
        assert summary.files_locked == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
