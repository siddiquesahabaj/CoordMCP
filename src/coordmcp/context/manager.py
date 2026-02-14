"""
Context management system for CoordMCP agents.
"""

from datetime import datetime
from typing import List, Optional, Dict
from uuid import uuid4

from coordmcp.storage.base import StorageBackend
from coordmcp.context.state import (
    AgentContext, AgentProfile, CurrentContext, 
    ContextEntry, SessionLogEntry, AgentType, Priority, OperationType
)
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
                registry[agent_id] = AgentProfile.parse_obj(agent_data)
            except Exception as e:
                logger.warning(f"Failed to parse agent profile for {agent_id}: {e}")
        
        return registry
    
    def _save_agent_registry(self, registry: Dict[str, AgentProfile]) -> bool:
        """Save the global agent registry."""
        key = self._get_agent_registry_key()
        
        data = {
            "agents": {agent_id: profile.dict() for agent_id, profile in registry.items()},
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
            return AgentContext.parse_obj(data)
        except Exception as e:
            logger.error(f"Failed to parse agent context for {agent_id}: {e}")
            return None
    
    def _save_agent_context(self, context: AgentContext) -> bool:
        """Save an agent's context."""
        key = self._get_agent_context_key(context.agent_id)
        return self.backend.save(key, context.dict())
    
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
        current_file: str = ""
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
            current_file=current_file
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
                    "priority": priority
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
                    "priority": priority
                }
            ))
        
        # Update agent profile
        agent_profile.add_project(project_id)
        agent_profile.increment_sessions()
        agent_profile.mark_active()
        
        registry = self._load_agent_registry()
        registry[agent_id] = agent_profile
        self._save_agent_registry(registry)
        
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
        
        # Log context end
        agent_context.add_session_log_entry(SessionLogEntry(
            event="context_ended",
            details={
                "project_id": project_id,
                "objective": agent_context.current_context.current_objective,
                "duration_seconds": agent_context.current_context.get_duration().total_seconds()
            }
        ))
        
        # Clear current context
        agent_context.current_context = None
        agent_context.locked_files = []
        
        self._save_agent_context(agent_context)
        
        logger.info(f"Agent {agent_id} ended context in project {project_id}")
        
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
