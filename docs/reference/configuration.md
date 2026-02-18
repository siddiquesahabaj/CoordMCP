# Configuration Reference

All CoordMCP configuration options.

## Environment Variables

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

### Storage Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `COORDMCP_STORAGE_BACKEND` | `json` | Storage backend type |
| `COORDMCP_ENABLE_COMPRESSION` | `false` | Compress stored data |

---

## Setting Variables

### Option 1: Environment Variables

```bash
# Linux/macOS
export COORDMCP_DATA_DIR=/path/to/data
export COORDMCP_LOG_LEVEL=DEBUG

# Windows (Command Prompt)
set COORDMCP_DATA_DIR=C:\coordmcp\data

# Windows (PowerShell)
$env:COORDMCP_DATA_DIR = "C:\coordmcp\data"
```

### Option 2: .env File

Create `.env` in project root:

```bash
# Data storage
COORDMCP_DATA_DIR=/path/to/data

# Logging
COORDMCP_LOG_LEVEL=INFO
COORDMCP_LOG_FILE=/var/log/coordmcp.log

# File locking
COORDMCP_LOCK_TIMEOUT_HOURS=12
COORDMCP_MAX_FILE_LOCKS_PER_AGENT=50
COORDMCP_AUTO_CLEANUP_STALE_LOCKS=true
```

### Option 3: Agent Configuration

In your MCP config (e.g., `opencode.jsonc`):

```json
{
  "mcp": {
    "coordmcp": {
      "environment": {
        "COORDMCP_DATA_DIR": "${workspaceFolder}/.coordmcp/data",
        "COORDMCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

---

## Log Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `DEBUG` | Detailed debug info | Development, troubleshooting |
| `INFO` | General information | Production (default) |
| `WARNING` | Warnings only | Minimal logging |
| `ERROR` | Errors only | Critical issues only |

---

## Data Directory

### Default Structure

```
~/.coordmcp/
├── data/
│   ├── memory/
│   │   └── {project_id}/
│   │       ├── project_info.json
│   │       ├── decisions.json
│   │       ├── tech_stack.json
│   │       ├── changes.json
│   │       └── file_metadata.json
│   ├── agents/
│   │   └── {agent_id}/
│   │       ├── context.json
│   │       ├── locked_files.json
│   │       └── session_log.json
│   └── global/
│       ├── agent_registry.json
│       └── project_registry.json
└── logs/
    └── coordmcp.log
```

### Custom Location

```bash
# Option 1: Environment variable
export COORDMCP_DATA_DIR=/mnt/data/coordmcp

# Option 2: In agent config
{
  "environment": {
    "COORDMCP_DATA_DIR": "/custom/path"
  }
}
```

---

## File Locking

### Lock Timeout

How long before locks expire:

```bash
# Short timeout (2 hours)
COORDMCP_LOCK_TIMEOUT_HOURS=2

# Long timeout (48 hours)
COORDMCP_LOCK_TIMEOUT_HOURS=48
```

### Max Locks Per Agent

```bash
# Limit to 50 files
COORDMCP_MAX_FILE_LOCKS_PER_AGENT=50

# Unlimited (not recommended)
COORDMCP_MAX_FILE_LOCKS_PER_AGENT=1000
```

### Auto Cleanup

```bash
# Enable auto cleanup (default)
COORDMCP_AUTO_CLEANUP_STALE_LOCKS=true

# Disable (manual cleanup required)
COORDMCP_AUTO_CLEANUP_STALE_LOCKS=false
```

---

## Configuration by Environment

### Development

```bash
COORDMCP_DATA_DIR=./data
COORDMCP_LOG_LEVEL=DEBUG
COORDMCP_LOCK_TIMEOUT_HOURS=2
COORDMCP_MAX_FILE_LOCKS_PER_AGENT=200
```

### Production

```bash
COORDMCP_DATA_DIR=/var/lib/coordmcp/data
COORDMCP_LOG_LEVEL=INFO
COORDMCP_LOG_FILE=/var/log/coordmcp/coordmcp.log
COORDMCP_LOCK_TIMEOUT_HOURS=24
COORDMCP_MAX_FILE_LOCKS_PER_AGENT=100
```

### CI/CD

```bash
COORDMCP_DATA_DIR=/tmp/coordmcp_test_data
COORDMCP_LOG_LEVEL=WARNING
COORDMCP_LOCK_TIMEOUT_HOURS=1
```

---

## Per-Project Configuration

Set different config per project:

```bash
# In project directory
cd my-project
export COORDMCP_DATA_DIR=./.coordmcp/data
python -m coordmcp
```

---

## Configuration Precedence

Settings are loaded in order (later overrides earlier):

1. Default values
2. `.env` file
3. Environment variables
4. Agent configuration

---

## Related

- [Installation](../user-guide/installation.md)
- [Troubleshooting](troubleshooting.md)
