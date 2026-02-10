# CoordMCP Setup Guide

Complete installation and configuration guide for CoordMCP.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [Integration with Agents](#integration-with-agents)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## Installation

### Option 1: Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode (optional)
pip install -e .
```

### Option 2: Install via pip (when published)

```bash
pip install coordmcp
```

## Configuration

### Environment Variables

CoordMCP can be configured via environment variables or a `.env` file in the project root.

Create a `.env` file:

```bash
# Data storage directory (default: ~/.coordmcp/data)
COORDMCP_DATA_DIR=/path/to/your/data

# Log level: DEBUG, INFO, WARNING, ERROR (default: INFO)
COORDMCP_LOG_LEVEL=INFO

# Log file path (default: ~/.coordmcp/logs/coordmcp.log)
COORDMCP_LOG_FILE=/path/to/your/logs/coordmcp.log

# Maximum file locks per agent (default: 100)
COORDMCP_MAX_FILE_LOCKS_PER_AGENT=100

# Lock timeout in hours (default: 24)
COORDMCP_LOCK_TIMEOUT_HOURS=24

# Auto-cleanup stale locks (default: true)
COORDMCP_AUTO_CLEANUP_STALE_LOCKS=true
```

### Configuration File

You can also create a `config.yaml` file:

```yaml
# config.yaml
data_dir: "~/.coordmcp/data"
log_level: "INFO"
log_file: "~/.coordmcp/logs/coordmcp.log"
max_file_locks_per_agent: 100
lock_timeout_hours: 24
auto_cleanup_stale_locks: true
```

## Running the Server

### Standalone Mode

```bash
# Run the server
python -m coordmcp.main

# Or using the package
python src/coordmcp/main.py
```

The server will start and listen for MCP connections.

### Development Mode

```bash
# Run with debug logging
COORDMCP_LOG_LEVEL=DEBUG python -m coordmcp.main
```

## Integration with Agents

### Opencode Integration

Add CoordMCP to your Opencode configuration file (`~/.opencode/config.toml`):

```toml
[[mcp_servers]]
name = "coordmcp"
command = "python"
args = ["-m", "coordmcp.main"]
# Or if using a specific path:
# args = ["/path/to/coordmcp/src/coordmcp/main.py"]
```

### Cursor Integration

Add to Cursor's MCP settings (settings.json):

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp.main"]
    }
  }
}
```

### Claude Code Integration

Add to Claude Code configuration:

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp.main"]
    }
  }
}
```

## Verifying Installation

### Test 1: Check Server Starts

```bash
python -m coordmcp.main
```

You should see:
```
INFO - Starting CoordMCP server...
INFO - Storage backend initialized
INFO - CoordMCP server v0.1.0 created
INFO - Registering tools...
INFO - All tools registered successfully
INFO - All resources registered successfully
INFO - CoordMCP server initialized and ready
```

### Test 2: Run Memory System Test

```bash
python src/tests/test_memory_system.py
```

### Test 3: Run Context System Test

```bash
python src/tests/test_context_system.py
```

### Test 4: Run Architecture Test

```bash
python src/tests/test_architecture_system.py
```

### Test 5: Run Integration Test

```bash
python src/tests/integration/test_full_integration.py
```

## Data Directory Structure

After running, CoordMCP creates the following structure:

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

## Troubleshooting

### Issue: ModuleNotFoundError

**Problem**: `ModuleNotFoundError: No module named 'coordmcp'`

**Solution**:
```bash
# Make sure you're in the project root
cd coordmcp

# Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or install in development mode
pip install -e .
```

### Issue: Permission Denied

**Problem**: Cannot write to data directory

**Solution**:
```bash
# Create data directory with proper permissions
mkdir -p ~/.coordmcp/data
chmod 755 ~/.coordmcp/data
```

### Issue: Port Already in Use

**Problem**: MCP server port conflict

**Solution**: CoordMCP uses stdio transport, not TCP ports. This error usually means another MCP server is using the same configuration name.

### Issue: Tools Not Available

**Problem**: Tools don't appear in agent

**Solution**:
1. Check server is running: `python -m coordmcp.main`
2. Verify configuration syntax in agent config
3. Restart the agent IDE
4. Check logs: `cat ~/.coordmcp/logs/coordmcp.log`

### Issue: Data Not Persisting

**Problem**: Changes lost after restart

**Solution**:
1. Check data directory path: `COORDMCP_DATA_DIR`
2. Verify directory exists and is writable
3. Check JSON files are valid: `python -m json.tool < file.json`

### Issue: File Locks Not Working

**Problem**: Multiple agents can lock same file

**Solution**:
1. Check that all agents are using the same CoordMCP instance
2. Verify lock timeout is appropriate
3. Run cleanup: Check for stale lock cleanup in logs

## Development Setup

For development work on CoordMCP itself:

```bash
# Clone and setup
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run specific test
pytest tests/test_memory_system.py -v

# Run with coverage
pytest --cov=coordmcp tests/
```

## Next Steps

After installation:

1. **Read the [API Reference](API_REFERENCE.md)** - Learn about available tools and resources
2. **Try the Examples** - Run `python examples/basic_project_setup.py`
3. **Configure Your Agent** - Add CoordMCP to Opencode, Cursor, or Claude Code
4. **Create Your First Project** - Use the `create_project` tool

## Support

- 📧 Email: support@coordmcp.dev
- 💬 Discord: [Join our community](https://discord.gg/coordmcp)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

## Uninstallation

```bash
# If installed with pip
pip uninstall coordmcp

# Remove data directory (optional)
rm -rf ~/.coordmcp
```
