# Windsurf Integration

Complete setup guide for using CoordMCP with Windsurf IDE.

## Prerequisites

- Windsurf IDE installed
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

### 2. Configure Windsurf

Windsurf uses a JSON configuration file for MCP servers.

**Location**: `~/.windsurf/mcp.json` or `.windsurf/mcp.json`

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

### 3. Alternative: Project-Level Configuration

Create `.windsurf/mcp.json` in your project:

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp.main"],
      "cwd": "${workspaceFolder}",
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src",
        "COORDMCP_DATA_DIR": "${workspaceFolder}/.coordmcp/data"
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

### 5. Restart Windsurf

⚠️ **Important**: Fully restart Windsurf to load MCP tools.

### 6. Verify Integration

In Windsurf AI panel, try:

```
Create a project called "Windsurf Test" with description "Testing integration"
```

Or:
```python
result = await create_project(
    project_name="Windsurf Test",
    description="Testing CoordMCP with Windsurf"
)
print(f"Project ID: {result['project_id']}")
```

Success! 🎉

## Configuration Options

### Global Configuration

Add to `~/.windsurf/mcp.json`:

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

### With Environment Variables

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp.main"],
      "env": {
        "COORDMCP_DATA_DIR": "~/.coordmcp/data",
        "COORDMCP_LOG_LEVEL": "DEBUG",
        "COORDMCP_LOCK_TIMEOUT_HOURS": "12"
      }
    }
  }
}
```

## Usage in Windsurf

### AI Panel

In the Windsurf AI panel, you can:

1. **Type naturally**:
   ```
   I want to start a new project for our mobile app
   ```

2. **Reference tools explicitly**:
   ```
   Use coordmcp to create a project and get architecture recommendations
   ```

3. **Write Python code**:
   ```python
   project = await create_project(
       project_name="Mobile App",
       description="React Native mobile application"
   )
   ```

### Cascade Workflow

Windsurf's Cascade feature works great with CoordMCP:

```
Cascade: What would you like to work on?

You: I need to build a new feature for user profiles.

Cascade: Let me check the current project and get recommendations.

[Cascade uses CoordMCP to analyze and recommend]

Cascade: Based on the architecture analysis, I recommend using the Repository 
pattern. Shall I proceed with this implementation?
```

### Example Workflow

```python
# 1. Setup project
project = await create_project(
    project_name="Dashboard",
    description="Analytics dashboard"
)

# 2. Register as agent
agent = await register_agent(
    agent_name="WindsurfDev",
    agent_type="windsurf",
    capabilities=["typescript", "react", "d3"]
)

# 3. Start context
await start_context(
    agent_id=agent["agent_id"],
    project_id=project["project_id"],
    objective="Build chart components"
)

# 4. Lock files
await lock_files(
    agent_id=agent["agent_id"],
    project_id=project["project_id"],
    files=["src/components/Charts/BarChart.tsx"],
    reason="Implementing bar chart"
)

# 5. Get recommendations
rec = await get_architecture_recommendation(
    project_id=project["project_id"],
    feature_description="Chart library integration",
    implementation_style="modular"
)

# 6. Save decision
await save_decision(
    project_id=project["project_id"],
    title="Use D3.js",
    description="Integrate D3.js for custom charts",
    rationale="Flexibility and performance"
)
```

## Troubleshooting

### "MCP servers not loading"

1. Check config file:
   ```bash
   ls ~/.windsurf/mcp.json
   ```

2. Verify JSON:
   ```bash
   cat ~/.windsurf/mcp.json | python -m json.tool
   ```

3. Check Windsurf logs:
   - Help → Toggle Developer Tools
   - Check Console tab

### "python command not found"

Use full path:

```bash
which python
# /usr/local/bin/python
```

Update config:
```json
{
  "command": "/usr/local/bin/python",
  "args": ["-m", "coordmcp.main"]
}
```

### "Tools not appearing"

1. Ensure server running:
   ```bash
   python -m coordmcp.main
   ```

2. Full restart Windsurf

3. Check MCP panel in settings

### "Permission errors"

```bash
chmod -R 755 ~/.coordmcp/data
```

## Windsurf-Specific Features

### Using with Cascade

CoordMCP enhances Cascade's capabilities:

```
You: I need to refactor the authentication system.

Cascade: Let me check the current architecture and locked files first.

[Cascade queries CoordMCP]

Cascade: I see the AuthService is locked by another agent. Let me check 
what decisions have been made about authentication.

[Cascade searches decisions]

Cascade: Based on the architecture, I'll follow the JWT pattern already decided. 
However, I notice we could improve the token refresh mechanism. 
Should I proceed with the refactor?
```

### Real-time Collaboration

When multiple developers use Windsurf with CoordMCP:

```python
# Check who's working
agents = await get_agents_in_project(project_id="proj-123")

# Avoid conflicts
locked = await get_locked_files(project_id="proj-123")
for f in locked['locked_files']:
    print(f"{f['file_path']} locked by {f['locked_by']}")
```

### AI-Assisted Architecture

```
You: What's the best way to implement real-time updates?

Windsurf AI: Let me get architecture recommendations from CoordMCP.

[Gets recommendation]

Windsurf AI: CoordMCP recommends using the Observer pattern with WebSockets. 
This aligns with the existing event-driven architecture. 
Shall I generate the implementation?
```

## Advanced Configuration

### Multiple Projects

Use project-specific configs:

```json
{
  "mcpServers": {
    "coordmcp": {
      "env": {
        "COORDMCP_DATA_DIR": "${workspaceFolder}/.coordmcp/data"
      }
    }
  }
}
```

### Debugging

Enable debug mode:

```json
{
  "mcpServers": {
    "coordmcp": {
      "env": {
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

## Tips for Windsurf Users

1. **Use Cascade** - Great for complex, multi-step tasks
2. **Lock early** - Prevent conflicts in collaborative mode
3. **Save decisions** - Document architectural choices
4. **Check context** - Verify you're working on the right task
5. **Log changes** - Keep audit trail of modifications

## Next Steps

- Try [Context Switching](../examples/context-switching.md)
- Learn [Multi-Agent Workflow](../examples/multi-agent-workflow.md)
- Read [API Reference](../API_REFERENCE.md)

## Getting Help

- 📧 **Email**: support@coordmcp.dev
- 💬 **Discord**: [Join our community](https://discord.gg/coordmcp)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

---

**Happy coding with Windsurf + CoordMCP!** 🚀
