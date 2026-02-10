"""
Plugin system for CoordMCP.

This module provides a foundation for custom tool plugins.
Plugins can be registered to extend CoordMCP functionality.

Example:
    # In your plugin file
    from coordmcp.plugins import plugin_manager
    
    @plugin_manager.register_tool
    async def my_custom_tool(project_id: str, data: str):
        return {"success": True, "result": "Processed"}
    
    # In main.py, register the plugin
    plugin_manager.load_plugin("my_plugin_module")
"""

import importlib
from typing import Dict, List, Callable, Any
from dataclasses import dataclass, field
from coordmcp.logger import get_logger

logger = get_logger("plugins")


@dataclass
class Plugin:
    """Represents a loaded plugin."""
    name: str
    version: str
    description: str
    tools: Dict[str, Callable] = field(default_factory=dict)
    resources: Dict[str, Callable] = field(default_factory=dict)
    
    def __post_init__(self):
        logger.info(f"Plugin '{self.name}' v{self.version} created")


class PluginManager:
    """
    Manager for CoordMCP plugins.
    
    Handles loading, registration, and management of custom plugins
    that extend CoordMCP functionality.
    """
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.custom_tools: Dict[str, Callable] = {}
        self.custom_resources: Dict[str, Callable] = {}
        logger.info("PluginManager initialized")
    
    def register_tool(self, func: Callable) -> Callable:
        """
        Decorator to register a custom tool.
        
        Args:
            func: Tool function to register
            
        Returns:
            The decorated function
            
        Example:
            @plugin_manager.register_tool
            async def my_tool(project_id: str):
                return {"success": True}
        """
        tool_name = func.__name__
        self.custom_tools[tool_name] = func
        logger.info(f"Custom tool registered: {tool_name}")
        return func
    
    def register_resource(self, uri_pattern: str):
        """
        Decorator to register a custom resource.
        
        Args:
            uri_pattern: Resource URI pattern (e.g., "custom://{param}")
            
        Returns:
            Decorator function
            
        Example:
            @plugin_manager.register_resource("custom://{id}")
            async def my_resource(id: str):
                return f"Resource {id}"
        """
        def decorator(func: Callable) -> Callable:
            self.custom_resources[uri_pattern] = func
            logger.info(f"Custom resource registered: {uri_pattern}")
            return func
        return decorator
    
    def load_plugin(self, module_path: str) -> Plugin:
        """
        Load a plugin from a module path.
        
        Args:
            module_path: Python module path (e.g., "plugins.my_plugin")
            
        Returns:
            Loaded Plugin instance
            
        Example:
            plugin = plugin_manager.load_plugin("coordmcp.plugins.custom")
        """
        try:
            # Import the module
            module = importlib.import_module(module_path)
            
            # Extract plugin metadata
            name = getattr(module, "PLUGIN_NAME", module_path.split(".")[-1])
            version = getattr(module, "PLUGIN_VERSION", "1.0.0")
            description = getattr(module, "PLUGIN_DESCRIPTION", "")
            
            # Create plugin instance
            plugin = Plugin(name=name, version=version, description=description)
            
            # Register any tools/resources defined in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if callable(attr) and hasattr(attr, "_is_coordmcp_tool"):
                    plugin.tools[attr_name] = attr
                    self.custom_tools[attr_name] = attr
                elif callable(attr) and hasattr(attr, "_is_coordmcp_resource"):
                    uri = getattr(attr, "_resource_uri", attr_name)
                    plugin.resources[uri] = attr
                    self.custom_resources[uri] = attr
            
            self.plugins[name] = plugin
            logger.info(f"Plugin '{name}' v{version} loaded successfully")
            return plugin
            
        except ImportError as e:
            logger.error(f"Failed to load plugin '{module_path}': {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading plugin '{module_path}': {e}")
            raise
    
    def load_plugins_from_directory(self, directory: str) -> List[Plugin]:
        """
        Load all plugins from a directory.
        
        Args:
            directory: Path to plugins directory
            
        Returns:
            List of loaded plugins
        """
        import os
        import glob
        
        plugins = []
        pattern = os.path.join(directory, "*.py")
        
        for file_path in glob.glob(pattern):
            if file_path.endswith("__init__.py"):
                continue
            
            # Convert file path to module path
            module_name = os.path.basename(file_path)[:-3]  # Remove .py
            try:
                plugin = self.load_plugin(f"coordmcp.plugins.{module_name}")
                plugins.append(plugin)
            except Exception as e:
                logger.warning(f"Failed to load plugin from {file_path}: {e}")
        
        return plugins
    
    def get_custom_tools(self) -> Dict[str, Callable]:
        """Get all registered custom tools."""
        return self.custom_tools.copy()
    
    def get_custom_resources(self) -> Dict[str, Callable]:
        """Get all registered custom resources."""
        return self.custom_resources.copy()
    
    def list_plugins(self) -> List[str]:
        """List names of all loaded plugins."""
        return list(self.plugins.keys())
    
    def unregister_tool(self, tool_name: str) -> bool:
        """
        Unregister a custom tool.
        
        Args:
            tool_name: Name of the tool to unregister
            
        Returns:
            True if unregistered, False if not found
        """
        if tool_name in self.custom_tools:
            del self.custom_tools[tool_name]
            logger.info(f"Custom tool unregistered: {tool_name}")
            return True
        return False
    
    def unregister_resource(self, uri_pattern: str) -> bool:
        """
        Unregister a custom resource.
        
        Args:
            uri_pattern: URI pattern of the resource
            
        Returns:
            True if unregistered, False if not found
        """
        if uri_pattern in self.custom_resources:
            del self.custom_resources[uri_pattern]
            logger.info(f"Custom resource unregistered: {uri_pattern}")
            return True
        return False


# Global plugin manager instance
plugin_manager = PluginManager()


def tool(func: Callable) -> Callable:
    """
    Decorator to mark a function as a CoordMCP tool.
    
    Use with plugin_manager.register_tool
    
    Example:
        @tool
        @plugin_manager.register_tool
        async def my_tool():
            pass
    """
    func._is_coordmcp_tool = True
    return func


def resource(uri_pattern: str):
    """
    Decorator to mark a function as a CoordMCP resource.
    
    Use with plugin_manager.register_resource
    
    Example:
        @resource("custom://{id}")
        @plugin_manager.register_resource("custom://{id}")
        async def my_resource(id: str):
            pass
    """
    def decorator(func: Callable) -> Callable:
        func._is_coordmcp_resource = True
        func._resource_uri = uri_pattern
        return func
    return decorator


__all__ = [
    "PluginManager",
    "Plugin",
    "plugin_manager",
    "tool",
    "resource",
]
