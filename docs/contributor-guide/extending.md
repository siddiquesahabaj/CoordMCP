# Extending CoordMCP

How to add new tools, resources, and storage backends.

## Adding a New Tool

### 1. Create Tool Function

In `src/coordmcp/tools/` (or create new file):

```python
# src/coordmcp/tools/my_tools.py
from typing import Dict, Any
from coordmcp.core.server import get_storage
from coordmcp.logger import get_logger

logger = get_logger("tools.my_tools")

async def my_new_tool(
    param1: str,
    param2: int = 10
) -> Dict[str, Any]:
    """
    Brief description of what the tool does.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)
        
    Returns:
        Dictionary with results
    """
    try:
        storage = get_storage()
        
        # Your implementation here
        result = do_something(param1, param2)
        
        return {
            "success": True,
            "result": result,
            "message": "Operation completed"
        }
    except Exception as e:
        logger.error(f"Error in my_new_tool: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }
```

### 2. Register Tool

In `src/coordmcp/core/tool_manager.py`:

```python
from coordmcp.tools.my_tools import my_new_tool

def register_all_tools(server: FastMCP) -> FastMCP:
    # ... existing tools ...
    
    @server.tool()
    async def coordmcp_my_new_tool(
        param1: str,
        param2: int = 10
    ):
        """Brief description for MCP."""
        return await my_new_tool(param1, param2)
    
    return server
```

### 3. Add Tests

```python
# src/tests/unit/test_tools/test_my_tools.py
import pytest
from coordmcp.tools.my_tools import my_new_tool

class TestMyNewTool:
    @pytest.mark.asyncio
    async def test_basic_operation(self):
        result = await my_new_tool("test", 5)
        assert result["success"] is True
```

---

## Adding a New Resource

### 1. Create Resource Handler

In `src/coordmcp/resources/`:

```python
# src/coordmcp/resources/my_resources.py
from coordmcp.logger import get_logger

logger = get_logger("resources.my_resources")

async def handle_my_resource(uri: str) -> str:
    """
    Handle resource requests.
    
    Args:
        uri: Resource URI (e.g., "my-resource://id")
        
    Returns:
        Resource content as string
    """
    # Parse URI
    parts = uri.split("://")[1].split("/")
    resource_id = parts[0]
    
    # Get data
    content = get_resource_content(resource_id)
    
    return content
```

### 2. Register Resource

In `src/coordmcp/core/resource_manager.py`:

```python
from coordmcp.resources.my_resources import handle_my_resource

def register_all_resources(server: FastMCP) -> FastMCP:
    # ... existing resources ...
    
    @server.resource("my-resource://{id}")
    async def my_resource(id: str):
        return await handle_my_resource(f"my-resource://{id}")
    
    return server
```

---

## Adding a Storage Backend

### 1. Implement Interface

```python
# src/coordmcp/storage/custom_adapter.py
from typing import Dict, List, Optional
from coordmcp.storage.base import StorageBackend

class CustomStorageBackend(StorageBackend):
    """Custom storage backend implementation."""
    
    def __init__(self, connection_string: str):
        """Initialize with connection string."""
        self.connection = connect(connection_string)
    
    def save(self, key: str, data: Dict) -> bool:
        """Save data to storage."""
        try:
            self.connection.set(key, data)
            return True
        except Exception:
            return False
    
    def load(self, key: str) -> Optional[Dict]:
        """Load data from storage."""
        return self.connection.get(key)
    
    def delete(self, key: str) -> bool:
        """Delete data from storage."""
        try:
            self.connection.delete(key)
            return True
        except Exception:
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        return self.connection.exists(key)
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with prefix."""
        return self.connection.keys(f"{prefix}*")
```

### 2. Register Backend

In `src/coordmcp/core/server.py`:

```python
def get_storage() -> StorageBackend:
    """Get storage backend based on configuration."""
    backend_type = os.getenv("COORDMCP_STORAGE_BACKEND", "json")
    
    if backend_type == "custom":
        from coordmcp.storage.custom_adapter import CustomStorageBackend
        return CustomStorageBackend(os.getenv("COORDMCP_CONNECTION_STRING"))
    else:
        from coordmcp.storage.json_adapter import JSONStorageBackend
        return JSONStorageBackend(get_data_dir())
```

---

## Adding Design Patterns

In `src/coordmcp/architecture/patterns.py`:

```python
PATTERNS = {
    # ... existing patterns ...
    
    "my_pattern": {
        "description": "Description of the pattern",
        "best_for": ["Use case 1", "Use case 2"],
        "structure": {
            "components": ["Component1", "Component2"],
            "file_suggestions": ["src/component1.py", "src/component2.py"]
        },
        "example": """
# Example code
class Component1:
    pass
        """,
        "best_practices": [
            "Practice 1",
            "Practice 2"
        ]
    }
}
```

---

## Adding Agent Types

In `src/coordmcp/context/models.py`:

```python
class AgentType(str, Enum):
    OPENCODE = "opencode"
    CURSOR = "cursor"
    CLAUDE_CODE = "claude_code"
    WINDSURF = "windsurf"
    MY_AGENT = "my_agent"  # Add new type
    CUSTOM = "custom"
```

Update validation in `context_tools.py`:

```python
valid_agent_types = [
    "opencode", 
    "cursor", 
    "claude_code",
    "windsurf",
    "my_agent",  # Add new type
    "custom"
]
```

---

## Best Practices

1. **Follow existing patterns** - Look at similar tools/resources
2. **Add docstrings** - Document purpose and parameters
3. **Handle errors** - Return consistent error format
4. **Log operations** - Use the logger
5. **Write tests** - Unit and integration tests
6. **Update docs** - Add to API reference

## See Also

- [Architecture](architecture.md) - System design
- [Testing](testing.md) - How to test
- [API Reference](../developer-guide/api-reference.md) - Existing tools
