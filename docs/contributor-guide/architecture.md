# Architecture

System architecture and design of CoordMCP.

## System Overview

```
┌──────────────────────────────────────────────┐
│         EXTERNAL AGENTS                       │
│  (OpenCode, Cursor, Claude Code, Windsurf)   │
└──────────┬───────────────────────────────────┘
            │ FastMCP Protocol (stdio)
┌──────────▼───────────────────────────────────┐
│   FastMCP SERVER (main.py)                    │
│   ├── Tool Manager (52 tools)                 │
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

## Components

### FastMCP Server

Entry point that handles MCP protocol communication.

- **Location:** `src/coordmcp/main.py`, `src/coordmcp/core/server.py`
- **Responsibility:** Protocol handling, tool/resource registration

### Tool Manager

Registers and dispatches tool calls.

- **Location:** `src/coordmcp/core/tool_manager.py`
- **Tools:** `src/coordmcp/tools/`
- **Count:** 52 tools across 8 categories

### Resource Manager

Handles resource requests.

- **Location:** `src/coordmcp/core/resource_manager.py`
- **Resources:** `src/coordmcp/resources/`
- **Count:** 14 resources

### Memory System

Manages long-term project memory.

- **Location:** `src/coordmcp/memory/`
- **Components:**
  - `json_store.py` - Storage operations
  - `models.py` - Data models

### Context System

Manages agent contexts and file locking.

- **Location:** `src/coordmcp/context/`
- **Components:**
  - `manager.py` - Context lifecycle
  - `file_tracker.py` - File locking
  - `state.py` - State models

### Architecture System

Provides architectural guidance.

- **Location:** `src/coordmcp/architecture/`
- **Components:**
  - `analyzer.py` - Project analysis
  - `recommender.py` - Pattern recommendations
  - `validators.py` - Structure validation
  - `patterns.py` - Pattern definitions

### Storage Abstraction

Pluggable storage backend.

- **Location:** `src/coordmcp/storage/`
- **Components:**
  - `base.py` - Abstract interface
  - `json_adapter.py` - JSON implementation

## Design Principles

### 1. Modularity

Each subsystem is independent and can be tested in isolation.

```
memory/     ← No dependencies on context/
context/    ← Depends on memory/ for project lookups
architecture/ ← Depends on memory/ for project data
```

### 2. Extensibility

- **Agent types:** Add new types by updating enum
- **Storage backends:** Implement `StorageBackend` interface
- **Tools:** Add new tools in `tools/` directory
- **Patterns:** Add patterns in `patterns.py`

### 3. Simplicity

- No external LLM calls for recommendations
- Rule-based architecture analysis
- JSON file storage (pluggable)

### 4. Traceability

Every operation is:
- Timestamped
- Attributed to an agent
- Logged for debugging

### 5. Conflict Prevention

File locking ensures:
- Mutual exclusion on edits
- Visibility into locks
- Automatic timeout

## Data Flow

### Project Creation

```
create_project()
    ↓
validate_workspace_path()
    ↓
check_uniqueness()
    ↓
JSONStorageBackend.save()
    ↓
ProjectInfo created
```

### Decision Save

```
save_decision()
    ↓
resolve_project_id()
    ↓
Decision model created
    ↓
JSONStorageBackend.save()
    ↓
Index updated
```

### File Lock

```
lock_files()
    ↓
get_agent()
    ↓
check_conflicts()
    ↓
LockedFile created
    ↓
JSONStorageBackend.save()
```

## File Structure

```
src/coordmcp/
├── __init__.py
├── __main__.py           # Entry point
├── main.py               # Server initialization
├── config.py             # Configuration
├── logger.py             # Logging setup
├── errors.py             # Error definitions
│
├── core/
│   ├── server.py         # FastMCP setup
│   ├── tool_manager.py   # Tool registration
│   └── resource_manager.py
│
├── tools/
│   ├── discovery_tools.py    # 4 tools
│   ├── memory_tools.py       # 12 tools
│   ├── context_tools.py      # 13 tools
│   ├── architecture_tools.py # 5 tools
│   ├── task_tools.py         # 8 tools
│   ├── message_tools.py      # 5 tools
│   ├── health_tools.py       # 1 tool
│   └── onboarding_tools.py   # 4 tools
│
├── resources/
│   ├── project_resources.py
│   ├── agent_resources.py
│   └── architecture_resources.py
│
├── memory/
│   ├── json_store.py     # Storage operations
│   └── models.py         # Pydantic models
│
├── context/
│   ├── manager.py        # Context management
│   ├── file_tracker.py   # File locking
│   └── state.py          # State models
│
├── architecture/
│   ├── analyzer.py       # Analysis
│   ├── recommender.py    # Recommendations
│   ├── validators.py     # Validation
│   └── patterns.py       # Pattern definitions
│
├── storage/
│   ├── base.py           # Abstract interface
│   └── json_adapter.py   # JSON implementation
│
└── utils/
    ├── project_resolver.py
    ├── error_handler.py
    └── validation.py
```

## Key Technologies

| Technology | Purpose |
|------------|---------|
| Python 3.10+ | Core language |
| FastMCP | MCP protocol implementation |
| Pydantic | Data validation |
| pytest | Testing |
| JSON | Storage format |

## See Also

- [Development Setup](development-setup.md)
- [Extending CoordMCP](extending.md)
- [Testing](testing.md)
