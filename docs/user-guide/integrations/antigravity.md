# Antigravity IDE Integration

Complete setup guide for using CoordMCP with Antigravity IDE.

## Prerequisites

- Antigravity IDE installed
- Python 3.10+ installed
- CoordMCP installed (`pip install coordmcp`)

## Quick Setup

### 1. Install CoordMCP

```bash
pip install coordmcp
coordmcp --version
```

### 2. Configure Antigravity

Add CoordMCP to Antigravity's MCP configuration file. The location is typically `mcp_config.json` in your user config directory or project directory.

**Location:** `~/.antigravity/mcp_config.json` or `<project>/mcp_config.json`

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

### 3. Restart Antigravity

Close and reopen Antigravity to load the MCP tools.

### 4. Test It

In Antigravity, say:

> "What CoordMCP tools are available?"

If Antigravity responds with tool information, you're all set!

## Usage

Just talk to Antigravity normally. CoordMCP works automatically.

### Example: Building a Feature

**You say:**
> "Build a user authentication system"

**What happens automatically:**
1. Project discovered or created
2. Agent registered
3. Files locked before editing
4. Architecture patterns suggested
5. Changes tracked and logged

### Example: Getting Architecture Advice

**You say:**
> "What's the best pattern for implementing a payment system?"

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

### Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `COORDMCP_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `COORDMCP_DATA_DIR` | Custom data directory path | ~/.coordmcp/data |

## Troubleshooting

### "MCP servers not loading"

1. Check config location: `ls ~/.antigravity/mcp_config.json`
2. Verify JSON syntax: `cat ~/.antigravity/mcp_config.json | python -m json.tool`
3. Check Antigravity console logs

### "Command not found"

If `coordmcp` is not in PATH, use the full path:

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "/full/path/to/coordmcp",
      "args": [],
      "env": {}
    }
  }
}
```

Find the path:
```bash
# macOS/Linux
which coordmcp

# Windows
where coordmcp
```

### "Tools not appearing in chat"

1. Verify server: `coordmcp --version`
2. Full restart Antigravity
3. Check Settings → MCP for "coordmcp"

## Next Steps

- [How It Works](../how-it-works.md) - Understand what happens behind the scenes
- [API Reference](../../developer-guide/api-reference.md) - See all available tools
- [Troubleshooting](../../reference/troubleshooting.md) - More solutions
