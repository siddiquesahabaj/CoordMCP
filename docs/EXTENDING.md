# CoordMCP Extension Guide

This guide covers the advanced features added to CoordMCP for extending and customizing its functionality.

## Table of Contents

- [Plugin System](#plugin-system)
- [Event System](#event-system)
- [Validation Decorators](#validation-decorators)
- [Creating Custom Tools](#creating-custom-tools)
- [Creating Custom Resources](#creating-custom-resources)
- [Best Practices](#best-practices)

---

## Plugin System

The plugin system allows you to extend CoordMCP with custom tools and resources.

### Basic Plugin Structure

```python
# my_plugin.py
from coordmcp.plugins import plugin_manager, tool, resource

PLUGIN_NAME = "My Plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "My custom CoordMCP plugin"

@tool
@plugin_manager.register_tool
async def my_custom_tool(project_id: str, data: str):
    """My custom tool that does something useful."""
    return {
        "success": True,
        "result": f"Processed {data} for project {project_id}"
    }

@resource("custom://{item_id}")
@plugin_manager.register_resource("custom://{item_id}")
async def my_custom_resource(item_id: str):
    """My custom resource."""
    return f"Custom resource data for {item_id}"
```

### Loading Plugins

```python
# In your main.py or configuration
from coordmcp.plugins import plugin_manager

# Load a single plugin
plugin_manager.load_plugin("my_plugin")

# Load all plugins from a directory
plugins = plugin_manager.load_plugins_from_directory("./plugins")

# List loaded plugins
print(plugin_manager.list_plugins())

# Get custom tools
custom_tools = plugin_manager.get_custom_tools()
```

### Plugin Manager API

```python
from coordmcp.plugins import plugin_manager

# Register a tool
@plugin_manager.register_tool
async def my_tool():
    pass

# Register a resource
@plugin_manager.register_resource("my-resource://{id}")
async def my_resource(id: str):
    pass

# Unregister
plugin_manager.unregister_tool("my_tool")
plugin_manager.unregister_resource("my-resource://{id}")
```

---

## Event System

The event system allows you to hook into tool execution and other system events.

### Before Tool Hooks

Use `before_tool` to add validation or preprocessing:

```python
from coordmcp.events import event_manager

@event_manager.before_tool("save_decision")
async def validate_decision(project_id: str, title: str, **kwargs):
    """Validate decision before saving."""
    if len(title) < 5:
        return {
            "success": False,
            "error": "Title must be at least 5 characters",
            "error_type": "ValidationError"
        }
    # Return None to allow the tool to execute
    return None
```

### After Tool Hooks

Use `after_tool` to add logging or post-processing:

```python
from coordmcp.events import event_manager
from coordmcp.logger import get_logger

logger = get_logger("my_hooks")

@event_manager.after_tool("save_decision")
async def log_decision(result: dict, **kwargs):
    """Log decision creation."""
    if result.get("success"):
        logger.info(f"Decision created: {result.get('decision_id')}")
        # Send notification, update metrics, etc.
```

### General Event Hooks

```python
from coordmcp.events import event_manager, EventType

@event_manager.on_event(EventType.CONTEXT_STARTED)
async def on_context_started(agent_id: str, project_id: str, **kwargs):
    """Called when an agent starts a context."""
    logger.info(f"Agent {agent_id} started working on {project_id}")

@event_manager.on_event(EventType.FILES_LOCKED)
async def on_files_locked(agent_id: str, files: list, **kwargs):
    """Called when files are locked."""
    logger.info(f"Agent {agent_id} locked {len(files)} files")
```

### Event Types

Available event types:

- `BEFORE_TOOL` - Before tool execution
- `AFTER_TOOL` - After tool execution
- `BEFORE_RESOURCE` - Before resource access
- `AFTER_RESOURCE` - After resource access
- `CONTEXT_STARTED` - When context is started
- `CONTEXT_ENDED` - When context is ended
- `FILES_LOCKED` - When files are locked
- `FILES_UNLOCKED` - When files are unlocked

---

## Validation Decorators

Use validation decorators to add input validation to tools.

### Required Fields

```python
from coordmcp.utils.validation import validate_required_fields

@validate_required_fields("project_id", "title", "description")
async def save_decision(project_id: str, title: str, description: str, **kwargs):
    # All required fields are guaranteed to be present
    pass
```

### UUID Validation

```python
from coordmcp.utils.validation import validate_project_id, validate_agent_id

@validate_project_id
async def get_project_info(project_id: str):
    # project_id is validated as UUID format
    pass
```

### Enum Validation

```python
from coordmcp.utils.validation import validate_enum_field

@validate_enum_field("status", ["active", "archived", "superseded", "all"])
async def get_project_decisions(project_id: str, status: str = "all"):
    # status is validated against allowed values
    pass
```

### File Path Validation

```python
from coordmcp.utils.validation import validate_file_path

@validate_file_path("file_path")
async def update_file_metadata(project_id: str, file_path: str):
    # file_path is validated for security (no path traversal)
    pass
```

### Length Validation

```python
from coordmcp.utils.validation import validate_length

@validate_length("title", min_length=5, max_length=100)
async def save_decision(title: str, **kwargs):
    # title length is validated
    pass
```

### Combining Validators

```python
from coordmcp.utils.validation import (
    validate_required_fields,
    validate_project_id,
    validate_enum_field
)

@validate_required_fields("project_id", "title", "description")
@validate_project_id
@validate_length("title", min_length=5, max_length=200)
async def save_decision(project_id: str, title: str, description: str, **kwargs):
    pass
```

---

## Creating Custom Tools

### Basic Custom Tool

```python
from coordmcp.tools.memory_tools import get_memory_store

async def my_custom_analysis_tool(project_id: str):
    """
    Custom tool that analyzes something specific.
    
    Args:
        project_id: Project ID to analyze
        
    Returns:
        Analysis results
    """
    store = get_memory_store()
    
    # Get project data
    project_info = store.get_project_info(project_id)
    decisions = store.get_all_decisions(project_id)
    
    # Perform custom analysis
    analysis = {
        "success": True,
        "project_name": project_info.project_name if project_info else None,
        "decision_count": len(decisions),
        "custom_metric": len(decisions) * 10
    }
    
    return analysis
```

### Registering in Tool Manager

```python
# In core/tool_manager.py, add to _register_memory_tools():

@server.tool()
async def my_custom_analysis_tool(project_id: str):
    """My custom analysis tool."""
    return await memory_tools.my_custom_analysis_tool(project_id)
```

---

## Creating Custom Resources

### Basic Custom Resource

```python
# In resources/custom_resources.py

async def handle_custom_resource(uri: str) -> str:
    """Handle custom:// resources."""
    # Parse URI
    parts = uri.replace("custom://", "").split("/")
    resource_id = parts[0]
    
    # Fetch data
    data = fetch_custom_data(resource_id)
    
    # Format as markdown
    return format_as_markdown(data)
```

### Registering in Resource Manager

```python
# In core/resource_manager.py, add to _register_custom_resources():

@server.resource("custom://{resource_id}")
async def custom_resource(resource_id: str):
    """Access custom resource."""
    return await handle_custom_resource(f"custom://{resource_id}")
```

---

## Best Practices

### 1. Error Handling

Always use the centralized exception classes:

```python
from coordmcp.errors import (
    ProjectNotFoundError,
    ValidationError,
    FileLockError
)

async def my_tool(project_id: str):
    if not project_exists(project_id):
        raise ProjectNotFoundError(project_id)
    
    try:
        result = do_something()
    except SomeException as e:
        raise ValidationError("field_name", str(e))
```

### 2. Logging

Use the centralized logger:

```python
from coordmcp.logger import get_logger

logger = get_logger("my_module")

logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
```

### 3. Type Hints

Always use type hints:

```python
from typing import Dict, List, Optional

async def my_tool(
    project_id: str,
    items: List[str],
    optional_param: Optional[str] = None
) -> Dict[str, Any]:
    pass
```

### 4. Documentation

Document your tools and resources:

```python
async def my_tool(project_id: str):
    """
    Short description of what the tool does.
    
    Longer description explaining:
    - What it does
    - When to use it
    - What it returns
    
    Args:
        project_id: Project ID (required)
        
    Returns:
        Dictionary with:
        - success: bool
        - data: Tool-specific data
        
    Example:
        >>> result = await my_tool("project-123")
        >>> print(result["data"])
    """
    pass
```

### 5. Testing

Write tests for custom tools:

```python
# tests/unit/test_custom_tools.py

import pytest
from coordmcp.tools import my_custom_tool

@pytest.mark.asyncio
async def test_my_custom_tool():
    result = await my_custom_tool("test-project")
    assert result["success"] is True
    assert "data" in result
```

---

## Examples

### Complete Plugin Example

```python
# plugins/my_plugin.py
"""
My Plugin for CoordMCP

This plugin adds custom analytics tools.
"""

from coordmcp.plugins import plugin_manager, tool, resource
from coordmcp.tools.memory_tools import get_memory_store
from coordmcp.events import event_manager
from coordmcp.logger import get_logger

logger = get_logger("plugins.my_plugin")

PLUGIN_NAME = "Analytics Plugin"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = "Advanced analytics for projects"


@tool
@plugin_manager.register_tool
async def analyze_decision_quality(project_id: str):
    """
    Analyze the quality of decisions in a project.
    
    Returns a score based on completeness of decisions.
    """
    store = get_memory_store()
    decisions = store.get_all_decisions(project_id)
    
    if not decisions:
        return {
            "success": True,
            "score": 0,
            "message": "No decisions found"
        }
    
    total_score = 0
    for decision in decisions:
        score = 0
        if decision.rationale:
            score += 25
        if decision.impact:
            score += 25
        if decision.tags:
            score += 25
        if decision.related_files:
            score += 25
        total_score += score
    
    avg_score = total_score / len(decisions)
    
    return {
        "success": True,
        "score": avg_score,
        "decision_count": len(decisions),
        "message": f"Average decision quality: {avg_score:.1f}%"
    }


@resource("analytics://{project_id}/summary")
@plugin_manager.register_resource("analytics://{project_id}/summary")
async def analytics_summary(project_id: str):
    """Get analytics summary for a project."""
    store = get_memory_store()
    
    project_info = store.get_project_info(project_id)
    decisions = store.get_all_decisions(project_id)
    changes = store.get_recent_changes(project_id, limit=50)
    
    summary = f"""# Analytics Summary

**Project:** {project_info.project_name if project_info else 'Unknown'}

## Statistics
- **Decisions:** {len(decisions)}
- **Recent Changes:** {len(changes)}

## Recent Activity
Last {len(changes)} changes recorded.
"""
    
    return summary


# Event hooks
@event_manager.after_tool("save_decision")
async def notify_on_decision(result: dict, **kwargs):
    """Log when decisions are saved."""
    if result.get("success"):
        logger.info(f"New decision saved: {result.get('decision_id')}")
```

---

## Further Reading

- [API Reference](API_REFERENCE.md) - Complete tool and resource reference
- [Architecture Guide](ARCHITECTURE.md) - System architecture details
- [Main README](../README.md) - General overview and quick start

## Support

- 📧 Email: support@coordmcp.dev
- 💬 Discord: [Join our community](https://discord.gg/coordmcp)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)
