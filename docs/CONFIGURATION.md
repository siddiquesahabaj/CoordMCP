# Configuration Guide

Complete configuration reference for CoordMCP.

## Table of Contents

- [Environment Variables](#environment-variables)
- [Configuration File](#configuration-file)
- [Data Directory](#data-directory)
- [Logging](#logging)
- [File Locking](#file-locking)
- [Agent Settings](#agent-settings)
- [Configuration Examples](#configuration-examples)

## Environment Variables

CoordMCP can be configured using environment variables. These can be set in your shell or in a `.env` file in the project root.

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `COORDMCP_DATA_DIR` | `~/.coordmcp/data` | Directory for storing project and agent data |
| `COORDMCP_LOG_LEVEL` | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR |
| `COORDMCP_LOG_FILE` | `~/.coordmcp/logs/coordmcp.log` | Path to log file |

### File Locking Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `COORDMCP_LOCK_TIMEOUT_HOURS` | `24` | Hours before file locks expire |
| `COORDMCP_MAX_FILE_LOCKS_PER_AGENT` | `100` | Maximum files one agent can lock |
| `COORDMCP_AUTO_CLEANUP_STALE_LOCKS` | `true` | Automatically remove expired locks |

### Example .env File

Create a `.env` file in your project root:

```bash
# Data storage
COORDMCP_DATA_DIR=/path/to/your/data

# Logging
COORDMCP_LOG_LEVEL=INFO
COORDMCP_LOG_FILE=/var/log/coordmcp.log

# File locking
COORDMCP_LOCK_TIMEOUT_HOURS=12
COORDMCP_MAX_FILE_LOCKS_PER_AGENT=50
COORDMCP_AUTO_CLEANUP_STALE_LOCKS=true
```

## Configuration File

You can also use a `config.yaml` file for configuration:

```yaml
# config.yaml
data_dir: "~/.coordmcp/data"
log_level: "INFO"
log_file: "~/.coordmcp/logs/coordmcp.log"
max_file_locks_per_agent: 100
lock_timeout_hours: 24
auto_cleanup_stale_locks: true
```

Place this file in:
- Project root: `./config.yaml`
- Or specify path via `COORDMCP_CONFIG` environment variable

## Data Directory

### Default Structure

```
~/.coordmcp/
├── data/
│   ├── memory/
│   │   └── {project_id}/
│   │       ├── decisions.json
│   │       ├── tech_stack.json
│   │       ├── architecture.json
│   │       ├── recent_changes.json
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

### Custom Data Directory

To use a custom location:

**Option 1: Environment Variable**
```bash
export COORDMCP_DATA_DIR=/mnt/data/coordmcp
python -m coordmcp.main
```

**Option 2: .env File**
```bash
# .env
COORDMCP_DATA_DIR=/mnt/data/coordmcp
```

**Option 3: Configuration File**
```yaml
# config.yaml
data_dir: /mnt/data/coordmcp
```

### Data Directory Permissions

Ensure the data directory is writable:

```bash
# Create directory
mkdir -p ~/.coordmcp/data

# Set permissions (Linux/macOS)
chmod 755 ~/.coordmcp/data

# Or more restrictive
chmod 700 ~/.coordmcp/data
```

## Logging

### Log Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `DEBUG` | Detailed debug info | Development, troubleshooting |
| `INFO` | General information | Production (default) |
| `WARNING` | Warnings only | Minimal logging |
| `ERROR` | Errors only | Critical issues only |

### Setting Log Level

**Environment Variable:**
```bash
export COORDMCP_LOG_LEVEL=DEBUG
python -m coordmcp.main
```

**Command Line:**
```bash
COORDMCP_LOG_LEVEL=DEBUG python -m coordmcp.main
```

### Log Rotation

Logs are automatically rotated when they reach 10MB. Up to 5 backup files are kept.

To customize:

```python
# In your setup code
from coordmcp.logger import setup_logging

setup_logging(
    log_file="/var/log/coordmcp.log",
    max_bytes=50*1024*1024,  # 50MB
    backup_count=10
)
```

### Viewing Logs

```bash
# View recent logs
tail -f ~/.coordmcp/logs/coordmcp.log

# Search for errors
grep ERROR ~/.coordmcp/logs/coordmcp.log

# View specific date
ls ~/.coordmcp/logs/
```

## File Locking

### Lock Timeout

By default, file locks expire after 24 hours. Adjust based on your workflow:

```bash
# Short timeout for quick tasks (2 hours)
COORDMCP_LOCK_TIMEOUT_HOURS=2

# Long timeout for complex features (48 hours)
COORDMCP_LOCK_TIMEOUT_HOURS=48
```

### Maximum Locks Per Agent

Prevent agents from locking too many files:

```bash
# Limit to 50 files per agent
COORDMCP_MAX_FILE_LOCKS_PER_AGENT=50
```

### Auto Cleanup

Stale locks are automatically cleaned up. To disable:

```bash
COORDMCP_AUTO_CLEANUP_STALE_LOCKS=false
```

**Note:** If disabled, you'll need to manually unlock files or wait for timeout.

## Agent Settings

### Agent Configuration File

Agents can have custom configurations stored in:

```
~/.coordmcp/data/agents/{agent_id}/config.json
```

Example:
```json
{
  "agent_name": "BackendDev",
  "agent_type": "opencode",
  "capabilities": ["python", "fastapi"],
  "preferences": {
    "default_lock_timeout": 12,
    "auto_save_decisions": true
  }
}
```

### Capability Tags

Common capability tags used by agents:

- `python` - Python development
- `javascript` - JavaScript/TypeScript
- `frontend` - Frontend frameworks (React, Vue, etc.)
- `backend` - Backend development
- `database` - Database work
- `devops` - DevOps and infrastructure
- `testing` - Testing and QA

## Configuration Examples

### Development Environment

```bash
# .env
COORDMCP_DATA_DIR=./data
COORDMCP_LOG_LEVEL=DEBUG
COORDMCP_LOCK_TIMEOUT_HOURS=2
COORDMCP_MAX_FILE_LOCKS_PER_AGENT=200
```

### Production Environment

```bash
# .env
COORDMCP_DATA_DIR=/var/lib/coordmcp/data
COORDMCP_LOG_LEVEL=INFO
COORDMCP_LOG_FILE=/var/log/coordmcp/coordmcp.log
COORDMCP_LOCK_TIMEOUT_HOURS=24
COORDMCP_MAX_FILE_LOCKS_PER_AGENT=100
COORDMCP_AUTO_CLEANUP_STALE_LOCKS=true
```

### Multi-Agent Setup

When multiple agents share the same CoordMCP instance:

```bash
# .env
COORDMCP_DATA_DIR=/shared/coordmcp/data
COORDMCP_LOCK_TIMEOUT_HOURS=12
COORDMCP_MAX_FILE_LOCKS_PER_AGENT=50
COORDMCP_AUTO_CLEANUP_STALE_LOCKS=true
```

Ensure all agents have write access to the shared directory.

### CI/CD Environment

```bash
# .env
COORDMCP_DATA_DIR=/tmp/coordmcp_test_data
COORDMCP_LOG_LEVEL=WARNING
COORDMCP_LOCK_TIMEOUT_HOURS=1
```

## Per-Project Configuration

You can have different configurations per project by setting environment variables in your project directory:

```bash
# In your project directory
cd my-project
export COORDMCP_DATA_DIR=./.coordmcp/data
python -m coordmcp.main
```

Or use a `.env` file in each project.

## Configuration Precedence

Settings are loaded in this order (later overrides earlier):

1. Default values
2. `config.yaml` file
3. `.env` file
4. Environment variables
5. Runtime configuration (in code)

## Troubleshooting Configuration

### "Permission denied on data directory"

```bash
# Check permissions
ls -la ~/.coordmcp/

# Fix permissions
chmod -R 755 ~/.coordmcp/

# Or create with proper permissions
mkdir -p ~/.coordmcp/data
chmod 700 ~/.coordmcp/data
```

### "Logs not appearing"

```bash
# Check log directory exists
mkdir -p ~/.coordmcp/logs

# Verify log level
python -c "import os; print(os.getenv('COORDMCP_LOG_LEVEL', 'INFO'))"

# Force debug logging
COORDMCP_LOG_LEVEL=DEBUG python -m coordmcp.main
```

### "Changes not persisting"

```bash
# Check data directory path
echo $COORDMCP_DATA_DIR

# Verify directory is writable
touch $COORDMCP_DATA_DIR/test && rm $COORDMCP_DATA_DIR/test

# Check disk space
df -h ~/.coordmcp/
```

## Best Practices

1. **Use .env files** for local development
2. **Set log level to INFO** in production
3. **Backup data directory** regularly
4. **Use short lock timeouts** for quick tasks
5. **Monitor disk space** for logs and data
6. **Version control your .env.example** but not .env

## Getting Help

- 📧 **Email**: support@coordmcp.dev
- 💬 **Discord**: [Join our community](https://discord.gg/coordmcp)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

---

**Configuration complete!** Now you're ready to use CoordMCP. See [Getting Started](./GETTING_STARTED.md) to begin.
