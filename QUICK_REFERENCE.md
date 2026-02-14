# CoordMCP Quick Reference

Quick guide for using CoordMCP multi-agent coordination system.

## 3-Step Startup (Always Do This First)

```python
import os

# 1. Discover or Create Project
discovery = await coordmcp_discover_project(path=os.getcwd())
if discovery["found"]:
    project_id = discovery["project"]["project_id"]
else:
    result = await coordmcp_create_project(
        project_name="Project Name",
        workspace_path=os.getcwd(),  # REQUIRED: Use current directory
        description="Brief description"
    )
    project_id = result["project_id"]

# 2. Register as Agent
agent = await coordmcp_register_agent(
    agent_name="YourName",  # Use SAME name across sessions
    agent_type="opencode",  # or "cursor", "claude_code"
    capabilities=["python", "fastapi"]  # Your skills
)
agent_id = agent["agent_id"]

# 3. Start Context
await coordmcp_start_context(
    agent_id=agent_id,
    project_id=project_id,
    objective="What you're building",
    priority="high"  # high, medium, low
)
```

## Core Workflow While Working

### Before Coding
```python
# Check who's working
agents = await coordmcp_get_active_agents(project_id=project_id)

# Check locked files
locked = await coordmcp_get_locked_files(project_id=project_id)

# Lock files before editing
await coordmcp_lock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["src/file.py"],
    reason="What you're doing"
)
```

### While Coding
```python
# Record important decisions
await coordmcp_save_decision(
    project_id=project_id,
    title="Use FastAPI",
    description="Using FastAPI for backend API",
    rationale="Async support, automatic docs"
)

# Track technologies
await coordmcp_update_tech_stack(
    project_id=project_id,
    category="backend",  # backend, frontend, database, infrastructure
    technology="FastAPI",
    version="0.104.0"
)
```

### After Coding
```python
# Log changes
await coordmcp_log_change(
    project_id=project_id,
    file_path="src/file.py",
    change_type="create",  # create, modify, delete, refactor
    description="Created API endpoint"
)

# Unlock files
await coordmcp_unlock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["src/file.py"]
)

# End session
await coordmcp_end_context(
    agent_id=agent_id,
    summary="What you completed"
)
```

## Essential Rules

✅ **DO:**
- Always use `os.getcwd()` for `workspace_path`
- Use consistent `agent_name` across sessions
- Lock files BEFORE editing
- Save decisions for technical choices
- Log changes after completing work
- Unlock files when done

❌ **DON'T:**
- Skip any workflow steps
- Edit files without locking
- Forget to record decisions
- Leave files locked
- Use relative paths

## Tool Quick Reference

**Project:**
- `discover_project(path)` - Find existing project
- `create_project(name, workspace_path, description)` - Create new
- `get_project(id/name/path)` - Get project info

**Agent:**
- `register_agent(name, type, capabilities)` - Register yourself
- `get_active_agents(project_id)` - See who's working

**Context:**
- `start_context(agent_id, project_id, objective)` - Start working
- `get_locked_files(project_id)` - Check locks
- `lock_files(agent_id, project_id, files, reason)` - Lock files
- `unlock_files(agent_id, project_id, files)` - Unlock files
- `end_context(agent_id)` - Finish session

**Memory:**
- `save_decision(project_id, title, description, rationale)` - Record decisions
- `update_tech_stack(project_id, category, technology)` - Track tech
- `log_change(project_id, file_path, change_type, description)` - Log changes
- `get_recent_changes(project_id)` - View activity

**Architecture:**
- `get_architecture_recommendation(project_id, feature)` - Get guidance

## Flexible Project Lookup

All project tools accept any of these:
- `project_id="proj-abc-123"` - Exact ID
- `project_name="Todo App"` - Project name
- `workspace_path=os.getcwd()` - Directory path

**Priority:** project_id > workspace_path > project_name

## Example Session

```python
import os

# 1. Setup
discovery = await coordmcp_discover_project(path=os.getcwd())
project_id = discovery["project"]["project_id"] if discovery["found"] else \
    (await coordmcp_create_project("MyApp", os.getcwd(), "Description"))["project_id"]

agent = await coordmcp_register_agent("Dev1", "opencode", ["python"])
agent_id = agent["agent_id"]

await coordmcp_start_context(agent_id, project_id, "Build feature X")

# 2. Work
await coordmcp_lock_files(agent_id, project_id, ["app.py"], "Adding feature")
# ... code ...

await coordmcp_save_decision(project_id, "Use Redis", "For caching", "Performance")
await coordmcp_update_tech_stack(project_id, "backend", "Redis", "7.0")
await coordmcp_log_change(project_id, "app.py", "modify", "Added Redis cache")

# 3. Cleanup
await coordmcp_unlock_files(agent_id, project_id, ["app.py"])
await coordmcp_end_context(agent_id, "Feature X complete")
```

## Troubleshooting

**"Project not found":**
```python
# Use discover_project first
discovery = await coordmcp_discover_project(path=os.getcwd())
```

**"Files locked":**
```python
# Check who's locking
locked = await coordmcp_get_locked_files(project_id=project_id)
# Wait or coordinate with that agent
```

**"Invalid workspace_path":**
- Must use absolute path: `os.getcwd()` not `"./project"`
- Directory must exist

## Key Points

1. **Workspace linking:** Projects are tied to directories via `workspace_path`
2. **Session persistence:** Your agent identity persists across sessions with same name
3. **Multi-agent:** Other agents can discover and work on same project
4. **Conflict prevention:** File locks prevent editing conflicts
5. **Decision history:** All technical choices are recorded for future reference

## Remember

**Coordination prevents conflicts.** Use CoordMCP for EVERY project to:
- Track decisions and rationale
- Prevent file conflicts
- Maintain context across sessions
- Enable multi-agent collaboration
- Build project history
