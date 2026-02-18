# Claude Code Integration

Complete setup guide for using CoordMCP with Claude Code CLI.

## Prerequisites

- Claude Code CLI installed
- Python 3.10+ installed
- CoordMCP installed (`pip install coordmcp`)

## Quick Setup

### 1. Install CoordMCP

```bash
pip install coordmcp
coordmcp --version
```

### 2. Configure Claude Code

Create or edit `claude.json` in your project root:

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp"],
      "env": {
        "COORDMCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 3. Restart Claude Code

Restart the Claude Code session to load the MCP tools.

### 4. Test It

In Claude Code, say:

> "What CoordMCP tools are available?"

If Claude responds with tool information, you're all set!

## Usage

Just talk to Claude Code normally. CoordMCP works automatically.

### Example: Creating a Project

**You say:**
> "Create a REST API project for a blog platform"

**What happens automatically:**
1. Project created in current directory
2. Claude registered as an agent
3. Architecture recommendation provided
4. Initial structure suggested

### Example: Implementing Features

**You say:**
> "Add user authentication with JWT tokens"

**What happens automatically:**
1. Files locked before editing
2. Pattern recommendation for auth
3. Implementation completed
4. Decision "Use JWT" recorded
5. Changes logged

## Configuration Options

### Custom Data Directory

```json
{
  "mcpServers": {
    "coordmcp": {
      "env": {
        "COORDMCP_DATA_DIR": "/path/to/custom/data"
      }
    }
  }
}
```

### Debug Logging

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

## Troubleshooting

### "MCP server not found"

1. Verify installation: `coordmcp --version`
2. Check config location and syntax
3. Ensure Python is in PATH

### "Python not found"

Use full path:
```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "/usr/bin/python3",
      "args": ["-m", "coordmcp"]
    }
  }
}
```

## Next Steps

- [How It Works](../how-it-works.md) - Understand what happens behind the scenes
- [API Reference](../../developer-guide/api-reference.md) - See all available tools
- [Troubleshooting](../../reference/troubleshooting.md) - More solutions
