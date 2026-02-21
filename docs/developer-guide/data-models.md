# Data Models

CoordMCP data structures and storage format.

## Storage Location

All data is stored in `~/.coordmcp/` by default:

```
~/.coordmcp/
├── data/
│   ├── memory/{project_id}/    # Project data
│   ├── agents/{agent_id}/      # Agent data
│   └── global/                 # Global registries
└── logs/
    └── coordmcp.log
```

## Project Data

### ProjectInfo

```python
{
    "project_id": "uuid",
    "project_name": "string",
    "description": "string",
    "workspace_path": "string",      # Absolute path
    "project_type": "string",        # webapp, library, api, cli, mobile
    "recommended_workflows": ["string"],  # Workflow names
    "schema_version": "string",
    "created_at": "ISO datetime",
    "updated_at": "ISO datetime",
    "created_by": "agent_id",
    "version": "integer"
}
```

### Decision

```python
{
    "id": "uuid",
    "timestamp": "ISO datetime",
    "title": "string",
    "description": "string",
    "context": "string",
    "rationale": "string",
    "impact": "string",
    "status": "active|archived|superseded",
    "related_files": ["file_path"],
    "author_agent_id": "agent_id",
    "tags": ["tag"],
    "superseded_by": "decision_id",    # If superseded
    "supersedes": ["decision_id"],     # Decisions this replaces
    "valid_from": "ISO datetime",
    "valid_to": "ISO datetime",        # Optional expiration
    "version": "integer",
    "is_deleted": "boolean",
    "metadata": {}
}
```

### TechStackEntry

```python
{
    "category": "backend|frontend|database|infrastructure",
    "technology": "string",
    "version": "string",
    "rationale": "string",
    "decision_ref": "decision_id",
    "added_at": "ISO datetime",
    "updated_at": "ISO datetime"
}
```

### Change

```python
{
    "id": "uuid",
    "timestamp": "ISO datetime",
    "file_path": "string",
    "change_type": "create|modify|delete|refactor",
    "description": "string",
    "code_summary": "string",
    "agent_id": "agent_id",
    "architecture_impact": "none|minor|significant",
    "related_decision": "decision_id",
    "lines_changed": "integer",
    "version": "integer",
    "is_deleted": "boolean",
    "metadata": {}
}
```

### FileMetadata

```python
{
    "id": "string",
    "path": "string",
    "file_type": "source|test|config|doc",
    "last_modified": "ISO datetime",
    "last_modified_by": "agent_id",
    "module": "string",
    "purpose": "string",
    "dependencies": ["file_path"],
    "dependents": ["file_path"],
    "lines_of_code": "integer",
    "complexity": "low|medium|high",
    "related_decisions": ["decision_id"],
    "related_changes": ["change_id"],
    "version": "integer",
    "is_deleted": "boolean"
}
```

### ArchitectureModule

```python
{
    "name": "string",
    "purpose": "string",
    "files": ["file_path"],
    "dependencies": ["module_name"],
    "dependents": ["module_name"],
    "responsibilities": ["string"]
}
```

## Task Data

### Task

```python
{
    "id": "uuid",
    "title": "string",
    "description": "string",
    "status": "pending|in_progress|blocked|completed|cancelled",
    "project_id": "string",
    "assigned_agent_id": "agent_id",
    "requested_agent_id": "agent_id",
    
    # Dependencies
    "depends_on": ["task_id"],
    "parent_task_id": "task_id",
    "child_tasks": ["task_id"],
    
    # Properties
    "priority": "critical|high|medium|low",
    "related_files": ["file_path"],
    "related_decision": "decision_id",
    
    # Time tracking
    "started_at": "ISO datetime",
    "completed_at": "ISO datetime",
    "estimated_hours": "float",
    "actual_hours": "float",
    
    # Base entity fields
    "created_at": "ISO datetime",
    "updated_at": "ISO datetime",
    "version": "integer",
    "is_deleted": "boolean",
    "metadata": {}
}
```

### TaskStatus Enum

| Value | Description |
|-------|-------------|
| `pending` | Task not yet started |
| `in_progress` | Task currently being worked on |
| `blocked` | Task blocked by dependency |
| `completed` | Task finished successfully |
| `cancelled` | Task cancelled |

## Agent Data

### AgentProfile

```python
{
    "agent_id": "uuid",
    "agent_name": "string",
    "agent_type": "opencode|cursor|claude_code|custom",
    "version": "string",
    "capabilities": ["capability"],
    "last_active": "ISO datetime",
    "total_sessions": "integer",
    "projects_involved": ["project_id"],
    "status": "active|inactive|deprecated",
    "typical_objectives": ["string"],
    "last_project_id": "project_id",
    "cross_project_history": [...]
}
```

### AgentContext

```python
{
    "agent_id": "uuid",
    "current_context": {
        "project_id": "uuid",
        "current_objective": "string",
        "task_description": "string",
        "priority": "critical|high|medium|low",
        "current_file": "string",
        "started_at": "ISO datetime",
        "task_id": "task_id"
    },
    "locked_files": [...],
    "history": [...],
    "workflow_state": "string",
    "workflow_progress": ["string"]
}
```

### LockedFile

```python
{
    "file_path": "string",
    "locked_by": "agent_id",
    "locked_at": "ISO datetime",
    "reason": "string",
    "expected_duration_minutes": "integer",
    "expected_unlock_time": "ISO datetime"
}
```

## Messaging Data

### AgentMessage

```python
{
    "id": "uuid",
    "from_agent_id": "agent_id",
    "from_agent_name": "string",
    "to_agent_id": "agent_id|broadcast",
    "project_id": "project_id",
    "message_type": "request|update|alert|question|review",
    "content": "string",
    "related_task_id": "task_id",
    "read": "boolean",
    "read_at": "ISO datetime",
    
    # Base entity fields
    "created_at": "ISO datetime",
    "updated_at": "ISO datetime",
    "version": "integer",
    "is_deleted": "boolean"
}
```

### MessageType Enum

| Value | Description |
|-------|-------------|
| `request` | Request for action |
| `update` | Status update |
| `alert` | Warning or alert |
| `question` | Question needing answer |
| `review` | Code review request |

## Activity Data

### ActivityFeedItem

```python
{
    "id": "uuid",
    "activity_type": "string",  # task_created, task_completed, decision_made, file_changed, etc.
    "agent_id": "agent_id",
    "agent_name": "string",
    "project_id": "project_id",
    "summary": "string",
    "related_entity_id": "string",
    "related_entity_type": "string",  # task, decision, file, etc.
    
    # Base entity fields
    "created_at": "ISO datetime",
    "updated_at": "ISO datetime"
}
```

### SessionSummary

```python
{
    "id": "uuid",
    "agent_id": "agent_id",
    "project_id": "project_id",
    "session_id": "string",
    "duration_minutes": "integer",
    "objective": "string",
    "objectives_completed": ["string"],
    "files_modified": ["file_path"],
    "key_decisions_made": ["decision_id"],
    "blockers_encountered": ["string"],
    "summary_text": "string",
    
    # Base entity fields
    "created_at": "ISO datetime",
    "updated_at": "ISO datetime"
}
```

## Index Models

### DecisionIndex

Used for fast decision lookups:

```python
{
    "by_tag": {"tag": ["decision_id"]},
    "by_author": {"agent_id": ["decision_id"]},
    "by_status": {"status": ["decision_id"]},
    "by_word": {"token": ["decision_id"]},
    "last_updated": "ISO datetime"
}
```

### ChangeIndex

Used for fast change lookups:

```python
{
    "by_file": {"file_path": ["change_id"]},
    "by_agent": {"agent_id": ["change_id"]},
    "by_date": {"YYYY-MM-DD": ["change_id"]},
    "by_type": {"change_type": ["change_id"]},
    "by_decision": {"decision_id": ["change_id"]},
    "last_updated": "ISO datetime"
}
```

### FileMetadataIndex

Used for file dependency tracking:

```python
{
    "by_module": {"module": ["file_path"]},
    "by_type": {"file_type": ["file_path"]},
    "by_complexity": {"complexity": ["file_path"]},
    "dependency_graph": {"file_path": ["dependency_file_path"]},
    "last_updated": "ISO datetime"
}
```

## Relationship Model

### Relationship

```python
{
    "source_type": "decision|file|module|change",
    "source_id": "string",
    "target_type": "decision|file|module|change",
    "target_id": "string",
    "relationship_type": "depends_on|implements|references|supersedes|related_to",
    "created_at": "ISO datetime",
    "created_by": "agent_id",
    "metadata": {}
}
```

## File Structure

### Project Directory

```
~/.coordmcp/data/memory/{project_id}/
├── project_info.json     # Project metadata
├── decisions.json        # All decisions + index
├── tech_stack.json       # Technology stack
├── changes.json          # Change log + index
├── file_metadata.json    # File information + index
├── architecture.json     # Architecture definition
├── tasks.json            # Tasks for this project
├── messages.json         # Agent messages
├── activities.json       # Activity feed
└── sessions.json         # Session summaries
```

### Agent Directory

```
~/.coordmcp/data/agents/{agent_id}/
├── context.json          # Current context
├── locked_files.json     # Locked files
└── session_log.json      # Activity log
```

### Global Registry

```
~/.coordmcp/data/global/
├── agent_registry.json   # All agents
└── project_registry.json # All projects
```

## Enums

### DecisionStatus
- `active` - Current decision
- `archived` - No longer relevant
- `superseded` - Replaced by newer decision

### ChangeType
- `create` - New file created
- `modify` - File modified
- `delete` - File deleted
- `refactor` - File refactored

### ArchitectureImpact
- `none` - No architectural impact
- `minor` - Minor changes
- `significant` - Major architectural changes

### FileType
- `source` - Source code
- `test` - Test files
- `config` - Configuration files
- `doc` - Documentation

### Complexity
- `low` - Simple, straightforward
- `medium` - Moderate complexity
- `high` - Complex, needs attention

### RelationshipType
- `depends_on` - Source depends on target
- `implements` - Source implements target
- `references` - Source references target
- `supersedes` - Source supersedes target
- `related_to` - General relationship

### AgentType
- `opencode` - OpenCode agent
- `cursor` - Cursor IDE agent
- `claude_code` - Claude Code CLI agent
- `custom` - Custom agent

### AgentStatus
- `active` - Currently active
- `inactive` - Not recently active
- `deprecated` - No longer used

## Base Entity

All entities inherit from `BaseEntity` which provides:

```python
{
    "id": "string",
    "created_at": "ISO datetime",
    "updated_at": "ISO datetime",
    "created_by": "agent_id",
    "updated_by": "agent_id",
    "version": "integer",        # For optimistic locking
    "is_deleted": "boolean",     # Soft delete flag
    "deleted_at": "ISO datetime",
    "metadata": {}               # Extensible metadata
}
```

### Base Entity Methods

| Method | Description |
|--------|-------------|
| `touch(agent_id)` | Update timestamps and increment version |
| `soft_delete(agent_id)` | Mark as deleted |
| `restore(agent_id)` | Restore from soft delete |

## See Also

- [API Reference](api-reference.md) - Tools that work with these models
- [Resources](resources.md) - MCP resources
- [Architecture Decisions](../adr/0001-record-architecture-decisions.md) - Design decisions
