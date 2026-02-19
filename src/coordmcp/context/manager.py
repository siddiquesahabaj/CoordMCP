"""
Context management system for CoordMCP agents.
"""

from datetime import datetime
from typing import List, Optional, Dict
from uuid import uuid4

from coordmcp.storage.base import StorageBackend
from coordmcp.context.state import (
    AgentContext, AgentProfile, CurrentContext, ProjectActivity,
    ContextEntry, SessionLogEntry, AgentType, Priority, OperationType
)
from coordmcp.memory.models import SessionSummary, ActivityFeedItem
from coordmcp.context.file_tracker import FileTracker
from coordmcp.logger import get_logger
from coordmcp.errors import AgentNotFoundError

logger = get_logger("context.manager")


class ContextManager:
    """Manages agent contexts, registration, and context switching."""
    
    def __init__(self, storage_backend: StorageBackend, file_tracker: FileTracker):
        """
        Initialize the context manager.
        
        Args:
            storage_backend: Storage backend for persistence
            file_tracker: File tracker for lock management
        """
        self.backend = storage_backend
        self.file_tracker = file_tracker
        logger.info("ContextManager initialized")
    
    def _get_agent_registry_key(self) -> str:
        """Get storage key for global agent registry."""
        return "global/agent_registry"
    
    def _get_agent_context_key(self, agent_id: str) -> str:
        """Get storage key for agent context."""
        return f"agents/{agent_id}/context"
    
    def _load_agent_registry(self) -> Dict[str, AgentProfile]:
        """Load the global agent registry."""
        key = self._get_agent_registry_key()
        data = self.backend.load(key)
        
        if not data or "agents" not in data:
            return {}
        
        registry = {}
        for agent_id, agent_data in data["agents"].items():
            try:
                registry[agent_id] = AgentProfile.model_validate(agent_data)
            except Exception as e:
                logger.warning(f"Failed to parse agent profile for {agent_id}: {e}")
        
        return registry
    
    def _save_agent_registry(self, registry: Dict[str, AgentProfile]) -> bool:
        """Save the global agent registry."""
        key = self._get_agent_registry_key()
        
        data = {
            "agents": {agent_id: profile.model_dump() for agent_id, profile in registry.items()},
            "updated_at": datetime.now().isoformat()
        }
        
        return self.backend.save(key, data)
    
    def _load_agent_context(self, agent_id: str) -> Optional[AgentContext]:
        """Load an agent's context."""
        key = self._get_agent_context_key(agent_id)
        data = self.backend.load(key)
        
        if not data:
            return None
        
        try:
            return AgentContext.model_validate(data)
        except Exception as e:
            logger.error(f"Failed to parse agent context for {agent_id}: {e}")
            return None
    
    def _save_agent_context(self, context: AgentContext) -> bool:
        """Save an agent's context."""
        key = self._get_agent_context_key(context.agent_id)
        return self.backend.save(key, context.model_dump())
    
    # ==================== Agent Registration ====================
    
    def register_agent(
        self,
        agent_name: str,
        agent_type: str,
        capabilities: List[str] = [],
        version: str = "1.0.0"
    ) -> str:
        """
        Register a new agent or reconnect to an existing agent.
        
        If an agent with the same name already exists, reconnects to that agent
        and updates their last_active timestamp. Otherwise, creates a new agent.
        
        Args:
            agent_name: Name of the agent
            agent_type: Type (opencode, cursor, claude_code, custom)
            capabilities: List of agent capabilities
            version: Agent version
            
        Returns:
            Agent ID (existing or new)
        """
        # Load registry first to check for existing agent
        registry = self._load_agent_registry()
        
        # Check if agent with this name already exists
        existing_agent_id = None
        existing_profile = None
        for aid, profile in registry.items():
            if profile.agent_name == agent_name and profile.status == "active":
                existing_agent_id = aid
                existing_profile = profile
                break
        
        if existing_agent_id:
            # Reconnect to existing agent
            existing_profile.last_active = datetime.now()
            existing_profile.version = version
            # Update capabilities if provided
            if capabilities:
                existing_profile.capabilities = capabilities
            
            self._save_agent_registry(registry)
            logger.info(f"Reconnected to existing agent '{agent_name}' with ID {existing_agent_id}")
            return existing_agent_id
        
        # Create new agent
        agent_id = str(uuid4())
        
        # Convert string to enum
        try:
            agent_type_enum = AgentType(agent_type)
        except ValueError:
            agent_type_enum = AgentType.CUSTOM
        
        profile = AgentProfile(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_type=agent_type_enum,
            version=version,
            capabilities=capabilities or [],
            last_active=datetime.now(),
            total_sessions=0,
            projects_involved=[],
            status="active"
        )
        
        # Add new agent to registry
        registry[agent_id] = profile
        self._save_agent_registry(registry)
        
        logger.info(f"Registered new agent '{agent_name}' ({agent_type}) with ID {agent_id}")
        
        return agent_id
    
    def get_agent(self, agent_id: str) -> Optional[AgentProfile]:
        """Get an agent's profile from the registry."""
        registry = self._load_agent_registry()
        return registry.get(agent_id)
    
    def get_all_agents(self) -> List[AgentProfile]:
        """Get all registered agents."""
        registry = self._load_agent_registry()
        return list(registry.values())
    
    def update_agent_status(self, agent_id: str, status: str) -> bool:
        """Update an agent's status."""
        registry = self._load_agent_registry()
        
        if agent_id not in registry:
            return False
        
        # Validate status
        if status not in ["active", "inactive", "suspended"]:
            logger.warning(f"Invalid status: {status}")
            return False
        
        registry[agent_id].status = status  # type: ignore
        registry[agent_id].mark_active()
        
        self._save_agent_registry(registry)
        return True
    
    def delete_agent(self, agent_id: str) -> bool:
        """Remove an agent from the registry."""
        registry = self._load_agent_registry()
        
        if agent_id not in registry:
            return False
        
        del registry[agent_id]
        self._save_agent_registry(registry)
        
        # Also delete context
        self.backend.delete(self._get_agent_context_key(agent_id))
        
        logger.info(f"Deleted agent {agent_id}")
        return True
    
    # ==================== Context Management ====================
    
    def start_context(
        self,
        agent_id: str,
        project_id: str,
        objective: str,
        task_description: str = "",
        priority: str = "medium",
        current_file: str = "",
        task_id: str = None
    ) -> AgentContext:
        """
        Start a new work context for an agent.
        
        Args:
            agent_id: Agent ID
            project_id: Project ID
            objective: Current objective
            task_description: Detailed task description
            priority: Priority level (critical, high, medium, low)
            current_file: Current file being worked on
            task_id: Optional task ID to link this context to
            
        Returns:
            Updated AgentContext
            
        Raises:
            AgentNotFoundError: If agent not registered
        """
        # Check if agent is registered
        agent_profile = self.get_agent(agent_id)
        if not agent_profile:
            raise AgentNotFoundError(f"Agent {agent_id} not found. Please register first.")
        
        # Convert priority string to enum
        try:
            priority_enum = Priority(priority)
        except ValueError:
            priority_enum = Priority.MEDIUM
        
        # Create current context
        current_context = CurrentContext(
            project_id=project_id,
            current_objective=objective,
            task_description=task_description,
            priority=priority_enum,
            current_file=current_file,
            current_task_id=task_id
        )
        
        # Load or create agent context
        agent_context = self._load_agent_context(agent_id)
        
        if agent_context:
            # End any existing context first
            if agent_context.current_context:
                self.end_context(agent_id)
            
            # Update context
            agent_context.current_context = current_context
            agent_context.add_session_log_entry(SessionLogEntry(
                event="context_started",
                details={
                    "project_id": project_id,
                    "objective": objective,
                    "priority": priority,
                    "task_id": task_id
                }
            ))
        else:
            # Create new context
            agent_context = AgentContext(
                agent_id=agent_id,
                agent_name=agent_profile.agent_name,
                agent_type=agent_profile.agent_type,
                session_id=str(uuid4()),
                current_context=current_context
            )
            agent_context.add_session_log_entry(SessionLogEntry(
                event="context_started",
                details={
                    "project_id": project_id,
                    "objective": objective,
                    "priority": priority,
                    "task_id": task_id
                }
            ))
        
        # Update agent profile
        agent_profile.add_project(project_id)
        agent_profile.increment_sessions()
        agent_profile.mark_active()
        
        registry = self._load_agent_registry()
        registry[agent_id] = agent_profile
        self._save_agent_registry(registry)
        
        # If task_id provided, update the task status
        if task_id:
            self._link_context_to_task(agent_id, project_id, task_id)
        
        # Save context
        self._save_agent_context(agent_context)
        
        logger.info(f"Agent {agent_id} started context in project {project_id}: {objective}")
        
        return agent_context
    
    def end_context(self, agent_id: str) -> bool:
        """
        End the current context for an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            True if successful
        """
        agent_context = self._load_agent_context(agent_id)
        if not agent_context:
            return False
        
        if not agent_context.current_context:
            logger.warning(f"Agent {agent_id} has no active context to end")
            return False
        
        project_id = agent_context.current_context.project_id
        
        # Unlock all files in the project
        locked_files = agent_context.get_locked_file_paths()
        if locked_files:
            try:
                self.file_tracker.unlock_files(agent_id, project_id, locked_files)
            except Exception as e:
                logger.error(f"Error unlocking files for agent {agent_id}: {e}")
        
        # Calculate session duration
        duration = agent_context.current_context.get_duration()
        duration_minutes = int(duration.total_seconds() / 60)
        
        # Generate session summary
        self._generate_and_save_session_summary(
            agent_id=agent_id,
            project_id=project_id,
            agent_context=agent_context,
            duration_minutes=duration_minutes
        )
        
        # Log activity
        self._log_session_activity(
            agent_id=agent_id,
            project_id=project_id,
            agent_context=agent_context,
            duration_minutes=duration_minutes
        )
        
        # Update agent's cross-project history
        self._update_agent_project_history(agent_id, project_id, duration_minutes)
        
        # Complete linked task if exists
        current_task_id = agent_context.current_context.current_task_id
        if current_task_id:
            self._complete_task_on_context_end(agent_id, project_id, current_task_id)
        
        # Log context end
        agent_context.add_session_log_entry(SessionLogEntry(
            event="context_ended",
            details={
                "project_id": project_id,
                "objective": agent_context.current_context.current_objective,
                "duration_seconds": duration.total_seconds(),
                "task_id": current_task_id
            }
        ))
        
        # Clear current context
        agent_context.current_context = None
        agent_context.locked_files = []
        
        self._save_agent_context(agent_context)
        
        logger.info(f"Agent {agent_id} ended context in project {project_id} (duration: {duration_minutes} min)")
        
        return True
    
    def switch_context(
        self,
        agent_id: str,
        new_project_id: str,
        new_objective: str,
        task_description: str = "",
        priority: str = "medium",
        current_file: str = ""
    ) -> AgentContext:
        """
        Switch agent from one context to another.
        
        Args:
            agent_id: Agent ID
            new_project_id: New project ID
            new_objective: New objective
            task_description: New task description
            priority: Priority level
            current_file: Current file
            
        Returns:
            Updated AgentContext
        """
        # End current context
        self.end_context(agent_id)
        
        # Start new context
        return self.start_context(
            agent_id=agent_id,
            project_id=new_project_id,
            objective=new_objective,
            task_description=task_description,
            priority=priority,
            current_file=current_file
        )
    
    def get_context(self, agent_id: str) -> Optional[AgentContext]:
        """Get an agent's current context."""
        return self._load_agent_context(agent_id)
    
    def get_current_context(self, agent_id: str) -> Optional[CurrentContext]:
        """Get an agent's current context info only."""
        context = self._load_agent_context(agent_id)
        if context:
            return context.current_context
        return None
    
    def add_context_entry(
        self,
        agent_id: str,
        file: str,
        operation: str,
        summary: str = ""
    ) -> bool:
        """
        Add a context entry for file operations.
        
        Args:
            agent_id: Agent ID
            file: File path
            operation: Operation type (read, write, analyze, delete)
            summary: Brief summary
            
        Returns:
            True if successful
        """
        agent_context = self._load_agent_context(agent_id)
        if not agent_context:
            return False
        
        # Convert operation string to enum
        try:
            operation_enum = OperationType(operation)
        except ValueError:
            operation_enum = OperationType.READ
        
        entry = ContextEntry(
            file=file,
            operation=operation_enum,
            summary=summary
        )
        
        agent_context.add_context_entry(entry)
        self._save_agent_context(agent_context)
        
        return True
    
    def lock_files(
        self,
        agent_id: str,
        files: List[str],
        reason: str = "",
        expected_duration_minutes: Optional[int] = None
    ) -> Dict:
        """
        Lock files for an agent.
        
        Args:
            agent_id: Agent ID
            files: List of file paths
            reason: Reason for locking
            expected_duration_minutes: Expected duration in minutes
            
        Returns:
            Dictionary with lock results
        """
        agent_context = self._load_agent_context(agent_id)
        if not agent_context:
            return {"success": False, "error": "Agent context not found"}
        
        if not agent_context.current_context:
            return {"success": False, "error": "Agent has no active context"}
        
        project_id = agent_context.current_context.project_id
        
        # Calculate expected unlock time
        expected_unlock_time = None
        if expected_duration_minutes:
            expected_unlock_time = datetime.now() + __import__('datetime').timedelta(minutes=expected_duration_minutes)
        
        try:
            result = self.file_tracker.lock_files(
                agent_id=agent_id,
                project_id=project_id,
                files=files,
                reason=reason,
                expected_unlock_time=expected_unlock_time
            )
            
            # Update agent context
            if result.get("success"):
                from coordmcp.context.state import LockInfo
                for file_path in result.get("locked_files", []):
                    lock_info = LockInfo(
                        file_path=file_path,
                        locked_by=agent_id,
                        reason=reason,
                        expected_unlock_time=expected_unlock_time
                    )
                    agent_context.lock_file(lock_info)
                
                self._save_agent_context(agent_context)
            
            return result
            
        except Exception as e:
            logger.error(f"Error locking files for agent {agent_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def unlock_files(self, agent_id: str, files: List[str]) -> Dict:
        """
        Unlock files for an agent.
        
        Args:
            agent_id: Agent ID
            files: List of file paths
            
        Returns:
            Dictionary with unlock results
        """
        agent_context = self._load_agent_context(agent_id)
        if not agent_context:
            return {"success": False, "error": "Agent context not found"}
        
        if not agent_context.current_context:
            return {"success": False, "error": "Agent has no active context"}
        
        project_id = agent_context.current_context.project_id
        
        try:
            result = self.file_tracker.unlock_files(
                agent_id=agent_id,
                project_id=project_id,
                files=files
            )
            
            # Update agent context
            if result.get("success"):
                for file_path in result.get("unlocked_files", []):
                    agent_context.unlock_file(file_path)
                
                self._save_agent_context(agent_context)
            
            return result
            
        except Exception as e:
            logger.error(f"Error unlocking files for agent {agent_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_agents_in_project(self, project_id: str) -> List[Dict]:
        """
        Get all agents working in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            List of agent summaries
        """
        agents = []
        
        for profile in self.get_all_agents():
            context = self._load_agent_context(profile.agent_id)
            
            if context and context.current_context and context.current_context.project_id == project_id:
                agents.append({
                    "agent_id": profile.agent_id,
                    "agent_name": profile.agent_name,
                    "current_objective": context.current_context.current_objective,
                    "locked_files_count": len(context.locked_files)
                })
        
        return agents
    
    def get_context_history(self, agent_id: str, limit: int = 10) -> List[ContextEntry]:
        """
        Get recent context history (file operations) for an agent.
        Returns entries in reverse chronological order (newest first).
        
        Args:
            agent_id: Agent ID
            limit: Maximum number of entries to return
            
        Returns:
            List of context entries
        """
        agent_context = self._load_agent_context(agent_id)
        if not agent_context:
            return []
        
        # Return last N entries in reverse order (newest first)
        return agent_context.recent_context[-limit:][::-1]
    
    def get_session_log(self, agent_id: str, limit: int = 50) -> List[SessionLogEntry]:
        """
        Get session log for an agent.
        
        Args:
            agent_id: Agent ID
            limit: Maximum number of entries to return
            
        Returns:
            List of session log entries
        """
        agent_context = self._load_agent_context(agent_id)
        if not agent_context:
            return []
        
        return agent_context.session_log[:limit]
    
    # ==================== Session Summary & Activity Methods ====================
    
    def _generate_and_save_session_summary(self, agent_id: str, project_id: str, 
                                           agent_context: AgentContext, 
                                           duration_minutes: int) -> None:
        """Generate and save a session summary."""
        try:
            # Get project info for project name
            from coordmcp.memory.json_store import ProjectMemoryStore
            memory_store = ProjectMemoryStore(self.backend)
            project_info = memory_store.get_project_info(project_id)
            project_name = project_info.project_name if project_info else "Unknown Project"
            
            # Get agent profile for agent name
            agent_profile = self.get_agent(agent_id)
            agent_name = agent_profile.agent_name if agent_profile else "Unknown Agent"
            
            # Extract session data
            current_context = agent_context.current_context
            if not current_context:
                return
            
            # Get files modified from recent context
            files_modified = []
            for entry in agent_context.recent_context:
                if entry.operation == OperationType.WRITE or entry.operation == OperationType.DELETE:
                    if entry.file not in files_modified:
                        files_modified.append(entry.file)
            
            # Create session summary
            summary = SessionSummary(
                id=str(uuid4()),
                agent_id=agent_id,
                project_id=project_id,
                session_id=agent_context.session_id,
                duration_minutes=duration_minutes,
                objective=current_context.current_objective,
                files_modified=files_modified,
                summary_text=""
            )
            
            # Generate summary text
            summary.summary_text = summary.generate_summary_text(agent_name, project_name)
            
            # Save summary
            memory_store.save_session_summary(project_id, summary)
            logger.info(f"Generated session summary for agent {agent_id}")
            
        except Exception as e:
            logger.error(f"Error generating session summary: {e}")
    
    def _log_session_activity(self, agent_id: str, project_id: str,
                              agent_context: AgentContext, 
                              duration_minutes: int) -> None:
        """Log session completion activity."""
        try:
            from coordmcp.memory.json_store import ProjectMemoryStore
            memory_store = ProjectMemoryStore(self.backend)
            
            # Get agent name
            agent_profile = self.get_agent(agent_id)
            agent_name = agent_profile.agent_name if agent_profile else "Unknown Agent"
            
            current_context = agent_context.current_context
            if not current_context:
                return
            
            # Create activity
            activity = ActivityFeedItem(
                id=str(uuid4()),
                activity_type="session_completed",
                agent_id=agent_id,
                agent_name=agent_name,
                project_id=project_id,
                summary=f"{agent_name} completed: {current_context.current_objective} ({duration_minutes} min)",
                related_entity_id=agent_context.session_id,
                related_entity_type="session"
            )
            
            # Log activity
            memory_store.log_activity(project_id, activity)
            logger.debug(f"Logged session activity for agent {agent_id}")
            
        except Exception as e:
            logger.error(f"Error logging session activity: {e}")
    
    def _update_agent_project_history(self, agent_id: str, project_id: str,
                                      duration_minutes: int) -> None:
        """Update agent's cross-project history."""
        try:
            # Get agent profile
            registry = self._load_agent_registry()
            agent_profile = registry.get(agent_id)
            
            if not agent_profile:
                return
            
            # Update last_project_id
            agent_profile.last_project_id = project_id
            
            # Find or create project activity
            project_activity = None
            for activity in agent_profile.cross_project_history:
                if activity.project_id == project_id:
                    project_activity = activity
                    break
            
            if project_activity:
                # Update existing activity
                project_activity.last_visited = datetime.now()
                project_activity.total_sessions += 1
            else:
                # Get project name
                from coordmcp.memory.json_store import ProjectMemoryStore
                memory_store = ProjectMemoryStore(self.backend)
                project_info = memory_store.get_project_info(project_id)
                project_name = project_info.project_name if project_info else "Unknown"
                
                # Create new project activity
                project_activity = ProjectActivity(
                    project_id=project_id,
                    project_name=project_name,
                    last_visited=datetime.now(),
                    total_sessions=1
                )
                agent_profile.cross_project_history.append(project_activity)
            
            # Save registry
            self._save_agent_registry(registry)
            logger.debug(f"Updated project history for agent {agent_id}")
            
        except Exception as e:
            logger.error(f"Error updating agent project history: {e}")
    
    def _link_context_to_task(self, agent_id: str, project_id: str, task_id: str) -> None:
        """Link context to task and update task status."""
        try:
            from coordmcp.memory.json_store import ProjectMemoryStore
            from coordmcp.memory.models import TaskStatus, ActivityFeedItem
            
            memory_store = ProjectMemoryStore(self.backend)
            
            # Get the task
            task = memory_store.get_task(project_id, task_id)
            if not task:
                logger.warning(f"Task {task_id} not found, cannot link context")
                return
            
            # Update task status to in_progress
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.IN_PROGRESS
                task.assigned_agent_id = agent_id
                task.started_at = datetime.now()
                memory_store.update_task(project_id, task, agent_id)
                
                # Log activity
                agent_profile = self.get_agent(agent_id)
                agent_name = agent_profile.agent_name if agent_profile else "Unknown"
                
                activity = ActivityFeedItem(
                    id=str(uuid4()),
                    activity_type="task_started",
                    agent_id=agent_id,
                    agent_name=agent_name,
                    project_id=project_id,
                    summary=f"Task '{task.title}' started by {agent_name}",
                    related_entity_id=task_id,
                    related_entity_type="task"
                )
                memory_store.log_activity(project_id, activity)
                
                logger.info(f"Linked context to task {task_id} and started it")
            
        except Exception as e:
            logger.error(f"Error linking context to task: {e}")
    
    def _complete_task_on_context_end(self, agent_id: str, project_id: str, task_id: str) -> None:
        """Complete task when context ends."""
        try:
            from coordmcp.memory.json_store import ProjectMemoryStore
            from coordmcp.memory.models import TaskStatus, ActivityFeedItem
            
            memory_store = ProjectMemoryStore(self.backend)
            
            # Get the task
            task = memory_store.get_task(project_id, task_id)
            if not task:
                return
            
            # Complete the task
            if task.status == TaskStatus.IN_PROGRESS:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                if task.started_at:
                    task.actual_hours = (task.completed_at - task.started_at).total_seconds() / 3600
                memory_store.update_task(project_id, task, agent_id)
                
                # Log activity
                agent_profile = self.get_agent(agent_id)
                agent_name = agent_profile.agent_name if agent_profile else "Unknown"
                
                activity = ActivityFeedItem(
                    id=str(uuid4()),
                    activity_type="task_completed_via_context",
                    agent_id=agent_id,
                    agent_name=agent_name,
                    project_id=project_id,
                    summary=f"Task '{task.title}' completed (context ended)",
                    related_entity_id=task_id,
                    related_entity_type="task"
                )
                memory_store.log_activity(project_id, activity)
                
                logger.info(f"Task {task_id} completed automatically when context ended")
            
        except Exception as e:
            logger.error(f"Error completing task on context end: {e}")
