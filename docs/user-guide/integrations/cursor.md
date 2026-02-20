# Cursor Integration

Complete setup guide for using CoordMCP with Cursor IDE.

## Why Use CoordMCP with Cursor?

CoordMCP provides Cursor with:
- **Long-term memory** - Remembers architectural decisions across sessions
- **File locking** - Prevents conflicts when multiple agents work on the same project
- **Architecture guidance** - Recommends design patterns without external API calls
- **Task tracking** - Manages tasks and agent activities

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
      "command": "coordmcp",
      "args": [],
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
      "command": "coordmcp",
      "args": []
    }
  }
}
```

> **Note:** You can also use `python -m coordmcp` if `coordmcp` is not in your PATH.

### 3. Restart Cursor

Close Cursor completely and reopen it.

### 4. Verify Installation

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

### Command Options

**Using coordmcp CLI (recommended):**
```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "coordmcp",
      "args": []
    }
  }
}
```

**Using Python module:**
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

### Custom Data Directory

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "coordmcp",
      "args": [],
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
      "command": "coordmcp",
      "args": [],
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

### "Command not found"

If `coordmcp` is not in PATH:

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "/full/path/to/coordmcp",
      "args": []
    }
  }
}
```

Or use Python module:

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

Find your paths:
```bash
which coordmcp    # macOS/Linux
where coordmcp    # Windows
which python3     # macOS/Linux
where python      # Windows
```

### "Tools not appearing in chat"

1. Verify server: `coordmcp --version`
2. Full restart Cursor (Cmd/Ctrl + Q, then reopen)
3. Check Settings → MCP for "coordmcp"

## Next Steps

- [How It Works](../how-it-works.md) - Understand what happens behind the scenes
- [API Reference](../../developer-guide/api-reference.md) - See all available tools
- [Troubleshooting](../../reference/troubleshooting.md) - More solutions
