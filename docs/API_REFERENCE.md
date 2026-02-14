# CoordMCP API Reference

Complete reference for all tools and resources available in CoordMCP.

## Table of Contents

- [Tools Overview](#tools-overview)
- [Discovery Tools](#discovery-tools)
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

CoordMCP provides **35+ tools** organized into four categories:

| Category | Count | Tools |
|----------|-------|-------|
| Discovery | 4 | Project discovery, flexible lookup, browsing |
| Memory | 11 | Project, decision, tech stack, and change management |
| Context | 13 | Agent registration, context switching, file locking |
| Architecture | 5 | Analysis, recommendations, validation |

**Key Features:**
- **Flexible Project Lookup**: Use `project_id`, `project_name`, or `workspace_path`
- **Session Persistence**: Agents reconnect with same ID using consistent names
- **Workspace Discovery**: Auto-discover projects by directory

---

## Discovery Tools

### 1. discover_project

**MUST BE CALLED FIRST** - Discover existing project in a directory.

Searches for a project associated with the given directory, checking the exact path and parent directories (up to 3 levels).

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| path | string | No | Directory path to search (default: current working directory) |
| max_parent_levels | integer | No | Max parent directories to search (default: 3) |

**Returns:**
```json
{
  "success": true,
  "found": true,
  "project": {
    "project_id": "uuid",
    "project_name": "My Project",
    "workspace_path": "/path/to/project"
  },
  "distance": 0,
  "message": "Found exact match: My Project"
}
```

**Example:**
```python
import os

# Check if project exists in current directory
discovery = await coordmcp_discover_project(path=os.getcwd())

if discovery["found"]:
    project_id = discovery["project"]["project_id"]
    print(f"Found project: {discovery['project']['project_name']}")
else:
    # Need to create project
    result = await coordmcp_create_project(
        project_name="My App",
        workspace_path=os.getcwd(),
        description="A new application"
    )
    project_id = result["project_id"]
```

---

### 2. get_project

Flexible project lookup by ID, name, or workspace path.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | No | Project ID (highest priority) |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace directory path |

**Priority:** project_id > workspace_path > project_name

**Returns:**
```json
{
  "success": true,
  "project": {
    "project_id": "uuid",
    "project_name": "My Project",
    "workspace_path": "/path/to/project",
    "description": "Project description"
  }
}
```

**Example:**
```python
# By ID
project = await coordmcp_get_project(project_id="proj-abc-123")

# By name
project = await coordmcp_get_project(project_name="My App")

# By workspace path
project = await coordmcp_get_project(workspace_path=os.getcwd())
```

---

### 3. list_projects

List all CoordMCP projects with optional filtering.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| status | string | No | Filter by status: "active", "archived", or "all" (default: "active") |
| workspace_base | string | No | Filter by base directory path |
| include_archived | boolean | No | Include archived projects (default: false) |

**Returns:**
```json
{
  "success": true,
  "projects": [
    {
      "project_id": "uuid",
      "project_name": "Project 1",
      "workspace_path": "/path/to/project1"
    }
  ],
  "total_count": 5
}
```

---

### 4. get_active_agents

Get information about active agents.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | No | Filter by project ID |
| project_name | string | No | Filter by project name |
| workspace_path | string | No | Filter by workspace path |

**Returns:**
```json
{
  "success": true,
  "agents": [
    {
      "agent_id": "uuid",
      "agent_name": "OpenCode",
      "agent_type": "opencode",
      "current_project": "My App",
      "current_objective": "Building auth",
      "locked_files_count": 2
    }
  ],
  "total_count": 3
}
```

**Example:**
```python
# Get all active agents
agents = await coordmcp_get_active_agents()

# Get agents working on specific project
agents = await coordmcp_get_active_agents(project_id=project_id)
```

---

## Memory Tools

### 5. create_project

**REQUIRES workspace_path** - Create a new project in the memory system.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_name | string | Yes | Name of the project |
| workspace_path | string | Yes | Absolute path to project workspace directory |
| description | string | No | Project description |

**Important:** The `workspace_path` must be an absolute path to an existing directory.

**Returns:**
```json
{
  "success": true,
  "project_id": "uuid",
  "project_name": "My Project",
  "workspace_path": "/path/to/project",
  "message": "Project 'My Project' created successfully"
}
```

**Example:**
```python
import os

result = await coordmcp_create_project(
    project_name="E-commerce Platform",
    workspace_path=os.getcwd(),  # Use current directory
    description="A full-stack e-commerce solution"
)
```

---

### 6. get_project_info

Get comprehensive information about a project.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |

**At least one identifier must be provided.**

**Returns:**
```json
{
  "success": true,
  "project": {
    "project_id": "uuid",
    "project_name": "My Project",
    "workspace_path": "/path/to/project",
    "description": "Description",
    "created_at": "2026-02-10T10:30:00",
    "updated_at": "2026-02-10T15:45:00"
  }
}
```

---

### 7. save_decision

Save a major architectural or technical decision.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| title | string | Yes | Decision title |
| description | string | Yes | Detailed description |
| rationale | string | Yes | Why this decision was made |
| project_id | string | No | Project ID (optional if project_name/workspace_path provided) |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |
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
await coordmcp_save_decision(
    project_id="proj-123",
    title="Use JWT for Authentication",
    description="Implement JWT-based authentication with refresh tokens",
    rationale="Stateless, scalable, industry standard for APIs",
    tags=["security", "authentication", "api"],
    related_files=["src/auth.py", "src/middleware/jwt.py"]
)
```

---

### 8. get_project_decisions

Retrieve all decisions for a project.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |
| status | string | No | Filter by status: "active", "archived", "superseded", "all" |
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

### 9. search_decisions

Search through decisions by keywords or metadata.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| query | string | Yes | Search keywords |
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |
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

### 10. update_tech_stack

Update technology stack information.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| category | string | Yes | backend, frontend, database, infrastructure, testing, devops |
| technology | string | Yes | Technology name |
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |
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

---

### 11. get_tech_stack

Get current technology stack.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |
| category | string | No | Specific category to retrieve |

---

### 12. log_change

Log a recent change to project structure.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_path | string | Yes | Path of changed file |
| change_type | string | Yes | create, modify, delete, refactor |
| description | string | Yes | Change description |
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |
| agent_id | string | No | Agent making the change |
| code_summary | string | No | Brief code summary |
| architecture_impact | string | No | none, minor, significant |
| related_decision | string | No | Related decision ID |

---

### 13. get_recent_changes

Get recent changes to a project.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |
| limit | integer | No | Maximum changes (default: 20) |
| architecture_impact_filter | string | No | all, none, minor, significant |

---

### 14. update_file_metadata

Update metadata for a file.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_path | string | Yes | File path |
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |
| file_type | string | No | source, test, config, doc |
| module | string | No | Module name |
| purpose | string | No | Purpose description |
| dependencies | array[string] | No | Files this depends on |
| dependents | array[string] | No | Files depending on this |
| lines_of_code | integer | No | Lines of code |
| complexity | string | No | low, medium, high |
| last_modified_by | string | No | Agent who modified |

---

### 15. get_file_dependencies

Get dependency graph for a file.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_path | string | Yes | File path |
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |
| direction | string | No | dependencies, dependents, both |

---

### 16. get_module_info

Get detailed module information.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| module_name | string | Yes | Module name |
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |

---

## Context Tools

### 17. register_agent

Register a new agent or reconnect to existing agent.

**Session Persistence:** If an agent with the same name already exists, reconnects to that agent instead of creating a new one.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_name | string | Yes | Name of the agent (use same name across sessions) |
| agent_type | string | Yes | opencode, cursor, claude_code, custom |
| capabilities | array[string] | No | List of capabilities |
| version | string | No | Agent version (default: 1.0.0) |

**Returns:**
```json
{
  "success": true,
  "agent_id": "uuid",
  "message": "Agent 'Name' reconnected successfully. Previous context restored."
}
```

**Example:**
```python
# First session - creates new agent
agent = await coordmcp_register_agent(
    agent_name="OpenCodeDev",
    agent_type="opencode",
    capabilities=["python", "fastapi"]
)
agent_id = agent["agent_id"]

# Second session - reconnects to same agent
agent = await coordmcp_register_agent(
    agent_name="OpenCodeDev",  # Same name!
    agent_type="opencode",
    capabilities=["python", "fastapi"]
)
# Returns same agent_id, preserves context
```

---

### 18. get_agents_list

Get list of all registered agents.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| status | string | No | Filter by status: active, inactive, deprecated, all |

---

### 19. get_agent_profile

Get an agent's profile information.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |

---

### 20. start_context

Start a new work context for an agent.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |
| project_id | string | No | Project ID (optional if project_name/workspace_path provided) |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |
| objective | string | Yes | Current objective |
| task_description | string | No | Detailed task description |
| priority | string | No | critical, high, medium, low |
| current_file | string | No | Current file being worked on |

---

### 21. get_agent_context

Get current context for an agent.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |

**Returns:** Full agent context including current project, objective, and locked files.

---

### 22. switch_context

Switch agent context between projects or objectives.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |
| to_project_id | string | No | Target project ID |
| to_project_name | string | No | Target project name |
| to_workspace_path | string | No | Target workspace path |
| to_objective | string | Yes | New objective |
| task_description | string | No | New task description |
| priority | string | No | Priority level |

---

### 23. end_context

End an agent's current context.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |
| summary | string | No | Summary of completed work |
| outcome | string | No | success, partial, blocked |

---

### 24. lock_files

Lock files to prevent conflicts.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |
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

### 25. unlock_files

Unlock files after work is complete.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |
| files | array[string] | Yes | Files to unlock |

---

### 26. get_locked_files

Get list of currently locked files.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |

---

### 27. get_context_history

Get recent context history for an agent.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |
| limit | integer | No | Maximum entries (default: 10) |

---

### 28. get_session_log

Get session log for an agent.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| agent_id | string | Yes | Agent ID |
| limit | integer | No | Maximum entries (default: 50) |

---

### 29. get_agents_in_project

Get all agents currently working in a project.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |

---

## Architecture Tools

### 30. analyze_architecture

Analyze current project architecture.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |

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

### 31. get_architecture_recommendation

Get architectural recommendation for a new feature.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| feature_description | string | Yes | Feature description |
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |
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

### 32. validate_code_structure

Validate proposed code structure.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file_path | string | Yes | File path |
| code_structure | object | Yes | Proposed structure |
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |
| strict_mode | boolean | No | Strict validation (default: false) |

---

### 33. get_design_patterns

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

### 34. update_architecture

Update project architecture after implementation.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| recommendation_id | string | Yes | Recommendation ID |
| implementation_summary | string | No | Summary of changes |
| project_id | string | No | Project ID |
| project_name | string | No | Project name |
| workspace_path | string | No | Workspace path |
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

| Error Type | Description | Solution |
|------------|-------------|----------|
| ProjectNotFound | Project doesn't exist | Use discover_project or check project_id |
| AgentNotFound | Agent not registered | Call register_agent first |
| FileLockError | File is locked by another agent | Check locked files and coordinate |
| ValidationError | Input validation failed | Check required parameters and types |
| InternalError | Unexpected server error | Check logs and retry |

---

## Usage Examples

### Complete Workflow Example

```python
import os

# 1. Discover or create project
discovery = await coordmcp_discover_project(path=os.getcwd())
if discovery["found"]:
    project_id = discovery["project"]["project_id"]
else:
    result = await coordmcp_create_project(
        project_name="My App",
        workspace_path=os.getcwd(),
        description="A web application"
    )
    project_id = result["project_id"]

# 2. Register as agent
agent = await coordmcp_register_agent(
    agent_name="DevAgent",
    agent_type="opencode",
    capabilities=["python", "fastapi"]
)
agent_id = agent["agent_id"]

# 3. Check who else is working
agents = await coordmcp_get_active_agents(project_id=project_id)

# 4. Start working
await coordmcp_start_context(
    agent_id=agent_id,
    project_id=project_id,
    objective="Implement user authentication",
    priority="high"
)

# 5. Lock files
await coordmcp_lock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["src/auth.py"],
    reason="Implementing JWT auth"
)

# 6. Save decision
await coordmcp_save_decision(
    project_id=project_id,
    title="Use JWT Authentication",
    description="Implement JWT-based auth",
    rationale="Stateless and scalable"
)

# 7. Log change
await coordmcp_log_change(
    project_id=project_id,
    file_path="src/auth.py",
    change_type="create",
    description="Created auth module"
)

# 8. Unlock files
await coordmcp_unlock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["src/auth.py"]
)

# 9. End context
await coordmcp_end_context(
    agent_id=agent_id,
    summary="Completed JWT auth implementation"
)
```

---

For more examples, see [examples/](./examples/)
