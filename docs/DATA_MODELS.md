# CoordMCP Data Structure Documentation

This document describes the complete data structure and storage organization used by CoordMCP.

## Overview

CoordMCP stores all data in JSON format in the user's home directory at `~/.coordmcp/data/`. The data is organized hierarchically by projects and agents, with a global registry for system-wide information.

## Directory Structure

```
~/.coordmcp/data/
├── memory/                          # Project-specific memory storage
│   └── {project_id}/               # One directory per project (UUID format)
│       ├── project_info.json       # Project metadata
│       ├── decisions.json          # Architectural decisions
│       ├── tech_stack.json         # Technology stack
│       ├── changes.json            # Recent changes log
│       ├── file_metadata.json      # File tracking information
│       └── architecture.json       # Architecture definition
│
├── agents/                          # Agent-specific data
│   └── {agent_id}/                 # One directory per agent (UUID format)
│       ├── context.json            # Current working context
│       ├── locked_files.json       # Files locked by this agent
│       └── session_log.json        # Activity and session history
│
├── global/                          # System-wide data
│   └── agent_registry.json         # Global registry of all agents
│
└── logs/                           # Application logs
    └── coordmcp.log               # Main application log file
```

## File Formats

### 1. Project Info (`memory/{project_id}/project_info.json`)

Stores basic project metadata.

**Schema:**
```json
{
  "project_id": "string (UUID)",
  "project_name": "string (required)",
  "description": "string (optional)",
  "workspace_path": "string (required - absolute path)",
  "created_at": "string (ISO 8601 datetime)",
  "last_updated": "string (ISO 8601 datetime)",
  "version": "string (default: 1.0.0)"
}
```

**Example:**
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "project_name": "E-Commerce Platform",
  "description": "Modern e-commerce solution with microservices",
  "workspace_path": "/home/user/projects/ecommerce",
  "created_at": "2026-02-10T10:30:00",
  "last_updated": "2026-02-10T15:45:00",
  "version": "1.0.0"
}
```

**Notes:**
- `workspace_path` must be an absolute path (not relative)
- This links the project to a specific directory for discovery
- Used by `discover_project()` tool to find projects

---

### 2. Decisions (`memory/{project_id}/decisions.json`)

Stores architectural and technical decisions.

**Schema:**
```json
{
  "decisions": {
    "{decision_id}": {
      "id": "string (UUID)",
      "timestamp": "string (ISO 8601 datetime)",
      "title": "string (required)",
      "description": "string (required)",
      "context": "string (optional)",
      "rationale": "string (required)",
      "impact": "string (optional)",
      "status": "string (active|archived|superseded)",
      "related_files": ["string (file paths)"],
      "author_agent": "string (agent UUID)",
      "tags": ["string"]
    }
  }
}
```

**Example:**
```json
{
  "decisions": {
    "dec-123e4567-e89b-12d3-a456-426614174000": {
      "id": "dec-123e4567-e89b-12d3-a456-426614174000",
      "timestamp": "2026-02-10T11:00:00",
      "title": "Use FastAPI for Backend",
      "description": "Adopt FastAPI as our primary web framework",
      "context": "Building REST API for the platform",
      "rationale": "High performance, automatic OpenAPI docs, type hints support",
      "impact": "All API endpoints will be built with FastAPI",
      "status": "active",
      "related_files": ["src/main.py", "requirements.txt"],
      "author_agent": "agent-uuid-here",
      "tags": ["backend", "framework", "api"]
    }
  }
}
```

---

### 3. Tech Stack (`memory/{project_id}/tech_stack.json`)

Stores technology choices by category.

**Schema:**
```json
{
  "tech_stack": {
    "{category}": {
      "category": "string (backend|frontend|database|infrastructure)",
      "technology": "string (required)",
      "version": "string (optional)",
      "rationale": "string (optional)",
      "decision_ref": "string (decision UUID)",
      "updated_at": "string (ISO 8601 datetime)"
    }
  }
}
```

**Example:**
```json
{
  "tech_stack": {
    "backend": {
      "category": "backend",
      "technology": "FastAPI",
      "version": "0.104.0",
      "rationale": "High performance async Python framework",
      "decision_ref": "dec-123e4567-e89b-12d3-a456-426614174000",
      "updated_at": "2026-02-10T11:00:00"
    },
    "database": {
      "category": "database",
      "technology": "PostgreSQL",
      "version": "15",
      "rationale": "Reliable relational database with ACID compliance",
      "decision_ref": "",
      "updated_at": "2026-02-10T11:30:00"
    }
  }
}
```

---

### 4. Changes (`memory/{project_id}/changes.json`)

Chronological log of all changes.

**Schema:**
```json
{
  "changes": [
    {
      "id": "string (UUID)",
      "timestamp": "string (ISO 8601 datetime)",
      "file_path": "string (required)",
      "change_type": "string (create|modify|delete|refactor)",
      "description": "string (required)",
      "code_summary": "string (optional)",
      "agent_id": "string (UUID)",
      "architecture_impact": "string (none|minor|significant)",
      "related_decision": "string (decision UUID)"
    }
  ]
}
```

**Example:**
```json
{
  "changes": [
    {
      "id": "chg-550e8400-e29b-41d4-a716-446655440000",
      "timestamp": "2026-02-10T14:20:00",
      "file_path": "src/api/auth.py",
      "change_type": "create",
      "description": "Created authentication endpoints",
      "code_summary": "Added login, logout, and token refresh endpoints",
      "agent_id": "agent-uuid-here",
      "architecture_impact": "significant",
      "related_decision": "dec-123e4567-e89b-12d3-a456-426614174000"
    }
  ]
}
```

---

### 5. File Metadata (`memory/{project_id}/file_metadata.json`)

Tracking information for project files.

**Schema:**
```json
{
  "files": {
    "{file_path}": {
      "path": "string (required)",
      "file_type": "string (source|test|config|doc)",
      "module": "string (optional)",
      "purpose": "string (optional)",
      "dependencies": ["string (file paths)"],
      "dependents": ["string (file paths)"],
      "lines_of_code": "integer",
      "complexity": "string (low|medium|high)",
      "last_modified_by": "string (agent UUID)",
      "last_modified_at": "string (ISO 8601 datetime)"
    }
  }
}
```

**Example:**
```json
{
  "files": {
    "src/main.py": {
      "path": "src/main.py",
      "file_type": "source",
      "module": "core",
      "purpose": "Application entry point",
      "dependencies": ["src/config.py", "src/api/routes.py"],
      "dependents": [],
      "lines_of_code": 50,
      "complexity": "low",
      "last_modified_by": "agent-uuid-here",
      "last_modified_at": "2026-02-10T14:20:00"
    }
  }
}
```

---

### 6. Architecture (`memory/{project_id}/architecture.json`)

Architecture definition and module structure.

**Schema:**
```json
{
  "architecture": {
    "overview": "string (description)",
    "pattern": "string (mvc|repository|microservices|etc)",
    "modules": {
      "{module_name}": {
        "name": "string",
        "purpose": "string",
        "files": ["string (file paths)"],
        "dependencies": ["string (module names)"],
        "responsibilities": ["string"]
      }
    },
    "updated_at": "string (ISO 8601 datetime)"
  }
}
```

**Example:**
```json
{
  "architecture": {
    "overview": "Clean Architecture with clear separation of concerns",
    "pattern": "clean_architecture",
    "modules": {
      "domain": {
        "name": "domain",
        "purpose": "Business entities and logic",
        "files": ["src/domain/models.py", "src/domain/services.py"],
        "dependencies": [],
        "responsibilities": ["Define entities", "Business rules"]
      },
      "api": {
        "name": "api",
        "purpose": "API endpoints and controllers",
        "files": ["src/api/routes.py", "src/api/middleware.py"],
        "dependencies": ["domain"],
        "responsibilities": ["Handle HTTP requests", "Input validation"]
      }
    },
    "updated_at": "2026-02-10T16:00:00"
  }
}
```

---

### 7. Agent Context (`agents/{agent_id}/context.json`)

Current working context for an agent.

**Schema:**
```json
{
  "agent_id": "string (UUID)",
  "current_context": {
    "project_id": "string (UUID)",
    "current_objective": "string",
    "task_description": "string",
    "priority": "string (critical|high|medium|low)",
    "current_file": "string (file path)",
    "started_at": "string (ISO 8601 datetime)"
  },
  "locked_files": [
    {
      "file_path": "string",
      "locked_at": "string (ISO 8601 datetime)",
      "reason": "string",
      "expected_unlock_time": "string (ISO 8601 datetime)"
    }
  ],
  "history": [
    {
      "timestamp": "string (ISO 8601 datetime)",
      "operation": "string",
      "file": "string",
      "summary": "string"
    }
  ]
}
```

**Example:**
```json
{
  "agent_id": "agent-550e8400-e29b-41d4-a716-446655440000",
  "current_context": {
    "project_id": "proj-123e4567-e89b-12d3-a456-426614174000",
    "current_objective": "Implement user authentication",
    "task_description": "Create login and registration endpoints",
    "priority": "high",
    "current_file": "src/api/auth.py",
    "started_at": "2026-02-10T14:00:00"
  },
  "locked_files": [
    {
      "file_path": "src/api/auth.py",
      "locked_at": "2026-02-10T14:05:00",
      "reason": "Implementing authentication endpoints",
      "expected_unlock_time": "2026-02-10T15:05:00"
    }
  ],
  "history": []
}
```

---

### 8. Locked Files (`agents/{agent_id}/locked_files.json`)

Files currently locked by the agent (alternative view).

**Schema:**
```json
{
  "{project_id}": {
    "{file_path}": {
      "file_path": "string",
      "locked_by": "string (agent UUID)",
      "locked_at": "string (ISO 8601 datetime)",
      "reason": "string",
      "expected_duration_minutes": "integer",
      "expected_unlock_time": "string (ISO 8601 datetime)"
    }
  }
}
```

---

### 9. Session Log (`agents/{agent_id}/session_log.json`)

Activity log for the agent.

**Schema:**
```json
{
  "entries": [
    {
      "timestamp": "string (ISO 8601 datetime)",
      "event": "string (context_started|context_switched|files_locked|decision_saved|etc)",
      "details": {
        "project_id": "string (optional)",
        "objective": "string (optional)",
        "files": ["string"] (optional),
        "decision_id": "string (optional)"
      }
    }
  ]
}
```

**Example:**
```json
{
  "entries": [
    {
      "timestamp": "2026-02-10T14:00:00",
      "event": "context_started",
      "details": {
        "project_id": "proj-123e4567-e89b-12d3-a456-426614174000",
        "objective": "Implement user authentication"
      }
    },
    {
      "timestamp": "2026-02-10T14:05:00",
      "event": "files_locked",
      "details": {
        "files": ["src/api/auth.py"],
        "reason": "Implementing authentication"
      }
    }
  ]
}
```

---

### 10. Agent Registry (`global/agent_registry.json`)

Global registry of all agents.

**Schema:**
```json
{
  "agents": {
    "{agent_id}": {
      "agent_id": "string (UUID)",
      "agent_name": "string",
      "agent_type": "string (opencode|cursor|claude_code|custom)",
      "capabilities": ["string"],
      "version": "string",
      "last_active": "string (ISO 8601 datetime)",
      "total_sessions": "integer",
      "projects_involved": ["string (project UUIDs)"],
      "status": "string (active|inactive|deprecated)"
    }
  },
  "updated_at": "string (ISO 8601 datetime)"
}
```

**Example:**
```json
{
  "agents": {
    "agent-550e8400-e29b-41d4-a716-446655440000": {
      "agent_id": "agent-550e8400-e29b-41d4-a716-446655440000",
      "agent_name": "FrontendDev",
      "agent_type": "opencode",
      "capabilities": ["react", "typescript", "css"],
      "version": "1.0.0",
      "last_active": "2026-02-10T14:30:00",
      "total_sessions": 42,
      "projects_involved": ["proj-123e4567-e89b-12d3-a456-426614174000"],
      "status": "active"
    }
  },
  "updated_at": "2026-02-10T16:00:00"
}
```

---

## Data Access Patterns

### Storage Backend Interface

All data access goes through the `StorageBackend` abstraction:

```python
from coordmcp.storage.json_adapter import JSONStorageBackend

storage = JSONStorageBackend(data_dir)

# Save data
storage.save("memory/{project_id}/decisions", data)

# Load data
data = storage.load("memory/{project_id}/decisions")

# Check existence
exists = storage.exists("memory/{project_id}/decisions")

# Delete
deleted = storage.delete("memory/{project_id}/decisions")
```

### Atomic Writes

All writes are atomic using temp files:
1. Write to temporary file
2. Rename to target file (atomic operation)
3. This prevents data corruption on crashes

---

## Data Lifecycle

### Project Creation
1. Create directory `memory/{project_id}/`
2. Initialize all JSON files with empty/default values
3. Create `project_info.json` with metadata

### Project Deletion
1. Remove directory `memory/{project_id}/` (not yet implemented)
2. Clean up agent references

### Agent Registration
1. Add entry to `global/agent_registry.json`
2. Create directory `agents/{agent_id}/`
3. Initialize context files

---

## Migration and Versioning

When schema changes:
1. Update code to handle both old and new formats
2. Migrate data on first read
3. Save in new format
4. Document changes in `docs/DATA_MIGRATIONS.md`

---

## Best Practices

1. **Always use StorageBackend** - Don't access files directly
2. **Handle missing files gracefully** - Return empty defaults
3. **Validate data on read** - Check required fields
4. **Use atomic writes** - Always use `storage.save()`
5. **Log data operations** - Use logging for debugging
6. **Backup regularly** - Data is in user's home directory

---

## Related Documentation

- [API Reference](API_REFERENCE.md) - Tools and resources
- [Architecture Guide](ARCHITECTURE.md) - System design
- [Setup Guide](SETUP.md) - Installation and configuration
- [Extending Guide](EXTENDING.md) - Custom plugins and events

---

**Last Updated:** 2026-02-10
**Version:** 1.0.0
