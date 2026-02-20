# Windsurf Integration

Complete setup guide for using CoordMCP with Windsurf IDE.

## Why Use CoordMCP with Windsurf?

CoordMCP provides Windsurf with:
- **Long-term memory** - Remembers architectural decisions across sessions
- **File locking** - Prevents conflicts when multiple agents work on the same project
- **Architecture guidance** - Recommends design patterns without external API calls
- **Task tracking** - Manages tasks and agent activities

## Prerequisites

- Windsurf IDE installed
- Python 3.10+ installed
- CoordMCP installed (`pip install coordmcp`)

## Quick Setup

### 1. Install CoordMCP

```bash
pip install coordmcp
coordmcp --version
```

### 2. Configure Windsurf

Create or edit the Windsurf MCP configuration.

**Location:** Windsurf Settings → MCP or `~/.windsurf/mcp.json`

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

> **Note:** You can also use `python -m coordmcp` if `coordmcp` is not in your PATH.

### 3. Restart Windsurf

Close and reopen Windsurf to load the MCP tools.

### 4. Verify Installation

In Windsurf, say:

> "What CoordMCP tools are available?"

If Windsurf responds with tool information, you're all set!

## Usage

Just talk to Windsurf normally. CoordMCP works automatically.

### Example: Building an Application

**You say:**
> "Create a real-time chat application"

**What happens automatically:**
1. Project discovered or created
2. Agent registered
3. WebSocket pattern recommended
4. Files locked before editing
5. All changes tracked

### Example: Multi-Agent Coordination

**You say:**
> "I'm working on the frontend, what's the backend agent doing?"

**What happens:**
1. Checks active agents
2. Shows what other agents are working on
3. Shows locked files
4. Helps you coordinate work

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

1. Verify installation: `coordmcp --version`
2. Check config location
3. Verify JSON syntax

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

## Next Steps

- [How It Works](../how-it-works.md) - Understand what happens behind the scenes
- [API Reference](../../developer-guide/api-reference.md) - See all available tools
- [Troubleshooting](../../reference/troubleshooting.md) - More solutions
