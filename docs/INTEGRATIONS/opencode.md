# OpenCode Integration

Complete setup guide for using CoordMCP with OpenCode.

## Prerequisites

- OpenCode installed and configured
- Python 3.8+ installed
- CoordMCP cloned and installed

## Step-by-Step Setup

### 1. Install CoordMCP

```bash
# Clone repository
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp

# Install
pip install -e .
```

### 2. Configure OpenCode

Create or edit your OpenCode configuration file.

**Location**: Project root or `~/.opencode/opencode.jsonc`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "coordmcp": {
      "type": "local",
      "command": [
        "python",
        "-m",
        "coordmcp.main"
      ],
      "enabled": true,
      "environment": {
        "COORDMCP_DATA_DIR": "./src/data",
        "COORDMCP_LOG_LEVEL": "INFO",
        "PYTHONPATH": "./src"
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
python -m coordmcp.main
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
# Create a test project
result = await create_project(
    project_name="OpenCode Test",
    description="Testing CoordMCP with OpenCode"
)
print(f"Project ID: {result['project_id']}")
```

If you see a project ID, you're all set! 🎉

## Configuration Options

### Project-Level Config

Create `.opencode/opencode.jsonc` in your project:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "coordmcp": {
      "type": "local",
      "command": ["python", "-m", "coordmcp.main"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src",
        "COORDMCP_DATA_DIR": "${workspaceFolder}/src/data"
      }
    }
  }
}
```

### Global Config

Add to `~/.opencode/opencode.jsonc` for global availability:

```json
{
  "mcp": {
    "coordmcp": {
      "type": "local",
      "command": ["/full/path/to/python", "-m", "coordmcp.main"],
      "enabled": true
    }
  }
}
```

## Usage in OpenCode

### Basic Workflow

```python
# 1. Create project
project = await create_project(
    project_name="My Project",
    description="Description here"
)
project_id = project["project_id"]

# 2. Register as agent
agent = await register_agent(
    agent_name="OpenCodeDev",
    agent_type="opencode",
    capabilities=["python", "backend"]
)
agent_id = agent["agent_id"]

# 3. Start working
await start_context(
    agent_id=agent_id,
    project_id=project_id,
    objective="Implement feature X",
    priority="high"
)

# 4. Lock files
await lock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["src/feature.py"],
    reason="Working on feature X"
)
```

### Viewing Tools

In OpenCode:
- Tools appear in the **MCP Tools** section
- Use `/` command to access tools
- Or type tool names directly in chat

### Example Session

```python
# Project setup
project = await create_project(
    project_name="E-commerce API",
    description="REST API for e-commerce"
)

# Get architecture advice
rec = await get_architecture_recommendation(
    project_id=project["project_id"],
    feature_description="User authentication system",
    implementation_style="modular"
)

# Save decision
await save_decision(
    project_id=project["project_id"],
    title="Use JWT Authentication",
    description="Implement JWT-based auth",
    rationale="Stateless, scalable, industry standard"
)

# Log change
await log_change(
    project_id=project["project_id"],
    file_path="src/auth.py",
    change_type="create",
    description="Created auth module"
)
```

## Troubleshooting

### "coordmcp not found"

```bash
# Verify Python path
which python

# Use full path in config
{
  "command": "/usr/bin/python3",
  "args": ["-m", "coordmcp.main"]
}
```

### "Tools don't appear"

1. Check server is running:
   ```bash
   python -m coordmcp.main
   ```

2. Restart OpenCode completely:
   ```bash
   opencode --restart
   ```

3. Check configuration syntax:
   ```bash
   cat .opencode/opencode.jsonc | python -m json.tool
   ```

### "Permission denied"

```bash
# Fix data directory permissions
chmod -R 755 ~/.coordmcp/data
```

### "Module errors"

```bash
# Ensure PYTHONPATH includes src
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or install in editable mode
pip install -e .
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

1. **Use `/` commands** - Quick access to tools
2. **Save context** - Always start_context before working
3. **Lock files** - Prevent conflicts with other agents
4. **Log changes** - Maintain audit trail
5. **Check locked files** - Before starting work

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
