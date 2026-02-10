# Claude Code Integration

Complete setup guide for using CoordMCP with Claude Code CLI.

## Prerequisites

- Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code`)
- Python 3.8+ installed
- CoordMCP cloned and installed

## Step-by-Step Setup

### 1. Install CoordMCP

```bash
# Clone repository
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install
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
      "args": ["-m", "coordmcp.main"],
      "env": {
        "COORDMCP_DATA_DIR": "~/.coordmcp/data",
        "COORDMCP_LOG_LEVEL": "INFO",
        "PYTHONPATH": "/path/to/coordmcp/src"
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

Create `.claude/config.json` in your project root:

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp.main"],
      "cwd": ".",
      "env": {
        "COORDMCP_DATA_DIR": "./.coordmcp/data",
        "PYTHONPATH": "./coordmcp/src"
      }
    }
  }
}
```

### 4. Start CoordMCP

In a separate terminal:

```bash
python -m coordmcp.main
```

Wait for:
```
INFO - CoordMCP server initialized and ready
```

### 5. Start Claude Code

```bash
claude
```

### 6. Verify Integration

In Claude Code, try:

```
Create a new project called "Claude Test" with description "Testing CoordMCP integration"
```

Or directly:
```
Use coordmcp to create_project with name="Claude Test" and description="Integration test"
```

If you get a project ID back, you're set! 🎉

## Configuration Options

### Global Configuration

Edit `~/.claude/config.json`:

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "/full/path/to/python",
      "args": ["-m", "coordmcp.main"],
      "env": {
        "COORDMCP_DATA_DIR": "~/.coordmcp/data"
      }
    }
  }
}
```

### With Custom Python Path

If `python` isn't in your PATH:

```bash
# Find Python path
which python3
# /usr/local/bin/python3
```

Then use full path:
```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "coordmcp.main"]
    }
  }
}
```

## Usage in Claude Code

### Natural Language

Claude Code understands natural language:

```
I want to start a new project for our API. Can you use coordmcp to set that up?
```

Claude will:
1. Call `create_project`
2. Ask you for details if needed
3. Return the project ID

### Direct Tool Calls

You can be explicit:

```
Use coordmcp to:
1. Create a project called "Auth Service"
2. Get an architecture recommendation for JWT authentication
3. Save the decision to use FastAPI
```

### Python Mode

Claude Code supports Python execution:

```python
# Setup
project = await create_project(
    project_name="Data Pipeline",
    description="ETL pipeline for analytics"
)

# Register
agent = await register_agent(
    agent_name="ClaudeDev",
    agent_type="claude",
    capabilities=["python", "data-engineering"]
)

# Start working
await start_context(
    agent_id=agent["agent_id"],
    project_id=project["project_id"],
    objective="Design data ingestion layer"
)

# Get guidance
rec = await get_architecture_recommendation(
    project_id=project["project_id"],
    feature_description="Real-time data streaming with Apache Kafka",
    implementation_style="modular"
)

print(f"Pattern: {rec['recommended_pattern']['pattern']}")
print(f"Rationale: {rec['recommended_pattern']['rationale']}")
```

### Working with Multiple Agents

If other agents use CoordMCP:

```python
# Check who's working
agents = await get_agents_in_project(project_id="your-project")
print(f"Active agents: {len(agents['agents'])}")

# Check locked files
locked = await get_locked_files(project_id="your-project")
for file in locked['locked_files']:
    print(f"Locked: {file['file_path']} by {file['locked_by']}")
```

### Context Management

```python
# Start new context
await start_context(
    agent_id="your-agent-id",
    project_id="your-project",
    objective="Implement OAuth2 flow",
    priority="high"
)

# Check current context
context = await get_agent_context(agent_id="your-agent-id")
print(f"Working on: {context['objective']}")

# Switch to different project
await switch_context(
    agent_id="your-agent-id",
    project_id="other-project",
    objective="Fix bug in reporting"
)
```

## Advanced Configuration

### Multiple MCP Servers

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp.main"]
    },
    "other-server": {
      "command": "other-command"
    }
  }
}
```

### Environment Variables

Create a `.env` file:

```bash
COORDMCP_DATA_DIR=/custom/data/path
COORDMCP_LOG_LEVEL=DEBUG
```

Then reference in config:
```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "bash",
      "args": ["-c", "source .env && python -m coordmcp.main"]
    }
  }
}
```

## Troubleshooting

### "command not found: claude"

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Or use npx
npx @anthropic-ai/claude-code
```

### "MCP server not connecting"

1. Verify server is running:
   ```bash
   python -m coordmcp.main
   ```

2. Check Claude Code config location:
   ```bash
   ls ~/.claude/config.json
   ```

3. Verify JSON syntax:
   ```bash
   cat ~/.claude/config.json | python -m json.tool
   ```

### "python: command not found"

Use full Python path:

```bash
# Find Python
which python3
# /usr/bin/python3
```

Update config:
```json
{
  "command": "/usr/bin/python3",
  "args": ["-m", "coordmcp.main"]
}
```

### "Tools not available"

1. Restart Claude Code completely:
   ```bash
   # Exit
   exit
   
   # Restart
   claude
   ```

2. Check MCP status in Claude:
   ```
   /mcp status
   ```

3. View Claude logs:
   ```bash
   cat ~/.claude/logs/claude.log
   ```

### "Permission denied on data"

```bash
chmod -R 755 ~/.coordmcp/data
```

## Claude Code Specific Tips

### Context Awareness

Claude Code maintains context across the conversation:

```
Me: Create a project called "API"
Claude: Created project with ID proj-123

Me: Now register me as an agent
Claude: Registers you and uses proj-123 automatically
```

### Combining with Claude's Capabilities

```
I need to implement a complex feature. Let me:
1. Get architecture guidance from coordmcp
2. Analyze the current codebase
3. Implement following the recommendation

[Claude will use both CoordMCP and its own analysis]
```

### Long-Running Sessions

For extended work sessions:

```python
# Check session periodically
log = await get_session_log(agent_id="your-agent")
print(f"Session activity: {len(log['entries'])} entries")

# Save decisions frequently
await save_decision(
    project_id="your-project",
    title="Progress Update",
    description="Completed module X",
    rationale="Milestone reached"
)
```

## Example Workflow

```
Me: I want to build a new microservice for user notifications.

Claude: I'll help you set that up. Let me create a project and get architecture recommendations.

[Claude creates project and gets recommendations]

Claude: Based on the analysis, I recommend using a message queue pattern. 
The recommended structure includes:
- Notification service (main handler)
- Queue processor (async workers)
- Templates module

Should I proceed with this architecture?

Me: Yes, and use RabbitMQ for the queue.

Claude: [Saves the decision and starts implementing]
```

## Next Steps

- Read [Architecture Recommendations](../examples/architecture-recommendation.md)
- Learn about [Context Switching](../examples/context-switching.md)
- Explore the [API Reference](../API_REFERENCE.md)

## Getting Help

- 📧 **Email**: support@coordmcp.dev
- 💬 **Discord**: [Join our community](https://discord.gg/coordmcp)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

---

**Happy coding with Claude Code + CoordMCP!** 🚀
