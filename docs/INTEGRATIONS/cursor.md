# Cursor Integration

Complete setup guide for using CoordMCP with Cursor IDE.

## Prerequisites

- Cursor IDE installed
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

### 2. Configure Cursor

Open Cursor Settings and add MCP server configuration.

**Path**: `Cursor` → `Settings` → `MCP` → `Add Server`

Or edit settings.json directly:

**Location**: `~/.cursor/mcp.json` or Cursor settings

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp.main"],
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
      "args": ["-m", "coordmcp.main"],
      "env": {
        "COORDMCP_DATA_DIR": "C:\\Users\\username\\.coordmcp\\data"
      }
    }
  }
}
```

### 3. Alternative: Project-Level Config

Create `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp.main"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src",
        "COORDMCP_DATA_DIR": "${workspaceFolder}/src/data"
      }
    }
  }
}
```

### 4. Start CoordMCP

```bash
python -m coordmcp.main
```

Wait for:
```
INFO - CoordMCP server initialized and ready
```

### 5. Restart Cursor

⚠️ **Important**: Fully restart Cursor to load MCP tools.

### 6. Verify Integration

In Cursor Chat, try:

```
Create a project called "Cursor Test" with description "Testing integration"
```

Or use Composer:
```python
result = await create_project(
    project_name="Cursor Test",
    description="Testing CoordMCP with Cursor"
)
```

If a project ID is returned, success! 🎉

## Configuration Options

### Global Configuration

Add to Cursor's global settings:

**Path**: `~/.cursor/settings.json`

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "/full/path/to/python",
      "args": ["-m", "coordmcp.main"]
    }
  }
}
```

### Workspace Configuration

Add to `.vscode/settings.json` in your workspace:

```json
{
  "cursor.mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp.main"]
    }
  }
}
```

## Usage in Cursor

### Using Chat

Simply mention tools in your prompts:

```
Use coordmcp to create a new project for our API
```

Or be specific:
```
create_project(project_name="Auth Service", description="Authentication microservice")
```

### Using Composer

In Composer mode, you can write Python code:

```python
# Setup project
project = await create_project(
    project_name="E-commerce Platform",
    description="Full-stack e-commerce app"
)

# Get architecture advice
rec = await get_architecture_recommendation(
    project_id=project["project_id"],
    feature_description="Shopping cart functionality",
    implementation_style="modular"
)

# Register as agent
agent = await register_agent(
    agent_name="CursorDev",
    agent_type="cursor",
    capabilities=["typescript", "react", "nodejs"]
)
```

### Accessing Tools

In Cursor:
1. Open **Chat** (Cmd/Ctrl + L)
2. Type `/` to see available tools
3. Or type tool name directly

### Example Workflow

```python
# 1. Create project
project = await create_project(
    project_name="SaaS Dashboard",
    description="Admin dashboard for SaaS platform"
)

# 2. Register
agent = await register_agent(
    agent_name="FrontendCursor",
    agent_type="cursor",
    capabilities=["typescript", "react", "tailwind"]
)

# 3. Start context
await start_context(
    agent_id=agent["agent_id"],
    project_id=project["project_id"],
    objective="Build authentication UI"
)

# 4. Lock files
await lock_files(
    agent_id=agent["agent_id"],
    project_id=project["project_id"],
    files=["src/components/Auth/Login.tsx"],
    reason="Implementing login form"
)

# 5. Get recommendation
rec = await get_architecture_recommendation(
    project_id=project["project_id"],
    feature_description="Form validation and state management",
    implementation_style="modular"
)

# 6. Save decision
await save_decision(
    project_id=project["project_id"],
    title="Use React Hook Form",
    description="Implement forms with React Hook Form",
    rationale="Better validation, performance, DX"
)
```

## Troubleshooting

### "MCP servers not loading"

1. Check config file location:
   ```bash
   ls ~/.cursor/mcp.json
   # or
   ls .cursor/mcp.json
   ```

2. Verify JSON syntax:
   ```bash
   cat ~/.cursor/mcp.json | python -m json.tool
   ```

3. Check Cursor logs:
   - Open Command Palette: `Cmd/Ctrl + Shift + P`
   - Type: "Developer: Toggle Developer Tools"
   - Check Console for errors

### "python command not found"

Use full Python path:

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "/usr/bin/python3",
      "args": ["-m", "coordmcp.main"]
    }
  }
}
```

Find your Python path:
```bash
which python
# or
which python3
```

### "Tools not appearing in chat"

1. Ensure server is running:
   ```bash
   python -m coordmcp.main
   ```

2. Full restart of Cursor:
   - Quit completely (Cmd/Ctrl + Q)
   - Reopen Cursor

3. Check MCP panel:
   - Settings → MCP
   - Should see "coordmcp" listed

### "Permission denied"

```bash
chmod -R 755 ~/.coordmcp/data
```

On Windows, ensure your user has write access to the data directory.

## Advanced Features

### Using with Cursor's AI

Combine Cursor's AI with CoordMCP:

```
Can you help me implement user authentication? First, let me check what pattern CoordMCP recommends.

[get_architecture_recommendation for auth system]

Based on the recommendation, implement JWT authentication with these requirements...
```

### Tab Completion

Cursor provides tab completion for CoordMCP tools once integrated:

```python
# Type:
await create_

# Press Tab, Cursor suggests:
await create_project(
    project_name="",
    description=""
)
```

## Tips for Cursor Users

1. **Use natural language** - Cursor understands context
2. **Reference tools explicitly** - "Use coordmcp to..."
3. **Check Composer** - Better for multi-step workflows
4. **Save frequently** - Log changes after completing features
5. **Lock before editing** - Prevent conflicts with other agents

## VS Code Extension

If using Cursor's VS Code extension:

1. Install extension
2. Add to VS Code settings.json:
   ```json
   {
     "cursor.mcpServers": {
       "coordmcp": {
         "command": "python",
         "args": ["-m", "coordmcp.main"]
       }
     }
   }
   ```

## Next Steps

- Try [Multi-Agent Workflow](../examples/multi-agent-workflow.md)
- Learn [Architecture Recommendations](../examples/architecture-recommendation.md)
- Read the full [API Reference](../API_REFERENCE.md)

## Getting Help

- 📧 **Email**: support@coordmcp.dev
- 💬 **Discord**: [Join our community](https://discord.gg/coordmcp)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

---

**Happy coding with Cursor + CoordMCP!** 🚀
