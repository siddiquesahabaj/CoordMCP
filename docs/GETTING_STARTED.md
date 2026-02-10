# Getting Started with CoordMCP

Welcome! This guide will get you up and running with CoordMCP in 5 minutes.

## What is CoordMCP?

CoordMCP is a coordination server that helps multiple coding agents (like OpenCode, Cursor, Claude Code) work together without conflicts. It provides:

- 📚 **Long-term Memory** - Track decisions, tech stack, and changes
- 🔄 **Context Management** - Switch between projects and tasks
- 🔒 **File Locking** - Prevent agents from overwriting each other's work
- 🏗️ **Architecture Guidance** - Get recommendations without LLM calls

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Step 1: Install (1 minute)

```bash
# Clone the repository
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp

# Install CoordMCP
pip install -e .
```

## Step 2: Start the Server (1 minute)

```bash
python -m coordmcp.main
```

You should see:
```
INFO - Starting CoordMCP server...
INFO - CoordMCP server initialized and ready
```

Leave this terminal running. The server is now ready to accept connections.

## Step 3: Configure Your Agent (2 minutes)

### For OpenCode

Add to your OpenCode configuration (`opencode.jsonc`):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "coordmcp": {
      "type": "local",
      "command": ["python", "-m", "coordmcp.main"],
      "enabled": true,
      "environment": {
        "COORDMCP_DATA_DIR": "./src/data",
        "COORDMCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### For Cursor

Add to Cursor's MCP settings:

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp.main"]
    }
  }
}
```

See [Integrations](./INTEGRATIONS/) for detailed setup guides for each agent.

## Step 4: Test Your Setup (1 minute)

In your agent, try these commands:

```python
# Create your first project
result = await create_project(
    project_name="Test Project",
    description="My first CoordMCP project"
)
print(f"Created project: {result['project_id']}")

# Register yourself
agent_result = await register_agent(
    agent_name="MyAgent",
    agent_type="opencode",
    capabilities=["python", "testing"]
)
print(f"Registered agent: {agent_result['agent_id']}")

# Save a decision
await save_decision(
    project_id=result["project_id"],
    title="Initial Setup Complete",
    description="CoordMCP is working correctly",
    rationale="Verified basic functionality"
)
```

If you see success messages, you're all set! 🎉

## What's Next?

### Learn More
- **[Installation Guide](./INSTALLATION.md)** - Detailed setup options
- **[Configuration](./CONFIGURATION.md)** - Environment variables and settings
- **[API Reference](./API_REFERENCE.md)** - All 29 tools and 14 resources

### Try Examples
- **[Basic Project Setup](./examples/basic-project-setup.md)** - Learn the basics
- **[Architecture Recommendations](./examples/architecture-recommendation.md)** - Get AI guidance
- **[Multi-Agent Workflow](./examples/multi-agent-workflow.md)** - Coordinate agents

### Common Tasks

#### Check Your Context
```python
# See what you're working on
context = await get_agent_context(agent_id="your-agent-id")
print(f"Current project: {context['project_id']}")
print(f"Objective: {context['objective']}")
```

#### Lock Files You're Working On
```python
# Prevent conflicts
await lock_files(
    agent_id="your-agent-id",
    project_id="your-project-id",
    files=["src/main.py", "src/config.py"],
    reason="Implementing feature X"
)
```

#### Get Architecture Advice
```python
# Get recommendations without LLM calls
rec = await get_architecture_recommendation(
    project_id="your-project-id",
    feature_description="Add user authentication",
    implementation_style="modular"
)
print(f"Recommended pattern: {rec['recommended_pattern']['pattern']}")
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'coordmcp'"

Make sure you're in the project directory and installed with:
```bash
pip install -e .
```

### "Tools not appearing in agent"

1. Check the server is running: `python -m coordmcp.main`
2. Verify your configuration syntax
3. Restart your agent

### More Issues?

See **[Troubleshooting](./TROUBLESHOOTING.md)** for detailed solutions.

## Quick Reference

### Essential Tools

| Tool | Purpose |
|------|---------|
| `create_project` | Create a new project |
| `register_agent` | Register yourself as an agent |
| `start_context` | Start working on a task |
| `save_decision` | Record an architectural decision |
| `lock_files` | Prevent file conflicts |
| `get_architecture_recommendation` | Get design guidance |

### Essential Resources

| Resource | Purpose |
|----------|---------|
| `project://{id}` | Project overview |
| `agent://{id}` | Agent profile |
| `agent://{id}/locked-files` | See locked files |

## Need Help?

- 📧 **Email**: support@coordmcp.dev
- 💬 **Discord**: [Join our community](https://discord.gg/coordmcp)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

---

**Welcome to CoordMCP!** Start building with confidence. 🚀
