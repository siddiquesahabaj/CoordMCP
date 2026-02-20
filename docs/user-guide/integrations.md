# Integrations Overview

CoordMCP integrates with various AI coding agents and IDEs to provide multi-agent coordination capabilities.

## Supported Agents

| Agent | Config File | Quick Setup |
|-------|-------------|-------------|
| [OpenCode](integrations/opencode.md) | `opencode.jsonc` | [Guide](integrations/opencode.md#quick-setup) |
| [Cursor](integrations/cursor.md) | `~/.cursor/mcp.json` | [Guide](integrations/cursor.md#quick-setup) |
| [Claude Code](integrations/claude-code.md) | `claude.json` | [Guide](integrations/claude-code.md#quick-setup) |
| [Windsurf](integrations/windsurf.md) | `~/.windsurf/mcp.json` | [Guide](integrations/windsurf.md#quick-setup) |
| [Antigravity](integrations/antigravity.md) | `~/.antigravity/mcp_config.json` | [Guide](integrations/antigravity.md#quick-setup) |

## Quick Configuration Templates

### Standard MCP Config (Cursor, Claude Code, Windsurf, Antigravity)

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

### OpenCode Config

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

## Choosing a Command Format

### Option 1: Using coordmcp CLI (Recommended)

```json
{
  "command": "coordmcp",
  "args": []
}
```

**Pros:**
- Simpler configuration
- Works across all platforms
- No need to specify Python path

**Requirements:**
- CoordMCP must be installed and in PATH
- `pip install coordmcp` adds it to PATH on most systems

### Option 2: Using Python Module

```json
{
  "command": "python",
  "args": ["-m", "coordmcp"]
}
```

Or with full path:

```json
{
  "command": "/usr/bin/python3",
  "args": ["-m", "coordmcp"]
}
```

**Pros:**
- Works when coordmcp is not in PATH
- Allows specific Python version selection
- More explicit about what's being run

**Requirements:**
- Python must be installed
- CoordMCP must be installed in that Python environment

## Environment Variables

Configure CoordMCP using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `COORDMCP_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `COORDMCP_DATA_DIR` | Custom data directory path | `~/.coordmcp/data` |

### Example with Environment Variables

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "coordmcp",
      "args": [],
      "env": {
        "COORDMCP_LOG_LEVEL": "DEBUG",
        "COORDMCP_DATA_DIR": "/path/to/custom/data"
      }
    }
  }
}
```

## Verifying Installation

After configuration, restart your agent and ask:

> "What CoordMCP tools are available?"

If the agent responds with tool information, the installation is successful.

## Multiple Agents

You can run multiple agents with CoordMCP on the same project:

1. **Install CoordMCP** (one time)
2. **Configure each agent** to connect to CoordMCP
3. **Start agents** - they'll automatically coordinate

CoordMCP will:
- Track which files each agent is working on
- Prevent file conflicts through locking
- Share decisions across all agents

## Common Issues

### Command Not Found

If you get "command not found" errors:

1. **Verify coordmcp is installed:**
   ```bash
   coordmcp --version
   ```

2. **Find the correct path:**
   ```bash
   which coordmcp    # macOS/Linux
   where coordmcp    # Windows
   ```

3. **Use full path in config** or switch to Python module format

### Tools Not Appearing

1. Restart the agent completely
2. Check the agent's MCP settings
3. Verify JSON syntax in config file

### Permission Denied

```bash
chmod -R 755 ~/.coordmcp/data    # macOS/Linux
```

## Next Steps

- [Installation Guide](../user-guide/installation.md) - Detailed installation
- [How It Works](../user-guide/how-it-works.md) - Understand the coordination system
- [API Reference](../developer-guide/api-reference.md) - Available tools
- [Troubleshooting](../reference/troubleshooting.md) - Common issues and solutions
