# Getting Started with CoordMCP

Welcome! This guide will get you up and running with CoordMCP in 5 minutes.

## What is CoordMCP?

CoordMCP is a coordination server that helps multiple coding agents (like OpenCode, Cursor, Claude Code) work together without conflicts. It provides:

- 📚 **Long-term Memory** - Track decisions, tech stack, and changes
- 🔄 **Multi-Agent Context** - Switch between projects and tasks
- 🔒 **File Locking** - Prevent agents from overwriting each other's work
- 🏗️ **Architecture Guidance** - Get recommendations without LLM calls
- 🔍 **Project Discovery** - Auto-discover projects by workspace directory

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## Step 1: Install (1 minute)

```bash
# Install from PyPI
pip install coordmcp

# Or install from source
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp
pip install -e .
```

## Step 2: Start the Server (1 minute)

```bash
# Start the CoordMCP server
python -m coordmcp

# Or use the command
coordmcp

# Check version
coordmcp --version
```

You should see:
```
INFO - CoordMCP server initialized and ready
INFO - Server is listening for MCP connections
```

Leave this terminal running. The server is now ready to accept connections.

## Step 3: Configure Your Agent (2 minutes)

### For OpenCode

Create an `opencode.jsonc` file in your project root:

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

See [Integrations](./INTEGRATIONS/) for detailed setup guides for each agent.

## Step 4: Test Your Setup (1 minute)

In your agent, try these commands:

```python
import os

# 1. Discover or create a project
discovery = await coordmcp_discover_project(path=os.getcwd())

if discovery["found"]:
    project_id = discovery["project"]["project_id"]
    print(f"Found existing project: {discovery['project']['project_name']}")
else:
    # Create new project
    result = await coordmcp_create_project(
        project_name="Test Project",
        workspace_path=os.getcwd(),  # Current directory
        description="My first CoordMCP project"
    )
    project_id = result["project_id"]
    print(f"Created project: {result['project_id']}")

# 2. Register yourself
agent = await coordmcp_register_agent(
    agent_name="MyAgent",
    agent_type="opencode",
    capabilities=["python", "testing"]
)
agent_id = agent["agent_id"]
print(f"Registered agent: {agent_id}")

# 3. Save a decision
await coordmcp_save_decision(
    project_id=project_id,
    title="Initial Setup Complete",
    description="CoordMCP is working correctly",
    rationale="Verified basic functionality"
)
print("Decision saved!")
```

If you see success messages, you're all set! 🎉

## Essential Workflow

### 1. Discover or Create Project (Always First!)

```python
import os

# Try to discover existing project
discovery = await coordmcp_discover_project(path=os.getcwd())

if discovery["found"]:
    project_id = discovery["project"]["project_id"]
else:
    # Create new project
    result = await coordmcp_create_project(
        project_name="My App",
        workspace_path=os.getcwd(),  # REQUIRED: Use current directory
        description="A web application"
    )
    project_id = result["project_id"]
```

### 2. Register as Agent

```python
agent = await coordmcp_register_agent(
    agent_name="YourName",  # Use SAME name across sessions
    agent_type="opencode",
    capabilities=["python", "fastapi", "react"]
)
agent_id = agent["agent_id"]
```

**Tip:** Use the same `agent_name` across sessions to reconnect to your identity!

### 3. Check Project State

```python
# See who's working
agents = await coordmcp_get_active_agents(project_id=project_id)

# Check locked files
locked = await coordmcp_get_locked_files(project_id=project_id)

# View recent changes
changes = await coordmcp_get_recent_changes(project_id=project_id, limit=10)
```

### 4. Start Working

```python
await coordmcp_start_context(
    agent_id=agent_id,
    project_id=project_id,
    objective="Implement user authentication",
    priority="high"
)
```

### 5. Lock Files Before Editing

```python
await coordmcp_lock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["src/auth.py", "src/models/user.py"],
    reason="Implementing JWT authentication"
)
```

### 6. Record Decisions & Log Changes

```python
# Save important decisions
await coordmcp_save_decision(
    project_id=project_id,
    title="Use JWT for Authentication",
    description="Implement JWT-based authentication",
    rationale="Stateless, scalable, industry standard"
)

# Log code changes
await coordmcp_log_change(
    project_id=project_id,
    file_path="src/auth.py",
    change_type="create",
    description="Created authentication endpoints"
)
```

### 7. Unlock Files & End Session

```python
# Unlock when done
await coordmcp_unlock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["src/auth.py", "src/models/user.py"]
)

# End your session
await coordmcp_end_context(
    agent_id=agent_id,
    summary="Completed JWT authentication implementation"
)
```

## Quick Example

Here's a complete example:

```python
import os

# 1. Setup
discovery = await coordmcp_discover_project(path=os.getcwd())
if discovery["found"]:
    project_id = discovery["project"]["project_id"]
else:
    result = await coordmcp_create_project(
        project_name="Todo App",
        workspace_path=os.getcwd(),
        description="Simple todo list app"
    )
    project_id = result["project_id"]

# 2. Register
agent = await coordmcp_register_agent(
    agent_name="DevAgent",
    agent_type="opencode",
    capabilities=["javascript", "html", "css"]
)
agent_id = agent["agent_id"]

# 3. Check state
agents = await coordmcp_get_active_agents(project_id=project_id)
print(f"Active agents: {agents['total_count']}")

# 4. Start context
await coordmcp_start_context(
    agent_id=agent_id,
    project_id=project_id,
    objective="Create todo app frontend"
)

# 5. Lock files
await coordmcp_lock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["index.html", "app.js", "styles.css"]
)

# 6. Work & document
# ... do your coding ...

await coordmcp_save_decision(
    project_id=project_id,
    title="Use Vanilla JS",
    description="No frameworks needed",
    rationale="Simple app doesn't need overhead"
)

await coordmcp_log_change(
    project_id=project_id,
    file_path="index.html",
    change_type="create",
    description="Created HTML structure"
)

# 7. Cleanup
await coordmcp_unlock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["index.html", "app.js", "styles.css"]
)

await coordmcp_end_context(agent_id=agent_id)
```

## Flexible Project Lookup

All project tools support flexible identifiers:

```python
# By project ID
await coordmcp_get_project_info(project_id="proj-abc-123")

# By project name
await coordmcp_get_project_info(project_name="My App")

# By workspace path
await coordmcp_get_project_info(workspace_path=os.getcwd())
```

**Priority:** project_id > workspace_path > project_name

## Session Persistence

Your agent identity persists across sessions:

```python
# First session
gent = await coordmcp_register_agent(name="Dev1", type="opencode")
# Returns: agent_id = "agent-xyz-789"

# Second session (same name = same ID!)
agent = await coordmcp_register_agent(name="Dev1", type="opencode")
# Returns: agent_id = "agent-xyz-789" (same!)
```

## What's Next?

### Learn More
- **[Installation Guide](./INSTALLATION.md)** - Detailed setup options
- **[Configuration](./CONFIGURATION.md)** - Environment variables and settings
- **[API Reference](./API_REFERENCE.md)** - All 35+ tools and resources

### Try Examples
- **[Basic Project Setup](./examples/basic-project-setup.md)** - Learn the basics
- **[Architecture Recommendations](./examples/architecture-recommendation.md)** - Get AI guidance
- **[Multi-Agent Workflow](./examples/multi-agent-workflow.md)** - Coordinate agents

### Common Tasks

#### Check Your Context
```python
context = await coordmcp_get_agent_context(agent_id=agent_id)
print(f"Current project: {context['project_id']}")
print(f"Objective: {context['objective']}")
```

#### Get Architecture Advice
```python
rec = await coordmcp_get_architecture_recommendation(
    project_id=project_id,
    feature_description="Add user authentication"
)
print(f"Recommended pattern: {rec['recommended_pattern']['pattern']}")
```

## Troubleshooting

### "Project not found"

```python
# Use discover_project first
discovery = await coordmcp_discover_project(path=os.getcwd())
```

### "Invalid workspace_path"

```python
# Must use absolute path
import os
await coordmcp_create_project(
    project_name="My App",
    workspace_path=os.getcwd()  # ✓ Absolute path
)
```

### More Issues?

See **[Troubleshooting](./TROUBLESHOOTING.md)** for detailed solutions.

## Quick Reference

### Essential Tools

| Tool | Purpose |
|------|---------|
| `discover_project` | Find existing project in directory |
| `create_project` | Create new project (requires workspace_path) |
| `register_agent` | Register/reconnect agent |
| `get_active_agents` | See who's working |
| `start_context` | Start working on task |
| `lock_files` | Prevent file conflicts |
| `save_decision` | Record decisions |
| `log_change` | Log code changes |

### Always Remember

✅ Use `os.getcwd()` for workspace_path  
✅ Call `discover_project` before creating  
✅ Use consistent agent_name across sessions  
✅ Lock files before editing  
✅ Unlock files when done  

## Need Help?

- 📧 **Email**: support@coordmcp.dev
- 💬 **Discord**: [Join our community](https://discord.gg/coordmcp)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

---

**Welcome to CoordMCP!** Start building with confidence. 🚀
