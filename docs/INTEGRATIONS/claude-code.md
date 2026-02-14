# Claude Code Integration

Complete setup guide for using CoordMCP with Claude Code CLI.

## Prerequisites

- Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code`)
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

### 2. Configure Claude Code

Claude Code uses a JSON configuration file for MCP servers.

**Location**: `~/.claude/config.json` or project-level `.claude/config.json`

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp"],
      "env": {
        "COORDMCP_DATA_DIR": "~/.coordmcp/data",
        "COORDMCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Windows users**:
```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp"],
      "env": {
        "COORDMCP_DATA_DIR": "C:\\Users\\username\\.coordmcp\\data"
      }
    }
  }
}
```

### 3. Alternative: Project-Level Configuration

Create `.claude/config.json` in your project root:

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp"],
      "env": {
        "COORDMCP_DATA_DIR": "./.coordmcp/data"
      }
    }
  }
}
```

### 4. Verify Integration

In Claude Code, try:

```python
import os

# Discover or create project
discovery = await coordmcp_discover_project(path=os.getcwd())

if discovery["found"]:
    print(f"Found: {discovery['project']['project_name']}")
else:
    result = await coordmcp_create_project(
        project_name="Claude Test",
        workspace_path=os.getcwd(),
        description="Testing with Claude"
    )
    print(f"Created: {result['project_id']}")
```

## Usage in Claude Code

### Complete Workflow

```python
import os

# 1. Discover or create project (ALWAYS FIRST)
discovery = await coordmcp_discover_project(path=os.getcwd())

if discovery["found"]:
    project_id = discovery["project"]["project_id"]
else:
    result = await coordmcp_create_project(
        project_name="My Project",
        workspace_path=os.getcwd(),  # REQUIRED
        description="Claude Code project"
    )
    project_id = result["project_id"]

# 2. Register as agent (use SAME name across sessions)
agent = await coordmcp_register_agent(
    agent_name="ClaudeDev",
    agent_type="claude_code",
    capabilities=["python", "typescript"]
)
agent_id = agent["agent_id"]

# 3. Check who's working
agents = await coordmcp_get_active_agents(project_id=project_id)

# 4. Start working
await coordmcp_start_context(
    agent_id=agent_id,
    project_id=project_id,
    objective="Implement feature X"
)

# 5. Lock files
await coordmcp_lock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["src/main.py"],
    reason="Working on feature"
)

# 6. Get architecture advice (optional)
rec = await coordmcp_get_architecture_recommendation(
    project_id=project_id,
    feature_description="Add user authentication"
)

# 7. Work and document
await coordmcp_save_decision(
    project_id=project_id,
    title="Use JWT",
    description="JWT for auth",
    rationale="Stateless"
)

await coordmcp_log_change(
    project_id=project_id,
    file_path="src/auth.py",
    change_type="create",
    description="Created auth"
)

# 8. Cleanup
await coordmcp_unlock_files(agent_id=agent_id, project_id=project_id, files=["src/main.py"])
await coordmcp_end_context(agent_id=agent_id)
```

### Natural Language

Claude Code understands natural language:

```
I want to start a new project for our API. Can you use coordmcp to set that up?
```

Claude will:
1. Call `coordmcp_discover_project` to check for existing project
2. Call `coordmcp_create_project` if needed
3. Return the project ID

### Key Points

- Use `os.getcwd()` for workspace_path
- Use consistent agent_name to reconnect
- Always lock files before editing
- Session persists across Claude Code restarts

## Troubleshooting

### "command not found: claude"

```bash
npm install -g @anthropic-ai/claude-code
```

### "MCP server not connecting"

1. Verify CoordMCP is installed: `pip show coordmcp`
2. Check config location: `cat ~/.claude/config.json`
3. Verify JSON syntax: `cat ~/.claude/config.json | python -m json.tool`

### "python: command not found"

Use full Python path:
```json
{
  "command": "/usr/bin/python3",
  "args": ["-m", "coordmcp"]
}
```

## Getting Help

- 📧 **Email**: support@coordmcp.dev
- 💬 **Discord**: [Join our community](https://discord.gg/coordmcp)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

---

**Happy coding with Claude Code + CoordMCP!** 🚀
