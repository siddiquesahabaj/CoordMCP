# OpenCode Integration

Complete setup guide for using CoordMCP with OpenCode.

## Prerequisites

- OpenCode installed and configured
- Python 3.10+ installed
- CoordMCP installed (`pip install coordmcp`)

## Step-by-Step Setup

### 1. Install CoordMCP

```bash
# Install from PyPI
pip install coordmcp

# Or from source
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp
pip install -e .
```

### 2. Configure OpenCode

Create or edit your OpenCode configuration file.

**Location**: Project root or `~/.config/opencode/opencode.jsonc`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "coordmcp": {
      "type": "local",
      "command": ["python", "-m", "coordmcp"],
      "enabled": true,
      "environment": {
        "COORDMCP_DATA_DIR": "${workspaceFolder}/.coordmcp/data",
        "COORDMCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Windows users** - use forward slashes or escaped backslashes:
```json
{
  "COORDMCP_DATA_DIR": "C:/Users/username/coordmcp/src/data"
}
```

### 3. Start CoordMCP

```bash
python -m coordmcp

# Or using the command
coordmcp
```

You should see:
```
INFO - CoordMCP server initialized and ready
```

### 4. Start OpenCode

```bash
opencode
```

### 5. Verify Integration

In OpenCode, try:

```python
import os

# 1. Discover or create project
discovery = await coordmcp_discover_project(path=os.getcwd())

if discovery["found"]:
    project_id = discovery["project"]["project_id"]
    print(f"Found project: {discovery['project']['project_name']}")
else:
    result = await coordmcp_create_project(
        project_name="OpenCode Test",
        workspace_path=os.getcwd(),
        description="Testing CoordMCP with OpenCode"
    )
    project_id = result["project_id"]
    print(f"Created project: {project_id}")

# 2. Register as agent
agent = await coordmcp_register_agent(
    agent_name="OpenCodeDev",
    agent_type="opencode",
    capabilities=["python", "backend"]
)
print(f"Agent: {agent['agent_id']}")
```

If you see project and agent IDs, you're all set! 🎉

## Configuration Options

### Project-Level Config

Create `opencode.jsonc` in your project:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "coordmcp": {
      "type": "local",
      "command": ["python", "-m", "coordmcp"],
      "enabled": true,
      "environment": {
        "COORDMCP_DATA_DIR": "${workspaceFolder}/.coordmcp/data",
        "COORDMCP_LOG_LEVEL": "INFO"
      }
    }
  },
  "tools": {
    "coordmcp_*": true
  },
  "agent": {
    "default": {
      "system": [
        "You are integrated with CoordMCP for multi-agent coordination.",
        "",
        "=== CRITICAL WORKFLOW ===",
        "1. ALWAYS call coordmcp_discover_project(path=os.getcwd()) first",
        "2. If not found, create with coordmcp_create_project(name, workspace_path=os.getcwd(), description)",
        "3. Register with coordmcp_register_agent(name, type='opencode', capabilities)",
        "4. Use coordmcp_start_context(agent_id, project_id, objective)",
        "5. Lock files: coordmcp_lock_files(agent_id, project_id, files=['src/file.py'])",
        "6. Save decisions: coordmcp_save_decision(project_id, title, description, rationale)",
        "7. Log changes: coordmcp_log_change(project_id, file_path, change_type, description)",
        "8. Unlock files when done: coordmcp_unlock_files(agent_id, project_id, files)",
        "9. End session: coordmcp_end_context(agent_id)",
        "",
        "Always use os.getcwd() for workspace_path parameter."
      ]
    }
  }
}
```

## Usage in OpenCode

### Complete Workflow Example

```python
import os

# 1. Discover or create project (ALWAYS FIRST)
discovery = await coordmcp_discover_project(path=os.getcwd())

if discovery["found"]:
    project_id = discovery["project"]["project_id"]
    print(f"Found existing project: {discovery['project']['project_name']}")
else:
    result = await coordmcp_create_project(
        project_name="My Project",
        workspace_path=os.getcwd(),  # REQUIRED
        description="A web application"
    )
    project_id = result["project_id"]

# 2. Register as agent (use SAME name across sessions!)
agent = await coordmcp_register_agent(
    agent_name="OpenCodeDev",
    agent_type="opencode",
    capabilities=["python", "fastapi"]
)
agent_id = agent["agent_id"]

# 3. Check who's working
agents = await coordmcp_get_active_agents(project_id=project_id)
print(f"Active agents: {agents['total_count']}")

# 4. Start working
await coordmcp_start_context(
    agent_id=agent_id,
    project_id=project_id,
    objective="Implement feature X",
    priority="high"
)

# 5. Lock files
await coordmcp_lock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["src/feature.py"],
    reason="Working on feature X"
)

# 6. Get architecture advice (optional)
rec = await coordmcp_get_architecture_recommendation(
    project_id=project_id,
    feature_description="Add user authentication"
)

# 7. Do your work...

# 8. Save decisions
await coordmcp_save_decision(
    project_id=project_id,
    title="Use JWT Authentication",
    description="Implement JWT-based auth",
    rationale="Stateless and scalable"
)

# 9. Log changes
await coordmcp_log_change(
    project_id=project_id,
    file_path="src/auth.py",
    change_type="create",
    description="Created auth module"
)

# 10. Unlock files
await coordmcp_unlock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["src/feature.py"]
)

# 11. End session
await coordmcp_end_context(
    agent_id=agent_id,
    summary="Completed feature X implementation"
)
```

### Flexible Project Lookup

All tools support flexible identifiers:

```python
# By project ID
await coordmcp_get_project_info(project_id="proj-abc-123")

# By project name
await coordmcp_get_project_info(project_name="My App")

# By workspace path
await coordmcp_get_project_info(workspace_path=os.getcwd())
```

### Session Persistence

Use the same agent name to reconnect:

```python
# First session
gent = await coordmcp_register_agent(name="Dev1", type="opencode")
# Returns: agent_id = "agent-xyz-789"

# Second session (same name = reconnect)
agent = await coordmcp_register_agent(name="Dev1", type="opencode")
# Returns: agent_id = "agent-xyz-789" (same ID!)
```

## Troubleshooting

### "coordmcp not found"

```bash
# Verify Python path
which python

# Use full path in config
{
  "command": "/usr/bin/python3",
  "args": ["-m", "coordmcp"]
}
```

### "Tools don't appear"

1. Check server is running:
   ```bash
   python -m coordmcp
   ```

2. Restart OpenCode completely:
   ```bash
   # Close and reopen
   ```

3. Check configuration syntax:
   ```bash
   cat opencode.jsonc | python -m json.tool
   ```

### "Project not found"

```python
# Always use discover_project first
discovery = await coordmcp_discover_project(path=os.getcwd())
```

### "Invalid workspace_path"

```python
# Must use absolute path
import os
await coordmcp_create_project(
    project_name="My App",
    workspace_path=os.getcwd()  # ✓ Correct
)
```

## Advanced Configuration

### Multiple Projects

Use project-specific configs:

```json
{
  "mcp": {
    "coordmcp": {
      "environment": {
        "COORDMCP_DATA_DIR": "${workspaceFolder}/.coordmcp/data"
      }
    }
  }
}
```

### Debugging

Enable debug logging:

```json
{
  "mcp": {
    "coordmcp": {
      "environment": {
        "COORDMCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

View logs:
```bash
tail -f ~/.coordmcp/logs/coordmcp.log
```

## Tips for OpenCode Users

1. **Use discover_project first** - Always check if project exists
2. **Use os.getcwd()** - For workspace_path parameter
3. **Consistent agent_name** - Same name reconnects to same identity
4. **Lock files** - Always lock before editing
5. **Save decisions** - Document technical choices
6. **Log changes** - Maintain audit trail

## Next Steps

- Try [Basic Project Setup](../examples/basic-project-setup.md)
- Learn [Context Switching](../examples/context-switching.md)
- Read the [API Reference](../API_REFERENCE.md)

## Getting Help

- 📧 **Email**: support@coordmcp.dev
- 💬 **Discord**: [Join our community](https://discord.gg/coordmcp)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

---

**Happy coding with OpenCode + CoordMCP!** 🚀
