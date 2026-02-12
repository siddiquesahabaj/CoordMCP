"""
File tracking and locking system for CoordMCP.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from coordmcp.storage.base import StorageBackend
from coordmcp.context.state import LockInfo
from coordmcp.config import get_config
from coordmcp.logger import get_logger
from coordmcp.errors import FileLockError

logger = get_logger("context.file_tracker")


class FileTracker:
    """Tracks file locks across all agents to prevent conflicts."""
    
    def __init__(self, storage_backend: StorageBackend):
        """
        Initialize the file tracker.
        
        Args:
            storage_backend: Storage backend for persistence
        """
        self.backend = storage_backend
        self.config = get_config()
        logger.info("FileTracker initialized")
    
    def _get_project_locks_key(self, project_id: str) -> str:
        """Get storage key for project file locks."""
        return f"agents/locks/{project_id}"
    
    def _load_project_locks(self, project_id: str) -> Dict[str, LockInfo]:
        """
        Load all locks for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary of file_path -> LockInfo
        """
        key = self._get_project_locks_key(project_id)
        data = self.backend.load(key)
        
        if not data or "locks" not in data:
            return {}
        
        locks = {}
        for file_path, lock_data in data["locks"].items():
            try:
                locks[file_path] = LockInfo.parse_obj(lock_data)
            except Exception as e:
                logger.warning(f"Failed to parse lock for {file_path}: {e}")
        
        return locks
    
    def _save_project_locks(self, project_id: str, locks: Dict[str, LockInfo]) -> bool:
        """
        Save all locks for a project.
        
        Args:
            project_id: Project ID
            locks: Dictionary of file_path -> LockInfo
            
        Returns:
            True if successful
        """
        key = self._get_project_locks_key(project_id)
        
        data = {
            "locks": {path: lock.dict() for path, lock in locks.items()},
            "updated_at": datetime.now().isoformat()
        }
        
        return self.backend.save(key, data)
    
    def lock_files(
        self,
        agent_id: str,
        project_id: str,
        files: List[str],
        reason: str,
        expected_unlock_time: Optional[datetime] = None,
        priority: int = 0
    ) -> Dict:
        """
        Lock files to prevent conflicts between agents.
        
        Args:
            agent_id: ID of the agent locking the files
            project_id: Project ID
            files: List of file paths to lock
            reason: Reason for locking
            expected_unlock_time: When the lock is expected to be released
            priority: Lock priority (higher can preempt lower)
            
        Returns:
            Dictionary with success status and locked/conflicted files
            
        Raises:
            FileLockError: If any file is already locked by another agent
        """
        # Load current locks
        locks = self._load_project_locks(project_id)
        
        # Check for conflicts
        conflicts = []
        for file_path in files:
            if file_path in locks:
                existing_lock = locks[file_path]
                if not existing_lock.is_held_by(agent_id):
                    # Check if lock is stale
                    if existing_lock.is_stale(self.config.lock_timeout_hours):
                        logger.warning(
                            f"Removing stale lock on {file_path} by {existing_lock.locked_by}"
                        )
                        del locks[file_path]
                    elif existing_lock.can_acquire(agent_id, priority):
                        # Higher priority can preempt
                        logger.warning(
                            f"Preempting lock on {file_path} by {existing_lock.locked_by} (priority {priority} > {existing_lock.priority})"
                        )
                        del locks[file_path]
                    else:
                        conflicts.append({
                            "file_path": file_path,
                            "locked_by": existing_lock.locked_by,
                            "locked_at": existing_lock.locked_at.isoformat(),
                            "reason": existing_lock.reason,
                            "expected_unlock_time": existing_lock.expected_unlock_time.isoformat() if existing_lock.expected_unlock_time else None
                        })
        
        if conflicts:
            raise FileLockError(
                file_path=files[0] if files else "unknown",
                message=f"Cannot lock {len(conflicts)} file(s) - already locked by other agents",
                conflicts=conflicts
            )
        
        # Create new locks
        locked_files = []
        for file_path in files:
            lock_info = LockInfo(
                file_path=file_path,
                locked_at=datetime.now(),
                locked_by=agent_id,
                reason=reason,
                expected_unlock_time=expected_unlock_time,
                priority=priority
            )
            locks[file_path] = lock_info
            locked_files.append(file_path)
        
        # Save locks
        self._save_project_locks(project_id, locks)
        
        logger.info(f"Agent {agent_id} locked {len(locked_files)} file(s) in project {project_id}")
        
        return {
            "success": True,
            "locked_files": locked_files,
            "message": f"Successfully locked {len(locked_files)} file(s)"
        }
    
    def unlock_files(
        self,
        agent_id: str,
        project_id: str,
        files: List[str],
        force: bool = False
    ) -> Dict:
        """
        Unlock files after work is complete.
        
        Args:
            agent_id: ID of the agent unlocking the files
            project_id: Project ID
            files: List of file paths to unlock
            force: Force unlock even if not owned by agent (with warning)
            
        Returns:
            Dictionary with success status and unlocked/not_found files
        """
        locks = self._load_project_locks(project_id)
        
        unlocked = []
        not_found = []
        warnings = []
        
        for file_path in files:
            if file_path not in locks:
                not_found.append(file_path)
                continue
            
            existing_lock = locks[file_path]
            
            # Check if agent owns the lock
            if not existing_lock.is_held_by(agent_id):
                if force:
                    warnings.append({
                        "file_path": file_path,
                        "warning": f"Force-unlocked file owned by {existing_lock.locked_by}"
                    })
                    logger.warning(
                        f"Agent {agent_id} force-unlocked {file_path} owned by {existing_lock.locked_by}"
                    )
                else:
                    warnings.append({
                        "file_path": file_path,
                        "warning": f"File locked by {existing_lock.locked_by}, not {agent_id}"
                    })
                    continue
            
            del locks[file_path]
            unlocked.append(file_path)
        
        # Save updated locks
        if unlocked or warnings:
            self._save_project_locks(project_id, locks)
        
        logger.info(f"Agent {agent_id} unlocked {len(unlocked)} file(s) in project {project_id}")
        
        return {
            "success": True,
            "unlocked_files": unlocked,
            "not_found": not_found,
            "warnings": warnings
        }
    
    def get_locked_files(self, project_id: str) -> Dict:
        """
        Get list of currently locked files in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary with locked files grouped by agent
        """
        locks = self._load_project_locks(project_id)
        
        # Clean up stale locks
        stale_locks = []
        for file_path, lock_info in list(locks.items()):
            if lock_info.is_stale(self.config.lock_timeout_hours):
                stale_locks.append(file_path)
                del locks[file_path]
                logger.info(f"Cleaned up stale lock on {file_path}")
        
        # Save if we removed any stale locks
        if stale_locks:
            self._save_project_locks(project_id, locks)
        
        # Group by agent
        by_agent: Dict[str, List[Dict]] = {}
        for file_path, lock_info in locks.items():
            agent_id = lock_info.locked_by
            if agent_id not in by_agent:
                by_agent[agent_id] = []
            
            by_agent[agent_id].append({
                "file_path": file_path,
                "locked_at": lock_info.locked_at.isoformat(),
                "reason": lock_info.reason,
                "expected_unlock_time": lock_info.expected_unlock_time.isoformat() if lock_info.expected_unlock_time else None,
                "priority": lock_info.priority
            })
        
        return {
            "success": True,
            "total_locked": len(locks),
            "by_agent": by_agent,
            "stale_locks_removed": len(stale_locks)
        }
    
    def is_locked(self, project_id: str, file_path: str) -> bool:
        """
        Check if a file is locked.
        
        Args:
            project_id: Project ID
            file_path: File path to check
            
        Returns:
            True if locked (and not stale)
        """
        locks = self._load_project_locks(project_id)
        
        if file_path not in locks:
            return False
        
        lock_info = locks[file_path]
        
        # Check if stale
        if lock_info.is_stale(self.config.lock_timeout_hours):
            # Clean up stale lock
            del locks[file_path]
            self._save_project_locks(project_id, locks)
            return False
        
        return True
    
    def get_lock_holder(self, project_id: str, file_path: str) -> Optional[str]:
        """
        Get the agent that holds the lock on a file.
        
        Args:
            project_id: Project ID
            file_path: File path to check
            
        Returns:
            Agent ID or None if not locked
        """
        locks = self._load_project_locks(project_id)
        
        if file_path not in locks:
            return None
        
        lock_info = locks[file_path]
        
        # Check if stale
        if lock_info.is_stale(self.config.lock_timeout_hours):
            del locks[file_path]
            self._save_project_locks(project_id, locks)
            return None
        
        return lock_info.locked_by
    
    def cleanup_stale_locks(self, project_id: str) -> int:
        """
        Clean up all stale locks in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Number of stale locks removed
        """
        locks = self._load_project_locks(project_id)
        
        stale_locks = []
        for file_path, lock_info in list(locks.items()):
            if lock_info.is_stale(self.config.lock_timeout_hours):
                stale_locks.append(file_path)
                del locks[file_path]
        
        if stale_locks:
            self._save_project_locks(project_id, locks)
            logger.info(f"Cleaned up {len(stale_locks)} stale locks in project {project_id}")
        
        return len(stale_locks)
    
    def extend_lock(
        self,
        agent_id: str,
        project_id: str,
        file_path: str,
        new_expected_unlock_time: Optional[datetime] = None
    ) -> bool:
        """
        Extend the lock on a file.
        
        Args:
            agent_id: Agent ID
            project_id: Project ID
            file_path: File to extend
            new_expected_unlock_time: New expected unlock time
            
        Returns:
            True if successful
        """
        locks = self._load_project_locks(project_id)
        
        if file_path not in locks:
            return False
        
        lock_info = locks[file_path]
        
        try:
            lock_info.extend(new_expected_unlock_time, agent_id)
            self._save_project_locks(project_id, locks)
            
            logger.info(f"Agent {agent_id} extended lock on {file_path}")
            return True
        except ValueError as e:
            logger.warning(f"Failed to extend lock: {e}")
            return False
