# API Reference

Complete reference for all 49 CoordMCP tools.

## Overview

CoordMCP provides **49 tools** organized into seven categories:

| Category | Count | Purpose |
|----------|-------|---------|
| Discovery | 4 | Project discovery and lookup |
| Memory | 13 | Decisions, tech stack, changes |
| Context | 13 | Agent registration, file locking |
| Architecture | 5 | Analysis and recommendations |
| Task | 8 | Task management and tracking |
| Message | 5 | Agent-to-agent communication |
| Health | 1 | Project health dashboard |

### Flexible Project Lookup

Most tools that work with projects accept flexible identifiers:

| Parameter | Description | Priority |
|-----------|-------------|----------|
| `project_id` | Exact project ID | Highest |
| `workspace_path` | Directory path | Medium |
| `project_name` | Project name | Lowest |

**Priority order:** `project_id` > `workspace_path` > `project_name`

### Response Format

All tools return a consistent format:

**Success:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error message",
  "error_type": "ErrorType",
  "suggestions": ["How to fix"]
}
```

---

## Discovery Tools (4)

### discover_project

Discover a project by searching from a directory path.

**When to use:** Starting work in a directory and want to check if it's already tracked.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | No | Directory to search (default: current directory) |
| `max_parent_levels` | integer | No | Parent directories to search (default: 3) |

**Returns:**
```json
{
  "success": true,
  "found": true,
  "project": {
    "project_id": "...",
    "project_name": "...",
    "workspace_path": "..."
  },
  "distance": 0
}
```

**Natural Language Example:**
> "Check if there's already a CoordMCP project in this directory"

**Behind the Scenes:**
```
discover_project(path=os.getcwd())
```

---

### get_project

Get project information by ID, name, or workspace path.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | No | Project ID |
| `project_name` | string | No | Project name |
| `workspace_path` | string | No | Workspace directory |

**Natural Language Example:**
> "Get details about the project named 'My App'"

**Behind the Scenes:**
```
get_project(project_name="My App")
```

---

### list_projects

List all CoordMCP projects.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter: "active", "archived", "all" |
| `workspace_base` | string | No | Filter by base directory |
| `include_archived` | boolean | No | Include archived projects |

**Natural Language Example:**
> "Show me all my CoordMCP projects"

**Behind the Scenes:**
```
list_projects()
```

---

### get_active_agents

Get information about active agents.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | No | Filter by project |
| `project_name` | string | No | Filter by project name |
| `workspace_path` | string | No | Filter by workspace |

**Natural Language Example:**
> "Who else is working on this project?"

**Behind the Scenes:**
```
get_active_agents(project_id="proj-123")
```

---

## Memory Tools (12)

### create_project

Create a new project linked to a workspace directory.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_name` | string | Yes | Project name |
| `workspace_path` | string | Yes | Absolute path to workspace |
| `description` | string | No | Project description |

**Natural Language Example:**
> "Create a new project called 'Todo App' in this directory"

**Behind the Scenes:**
```
create_project(
    project_name="Todo App",
    workspace_path=os.getcwd(),
    description="A task management application"
)
```

---

### get_project_info

Get comprehensive project information.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | No | Project ID |
| `project_name` | string | No | Project name |
| `workspace_path` | string | No | Workspace path |

**Natural Language Example:**
> "Tell me about this project"

**Behind the Scenes:**
```
get_project_info(workspace_path=os.getcwd())
```

---

### save_decision

Save an architectural or technical decision.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | Yes | Decision title |
| `description` | string | Yes | Detailed description |
| `rationale` | string | Yes | Why this decision was made |
| `project_id` | string | No | Project ID |
| `context` | string | No | Additional context |
| `impact` | string | No | Expected impact |
| `tags` | array | No | Tags for categorization |
| `related_files` | array | No | Related file paths |

**Natural Language Example:**
> "Record that we decided to use PostgreSQL for the database because we need ACID compliance"

**Behind the Scenes:**
```
save_decision(
    project_id="proj-123",
    title="Use PostgreSQL",
    description="PostgreSQL as primary database",
    rationale="ACID compliance, complex queries",
    tags=["database", "backend"]
)
```

---

### get_project_decisions

Retrieve all decisions for a project.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | No | Project ID |
| `status` | string | No | Filter: "active", "archived", "all" |
| `tags` | array | No | Filter by tags |

**Natural Language Example:**
> "What decisions have we made about the database?"

**Behind the Scenes:**
```
get_project_decisions(project_id="proj-123", tags=["database"])
```

---

### search_decisions

Search through decisions by keywords.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Search query |
| `project_id` | string | No | Project ID |
| `tags` | array | No | Filter by tags |

**Natural Language Example:**
> "Find decisions about authentication"

**Behind the Scenes:**
```
search_decisions(project_id="proj-123", query="authentication")
```

---

### update_tech_stack

Update technology stack information.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | Yes | "backend", "frontend", "database", "infrastructure" |
| `technology` | string | Yes | Technology name |
| `project_id` | string | No | Project ID |
| `version` | string | No | Version string |
| `rationale` | string | No | Why chosen |

**Natural Language Example:**
> "Record that we're using React 18 for the frontend"

**Behind the Scenes:**
```
update_tech_stack(
    project_id="proj-123",
    category="frontend",
    technology="React",
    version="18.2.0",
    rationale="Component-based, large ecosystem"
)
```

---

### get_tech_stack

Get current technology stack.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | No | Project ID |
| `category` | string | No | Specific category |

**Natural Language Example:**
> "What technologies are we using in this project?"

**Behind the Scenes:**
```
get_tech_stack(project_id="proj-123")
```

---

### log_change

Log a code change.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Path of changed file |
| `change_type` | string | Yes | "create", "modify", "delete", "refactor" |
| `description` | string | Yes | Change description |
| `project_id` | string | No | Project ID |
| `architecture_impact` | string | No | "none", "minor", "significant" |

**Natural Language Example:**
> "Log that I created the authentication module"

**Behind the Scenes:**
```
log_change(
    project_id="proj-123",
    file_path="src/auth.py",
    change_type="create",
    description="Created authentication module",
    architecture_impact="significant"
)
```

---

### get_recent_changes

Get recent changes to a project.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | No | Project ID |
| `limit` | integer | No | Max results (default: 20) |
| `architecture_impact_filter` | string | No | "all", "none", "minor", "significant" |

**Natural Language Example:**
> "What changes were made recently?"

**Behind the Scenes:**
```
get_recent_changes(project_id="proj-123", limit=10)
```

---

### update_file_metadata

Update metadata for a file.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | File path |
| `project_id` | string | No | Project ID |
| `file_type` | string | No | "source", "test", "config", "doc" |
| `module` | string | No | Module name |
| `purpose` | string | No | File purpose |
| `dependencies` | array | No | Files this depends on |
| `complexity` | string | No | "low", "medium", "high" |

---

### get_file_dependencies

Get dependency graph for a file.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | File path |
| `project_id` | string | No | Project ID |
| `direction` | string | No | "dependencies", "dependents", "both" |

---

### get_module_info

Get detailed module information.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `module_name` | string | Yes | Module name |
| `project_id` | string | No | Project ID |

---

## Context Tools (13)

### register_agent

Register a new agent or reconnect to existing one.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_name` | string | Yes | Agent name (use same name to reconnect) |
| `agent_type` | string | Yes | "opencode", "cursor", "claude_code", "custom" |
| `capabilities` | array | No | List of capabilities |
| `version` | string | No | Agent version |

**Natural Language Example:**
> "Register me as an agent with Python capabilities"

**Behind the Scenes:**
```
register_agent(
    agent_name="DevAgent",
    agent_type="opencode",
    capabilities=["python", "fastapi"]
)
```

**Note:** Using the same `agent_name` across sessions reconnects to the same agent ID.

---

### get_agents_list

Get list of all registered agents.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | "active", "inactive", "all" |

---

### get_agent_profile

Get an agent's profile information.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |

---

### start_context

Start a new work context.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |
| `project_id` | string | No | Project ID |
| `objective` | string | Yes | Current objective |
| `task_description` | string | No | Detailed task |
| `priority` | string | No | "critical", "high", "medium", "low" |

**Natural Language Example:**
> "I'm starting to work on the authentication feature"

**Behind the Scenes:**
```
start_context(
    agent_id="agent-123",
    project_id="proj-456",
    objective="Implement authentication",
    priority="high"
)
```

---

### get_agent_context

Get current context for an agent.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |

---

### switch_context

Switch context between projects or objectives.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |
| `to_project_id` | string | Yes | Target project |
| `to_objective` | string | Yes | New objective |
| `task_description` | string | No | New task description |

---

### end_context

End current context.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |

**Natural Language Example:**
> "I'm done with this task"

**Behind the Scenes:**
```
end_context(agent_id="agent-123")
```

---

### lock_files

Lock files to prevent conflicts.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |
| `project_id` | string | Yes | Project ID |
| `files` | array | Yes | Files to lock |
| `reason` | string | Yes | Reason for locking |
| `expected_duration_minutes` | integer | No | Expected duration |

**Natural Language Example:**
> "I'm going to edit the authentication module"

**Behind the Scenes:**
```
lock_files(
    agent_id="agent-123",
    project_id="proj-456",
    files=["src/auth.py"],
    reason="Implementing JWT authentication"
)
```

---

### unlock_files

Unlock files after work is complete.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |
| `project_id` | string | Yes | Project ID |
| `files` | array | Yes | Files to unlock |

---

### get_locked_files

Get list of currently locked files.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | No | Project ID |

**Natural Language Example:**
> "Which files are currently locked?"

**Behind the Scenes:**
```
get_locked_files(project_id="proj-123")
```

---

### get_context_history

Get recent context history for an agent.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |
| `limit` | integer | No | Max entries (default: 10) |

---

### get_session_log

Get session log for an agent.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |
| `limit` | integer | No | Max entries (default: 50) |

---

### get_agents_in_project

Get all agents working in a project.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | No | Project ID |

---

## Architecture Tools (5)

### analyze_architecture

Analyze current project architecture.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | No | Project ID |

**Natural Language Example:**
> "Analyze the architecture of this project"

**Behind the Scenes:**
```
analyze_architecture(project_id="proj-123")
```

---

### get_architecture_recommendation

Get architectural recommendation for a feature.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `feature_description` | string | Yes | Feature description |
| `project_id` | string | No | Project ID |
| `context` | string | No | Additional context |
| `constraints` | array | No | Implementation constraints |
| `implementation_style` | string | No | "modular", "monolithic" |

**Natural Language Example:**
> "What's the best pattern for implementing a shopping cart?"

**Behind the Scenes:**
```
get_architecture_recommendation(
    project_id="proj-123",
    feature_description="Shopping cart with items, quantities, and checkout"
)
```

**Returns:**
```json
{
  "success": true,
  "recommended_pattern": {
    "pattern": "Repository",
    "confidence": 95
  },
  "file_structure": { ... },
  "implementation_guide": { ... }
}
```

---

### validate_code_structure

Validate proposed code structure.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | File path |
| `code_structure` | object | Yes | Proposed structure |
| `project_id` | string | No | Project ID |
| `strict_mode` | boolean | No | Enable strict validation |

---

### get_design_patterns

Get all available design patterns.

**Natural Language Example:**
> "What design patterns does CoordMCP know about?"

**Behind the Scenes:**
```
get_design_patterns()
```

**Available Patterns:**

| Pattern | Best For |
|---------|----------|
| CRUD | Simple data operations |
| MVC | Web applications |
| Repository | Data access abstraction |
| Service | Business logic layer |
| Factory | Complex object creation |
| Observer | Event-driven systems |
| Adapter | Interface compatibility |
| Strategy | Interchangeable algorithms |
| Decorator | Extending functionality |

---

### update_architecture

Update project architecture after implementation.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `recommendation_id` | string | Yes | Recommendation ID |
| `implementation_summary` | string | Yes | What was implemented |
| `project_id` | string | No | Project ID |
| `actual_files_created` | array | No | Files created |
| `actual_files_modified` | array | No | Files modified |

---

## Task Tools (8)

### create_task

Create a new task in a project.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | Yes | Task title |
| `description` | string | No | Task description |
| `project_id` | string | No | Project ID |
| `project_name` | string | No | Project name |
| `workspace_path` | string | No | Workspace path |
| `priority` | string | No | "critical", "high", "medium", "low" |
| `related_files` | array | No | Related file paths |
| `depends_on` | array | No | Task IDs this depends on |
| `estimated_hours` | float | No | Estimated hours |

---

### get_task

Get task details.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | Yes | Project ID |
| `task_id` | string | Yes | Task ID |

---

### assign_task

Assign a task to an agent.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | Yes | Project ID |
| `task_id` | string | Yes | Task ID |
| `agent_id` | string | Yes | Agent ID |
| `requested_by_user` | boolean | No | User requested |

---

### update_task_status

Update task status.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | Yes | Project ID |
| `task_id` | string | Yes | Task ID |
| `agent_id` | string | Yes | Agent ID |
| `status` | string | Yes | "pending", "in_progress", "blocked", "completed", "cancelled" |
| `notes` | string | No | Status notes |

---

### get_project_tasks

Get all tasks for a project.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | No | Project ID |
| `project_name` | string | No | Project name |
| `workspace_path` | string | No | Workspace path |
| `status` | string | No | Filter by status |
| `assigned_agent_id` | string | No | Filter by agent |

---

### get_my_tasks

Get tasks assigned to an agent.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |
| `status` | string | No | Filter by status |

---

### complete_task

Mark a task as completed.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | Yes | Project ID |
| `task_id` | string | Yes | Task ID |
| `agent_id` | string | Yes | Agent ID |
| `completion_notes` | string | No | Completion notes |

---

### delete_task

Delete (soft delete) a task.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | Yes | Project ID |
| `task_id` | string | Yes | Task ID |
| `agent_id` | string | Yes | Agent ID |
| `reason` | string | No | Deletion reason |

---

## Message Tools (5)

### send_message

Send a message to another agent.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `from_agent_id` | string | Yes | Sender agent ID |
| `to_agent_id` | string | Yes | Recipient agent ID (or "broadcast") |
| `project_id` | string | Yes | Project ID |
| `content` | string | Yes | Message content |
| `message_type` | string | No | "request", "update", "alert", "question", "review" |
| `related_task_id` | string | No | Related task ID |

---

### get_messages

Get messages for an agent.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |
| `project_id` | string | No | Project ID |
| `project_name` | string | No | Project name |
| `workspace_path` | string | No | Workspace path |
| `unread_only` | boolean | No | Only unread messages |
| `limit` | integer | No | Max results (default: 50) |

---

### get_sent_messages

Get messages sent by an agent.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |
| `project_id` | string | No | Project ID |
| `project_name` | string | No | Project name |
| `workspace_path` | string | No | Workspace path |
| `limit` | integer | No | Max results (default: 50) |

---

### mark_message_read

Mark a message as read.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Agent ID |
| `message_id` | string | Yes | Message ID |
| `project_id` | string | No | Project ID |
| `project_name` | string | No | Project name |
| `workspace_path` | string | No | Workspace path |

---

### broadcast_message

Broadcast a message to all agents in a project.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `from_agent_id` | string | Yes | Sender agent ID |
| `project_id` | string | Yes | Project ID |
| `content` | string | Yes | Message content |
| `message_type` | string | No | "request", "update", "alert", "question", "review" |

---

## Health Tools (1)

### get_project_dashboard

Get comprehensive project health dashboard.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | No | Project ID |
| `project_name` | string | No | Project name |
| `workspace_path` | string | No | Workspace path |

**Returns:**
```json
{
  "success": true,
  "health_score": 85,
  "health_status": "Healthy",
  "tasks_summary": { "total": 10, "completed": 7, "in_progress": 2, "blocked": 1 },
  "agents_summary": { "active": 2, "inactive": 1 },
  "locks_summary": { "locked": 3, "available": 15 },
  "recommendations": ["Consider reviewing blocked tasks"]
}
```

---

## Error Types

| Error Type | Description | Solution |
|------------|-------------|----------|
| `ProjectNotFound` | Project doesn't exist | Use `discover_project` first |
| `AgentNotFound` | Agent not registered | Call `register_agent` first |
| `FileLockConflict` | File locked by another agent | Check locked files, coordinate |
| `ValidationError` | Invalid parameters | Check required parameters |
| `InternalError` | Server error | Check logs, retry |

---

## See Also

- [Resources](resources.md) - MCP resources available
- [Data Models](data-models.md) - Data structures
- [Examples](examples/) - Usage examples
