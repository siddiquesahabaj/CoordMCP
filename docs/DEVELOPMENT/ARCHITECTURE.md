# CoordMCP - Detailed Project Plan & Architecture

## Executive Summary

CoordMCP is a FastMCP-based Model Context Protocol server designed to enable intelligent coordination between multiple coding agents. It provides shared long-term memory, context switching capabilities, and architectural guidance without requiring additional LLM API calls.

**Timeline:** 5 days, 6 hours/day (30 hours total)
**Technology Stack:** Python, FastMCP, JSON-based storage
**Primary Use Cases:** Opencode, Cursor, Claude Code integration

---

## Part 1: Project Structure

```
coordmcp/
├── src/
│   ├── coordmcp/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastMCP server entry point
│   │   ├── config.py               # Configuration management
│   │   ├── logger.py               # Logging setup
│   │   │
│   │   ├── core/                   # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── server.py           # FastMCP server setup
│   │   │   ├── resource_manager.py # MCP resource handler
│   │   │   └── tool_manager.py     # MCP tool handler
│   │   │
│   │   ├── memory/                 # Long-term memory system
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Abstract memory interface
│   │   │   ├── json_store.py       # JSON-based storage (current)
│   │   │   ├── models.py           # Memory data models
│   │   │   └── utils.py            # Memory utilities
│   │   │
│   │   ├── context/                # Multi-agent context management
│   │   │   ├── __init__.py
│   │   │   ├── manager.py          # Context manager
│   │   │   ├── state.py            # Context state models
│   │   │   ├── file_tracker.py     # File locking & tracking
│   │   │   └── change_log.py       # Change tracking
│   │   │
│   │   ├── architecture/           # Architectural guidance
│   │   │   ├── __init__.py
│   │   │   ├── analyzer.py         # Architecture analyzer
│   │   │   ├── recommender.py      # Structure recommendations
│   │   │   ├── validators.py       # Code structure validators
│   │   │   └── patterns.py         # Design patterns reference
│   │   │
│   │   ├── tools/                  # FastMCP Tool implementations
│   │   │   ├── __init__.py
│   │   │   ├── memory_tools.py     # Memory CRUD operations
│   │   │   ├── context_tools.py    # Context switching tools
│   │   │   ├── architecture_tools.py # Architecture tools
│   │   │   └── query_tools.py      # Query/search tools
│   │   │
│   │   ├── resources/              # FastMCP Resource implementations
│   │   │   ├── __init__.py
│   │   │   ├── project_resources.py  # Project-level resources
│   │   │   ├── agent_resources.py    # Agent-level resources
│   │   │   └── architecture_resources.py  # Architecture resources
│   │   │
│   │   └── storage/                # Storage abstraction (future extensible)
│   │       ├── __init__.py
│   │       ├── base.py             # Abstract storage interface
│   │       ├── json_adapter.py     # JSON adapter
│   │       └── utils.py            # Storage utilities
│   │
│   ├── data/                       # Data storage directory
│   │   ├── projects.json           # Project configurations
│   │   ├── memory/                 # Project-specific memory
│   │   │   └── {project_id}/
│   │   │       ├── decisions.json
│   │   │       ├── tech_stack.json
│   │   │       ├── architecture.json
│   │   │       ├── recent_changes.json
│   │   │       └── file_metadata.json
│   │   ├── agents/                 # Agent tracking
│   │   │   └── {agent_id}/
│   │   │       ├── context.json
│   │   │       ├── locked_files.json
│   │   │       └── session_log.json
│   │   └── global/
│   │       └── agent_registry.json # Global agent registry
│   │
│   └── tests/
│       ├── __init__.py
│       ├── unit/
│       │   ├── test_memory_store.py
│       │   ├── test_context_manager.py
│       │   ├── test_architecture_analyzer.py
│       │   └── test_file_tracker.py
│       ├── integration/
│       │   ├── test_tools_integration.py
│       │   ├── test_resources_integration.py
│       │   └── test_full_workflow.py
│       └── fixtures/
│           ├── sample_project.json
│           └── sample_agents.json
│
├── docs/
│   ├── README.md                   # Main documentation
│   ├── ARCHITECTURE.md             # Architecture deep-dive
│   ├── API_REFERENCE.md            # Tools & Resources reference
│   ├── SETUP.md                    # Installation & setup guide
│   ├── USAGE_EXAMPLES.md           # Usage examples
│   ├── DATA_SCHEMAS.md             # Data schema documentation
│   ├── EXTENDING.md                # Extension guidelines
│   └── DEVELOPMENT.md              # Development guidelines
│
├── examples/
│   ├── basic_project_setup.py      # Basic usage example
│   ├── multi_agent_workflow.py     # Multi-agent workflow example
│   ├── architecture_recommendation.py  # Architecture example
│   └── context_switching.py        # Context switching example
│
├── pyproject.toml                  # Project configuration
├── requirements.txt                # Dependencies
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore
└── Makefile                        # Development commands

```

---

## Part 2: Data Schemas

### 2.1 Memory Models

#### Project Memory Structure
```json
{
  "project_id": "uuid",
  "project_name": "string",
  "created_at": "ISO timestamp",
  "last_updated": "ISO timestamp",
  
  "decisions": {
    "decision_id": {
      "id": "uuid",
      "timestamp": "ISO timestamp",
      "title": "string",
      "description": "string",
      "context": "string",
      "rationale": "string",
      "impact": "string",
      "status": "active|archived|superseded",
      "related_files": ["file_path"],
      "author_agent": "agent_id",
      "tags": ["tag"]
    }
  },
  
  "tech_stack": {
    "backend": {
      "language": "python",
      "framework": "fastapi",
      "version": "0.100.0",
      "rationale": "string",
      "decision_ref": "decision_id"
    },
    "frontend": {...},
    "database": {...},
    "infrastructure": {...}
  },
  
  "architecture": {
    "overview": "string",
    "layers": {
      "presentation": {...},
      "business_logic": {...},
      "data_access": {...}
    },
    "design_patterns": ["pattern_name"],
    "modules": {
      "module_name": {
        "purpose": "string",
        "files": ["file_path"],
        "dependencies": ["module_name"],
        "responsibilities": ["responsibility"]
      }
    }
  },
  
  "recent_changes": [
    {
      "id": "uuid",
      "timestamp": "ISO timestamp",
      "file_path": "string",
      "change_type": "create|modify|delete|refactor",
      "description": "string",
      "agent_id": "agent_id",
      "impact_area": "string",
      "architecture_impact": "none|minor|significant",
      "related_decision": "decision_id",
      "code_summary": "string (brief)"
    }
  ],
  
  "file_metadata": {
    "file_path": {
      "path": "string",
      "type": "source|test|config|doc",
      "last_modified": "ISO timestamp",
      "last_modified_by": "agent_id",
      "module": "module_name",
      "purpose": "string",
      "dependencies": ["file_path"],
      "dependents": ["file_path"],
      "lines_of_code": "number",
      "complexity": "low|medium|high"
    }
  }
}
```

### 2.2 Agent Context Model
```json
{
  "agent_id": "uuid",
  "agent_name": "string",
  "agent_type": "opencode|cursor|claude_code|custom",
  "session_id": "uuid",
  "created_at": "ISO timestamp",
  
  "current_context": {
    "project_id": "uuid",
    "current_objective": "string",
    "current_file": "file_path",
    "task_description": "string",
    "priority": "critical|high|medium|low",
    "started_at": "ISO timestamp",
    "estimated_completion": "ISO timestamp"
  },
  
  "locked_files": [
    {
      "file_path": "string",
      "locked_at": "ISO timestamp",
      "locked_by": "agent_id",
      "reason": "string",
      "expected_unlock_time": "ISO timestamp"
    }
  ],
  
  "recent_context": [
    {
      "timestamp": "ISO timestamp",
      "file": "file_path",
      "operation": "read|write|analyze",
      "summary": "string"
    }
  ],
  
  "session_log": [
    {
      "timestamp": "ISO timestamp",
      "event": "string",
      "details": "object"
    }
  ]
}
```

### 2.3 Architecture Recommendation Model
```json
{
  "recommendation_id": "uuid",
  "timestamp": "ISO timestamp",
  "project_id": "uuid",
  "requested_by": "agent_id",
  
  "request": {
    "feature_description": "string",
    "context": "string",
    "constraints": ["constraint"]
  },
  
  "recommendation": {
    "file_structure": {
      "new_files": [
        {
          "path": "string",
          "purpose": "string",
          "type": "class|function|module|config",
          "suggested_content_outline": "string"
        }
      ],
      "modified_files": [
        {
          "path": "string",
          "modifications": "string"
        }
      ],
      "deleted_files": ["file_path"]
    },
    
    "code_structure": {
      "new_classes": [
        {
          "name": "string",
          "purpose": "string",
          "methods": ["method_signature"],
          "module": "module_path",
          "design_pattern": "pattern_name"
        }
      ],
      "new_functions": [
        {
          "name": "string",
          "signature": "string",
          "purpose": "string",
          "module": "module_path"
        }
      ],
      "refactoring_suggestions": ["suggestion"]
    },
    
    "architecture_impact": {
      "new_modules": [
        {
          "name": "string",
          "purpose": "string",
          "dependencies": ["module_name"],
          "rationale": "string"
        }
      ],
      "layer_changes": "string",
      "scalability_notes": "string",
      "future_expandability": "string"
    },
    
    "design_principles": [
      {
        "principle": "string",
        "application": "string",
        "rationale": "string"
      }
    ]
  },
  
  "implementation_guide": {
    "steps": [
      {
        "order": "number",
        "description": "string",
        "files_affected": ["file_path"]
      }
    ],
    "estimated_effort": "string",
    "testing_strategy": "string"
  },
  
  "status": "pending|approved|implemented|archived"
}
```

### 2.4 Global Agent Registry
```json
{
  "agents": [
    {
      "agent_id": "uuid",
      "agent_name": "string",
      "agent_type": "opencode|cursor|claude_code|custom",
      "version": "string",
      "capabilities": ["capability"],
      "last_active": "ISO timestamp",
      "total_sessions": "number",
      "projects_involved": ["project_id"],
      "status": "active|inactive|deprecated"
    }
  ],
  "updated_at": "ISO timestamp"
}
```

---

## Part 3: FastMCP Tools

### 3.1 Memory Management Tools

#### Tool: `save_decision`
```python
{
  "name": "save_decision",
  "description": "Save a major architectural or technical decision to project memory",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_id": {"type": "string"},
      "title": {"type": "string"},
      "description": {"type": "string"},
      "context": {"type": "string"},
      "rationale": {"type": "string"},
      "impact": {"type": "string"},
      "tags": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["project_id", "title", "description", "rationale"]
  }
}
```

#### Tool: `get_project_decisions`
```python
{
  "name": "get_project_decisions",
  "description": "Retrieve all major decisions for a project",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_id": {"type": "string"},
      "status": {"type": "string", "enum": ["active", "archived", "all"]},
      "tags": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["project_id"]
  }
}
```

#### Tool: `update_tech_stack`
```python
{
  "name": "update_tech_stack",
  "description": "Update technology stack information for a project",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_id": {"type": "string"},
      "category": {"type": "string", "enum": ["backend", "frontend", "database", "infrastructure"]},
      "technology": {"type": "string"},
      "version": {"type": "string"},
      "rationale": {"type": "string"},
      "decision_ref": {"type": "string"}
    },
    "required": ["project_id", "category", "technology"]
  }
}
```

#### Tool: `get_tech_stack`
```python
{
  "name": "get_tech_stack",
  "description": "Get current technology stack for a project",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_id": {"type": "string"},
      "category": {"type": "string"}
    },
    "required": ["project_id"]
  }
}
```

#### Tool: `log_change`
```python
{
  "name": "log_change",
  "description": "Log a recent change to project structure or architecture",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_id": {"type": "string"},
      "file_path": {"type": "string"},
      "change_type": {"type": "string", "enum": ["create", "modify", "delete", "refactor"]},
      "description": {"type": "string"},
      "code_summary": {"type": "string"},
      "architecture_impact": {"type": "string", "enum": ["none", "minor", "significant"]},
      "related_decision": {"type": "string"}
    },
    "required": ["project_id", "file_path", "change_type", "description"]
  }
}
```

#### Tool: `get_recent_changes`
```python
{
  "name": "get_recent_changes",
  "description": "Get recent changes to a project",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_id": {"type": "string"},
      "limit": {"type": "number", "default": 20},
      "architecture_impact_filter": {"type": "string", "enum": ["all", "none", "minor", "significant"]}
    },
    "required": ["project_id"]
  }
}
```

### 3.2 Context Management Tools

#### Tool: `register_agent`
```python
{
  "name": "register_agent",
  "description": "Register a new agent in the global registry",
  "input_schema": {
    "type": "object",
    "properties": {
      "agent_name": {"type": "string"},
      "agent_type": {"type": "string", "enum": ["opencode", "cursor", "claude_code", "custom"]},
      "capabilities": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["agent_name", "agent_type"]
  }
}
```

#### Tool: `start_context`
```python
{
  "name": "start_context",
  "description": "Start a new work context for an agent",
  "input_schema": {
    "type": "object",
    "properties": {
      "agent_id": {"type": "string"},
      "project_id": {"type": "string"},
      "objective": {"type": "string"},
      "task_description": {"type": "string"},
      "priority": {"type": "string", "enum": ["critical", "high", "medium", "low"]}
    },
    "required": ["agent_id", "project_id", "objective"]
  }
}
```

#### Tool: `lock_files`
```python
{
  "name": "lock_files",
  "description": "Lock files to prevent conflicts between agents",
  "input_schema": {
    "type": "object",
    "properties": {
      "agent_id": {"type": "string"},
      "project_id": {"type": "string"},
      "files": {"type": "array", "items": {"type": "string"}},
      "reason": {"type": "string"},
      "expected_unlock_time": {"type": "string", "format": "date-time"}
    },
    "required": ["agent_id", "project_id", "files", "reason"]
  }
}
```

#### Tool: `unlock_files`
```python
{
  "name": "unlock_files",
  "description": "Unlock files after work is complete",
  "input_schema": {
    "type": "object",
    "properties": {
      "agent_id": {"type": "string"},
      "project_id": {"type": "string"},
      "files": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["agent_id", "project_id", "files"]
  }
}
```

#### Tool: `get_locked_files`
```python
{
  "name": "get_locked_files",
  "description": "Get list of currently locked files in a project",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_id": {"type": "string"}
    },
    "required": ["project_id"]
  }
}
```

#### Tool: `switch_context`
```python
{
  "name": "switch_context",
  "description": "Switch agent context between projects or objectives",
  "input_schema": {
    "type": "object",
    "properties": {
      "agent_id": {"type": "string"},
      "from_context": {"type": "object"},
      "to_project_id": {"type": "string"},
      "to_objective": {"type": "string"}
    },
    "required": ["agent_id", "to_project_id", "to_objective"]
  }
}
```

#### Tool: `get_agent_context`
```python
{
  "name": "get_agent_context",
  "description": "Get current context for an agent",
  "input_schema": {
    "type": "object",
    "properties": {
      "agent_id": {"type": "string"}
    },
    "required": ["agent_id"]
  }
}
```

### 3.3 Architecture Tools

#### Tool: `analyze_architecture`
```python
{
  "name": "analyze_architecture",
  "description": "Analyze current project architecture",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_id": {"type": "string"}
    },
    "required": ["project_id"]
  }
}
```

#### Tool: `get_architecture_recommendation`
```python
{
  "name": "get_architecture_recommendation",
  "description": "Get architectural recommendation for a new feature or change",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_id": {"type": "string"},
      "feature_description": {"type": "string"},
      "context": {"type": "string"},
      "constraints": {"type": "array", "items": {"type": "string"}},
      "implementation_style": {"type": "string", "enum": ["modular", "monolithic", "auto"]}
    },
    "required": ["project_id", "feature_description"]
  }
}
```

#### Tool: `validate_code_structure`
```python
{
  "name": "validate_code_structure",
  "description": "Validate if proposed code structure follows architectural guidelines",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_id": {"type": "string"},
      "file_path": {"type": "string"},
      "code_structure": {"type": "object"},
      "strict_mode": {"type": "boolean", "default": false}
    },
    "required": ["project_id", "file_path", "code_structure"]
  }
}
```

#### Tool: `update_architecture`
```python
{
  "name": "update_architecture",
  "description": "Update project architecture after implementation",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_id": {"type": "string"},
      "recommendation_id": {"type": "string"},
      "implementation_summary": {"type": "string"},
      "actual_files_created": {"type": "array", "items": {"type": "string"}},
      "actual_files_modified": {"type": "array", "items": {"type": "string"}},
      "lessons_learned": {"type": "string"}
    },
    "required": ["project_id", "recommendation_id"]
  }
}
```

### 3.4 Memory Query Tools (Part of Memory Tools)

These tools are implemented in `memory_tools.py` but provide query capabilities:

#### Tool: `search_decisions`
```python
{
  "name": "search_decisions",
  "description": "Search through decisions by keywords or metadata",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_id": {"type": "string"},
      "query": {"type": "string"},
      "tags": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["project_id", "query"]
  }
}
```

#### Tool: `get_module_info`
```python
{
  "name": "get_module_info",
  "description": "Get detailed information about a project module",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_id": {"type": "string"},
      "module_name": {"type": "string"}
    },
    "required": ["project_id", "module_name"]
  }
}
```

#### Tool: `get_file_dependencies`
```python
{
  "name": "get_file_dependencies",
  "description": "Get dependency graph for a file",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_id": {"type": "string"},
      "file_path": {"type": "string"},
      "direction": {"type": "string", "enum": ["dependencies", "dependents", "both"]}
    },
    "required": ["project_id", "file_path"]
  }
}
```

#### Tool: `get_project_info`
```python
{
  "name": "get_project_info",
  "description": "Get complete project information",
  "input_schema": {
    "type": "object",
    "properties": {
      "project_id": {"type": "string"}
    },
    "required": ["project_id"]
  }
}
```

---

## Part 4: FastMCP Resources

### 4.1 Project Resources

#### Resource: `project://{project_id}`
- **Description:** Main project resource containing all project information
- **Content:** Full project configuration, metadata, and overview
- **Use Case:** Agents reading project-wide information

#### Resource: `project://{project_id}/decisions`
- **Description:** All decisions for a project with detailed information
- **Content:** Paginated list of decisions

#### Resource: `project://{project_id}/tech-stack`
- **Description:** Technology stack overview
- **Content:** All selected technologies with versions and rationale

#### Resource: `project://{project_id}/architecture`
- **Description:** Architecture overview
- **Content:** High-level architecture, modules, design patterns

#### Resource: `project://{project_id}/recent-changes`
- **Description:** Recent changes to project
- **Content:** Last N changes with impact analysis

### 4.2 Agent Resources

#### Resource: `agent://{agent_id}`
- **Description:** Agent profile and capabilities
- **Content:** Agent information, type, capabilities, activity

#### Resource: `agent://{agent_id}/context`
- **Description:** Current working context
- **Content:** Current project, objective, locked files

#### Resource: `agent://{agent_id}/session-log`
- **Description:** Agent session activity log
- **Content:** Timestamped events from current session

### 4.3 Architecture Resources

#### Resource: `design-patterns://list`
- **Description:** List of all available design patterns
- **Content:** Pattern names, descriptions, and best use cases

#### Resource: `design-patterns://{pattern_name}`
- **Description:** Specific pattern details
- **Content:** Pattern description, structure, examples, best practices

#### Resource: `module://{project_id}/{module_name}`
- **Description:** Detailed module information
- **Content:** Purpose, files, dependencies, responsibilities

---

## Part 5: Development Timeline (5 Days × 6 Hours)

### Day 1: Foundation & Setup (6 hours)
**Goal:** Project structure, basic configuration, FastMCP integration

- [ ] 1.0 (1h) Initialize project structure, pyproject.toml, requirements.txt
- [ ] 1.1 (1h) Setup FastMCP server scaffolding and configuration
- [ ] 1.2 (1h) Create core logger and config systems
- [ ] 1.3 (1.5h) Implement base storage abstraction layer
- [ ] 1.4 (1h) Create JSON storage adapter
- [ ] 1.5 (0.5h) Setup data directory structure and initialization

**Deliverable:** Runnable FastMCP server (no tools/resources yet)

---

### Day 2: Memory System & Data Models (6 hours)
**Goal:** Long-term memory system with full CRUD operations

- [ ] 2.0 (1h) Create all Pydantic/dataclass models (decisions, tech_stack, architecture, changes)
- [ ] 2.1 (1h) Implement ProjectMemory class with decision management
- [ ] 2.2 (1h) Implement tech stack and architecture management
- [ ] 2.3 (1h) Implement change logging and retrieval
- [ ] 2.4 (1h) Implement file metadata tracking
- [ ] 2.5 (1h) Create memory tools (save_decision, get_decisions, update_tech_stack, etc.)

**Deliverable:** Complete memory system with 6 working tools

---

### Day 3: Context Management & File Tracking (6 hours)
**Goal:** Multi-agent context switching and file conflict prevention

- [ ] 3.0 (1h) Create agent context models and agent registry
- [ ] 3.1 (1h) Implement ContextManager class
- [ ] 3.2 (1.5h) Implement FileTracker with locking mechanism
- [ ] 3.3 (1h) Implement session logging
- [ ] 3.4 (1.5h) Create context tools (register_agent, start_context, lock_files, switch_context, etc.)

**Deliverable:** 7 working context management tools

---

### Day 4: Architecture Guidance System (6 hours)
**Goal:** Architecture recommendations and validation

- [ ] 4.0 (1h) Create architecture analyzer
- [ ] 4.1 (1.5h) Implement recommendation engine (non-LLM based)
- [ ] 4.2 (1h) Implement code structure validators
- [ ] 4.3 (1h) Create design patterns reference
- [ ] 4.4 (1.5h) Create architecture tools (analyze_architecture, get_recommendation, validate_structure, update_architecture)

**Deliverable:** 4 working architecture tools

---

### Day 5: Resources, Integration & Polish (6 hours)
**Goal:** FastMCP resources, testing, documentation, examples

- [ ] 5.0 (1h) Implement all FastMCP resources (project, agent, architecture)
- [ ] 5.1 (1h) Create comprehensive test suite (unit + integration tests)
- [ ] 5.2 (1.5h) Create usage examples (basic, multi-agent, architecture, context-switching)
- [ ] 5.3 (1h) Write documentation (setup, usage, API reference, extending)
- [ ] 5.4 (0.5h) Error handling and edge case fixes
- [ ] 5.5 (0.5h) Final validation and demo script

**Deliverable:** Complete, documented, tested CoordMCP

---

## Part 6: Technology Choices & Rationale

### Why These Choices?

**FastMCP:**
- Native Python support with simple decorator-based tool/resource registration
- Built for AI agent integration (perfect for Opencode, Cursor, Claude Code)
- Lightweight and easy to extend
- No complex routing or middleware needed

**JSON Storage:**
- Simple, human-readable, easy to debug
- Perfect for initial launch and 5-day timeline
- Easy to migrate to vector DBs later
- No database setup/maintenance overhead

**Pydantic/Dataclasses:**
- Type safety without heavy dependencies
- Automatic validation
- Easy serialization
- IDE autocomplete support

**Storage Abstraction:**
- Abstract base classes allow future migration to PostgreSQL, MongoDB, Vector DBs
- Clean separation of concerns
- Can swap implementations without changing tools
- Follows SOLID principles

---

## Part 7: Key Design Principles

### 1. **Modularity**
- Each subsystem (memory, context, architecture) is independent
- Storage is abstracted and swappable
- Tools don't directly touch data; they use managers

### 2. **Extensibility**
- Agent types are extensible (currently: opencode, cursor, claude_code, custom)
- Storage backends are pluggable
- New tools can be added without touching existing code
- Design patterns can be extended

### 3. **Simplicity**
- No external LLM calls for recommendations (built-in logic)
- Straightforward JSON-based storage
- Clear separation between API (tools) and implementation
- Minimal dependencies

### 4. **Traceability**
- Every decision, change, and recommendation is timestamped and logged
- Full audit trail for debugging
- Relationships tracked (decisions → changes → files)

### 5. **Conflict Prevention**
- File locking prevents simultaneous edits
- Context awareness prevents context confusion
- Change logs provide full visibility

---

## Part 8: File Naming & Conventions

### Python Modules
- `managers/*_manager.py` - High-level orchestrators
- `stores/*_store.py` - Data persistence layer
- `models.py` - Data models (Pydantic/dataclass)
- `utils.py` - Helper functions
- `tools/*_tools.py` - FastMCP tool implementations

### JSON Files
- Project-level: `projects.json`, `agent_registry.json`
- Project data: `memory/{project_id}/decisions.json`, etc.
- Agent data: `agents/{agent_id}/context.json`, etc.

### Functions
- Getters: `get_*`, `fetch_*`, `retrieve_*`
- Setters: `set_*`, `save_*`, `update_*`
- Managers: `*_manager.py` classes
- Validators: `validate_*`, `is_*`

---

## Part 9: Recommended Opencode/Cursor Workflow

### Step 1: Project Initialization
```python
opencode> initialize CoordMCP project structure as outlined in the plan
```

### Step 2: Core Infrastructure
```python
opencode> implement core storage layer, logger, and config systems
```

### Step 3: Memory System
```python
opencode> implement memory models and ProjectMemory manager with all CRUD operations
```

### Step 4: FastMCP Integration
```python
opencode> register memory tools with FastMCP server
```

### Step 5: Context System
```python
opencode> implement context manager and file tracker with locking mechanism
```

### Step 6: Architecture System
```python
opencode> implement architecture analyzer and recommendation engine
```

### Step 7: Resources
```python
opencode> implement all FastMCP resources for projects, agents, and architecture
```

### Step 8: Testing & Polish
```python
opencode> create comprehensive test suite and documentation
```

---

## Part 10: Deployment & Launch

### Pre-Launch Checklist
- [ ] All tools tested individually
- [ ] Integration tests pass
- [ ] Data persistence verified
- [ ] Error handling in place
- [ ] Documentation complete
- [ ] Examples runnable
- [ ] MCP server starts cleanly

### Launch Steps
1. Configure environment (`.env`)
2. Initialize data directory
3. Start MCP server: `python -m coordmcp.main`
4. Connect with Opencode, Cursor, or Claude Code
5. Test with provided examples

### Future Extensions (Post-Launch)
- Vector DB integration for semantic search of decisions
- PostgreSQL backend for production deployments
- Advanced recommendation engine using embeddings
- Real-time collaboration features
- Analytics dashboard
- Integration with version control systems
- Custom agent types

---

## Part 11: Error Handling Strategy

### Critical Errors (Fail Fast)
- Invalid project_id → Raise ProjectNotFoundError
- Invalid agent_id → Raise AgentNotFoundError
- File lock conflicts → Raise FileLockError
- Corrupted JSON data → Raise DataCorruptionError

### Warnings (Log & Continue)
- File unlock not owned by agent → Log warning, allow override
- Stale locks (> 24 hours) → Log warning, auto-unlock
- Missing optional fields → Log warning, use defaults

### Validation
- All inputs validated against schemas
- Pydantic models auto-validate
- Custom validators for complex logic
- Clear error messages for debugging

---

## Part 12: Testing Strategy

### Unit Tests (Day 5)
- Memory store CRUD operations
- Context manager operations
- File tracker locking/unlocking
- Architecture analyzer logic
- Data model validation

### Integration Tests (Day 5)
- Full workflow: register agent → start context → lock files → log changes
- Memory system end-to-end
- Context switching scenario
- Architecture recommendation flow

### Example Tests
- Basic project setup
- Multi-agent workflow
- Conflict detection
- Context restoration

---

## Summary

This plan provides:
1. **Clear project structure** that scales
2. **Comprehensive data schemas** that capture all requirements
3. **29+ FastMCP tools** covering all functionality
4. **6 FastMCP resource types** for agent accessibility
5. **5-day timeline** with clear daily milestones
6. **Extensibility** for future backends and features
7. **Production-ready** architecture with error handling
8. **Full documentation** and examples included

The modular design allows Opencode to implement features independently and parallelize where possible. Each subsystem has clear boundaries and dependencies.

Good luck with CoordMCP! 🚀
