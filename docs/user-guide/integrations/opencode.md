# OpenCode Integration

Complete setup guide for using CoordMCP with OpenCode.

## Why Use CoordMCP with OpenCode?

CoordMCP provides OpenCode with:
- **Long-term memory** - Remembers architectural decisions across sessions
- **File locking** - Prevents conflicts when multiple agents work on the same project
- **Architecture guidance** - Recommends design patterns without external API calls
- **Task tracking** - Manages tasks and agent activities

## Prerequisites

- OpenCode installed and configured
- Python 3.10+ installed
- CoordMCP installed (`pip install coordmcp`)

## Quick Setup

### 1. Install CoordMCP

```bash
pip install coordmcp
coordmcp --version
```

### 2. Configure OpenCode

Create `opencode.jsonc` in your project root:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "coordmcp": {
      "type": "local",
      "command": ["coordmcp"],
      "enabled": true,
      "environment": {
        "COORDMCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

> **Note:** You can also use `["python", "-m", "coordmcp"]` if `coordmcp` is not in your PATH.

### 3. Restart OpenCode

Close and reopen OpenCode to load the MCP tools.

### 4. Verify Installation

Say to OpenCode:

> "What CoordMCP tools are available?"

If OpenCode responds with tool information, you're all set!

## Usage

Just talk to OpenCode normally. CoordMCP works automatically.

### Example: Creating a Todo App

**You say:**
> "Create a todo app with React and FastAPI"

**What happens automatically:**
1. Project discovered or created
2. Agent registered
3. Files locked before editing
4. "Use React" and "Use FastAPI" decisions recorded
5. All changes tracked

### Example: Adding Authentication

**You say:**
> "Add JWT authentication to my app"

**What happens automatically:**
1. Files locked (auth.py, etc.)
2. Architecture recommendation retrieved
3. Implementation done
4. Decision "Use JWT" saved with rationale
5. Changes logged
6. Files unlocked

## Configuration Options

### Command Options

**Using coordmcp CLI (recommended):**
```json
{
  "mcp": {
    "coordmcp": {
      "type": "local",
      "command": ["coordmcp"],
      "enabled": true
    }
  }
}
```

**Using Python module:**
```json
{
  "mcp": {
    "coordmcp": {
      "type": "local",
      "command": ["python", "-m", "coordmcp"],
      "enabled": true
    }
  }
}
```

### Custom Data Directory

```json
{
  "mcp": {
    "coordmcp": {
      "type": "local",
      "command": ["coordmcp"],
      "enabled": true,
      "environment": {
        "COORDMCP_DATA_DIR": "${workspaceFolder}/.coordmcp/data"
      }
    }
  }
}
```

### Debug Logging

```json
{
  "mcp": {
    "coordmcp": {
      "type": "local",
      "command": ["coordmcp"],
      "enabled": true,
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

## Troubleshooting

### "Tools not appearing"

1. Verify server works: `coordmcp --version`
2. Check config syntax: `cat opencode.jsonc | python -m json.tool`
3. Restart OpenCode completely

### "Command not found"

If `coordmcp` is not in PATH, use full path or Python module:

```json
{
  "mcp": {
    "coordmcp": {
      "type": "local",
      "command": ["/full/path/to/coordmcp"],
      "enabled": true
    }
  }
}
```

Or:

```json
{
  "mcp": {
    "coordmcp": {
      "type": "local",
      "command": ["python", "-m", "coordmcp"],
      "enabled": true
    }
  }
}
```

Find your paths:
```bash
which coordmcp    # macOS/Linux
where coordmcp    # Windows
which python3     # macOS/Linux
where python      # Windows
```

### "Permission denied on data directory"

```bash
chmod -R 755 ~/.coordmcp/data    # macOS/Linux
```

## Next Steps

- [How It Works](../how-it-works.md) - Understand what happens behind the scenes
- [API Reference](../../developer-guide/api-reference.md) - See all available tools
- [Troubleshooting](../../reference/troubleshooting.md) - More solutions
