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
    "created_at": "ISO datetime",
    "updated_at": "ISO datetime",
    "created_by": "agent_id",
    "version": "string"
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
    "tags": ["tag"]
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
    "related_decision": "decision_id"
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
    "complexity": "low|medium|high"
}
```

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
    "status": "active|inactive|deprecated"
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
        "started_at": "ISO datetime"
    },
    "locked_files": [...],
    "history": [...]
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

## File Structure

### Project Directory

```
~/.coordmcp/data/memory/{project_id}/
├── project_info.json     # Project metadata
├── decisions.json        # All decisions
├── tech_stack.json       # Technology stack
├── changes.json          # Change log
├── file_metadata.json    # File information
└── architecture.json     # Architecture definition
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

### AgentType
- `opencode` - OpenCode agent
- `cursor` - Cursor IDE agent
- `claude_code` - Claude Code CLI agent
- `custom` - Custom agent

### AgentStatus
- `active` - Currently active
- `inactive` - Not recently active
- `deprecated` - No longer used

## See Also

- [API Reference](api-reference.md) - Tools that work with these models
- [Resources](resources.md) - MCP resources
