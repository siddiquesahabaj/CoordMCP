"""
Context management system for CoordMCP agents.
"""

from datetime import datetime
from typing import List, Optional, Dict
from uuid import uuid4

from coordmcp.storage.base import StorageBackend
from coordmcp.context.state import (
    AgentContext, AgentProfile, CurrentContext, 
    ContextEntry, SessionLogEntry
)
from coordmcp.context.file_tracker import FileTracker
from coordmcp.logger import get_logger

logger = get_logger("context.manager")


class AgentNotFoundError(Exception):
    """Exception raised when an agent is not found."""
    pass


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
                registry[agent_id] = AgentProfile.from_dict(agent_data)
            except Exception as e:
                logger.warning(f"Failed to parse agent profile for {agent_id}: {e}")
        
        return registry
    
    def _save_agent_registry(self, registry: Dict[str, AgentProfile]) -> bool:
        """Save the global agent registry."""
        key = self._get_agent_registry_key()
        
        data = {
            "agents": {agent_id: profile.to_dict() for agent_id, profile in registry.items()},
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
            return AgentContext.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to parse agent context for {agent_id}: {e}")
            return None
    
    def _save_agent_context(self, context: AgentContext) -> bool:
        """Save an agent's context."""
        key = self._get_agent_context_key(context.agent_id)
        return self.backend.save(key, context.to_dict())
    
    # ==================== Agent Registration ====================
    
    def register_agent(
        self,
        agent_name: str,
        agent_type: str,
        capabilities: List[str] = [],
        version: str = "1.0.0"
    ) -> str:
        """
        Register a new agent in the global registry.
        
        Args:
            agent_name: Name of the agent
            agent_type: Type (opencode, cursor, claude_code, custom)
            capabilities: List of agent capabilities
            version: Agent version
            
        Returns:
            Agent ID
        """
        agent_id = str(uuid4())
        
        profile = AgentProfile(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_type=agent_type,
            version=version,
            capabilities=capabilities or [],
            last_active=datetime.now(),
            total_sessions=0,
            projects_involved=[],
            status="active"
        )
        
        # Load registry and add agent
        registry = self._load_agent_registry()
        registry[agent_id] = profile
        self._save_agent_registry(registry)
        
        logger.info(f"Registered agent '{agent_name}' ({agent_type}) with ID {agent_id}")
        
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
        
        registry[agent_id].status = status
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
        # Verify agent exists
        agent = self.get_agent(agent_id)
        if not agent:
            raise AgentNotFoundError(f"Agent {agent_id} not found")
        
        # Load or create context
        context = self._load_agent_context(agent_id)
        
        if context is None:
            # Create new context
            session_id = str(uuid4())
            context = AgentContext(
                agent_id=agent_id,
                agent_name=agent.agent_name,
                agent_type=agent.agent_type,
                session_id=session_id,
                created_at=datetime.now()
            )
            
            # Update agent stats
            registry = self._load_agent_registry()
            if agent_id in registry:
                registry[agent_id].total_sessions += 1
                registry[agent_id].add_project(project_id)
                self._save_agent_registry(registry)
        
        # Set current context
        context.current_context = CurrentContext(
            project_id=project_id,
            current_objective=objective,
            task_description=task_description,
            priority=priority,
            current_file=current_file,
            started_at=datetime.now()
        )
        
        # Log session event
        context.add_session_log_entry(SessionLogEntry(
            timestamp=datetime.now(),
            event="context_started",
            details={
                "project_id": project_id,
                "objective": objective,
                "priority": priority
            }
        ))
        
        # Save context
        self._save_agent_context(context)
        
        # Mark agent as active
        agent.mark_active()
        registry = self._load_agent_registry()
        if agent_id in registry:
            registry[agent_id].mark_active()
            self._save_agent_registry(registry)
        
        logger.info(f"Agent {agent_id} started context on project {project_id}: {objective}")
        
        return context
    
    def get_current_context(self, agent_id: str) -> Optional[CurrentContext]:
        """Get an agent's current context."""
        context = self._load_agent_context(agent_id)
        if context:
            return context.current_context
        return None
    
    def end_context(self, agent_id: str) -> bool:
        """End an agent's current context."""
        context = self._load_agent_context(agent_id)
        
        if not context or not context.current_context:
            return False
        
        # Log end of context
        context.add_session_log_entry(SessionLogEntry(
            timestamp=datetime.now(),
            event="context_ended",
            details={
                "project_id": context.current_context.project_id,
                "objective": context.current_context.current_objective
            }
        ))
        
        # Clear current context
        old_context = context.current_context
        context.current_context = None
        
        # Unlock all files
        if context.locked_files:
            files_to_unlock = [lock.file_path for lock in context.locked_files]
            self.file_tracker.unlock_files(agent_id, old_context.project_id, files_to_unlock)
            context.locked_files = []
        
        # Save context
        self._save_agent_context(context)
        
        logger.info(f"Agent {agent_id} ended context")
        
        return True
    
    def switch_context(
        self,
        agent_id: str,
        to_project_id: str,
        to_objective: str,
        task_description: str = "",
        priority: str = "medium"
    ) -> AgentContext:
        """
        Switch agent context between projects or objectives.
        
        Args:
            agent_id: Agent ID
            to_project_id: Target project ID
            to_objective: New objective
            task_description: New task description
            priority: Priority level
            
        Returns:
            Updated AgentContext
        """
        # End current context
        old_context = self.get_current_context(agent_id)
        if old_context:
            # Unlock files in old project
            context = self._load_agent_context(agent_id)
            if context and context.locked_files:
                files_to_unlock = [lock.file_path for lock in context.locked_files]
                self.file_tracker.unlock_files(agent_id, old_context.project_id, files_to_unlock)
                context.locked_files = []
                self._save_agent_context(context)
            
            self.end_context(agent_id)
        
        # Start new context
        return self.start_context(
            agent_id=agent_id,
            project_id=to_project_id,
            objective=to_objective,
            task_description=task_description,
            priority=priority
        )
    
    def get_context_history(self, agent_id: str, limit: int = 10) -> List[ContextEntry]:
        """Get recent context entries for an agent."""
        context = self._load_agent_context(agent_id)
        if not context:
            return []
        
        return context.recent_context[-limit:]
    
    def get_session_log(self, agent_id: str, limit: int = 50) -> List[SessionLogEntry]:
        """Get session log for an agent."""
        context = self._load_agent_context(agent_id)
        if not context:
            return []
        
        return context.session_log[-limit:]
    
    # ==================== Context Operations ====================
    
    def add_context_entry(
        self,
        agent_id: str,
        file: str,
        operation: str,
        summary: str
    ) -> bool:
        """
        Add a context entry for an agent.
        
        Args:
            agent_id: Agent ID
            file: File being operated on
            operation: Operation type (read, write, analyze)
            summary: Brief summary
            
        Returns:
            True if successful
        """
        context = self._load_agent_context(agent_id)
        
        if not context:
            return False
        
        entry = ContextEntry(
            timestamp=datetime.now(),
            file=file,
            operation=operation,
            summary=summary
        )
        
        context.add_context_entry(entry)
        self._save_agent_context(context)
        
        return True
    
    def get_agent_context_full(self, agent_id: str) -> Optional[AgentContext]:
        """Get complete agent context."""
        return self._load_agent_context(agent_id)
    
    def get_agents_in_project(self, project_id: str) -> List[Dict]:
        """Get all agents currently working in a project."""
        agents = []
        
        for agent_profile in self.get_all_agents():
            context = self._load_agent_context(agent_profile.agent_id)
            if context and context.current_context:
                if context.current_context.project_id == project_id:
                    agents.append({
                        "agent_id": agent_profile.agent_id,
                        "agent_name": agent_profile.agent_name,
                        "agent_type": agent_profile.agent_type,
                        "current_objective": context.current_context.current_objective,
                        "locked_files_count": len(context.locked_files)
                    })
        
        return agents
