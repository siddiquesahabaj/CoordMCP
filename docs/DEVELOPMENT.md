# CoordMCP Developer Guide

Complete guide for developers contributing to or extending CoordMCP.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Data Models](#data-models)
- [Tools Reference](#tools-reference)
- [Resources Reference](#resources-reference)
- [Development Setup](#development-setup)
- [Testing](#testing)
- [Contributing](#contributing)
- [Extending CoordMCP](#extending-coordmcp)

## Architecture Overview

### System Architecture

```
┌──────────────────────────────────────────────┐
│         EXTERNAL AGENTS                       │
│  (OpenCode, Cursor, Claude Code, Windsurf)   │
└──────────┬───────────────────────────────────┘
           │ FastMCP Protocol
┌──────────▼───────────────────────────────────┐
│   FastMCP SERVER (main.py)                    │
│   ├── Tool Manager (33 tools)                 │
│   └── Resource Manager (14 resources)         │
└──────────┬───────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────┐
│   BUSINESS LOGIC                              │
│   ├── Memory System (json_store.py)           │
│   ├── Context System (manager.py)             │
│   └── Architecture System (analyzer.py)       │
└──────────┬───────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────┐
│   STORAGE ABSTRACTION                         │
│   └── JSONStorageBackend (json_adapter.py)    │
└──────────┬───────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────┐
│   DATA STORAGE (~/.coordmcp/data)             │
│   ├── memory/{project_id}/                    │
│   ├── agents/{agent_id}/                      │
│   └── global/                                 │
└──────────────────────────────────────────────┘
```

### Design Principles

1. **Modularity**: Each subsystem (memory, context, architecture) is independent
2. **Extensibility**: Agent types are extensible, storage backends are pluggable
3. **Simplicity**: No external LLM calls for recommendations (rule-based logic)
4. **Traceability**: Every decision, change, and recommendation is timestamped and logged
5. **Conflict Prevention**: File locking prevents simultaneous edits

### Key Technologies

- **Python 3.10+** - Core language
- **FastMCP** - MCP protocol implementation
- **Pydantic** - Data validation and models
- **pytest** - Testing framework
- **JSON** - Storage format (pluggable)

## Project Structure

```
coordmcp/
├── src/coordmcp/
│   ├── __init__.py
│   ├── __main__.py           # Entry point
│   ├── main.py               # Main server logic
│   ├── config.py             # Configuration management
│   ├── logger.py             # Logging setup
│   ├── events.py             # Event system
│   ├── plugins.py            # Plugin system
│   │
│   ├── core/                 # Core functionality
│   │   ├── server.py         # FastMCP server setup
│   │   ├── tool_manager.py   # Tool registration
│   │   └── resource_manager.py # Resource registration
│   │
│   ├── memory/               # Long-term memory system
│   │   ├── json_store.py     # Project memory storage
│   │   └── models.py         # Data models
│   │
│   ├── context/              # Multi-agent context management
│   │   ├── manager.py        # Context manager
│   │   ├── state.py          # Context state models
│   │   └── file_tracker.py   # File locking & tracking
│   │
│   ├── architecture/         # Architectural guidance
│   │   ├── analyzer.py       # Architecture analyzer
│   │   ├── recommender.py    # Structure recommendations
│   │   ├── validators.py     # Code structure validators
│   │   └── patterns.py       # Design patterns reference
│   │
│   ├── tools/                # FastMCP Tool implementations
│   │   ├── memory_tools.py   # Memory CRUD operations
│   │   ├── context_tools.py  # Context switching tools
│   │   ├── architecture_tools.py # Architecture tools
│   │   └── discovery_tools.py # Project discovery tools
│   │
│   ├── resources/            # FastMCP Resource implementations
│   │   ├── project_resources.py
│   │   ├── agent_resources.py
│   │   └── architecture_resources.py
│   │
│   ├── storage/              # Storage abstraction
│   │   ├── base.py           # Abstract storage interface
│   │   └── json_adapter.py   # JSON adapter
│   │
│   ├── utils/                # Utilities
│   │   ├── project_resolver.py
│   │   ├── error_handler.py
│   │   └── validation.py
│   │
│   └── errors/               # Error definitions
│       └── __init__.py
│
├── src/tests/                # Test suite
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
│
├── docs/                     # Documentation
├── examples/                 # Usage examples
└── pyproject.toml           # Project configuration
```

## Data Models

### Project Memory Models

#### Decision

```python
class Decision(BaseModel):
    id: str
    timestamp: datetime
    title: str
    description: str
    context: str
    rationale: str
    impact: str
    status: DecisionStatus  # active, archived, superseded
    related_files: List[str]
    author_agent_id: str
    tags: List[str]
```

#### TechStackEntry

```python
class TechStackEntry(BaseModel):
    category: str  # backend, frontend, database, infrastructure
    technology: str
    version: str
    rationale: str
    decision_ref: Optional[str]
```

#### Change

```python
class Change(BaseModel):
    id: str
    timestamp: datetime
    file_path: str
    change_type: ChangeType  # create, modify, delete, refactor
    description: str
    agent_id: str
    architecture_impact: ArchitectureImpact  # none, minor, significant
    related_decision: Optional[str]
    code_summary: str
```

#### FileMetadata

```python
class FileMetadata(BaseModel):
    id: str
    path: str
    file_type: FileType  # source, test, config, doc
    last_modified: datetime
    last_modified_by: str
    module: str
    purpose: str
    dependencies: List[str]
    dependents: List[str]
    lines_of_code: int
    complexity: Complexity  # low, medium, high
```

### Agent Context Models

```python
class AgentProfile(BaseModel):
    agent_id: str
    agent_name: str
    agent_type: AgentType  # opencode, cursor, claude_code, custom
    version: str
    capabilities: List[str]
    last_active: datetime
    total_sessions: int
    projects_involved: List[str]
    status: AgentStatus  # active, inactive, deprecated

class AgentContext(BaseModel):
    agent_id: str
    current_context: Optional[Context]
    locked_files: List[LockedFile]
    recent_context: List[ContextEntry]
    session_log: List[SessionLogEntry]

class Context(BaseModel):
    project_id: str
    current_objective: str
    current_file: str
    task_description: str
    priority: Priority  # critical, high, medium, low
    started_at: datetime
    estimated_completion: datetime
```

## Tools Reference

### Discovery Tools (4)

1. **discover_project** - Find project by directory path
2. **get_project** - Get project by ID/name/path
3. **list_projects** - List all projects
4. **get_active_agents** - Get active agents

### Memory Tools (11)

1. **create_project** - Create new project (requires workspace_path)
2. **get_project_info** - Get project information
3. **save_decision** - Save architectural decision
4. **get_project_decisions** - Get project decisions
5. **search_decisions** - Search decisions
6. **update_tech_stack** - Update technology stack
7. **get_tech_stack** - Get technology stack
8. **log_change** - Log code changes
9. **get_recent_changes** - Get recent changes
10. **update_file_metadata** - Update file metadata
11. **get_file_dependencies** - Get file dependencies
12. **get_module_info** - Get module information

### Context Tools (13)

1. **register_agent** - Register/reconnect agent
2. **get_agents_list** - List all agents
3. **get_agent_profile** - Get agent profile
4. **start_context** - Start work context
5. **get_agent_context** - Get agent context
6. **switch_context** - Switch context
7. **end_context** - End context
8. **lock_files** - Lock files
9. **unlock_files** - Unlock files
10. **get_locked_files** - Get locked files
11. **get_context_history** - Get context history
12. **get_session_log** - Get session log
13. **get_agents_in_project** - Get agents in project

### Architecture Tools (5)

1. **analyze_architecture** - Analyze project architecture
2. **get_architecture_recommendation** - Get recommendations
3. **validate_code_structure** - Validate code structure
4. **get_design_patterns** - Get design patterns
5. **update_architecture** - Update architecture

## Resources Reference

### Project Resources

- `project://{project_id}` - Project overview
- `project://{project_id}/decisions` - Project decisions
- `project://{project_id}/tech-stack` - Technology stack
- `project://{project_id}/architecture` - Architecture overview
- `project://{project_id}/recent-changes` - Recent changes
- `project://{project_id}/modules` - Module list
- `project://{project_id}/modules/{module_name}` - Module details

### Agent Resources

- `agent://{agent_id}` - Agent profile
- `agent://{agent_id}/context` - Agent context
- `agent://{agent_id}/locked-files` - Locked files
- `agent://{agent_id}/session-log` - Session log
- `agent://registry` - Agent registry

### Architecture Resources

- `design-patterns://list` - List all patterns
- `design-patterns://{pattern_name}` - Pattern details

## Development Setup

### Prerequisites

- Python 3.10+
- pip
- git

### Setup Steps

```bash
# Clone repository
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
python -m pytest src/tests/ -v
```

### Environment Variables

```bash
export COORDMCP_DATA_DIR="~/.coordmcp/data"
export COORDMCP_LOG_LEVEL="DEBUG"
export COORDMCP_MAX_FILE_LOCKS_PER_AGENT="100"
export COORDMCP_LOCK_TIMEOUT_HOURS="24"
export COORDMCP_ENABLE_COMPRESSION="false"
```

## Testing

### Test Structure

```
src/tests/
├── unit/                   # Unit tests
│   ├── test_memory/
│   ├── test_context/
│   ├── test_architecture/
│   ├── test_core/
│   ├── test_tools/
│   └── test_utils/
├── integration/            # Integration tests
├── e2e/                   # End-to-end tests
└── fixtures/              # Test data
```

### Running Tests

```bash
# Run all tests
python -m pytest src/tests/ -v

# Run specific test file
python -m pytest src/tests/unit/test_memory/test_json_store.py -v

# Run with coverage
python -m pytest src/tests/ --cov=coordmcp --cov-report=html

# Run specific markers
python -m pytest -m unit
python -m pytest -m integration
python -m pytest -m e2e
```

### Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow tests

## Contributing

### Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run tests
6. Submit a pull request

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Keep functions focused

### Commit Messages

```
feat: Add new tool for X
fix: Fix issue with Y
docs: Update documentation
refactor: Improve code structure
test: Add tests for Z
```

## Extending CoordMCP

### Adding a New Tool

```python
# In tools/my_tools.py
from coordmcp.core.server import get_storage

async def my_new_tool(param1: str, param2: int):
    """
    Description of what the tool does.
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Dictionary with results
    """
    storage = get_storage()
    # Implementation
    return {"success": True, "result": ...}

# Register in core/tool_manager.py
def register_all_tools(server: FastMCP) -> FastMCP:
    @server.tool()
    async def my_tool(param1: str, param2: int = 0):
        return await my_new_tool(param1, param2)
```

### Adding a New Resource

```python
# In resources/my_resources.py
async def handle_my_resource(uri: str) -> str:
    """Handle resource requests."""
    parts = uri.split("://")[1].split("/")
    # Parse URI and return content
    return "Resource content"

# Register in core/resource_manager.py
def register_all_resources(server: FastMCP) -> FastMCP:
    @server.resource("my-resource://{id}")
    async def my_resource(id: str):
        return await handle_my_resource(f"my-resource://{id}")
```

### Custom Storage Backend

```python
# In storage/custom_adapter.py
from coordmcp.storage.base import StorageBackend

class CustomStorageBackend(StorageBackend):
    def __init__(self, connection_string: str):
        self.connection = connect(connection_string)
    
    def save(self, key: str, data: Dict) -> bool:
        # Implementation
        pass
    
    def load(self, key: str) -> Optional[Dict]:
        # Implementation
        pass
    
    def delete(self, key: str) -> bool:
        # Implementation
        pass
    
    def exists(self, key: str) -> bool:
        # Implementation
        pass
    
    def list_keys(self, prefix: str) -> List[str]:
        # Implementation
        pass
```

### Design Patterns Reference

Available patterns in `architecture/patterns.py`:

- **CRUD** - Basic create, read, update, delete
- **MVC** - Model-View-Controller
- **Repository** - Data access abstraction
- **Service** - Business logic layer
- **Factory** - Object creation pattern
- **Observer** - Event-driven architecture
- **Adapter** - Interface adaptation
- **Strategy** - Algorithm selection
- **Decorator** - Extend functionality

---

For more information, see the [API Reference](API_REFERENCE.md) and [Contributing Guide](../CONTRIBUTING.md).
