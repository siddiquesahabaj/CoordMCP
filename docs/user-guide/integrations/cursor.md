# Cursor Integration

Complete setup guide for using CoordMCP with Cursor IDE.

## Prerequisites

- Cursor IDE installed
- Python 3.10+ installed
- CoordMCP installed (`pip install coordmcp`)

## Quick Setup

### 1. Install CoordMCP

```bash
pip install coordmcp
coordmcp --version
```

### 2. Configure Cursor

Add to Cursor's MCP settings.

**Option A: Global Config**

Create or edit `~/.cursor/mcp.json`:

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

**Option B: Project Config**

Create `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp"]
    }
  }
}
```

### 3. Restart Cursor

Close Cursor completely and reopen it.

### 4. Test It

In Cursor Chat, say:

> "What CoordMCP tools are available?"

If Cursor responds with tool information, you're all set!

## Usage

Just talk to Cursor normally. CoordMCP works automatically.

### Example: Building a Feature

**You say:**
> "Build a user dashboard with charts"

**What happens automatically:**
1. Project discovered or created
2. Agent registered
3. Files locked before editing
4. Architecture patterns suggested
5. Changes tracked and logged

### Example: Getting Architecture Advice

**You say:**
> "What's the best pattern for implementing a shopping cart?"

**What happens:**
1. CoordMCP analyzes your project
2. Recommends appropriate pattern
3. Suggests file structure
4. Provides implementation guidance

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

### "MCP servers not loading"

1. Check config location: `ls ~/.cursor/mcp.json`
2. Verify JSON syntax: `cat ~/.cursor/mcp.json | python -m json.tool`
3. Check Cursor console (Developer Tools)

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

### "Tools not appearing in chat"

1. Verify server: `python -m coordmcp`
2. Full restart Cursor (Cmd/Ctrl + Q, then reopen)
3. Check Settings → MCP for "coordmcp"

## Next Steps

- [How It Works](../how-it-works.md) - Understand what happens behind the scenes
- [API Reference](../../developer-guide/api-reference.md) - See all available tools
- [Troubleshooting](../../reference/troubleshooting.md) - More solutions
