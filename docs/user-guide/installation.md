# Installation

Get CoordMCP running with your AI coding agent.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## Install CoordMCP

### Option 1: Install from PyPI (Recommended)

```bash
pip install coordmcp

# Verify installation
coordmcp --version
```

### Option 2: Install from Source

```bash
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp
pip install -e .
```

## Configure Your AI Agent

Choose your AI agent below for specific setup instructions:

| Agent | Configuration |
|-------|---------------|
| [OpenCode](integrations/opencode.md) | `opencode.jsonc` |
| [Cursor](integrations/cursor.md) | `settings.json` |
| [Claude Code](integrations/claude-code.md) | `claude.json` |
| [Windsurf](integrations/windsurf.md) | `windsurf-tools.json` |

## Quick Configuration Example

For OpenCode, create `opencode.jsonc` in your project root:

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

## Verify It Works

After configuration, restart your AI agent and try:

> "What tools does CoordMCP provide?"

Your AI agent should respond with information about CoordMCP tools.

## Data Storage

CoordMCP stores all data in `~/.coordmcp/` by default:

```
~/.coordmcp/
├── data/           # Projects, decisions, agents
└── logs/           # Log files
```

### Custom Data Directory

Set the `COORDMCP_DATA_DIR` environment variable:

```json
{
  "mcp": {
    "coordmcp": {
      "environment": {
        "COORDMCP_DATA_DIR": "/path/to/custom/data"
      }
    }
  }
}
```

## Optional: System Prompt

For better AI agent behavior, you can copy the contents of `SYSTEM_PROMPT.md` to your project's system prompt configuration. This helps the AI agent understand how to use CoordMCP effectively.

## Next Steps

- [How It Works](how-it-works.md) - Understand what happens behind the scenes
- [Integrations](integrations/) - Detailed setup for your AI agent
- [Troubleshooting](../reference/troubleshooting.md) - Common issues
