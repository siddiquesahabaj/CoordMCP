# CLI Reference

Command-line interface for CoordMCP.

## Installation

```bash
pip install coordmcp
```

## Commands

### coordmcp

Start the CoordMCP MCP server.

```bash
coordmcp [options]
```

#### Options

| Option | Description |
|--------|-------------|
| `--version` | Show version number and exit |
| `--help` | Show help message and exit |

#### Examples

```bash
# Start the server
coordmcp

# Check version
coordmcp --version

# Show help
coordmcp --help

# Run with debug logging
COORDMCP_LOG_LEVEL=DEBUG coordmcp
```

### python -m coordmcp

Alternative way to run the server using Python module syntax.

```bash
python -m coordmcp [options]
```

This is useful when `coordmcp` is not in your PATH.

#### Examples

```bash
# Start the server
python -m coordmcp

# Check version
python -m coordmcp --version

# Run with custom data directory
COORDMCP_DATA_DIR=/custom/path python -m coordmcp
```

## Environment Variables

Configure CoordMCP behavior with environment variables:

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `COORDMCP_DATA_DIR` | `~/.coordmcp/data` | Data storage directory |
| `COORDMCP_LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `COORDMCP_LOG_FILE` | `~/.coordmcp/logs/coordmcp.log` | Log file path |

### File Locking Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `COORDMCP_LOCK_TIMEOUT_HOURS` | `24` | Hours before locks expire |
| `COORDMCP_MAX_FILE_LOCKS_PER_AGENT` | `100` | Max files one agent can lock |
| `COORDMCP_AUTO_CLEANUP_STALE_LOCKS` | `true` | Auto-remove expired locks |

## Usage with AI Agents

### OpenCode

Add to `opencode.jsonc`:

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

### Cursor

Add to Cursor settings:

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

### Claude Code

Add to Claude config:

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

## Data Directory

### Default Location

```
~/.coordmcp/
├── data/
│   ├── memory/{project_id}/
│   ├── agents/{agent_id}/
│   └── global/
└── logs/
    └── coordmcp.log
```

### Custom Location

```bash
# Linux/macOS
export COORDMCP_DATA_DIR=/custom/path
coordmcp

# Windows
set COORDMCP_DATA_DIR=C:\custom\path
coordmcp
```

## Logging

### Log Levels

| Level | Description |
|-------|-------------|
| `DEBUG` | Detailed debug information |
| `INFO` | General information (default) |
| `WARNING` | Warnings only |
| `ERROR` | Errors only |

### Enable Debug Logging

```bash
# Linux/macOS
export COORDMCP_LOG_LEVEL=DEBUG
coordmcp

# Windows
set COORDMCP_LOG_LEVEL=DEBUG
coordmcp
```

### View Logs

```bash
# Tail logs
tail -f ~/.coordmcp/logs/coordmcp.log

# Search for errors
grep ERROR ~/.coordmcp/logs/coordmcp.log

# View recent entries
tail -100 ~/.coordmcp/logs/coordmcp.log
```

## Troubleshooting

### Command not found

If `coordmcp` command is not found:

1. Verify installation: `pip show coordmcp`
2. Use Python module syntax: `python -m coordmcp`
3. Check PATH includes Python scripts directory

### Permission errors

```bash
# Fix data directory permissions (Linux/macOS)
chmod -R 755 ~/.coordmcp/data

# Windows: Run as administrator or check folder permissions
```

### Server won't start

1. Check logs: `cat ~/.coordmcp/logs/coordmcp.log`
2. Verify Python version: `python --version` (needs 3.10+)
3. Check dependencies: `pip install -e ".[dev]"`

## Development

### Run from Source

```bash
# Clone repository
git clone https://github.com/siddiquesahabaj/coordmcp.git
cd coordmcp

# Install in development mode
pip install -e ".[dev]"

# Run server
python -m coordmcp
```

### Run Tests

```bash
# All tests
python -m pytest src/tests/ -v

# Unit tests only
python -m pytest src/tests/unit/ -v

# With coverage
python -m pytest src/tests/ --cov=coordmcp
```

## See Also

- [Configuration Reference](../reference/configuration.md)
- [Installation Guide](../user-guide/installation.md)
- [Troubleshooting](../reference/troubleshooting.md)
