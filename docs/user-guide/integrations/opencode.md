# OpenCode Integration

Complete setup guide for using CoordMCP with OpenCode.

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
      "command": ["python", "-m", "coordmcp"],
      "enabled": true,
      "environment": {
        "COORDMCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 3. Restart OpenCode

Close and reopen OpenCode to load the MCP tools.

### 4. Test It

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

### Custom Data Directory

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

### Debug Logging

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

## Troubleshooting

### "Tools not appearing"

1. Verify server works: `coordmcp --version`
2. Check config syntax: `cat opencode.jsonc | python -m json.tool`
3. Restart OpenCode completely

### "Python not found"

Use full Python path:
```json
{
  "mcp": {
    "coordmcp": {
      "command": ["/full/path/to/python", "-m", "coordmcp"]
    }
  }
}
```

Find your path:
```bash
which python    # macOS/Linux
where python    # Windows
```

### "Permission denied on data directory"

```bash
chmod -R 755 ~/.coordmcp/data    # macOS/Linux
```

## Next Steps

- [How It Works](../how-it-works.md) - Understand what happens behind the scenes
- [API Reference](../../developer-guide/api-reference.md) - See all available tools
- [Troubleshooting](../../reference/troubleshooting.md) - More solutions
