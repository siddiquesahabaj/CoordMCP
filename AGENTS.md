# AGENTS.md

Instructions for AI coding agents (like OpenCode, Cursor, Claude Code) working on the CoordMCP codebase.

## Project Overview

CoordMCP is a FastMCP-based Model Context Protocol server for multi-agent code coordination. It provides:
- Long-term memory for projects (decisions, tech stack, changes)
- Multi-agent context management and file locking
- Architecture guidance with rule-based pattern recommendations
- Task management and agent messaging
- Zero external API calls - all analysis is local

## Build & Test Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run all tests
python -m pytest src/tests/ -v

# Run unit tests only
python -m pytest src/tests/unit/ -v -m unit

# Run integration tests
python -m pytest src/tests/ -v -m integration

# Run end-to-end tests
python -m pytest src/tests/e2e/ -v

# Run with coverage
python -m pytest src/tests/ --cov=coordmcp --cov-report=html

# Run specific test file
python -m pytest src/tests/unit/test_memory/test_json_store.py -v

# Run server locally
python -m coordmcp

# Check version
coordmcp --version
```

## Code Style

- **Python Version**: 3.10+ (uses modern type hints)
- **Formatting**: Follow PEP 8
- **Type Hints**: Required on all public functions
- **Docstrings**: Google-style docstrings with examples
- **Line Length**: 100 characters max
- **Imports**: Absolute imports from `coordmcp.*`

### Example Function

```python
async def save_decision(
    title: str,
    description: str,
    rationale: str,
    project_id: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Save an architectural decision to project memory.
    
    Args:
        title: Decision title (e.g., "Use PostgreSQL")
        description: Detailed description
        rationale: Why this decision was made
        project_id: Project ID (optional if resolved by context)
        tags: Categorization tags
        
    Returns:
        Dictionary with decision_id and success status
        
    Example:
        result = await save_decision(
            title="Use FastAPI",
            description="FastAPI for REST API",
            rationale="Async support, type hints, auto docs"
        )
    """
```

## Project Structure

```
src/coordmcp/
├── main.py                 # Entry point, server creation
├── config.py               # Configuration management
├── logger.py               # Logging setup
├── plugins.py              # Plugin system (@tool, @resource decorators)
├── events.py               # Event system (hooks)
│
├── core/
│   ├── server.py           # FastMCP server setup
│   ├── tool_manager.py     # Tool registration
│   └── resource_manager.py # Resource registration
│
├── tools/                  # 52 MCP tools organized by category
│   ├── discovery_tools.py  # 4 tools: discover_project, get_project, list_projects, get_active_agents
│   ├── memory_tools.py     # 12 tools: projects, decisions, tech_stack, changes, files
│   ├── context_tools.py    # 13 tools: agents, context, file locking
│   ├── task_tools.py       # 8 tools: CRUD for tasks
│   ├── message_tools.py    # 5 tools: agent messaging
│   ├── architecture_tools.py # 5 tools: analysis, recommendations
│   ├── health_tools.py     # 1 tool: project dashboard
│   └── onboarding_tools.py # 4 tools: context, workflow, validation, system prompt
│
├── memory/
│   ├── json_store.py       # Storage operations
│   └── models.py           # Pydantic data models
│
├── context/
│   ├── manager.py          # Context lifecycle
│   ├── file_tracker.py     # File locking
│   └── state.py            # State models
│
├── architecture/
│   ├── analyzer.py         # Project analysis
│   ├── recommender.py      # Pattern recommendations
│   ├── validators.py       # Code validation
│   └── patterns.py         # 9 design patterns
│
├── storage/
│   ├── base.py             # Abstract storage interface
│   └── json_adapter.py     # JSON implementation
│
├── resources/              # 14 MCP resources
│   ├── project_resources.py
│   ├── agent_resources.py
│   └── architecture_resources.py
│
├── utils/
│   ├── project_resolver.py # Project ID resolution
│   ├── error_handler.py    # Error handling
│   └── validation.py       # Input validation
│
└── errors/
    └── __init__.py         # Exception definitions
```

## Key Conventions

### Tool Implementation Pattern

All tools follow this pattern:

```python
async def tool_name(
    required_param: str,
    optional_param: Optional[str] = None,
    project_id: Optional[str] = None,
    project_name: Optional[str] = None,
    workspace_path: Optional[str] = None
) -> Dict[str, Any]:
    """Docstring with examples."""
    try:
        # 1. Resolve project if needed
        success, resolved_id, message = resolve_project_id(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
        if not success:
            return {"success": False, "error": message, "error_type": "ProjectNotFound"}
        
        # 2. Get storage/context
        store = get_memory_store()
        
        # 3. Perform operation
        result = store.do_something(resolved_id)
        
        # 4. Return consistent format
        return {
            "success": True,
            "data": result,
            "message": "Operation completed"
        }
    except Exception as e:
        logger.error(f"Error in tool_name: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }
```

### Response Format

All tools return consistent format:

```python
# Success
{"success": True, "data": {...}, "message": "..."}

# Error
{"success": False, "error": "...", "error_type": "ErrorType"}
```

### Error Types

- `ProjectNotFound` - Project doesn't exist
- `AgentNotFound` - Agent not registered
- `FileLockConflict` - File locked by another agent
- `ValidationError` - Invalid input parameters
- `InternalError` - Server error

### Flexible Project Lookup

Most tools accept any of these:
- `project_id` - Exact ID (highest priority)
- `workspace_path` - Directory path
- `project_name` - Project name (lowest priority)

Priority: `project_id` > `workspace_path` > `project_name`

## Data Storage

All data stored in `~/.coordmcp/data/`:

```
~/.coordmcp/
├── data/
│   ├── memory/{project_id}/
│   │   ├── project_info.json
│   │   ├── decisions.json
│   │   ├── tech_stack.json
│   │   ├── changes.json
│   │   ├── file_metadata.json
│   │   └── tasks.json
│   ├── agents/{agent_id}/
│   │   ├── context.json
│   │   └── locked_files.json
│   └── global/
│       ├── agent_registry.json
│       └── project_registry.json
└── logs/
    └── coordmcp.log
```

## Testing Guidelines

### Test Structure

```
src/tests/
├── conftest.py             # Shared fixtures
├── unit/                   # Unit tests
├── integration/            # Integration tests
└── e2e/                    # End-to-end tests
```

### Writing Tests

```python
import pytest
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.storage.json_adapter import JSONStorageBackend

@pytest.fixture
def memory_store(tmp_path):
    """Create a test memory store."""
    storage = JSONStorageBackend(str(tmp_path))
    return ProjectMemoryStore(storage)

def test_create_project(memory_store):
    """Test project creation."""
    project_id = memory_store.create_project(
        project_name="Test Project",
        workspace_path="/tmp/test"
    )
    assert project_id is not None
    assert memory_store.project_exists(project_id)
```

### Test Markers

```bash
@pytest.mark.unit           # Fast, isolated tests
@pytest.mark.integration    # Tests with real storage
@pytest.mark.e2e            # Full workflow tests
@pytest.mark.slow           # Long-running tests
```

## Adding New Tools

1. Create tool function in appropriate `tools/*.py` file
2. Follow the tool implementation pattern
3. Add to `tool_manager.py` registration
4. Add tests in `src/tests/`
5. Update API documentation

### Example: Adding a New Tool

```python
# In tools/new_tools.py
async def my_new_tool(project_id: str, param: str) -> Dict[str, Any]:
    """Description of what the tool does."""
    try:
        store = get_memory_store()
        result = store.do_something(project_id, param)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

# In core/tool_manager.py
from coordmcp.tools.new_tools import my_new_tool

def register_new_tools(server: FastMCP) -> FastMCP:
    @server.tool()
    async def my_new_tool(project_id: str, param: str):
        return await my_new_tool(project_id, param)
    return server
```

## PR Guidelines

1. **Tests**: All new code must have tests
2. **Type hints**: Required on all public functions
3. **Docstrings**: Required on all public functions
4. **Error handling**: Use try/except with proper error types
5. **No external API calls**: CoordMCP must remain local-only
6. **Backward compatibility**: Don't break existing tool signatures

## Debugging

```bash
# Enable debug logging
export COORDMCP_LOG_LEVEL=DEBUG
python -m coordmcp

# View logs
tail -f ~/.coordmcp/logs/coordmcp.log

# Search for errors
grep ERROR ~/.coordmcp/logs/coordmcp.log
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `COORDMCP_DATA_DIR` | `~/.coordmcp/data` | Data storage directory |
| `COORDMCP_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `COORDMCP_LOG_FILE` | `~/.coordmcp/logs/coordmcp.log` | Log file path |
| `COORDMCP_LOCK_TIMEOUT_HOURS` | `24` | Hours before file locks expire |
| `COORDMCP_MAX_FILE_LOCKS_PER_AGENT` | `100` | Max files per agent |

## Key Files to Understand

1. **`main.py`** - Entry point, server initialization
2. **`memory/json_store.py`** - Core storage operations
3. **`memory/models.py`** - All data models (Pydantic)
4. **`tools/context_tools.py`** - File locking and agent management
5. **`architecture/patterns.py`** - Design pattern definitions

## Common Tasks

### Add a new data model

1. Define in `memory/models.py` extending `BaseEntity`
2. Add storage methods in `memory/json_store.py`
3. Create tools in `tools/*.py`
4. Add tests

### Add a new design pattern

1. Add pattern definition in `architecture/patterns.py`
2. Update recommender logic in `architecture/recommender.py`
3. Add tests

### Add a new storage backend

1. Implement `StorageBackend` interface from `storage/base.py`
2. Create adapter in `storage/new_adapter.py`
3. Add configuration option
4. Add tests
