# CoordMCP API Reference

Complete reference for all tools and resources available in CoordMCP.

## Table of Contents

- [Tools Overview](#tools-overview)
- [Memory Tools](#memory-tools)
- [Context Tools](#context-tools)
- [Architecture Tools](#architecture-tools)
- [Resources Overview](#resources-overview)
- [Project Resources](#project-resources)
- [Agent Resources](#agent-resources)
- [Architecture Resources](#architecture-resources)
- [Data Models](#data-models)
- [Error Handling](#error-handling)

## Tools Overview

CoordMCP provides 25+ tools organized into four categories:

| Category | Count | Tools |
|----------|-------|-------|
| Memory | 8 | Project, decision, tech stack, and change management |
| Context | 8 | Agent registration, context switching, file locking |
| Architecture | 5 | Analysis, recommendations, validation |
| Query | 4 | Search and retrieval operations |

---

## Memory Tools

### 1. create_project

Create a new project in the memory system.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_name | string | Yes | Name of the project |
| description | string | No | Project description |

**Returns:**
```json
{
  "success": true,
  "project_id": "uuid",
  "message": "Project 'Name' created successfully"
}
```

**Example:**
```python
await create_project(
    project_name="My API",
    description="RESTful API service"
)
```

---

### 2. save_decision

Save a major architectural or technical decision.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |
| title | string | Yes | Decision title |
| description | string | Yes | Detailed description |
| rationale | string | Yes | Why this decision was made |
| context | string | No | Context around the decision |
| impact | string | No | Expected impact |
| tags | array[string] | No | List of tags |
| related_files | array[string] | No | Related file paths |
| author_agent | string | No | Agent making the decision |

**Returns:**
```json
{
  "success": true,
  "decision_id": "uuid",
  "message": "Decision 'Title' saved successfully"
}
```

**Example:**
```python
await save_decision(
    project_id="proj-123",
    title="Use FastAPI",
    description="FastAPI for API layer",
    rationale="Performance and type safety",
    tags=["backend", "framework"]
)
```

---

### 3. get_project_decisions

Retrieve all decisions for a project.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |
| status | string | No | Filter by status: active, archived, superseded, all |
| tags | array[string] | No | Filter by tags |

**Returns:**
```json
{
  "success": true,
  "decisions": [...],
  "count": 5
}
```

---

### 4. search_decisions

Search through decisions by keywords or metadata.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |
| query | string | Yes | Search query |
| tags | array[string] | No | Filter by tags |

**Returns:**
```json
{
  "success": true,
  "decisions": [...],
  "count": 2
}
```

---

### 5. update_tech_stack

Update technology stack information.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |
| category | string | Yes | backend, frontend, database, infrastructure |
| technology | string | Yes | Technology name |
| version | string | No | Version string |
| rationale | string | No | Why chosen |
| decision_ref | string | No | Related decision ID |

**Returns:**
```json
{
  "success": true,
  "message": "Tech stack updated: backend = FastAPI"
}
```

**Example:**
```python
await update_tech_stack(
    project_id="proj-123",
    category="backend",
    technology="FastAPI",
    version="0.104.0"
)
```

---

### 6. get_tech_stack

Get current technology stack.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |
| category | string | No | Specific category to retrieve |

**Returns:**
```json
{
  "success": true,
  "tech_stack": {
    "backend": {
      "technology": "FastAPI",
      "version": "0.104.0"
    }
  }
}
```

---

### 7. log_change

Log a recent change to project structure.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |
| file_path | string | Yes | Path of changed file |
| change_type | string | Yes | create, modify, delete, refactor |
| description | string | Yes | Change description |
| agent_id | string | No | Agent making the change |
| code_summary | string | No | Brief code summary |
| architecture_impact | string | No | none, minor, significant |
| related_decision | string | No | Related decision ID |

**Returns:**
```json
{
  "success": true,
  "change_id": "uuid",
  "message": "Change logged for src/main.py"
}
```

---

### 8. get_recent_changes

Get recent changes to a project.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |
| limit | integer | No | Maximum changes (default: 20) |
| architecture_impact_filter | string | No | all, none, minor, significant |

**Returns:**
```json
{
  "success": true,
  "changes": [...],
  "count": 10
}
```

---

### 9. update_file_metadata

Update metadata for a file.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |
| file_path | string | Yes | File path |
| file_type | string | No | source, test, config, doc |
| module | string | No | Module name |
| purpose | string | No | Purpose description |
| dependencies | array[string] | No | Files this depends on |
| dependents | array[string] | No | Files depending on this |
| lines_of_code | integer | No | Lines of code |
| complexity | string | No | low, medium, high |
| last_modified_by | string | No | Agent who modified |

---

### 10. get_file_dependencies

Get dependency graph for a file.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |
| file_path | string | Yes | File path |
| direction | string | No | dependencies, dependents, both |

---

### 11. get_module_info

Get detailed module information.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |
| module_name | string | Yes | Module name |

---

## Context Tools

### 12. register_agent

Register a new agent in the global registry.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_name | string | Yes | Name of agent |
| agent_type | string | Yes | opencode, cursor, claude_code, custom |
| capabilities | array[string] | No | List of capabilities |
| version | string | No | Agent version (default: 1.0.0) |

**Returns:**
```json
{
  "success": true,
  "agent_id": "uuid",
  "message": "Agent 'Name' registered successfully"
}
```

**Example:**
```python
await register_agent(
    agent_name="MyAgent",
    agent_type="opencode",
    capabilities=["python", "fastapi"]
)
```

---

### 13. get_agents_list

Get list of all registered agents.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| status | string | No | Filter by status: active, inactive, deprecated, all |

**Returns:**
```json
{
  "success": true,
  "agents": [...],
  "count": 3
}
```

---

### 14. get_agent_profile

Get an agent's profile information.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |

---

### 15. start_context

Start a new work context for an agent.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |
| project_id | string | Yes | Project ID |
| objective | string | Yes | Current objective |
| task_description | string | No | Detailed task description |
| priority | string | No | critical, high, medium, low |
| current_file | string | No | Current file being worked on |

---

### 16. get_agent_context

Get current context for an agent.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |

---

### 17. switch_context

Switch agent context between projects or objectives.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |
| to_project_id | string | Yes | Target project ID |
| to_objective | string | Yes | New objective |
| task_description | string | No | New task description |
| priority | string | No | Priority level |

---

### 18. end_context

End an agent's current context.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |

---

### 19. lock_files

Lock files to prevent conflicts.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |
| project_id | string | Yes | Project ID |
| files | array[string] | Yes | Files to lock |
| reason | string | Yes | Reason for locking |
| expected_duration_minutes | integer | No | Expected duration (default: 60) |

**Returns:**
```json
{
  "success": true,
  "locked_files": ["file1.py", "file2.py"],
  "count": 2
}
```

---

### 20. unlock_files

Unlock files after work is complete.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |
| project_id | string | Yes | Project ID |
| files | array[string] | Yes | Files to unlock |

---

### 21. get_locked_files

Get list of currently locked files.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |

---

### 22. get_context_history

Get recent context history for an agent.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |
| limit | integer | No | Maximum entries (default: 10) |

---

### 23. get_session_log

Get session log for an agent.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |
| limit | integer | No | Maximum entries (default: 50) |

---

### 24. get_agents_in_project

Get all agents currently working in a project.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |

---

## Architecture Tools

### 25. analyze_architecture

Analyze current project architecture.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |

**Returns:**
```json
{
  "success": true,
  "overview": {
    "total_files": 25,
    "total_modules": 5
  },
  "architecture_assessment": {
    "overall_score": 85,
    "issues": [],
    "strengths": []
  }
}
```

---

### 26. get_architecture_recommendation

Get architectural recommendation for a new feature.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |
| feature_description | string | Yes | Feature description |
| context | string | No | Additional context |
| constraints | array[string] | No | Implementation constraints |
| implementation_style | string | No | modular, monolithic, auto |

**Returns:**
```json
{
  "success": true,
  "recommendation_id": "uuid",
  "recommended_pattern": {
    "pattern": "Repository",
    "confidence": 95
  },
  "file_structure": {
    "new_files": [...]
  },
  "implementation_guide": {
    "steps": [...],
    "estimated_effort": "2-3 days"
  }
}
```

---

### 27. validate_code_structure

Validate proposed code structure.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |
| file_path | string | Yes | File path |
| code_structure | object | Yes | Proposed structure |
| strict_mode | boolean | No | Strict validation (default: false) |

---

### 28. get_design_patterns

Get all available design patterns.

**Returns:**
```json
{
  "success": true,
  "patterns": [
    {"name": "MVC", "description": "..."},
    {"name": "Repository", "description": "..."}
  ],
  "count": 9
}
```

---

### 29. update_architecture

Update project architecture after implementation.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | Yes | Project ID |
| recommendation_id | string | Yes | Recommendation ID |
| implementation_summary | string | No | Summary of changes |
| actual_files_created | array[string] | No | Files created |
| actual_files_modified | array[string] | No | Files modified |

---

## Resources Overview

Resources provide read-only access to project information via MCP resources.

## Project Resources

### project://{project_id}

Returns full project overview including:
- Project name and description
- Quick stats
- Links to other resources

### project://{project_id}/decisions

Returns all decisions for a project in markdown format.

### project://{project_id}/tech-stack

Returns technology stack with versions and rationale.

### project://{project_id}/architecture

Returns architecture overview with modules and file organization.

### project://{project_id}/recent-changes

Returns recent changes with impact assessment.

### project://{project_id}/modules

Returns list of all modules in the project.

### project://{project_id}/modules/{module_name}

Returns detailed information about a specific module.

## Agent Resources

### agent://{agent_id}

Returns agent profile including:
- Agent name and type
- Capabilities
- Activity statistics

### agent://{agent_id}/context

Returns current working context including:
- Current objective
- Project being worked on
- Locked files
- Recent activity

### agent://{agent_id}/locked-files

Returns files currently locked by the agent.

### agent://{agent_id}/session-log

Returns session activity log.

### agent://registry

Returns all registered agents.

## Architecture Resources

### design-patterns://list

Returns all available design patterns with descriptions.

### design-patterns://{pattern_name}

Returns detailed information about a specific pattern including:
- Description
- Best use cases
- Structure
- Example code
- Best practices

## Data Models

### Decision

```python
{
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
```

### Change

```python
{
  "id": "uuid",
  "timestamp": "ISO timestamp",
  "file_path": "string",
  "change_type": "create|modify|delete|refactor",
  "description": "string",
  "code_summary": "string",
  "agent_id": "agent_id",
  "architecture_impact": "none|minor|significant",
  "related_decision": "decision_id"
}
```

### AgentProfile

```python
{
  "agent_id": "uuid",
  "agent_name": "string",
  "agent_type": "opencode|cursor|claude_code|custom",
  "version": "string",
  "capabilities": ["capability"],
  "last_active": "ISO timestamp",
  "total_sessions": number,
  "projects_involved": ["project_id"],
  "status": "active|inactive|deprecated"
}
```

## Error Handling

All tools return a consistent response format:

### Success Response

```json
{
  "success": true,
  "data": {...},
  "message": "Optional success message"
}
```

### Error Response

```json
{
  "success": false,
  "error": "Error message",
  "error_type": "ErrorType",
  "suggestions": ["How to fix"]
}
```

### Common Error Types

| Error Type | Description |
|------------|-------------|
| ProjectNotFound | Project doesn't exist |
| AgentNotFound | Agent not registered |
| FileLockError | File is locked by another agent |
| ValidationError | Input validation failed |
| InternalError | Unexpected server error |

---

For more examples, see [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
