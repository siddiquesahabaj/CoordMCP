"""
Event system for CoordMCP.

Provides hooks for before/after tool execution and other events.
Allows plugins and extensions to add custom behavior.

Example:
    from coordmcp.events import event_manager, ToolEvent
    
    @event_manager.before_tool("save_decision")
    async def validate_decision(project_id: str, **kwargs):
        # Custom validation logic
        if not is_valid(kwargs.get("title")):
            return {"success": False, "error": "Invalid title"}
    
    @event_manager.after_tool("save_decision")
    async def log_decision(result: dict, **kwargs):
        # Custom logging logic
        logger.info(f"Decision saved: {result}")
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum
from coordmcp.logger import get_logger

logger = get_logger("events")


class EventType(Enum):
    """Types of events that can be triggered."""
    BEFORE_TOOL = "before_tool"
    AFTER_TOOL = "after_tool"
    BEFORE_RESOURCE = "before_resource"
    AFTER_RESOURCE = "after_resource"
    CONTEXT_STARTED = "context_started"
    CONTEXT_ENDED = "context_ended"
    FILES_LOCKED = "files_locked"
    FILES_UNLOCKED = "files_unlocked"


@dataclass
class Event:
    """Represents an event in the system."""
    type: EventType
    name: str
    data: Dict[str, Any]
    timestamp: float
    
    def __post_init__(self):
        import time
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class ToolEvent:
    """Represents a tool execution event."""
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    duration_ms: Optional[float] = None


class EventManager:
    """
    Manager for CoordMCP events and hooks.
    
    Allows registering callbacks for various events in the system
    to add custom behavior, logging, validation, etc.
    """
    
    def __init__(self):
        # Event handlers: event_type -> name -> list of handlers
        self._handlers: Dict[EventType, Dict[str, List[Callable]]] = {
            event_type: {} for event_type in EventType
        }
        
        # Global handlers that run for all events of a type
        self._global_handlers: Dict[EventType, List[Callable]] = {
            event_type: [] for event_type in EventType
        }
        
        # Event history (optional, for debugging)
        self._event_history: List[Event] = []
        self._max_history = 1000
        
        logger.info("EventManager initialized")
    
    def before_tool(self, tool_name: str):
        """
        Decorator to register a handler that runs before a tool.
        
        Args:
            tool_name: Name of the tool to hook
            
        Returns:
            Decorator function
            
        Example:
            @event_manager.before_tool("save_decision")
            async def validate(project_id: str, title: str, **kwargs):
                if len(title) < 3:
                    return {"success": False, "error": "Title too short"}
        """
        def decorator(func: Callable) -> Callable:
            self._register_handler(
                EventType.BEFORE_TOOL,
                tool_name,
                func
            )
            return func
        return decorator
    
    def after_tool(self, tool_name: str):
        """
        Decorator to register a handler that runs after a tool.
        
        Args:
            tool_name: Name of the tool to hook
            
        Returns:
            Decorator function
            
        Example:
            @event_manager.after_tool("save_decision")
            async def log_result(result: dict, **kwargs):
                logger.info(f"Decision saved: {result.get('decision_id')}")
        """
        def decorator(func: Callable) -> Callable:
            self._register_handler(
                EventType.AFTER_TOOL,
                tool_name,
                func
            )
            return func
        return decorator
    
    def on_event(self, event_type: EventType, name: str = "*"):
        """
        Decorator to register a handler for a specific event type.
        
        Args:
            event_type: Type of event to listen for
            name: Specific event name, or "*" for all events of this type
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            if name == "*":
                self._global_handlers[event_type].append(func)
            else:
                self._register_handler(event_type, name, func)
            return func
        return decorator
    
    def _register_handler(
        self,
        event_type: EventType,
        name: str,
        handler: Callable
    ) -> None:
        """Register an event handler."""
        if name not in self._handlers[event_type]:
            self._handlers[event_type][name] = []
        self._handlers[event_type][name].append(handler)
        logger.debug(f"Handler registered for {event_type.value}:{name}")
    
    async def trigger_before_tool(
        self,
        tool_name: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Trigger before_tool handlers.
        
        Args:
            tool_name: Name of the tool being called
            **kwargs: Tool arguments
            
        Returns:
            If any handler returns a dict with "success": False,
            that result is returned and tool execution should be stopped.
            Otherwise returns None.
        """
        # Trigger global handlers first
        for handler in self._global_handlers[EventType.BEFORE_TOOL]:
            try:
                result = await handler(tool_name=tool_name, **kwargs)
                if result and not result.get("success", True):
                    return result
            except Exception as e:
                logger.error(f"Error in global before_tool handler: {e}")
        
        # Trigger specific handlers
        handlers = self._handlers[EventType.BEFORE_TOOL].get(tool_name, [])
        for handler in handlers:
            try:
                result = await handler(**kwargs)
                if result and not result.get("success", True):
                    return result
            except Exception as e:
                logger.error(f"Error in before_tool handler for {tool_name}: {e}")
        
        return None
    
    async def trigger_after_tool(
        self,
        tool_name: str,
        result: Dict[str, Any],
        **kwargs
    ) -> None:
        """
        Trigger after_tool handlers.
        
        Args:
            tool_name: Name of the tool that was called
            result: Tool execution result
            **kwargs: Tool arguments
        """
        event_data = {"tool_name": tool_name, "result": result, "args": kwargs}
        
        # Trigger specific handlers
        handlers = self._handlers[EventType.AFTER_TOOL].get(tool_name, [])
        for handler in handlers:
            try:
                await handler(result=result, **kwargs)
            except Exception as e:
                logger.error(f"Error in after_tool handler for {tool_name}: {e}")
        
        # Trigger global handlers
        for handler in self._global_handlers[EventType.AFTER_TOOL]:
            try:
                await handler(tool_name=tool_name, result=result, **kwargs)
            except Exception as e:
                logger.error(f"Error in global after_tool handler: {e}")
    
    async def trigger_event(
        self,
        event_type: EventType,
        name: str,
        **data
    ) -> None:
        """
        Trigger an arbitrary event.
        
        Args:
            event_type: Type of event
            name: Event name
            **data: Event data
        """
        import time
        
        # Create event record
        event = Event(
            type=event_type,
            name=name,
            data=data,
            timestamp=time.time()
        )
        
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Trigger specific handlers
        handlers = self._handlers[event_type].get(name, [])
        for handler in handlers:
            try:
                await handler(**data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type.value}:{name}: {e}")
        
        # Trigger global handlers
        for handler in self._global_handlers[event_type]:
            try:
                await handler(event_type=event_type, name=name, **data)
            except Exception as e:
                logger.error(f"Error in global event handler: {e}")
    
    def remove_handler(
        self,
        event_type: EventType,
        name: str,
        handler: Callable
    ) -> bool:
        """
        Remove a specific event handler.
        
        Args:
            event_type: Type of event
            name: Event name
            handler: Handler function to remove
            
        Returns:
            True if removed, False if not found
        """
        handlers = self._handlers[event_type].get(name, [])
        if handler in handlers:
            handlers.remove(handler)
            return True
        return False
    
    def clear_handlers(self, event_type: Optional[EventType] = None) -> None:
        """
        Clear all handlers for an event type or all event types.
        
        Args:
            event_type: Specific type to clear, or None for all
        """
        if event_type:
            self._handlers[event_type].clear()
            self._global_handlers[event_type].clear()
        else:
            for et in EventType:
                self._handlers[et].clear()
                self._global_handlers[et].clear()
        
        logger.info(f"Handlers cleared for {event_type or 'all events'}")
    
    def get_event_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[Event]:
        """
        Get recent event history.
        
        Args:
            event_type: Filter by event type
            limit: Maximum number of events
            
        Returns:
            List of recent events
        """
        events = self._event_history
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:]
    
    def list_handlers(self, event_type: Optional[EventType] = None) -> Dict[str, List[str]]:
        """
        List all registered handlers.
        
        Args:
            event_type: Filter by event type
            
        Returns:
            Dictionary mapping event names to handler names
        """
        result = {}
        types_to_check = [event_type] if event_type else list(EventType)
        
        for et in types_to_check:
            for name, handlers in self._handlers[et].items():
                key = f"{et.value}:{name}"
                result[key] = [h.__name__ for h in handlers]
        
        return result


# Global event manager instance
event_manager = EventManager()


__all__ = [
    "EventManager",
    "EventType",
    "Event",
    "ToolEvent",
    "event_manager",
]
