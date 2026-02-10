# Troubleshooting Guide

Common issues and solutions for CoordMCP.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Server Issues](#server-issues)
- [Agent Integration Issues](#agent-integration-issues)
- [Data Issues](#data-issues)
- [File Locking Issues](#file-locking-issues)
- [Tool Issues](#tool-issues)
- [Getting Help](#getting-help)

## Installation Issues

### "ModuleNotFoundError: No module named 'coordmcp'"

**Problem**: Python can't find the CoordMCP module.

**Solution**:
```bash
# 1. Ensure you're in the project directory
cd coordmcp
pwd  # Should show .../coordmcp

# 2. Install in development mode
pip install -e .

# 3. Verify installation
python -c "import coordmcp; print('OK')"

# 4. If still failing, check Python path
python -c "import sys; print('\n'.join(sys.path))"

# 5. Add to PYTHONPATH if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### "pip install fails with permission error"

**Problem**: Permission denied when installing packages.

**Solution**:
```bash
# Don't use sudo! Use virtual environment instead
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
```

### "fastmcp module not found"

**Problem**: Dependencies not installed.

**Solution**:
```bash
# Reinstall with dependencies
pip install -e . --force-reinstall

# Or install manually
pip install fastmcp>=0.4.0 pydantic>=2.0.0 python-dotenv>=1.0.0
```

## Server Issues

### "Server won't start"

**Problem**: Nothing happens or error on startup.

**Solution**:
```bash
# 1. Check Python version (need 3.8+)
python --version

# 2. Run with debug logging
COORDMCP_LOG_LEVEL=DEBUG python -m coordmcp.main

# 3. Check for import errors
python -c "from coordmcp.main import main"

# 4. Verify data directory is writable
mkdir -p ~/.coordmcp/data
touch ~/.coordmcp/data/test && rm ~/.coordmcp/data/test
```

### "Address already in use" or port errors

**Problem**: Port conflicts (unusual for stdio transport).

**Solution**:
CoordMCP uses stdio transport, not TCP ports. This error usually means:
- Another MCP server is using the same name
- Multiple CoordMCP instances running

```bash
# Check for running processes
ps aux | grep coordmcp

# Kill if needed
pkill -f "python -m coordmcp.main"
```

### "Server starts but doesn't respond"

**Problem**: Server appears running but tools don't work.

**Solution**:
1. Check logs: `cat ~/.coordmcp/logs/coordmcp.log`
2. Verify server initialized: Look for "CoordMCP server initialized and ready"
3. Check if tools registered: Look for "All tools registered successfully"
4. Restart the server
5. Restart your agent IDE

## Agent Integration Issues

### "Tools not appearing in agent"

**Problem**: CoordMCP tools don't show up in agent interface.

**Solution**:
```bash
# 1. Verify server is running
python -m coordmcp.main

# 2. Check agent configuration syntax
# OpenCode example:
cat opencode.jsonc | python -m json.tool  # Should be valid JSON

# 3. Restart agent IDE completely
# Close and reopen VS Code/Cursor/etc

# 4. Check agent logs for connection errors
# Look in agent's output/console panel

# 5. Test with a simple tool
# In agent console, try: await create_project(name="test", description="test")
```

### "Connection refused" or "Connection error"

**Problem**: Agent can't connect to CoordMCP.

**Solution**:
1. Ensure CoordMCP server is running
2. Check configuration path in agent settings
3. Verify Python is accessible from agent's environment
4. Try using full Python path:
   ```json
   {
     "command": "/full/path/to/python",
     "args": ["-m", "coordmcp.main"]
   }
   ```

### "Tools appear but don't work"

**Problem**: Tools visible but executing fails.

**Solution**:
1. Check CoordMCP logs: `cat ~/.coordmcp/logs/coordmcp.log`
2. Verify data directory is writable
3. Check for errors in agent console
4. Try running a simple test:
   ```python
   # In agent
   await create_project(project_name="test", description="test")
   ```

## Data Issues

### "Data not persisting after restart"

**Problem**: Projects/agents disappear after stopping server.

**Solution**:
```bash
# 1. Check data directory location
echo $COORDMCP_DATA_DIR
# Should show: ~/.coordmcp/data or your custom path

# 2. Verify directory exists
ls -la ~/.coordmcp/data/

# 3. Check if JSON files are being created
ls -la ~/.coordmcp/data/memory/

# 4. Verify permissions
chmod -R 755 ~/.coordmcp/data

# 5. Check disk space
df -h ~/.coordmcp/
```

### "Permission denied on data directory"

**Problem**: Can't read/write data files.

**Solution**:
```bash
# Linux/macOS
mkdir -p ~/.coordmcp/data
chmod 755 ~/.coordmcp/data
chmod 644 ~/.coordmcp/data/*.json

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.coordmcp\data"
# Permissions handled differently on Windows
```

### "JSON decode error" or "Data corruption"

**Problem**: JSON files are corrupted or invalid.

**Solution**:
```bash
# 1. Check JSON validity
python -m json.tool ~/.coordmcp/data/memory/projects.json

# 2. If corrupted, restore from backup
# Or reset (WARNING: loses all data)
rm -rf ~/.coordmcp/data/

# 3. Restart server - it will recreate structure
python -m coordmcp.main
```

### "Project not found" errors

**Problem**: Can't access previously created projects.

**Solution**:
1. Verify you're using the same data directory
2. Check project exists:
   ```bash
   ls ~/.coordmcp/data/memory/
   cat ~/.coordmcp/data/global/project_registry.json
   ```
3. Ensure correct project_id in your calls

## File Locking Issues

### "File already locked by another agent"

**Problem**: Can't lock a file someone else is working on.

**Solution**:
```python
# 1. Check who has it locked
locked = await get_locked_files(project_id="your-project")

# 2. Contact the other agent to unlock
# Or wait for lock timeout (default: 24 hours)

# 3. If stale lock, cleanup may help
# Locks auto-expire after timeout
```

### "Cannot unlock file I didn't lock"

**Problem**: Trying to unlock someone else's file.

**Solution**:
- Only the agent that locked a file can unlock it
- Wait for automatic timeout
- Admin can manually edit lock files (advanced)

### "Too many files locked"

**Problem**: Hit the lock limit per agent.

**Solution**:
```python
# 1. Unlock files you're done with
await unlock_files(
    agent_id="your-agent-id",
    project_id="your-project",
    files=["src/file1.py", "src/file2.py"]
)

# 2. Or increase limit (not recommended)
# Set COORDMCP_MAX_FILE_LOCKS_PER_AGENT=200
```

## Tool Issues

### "Tool returns 'Project not found'"

**Problem**: Referencing non-existent project.

**Solution**:
```python
# 1. List all projects
from coordmcp.memory.json_store import JSONStorageBackend
storage = JSONStorageBackend()
registry = await storage.read("global/project_registry.json")
print(registry["projects"].keys())

# 2. Create project if needed
result = await create_project(
    project_name="My Project",
    description="Description"
)
project_id = result["project_id"]
```

### "Tool returns 'Agent not found'"

**Problem**: Agent ID doesn't exist.

**Solution**:
```python
# Register yourself first
result = await register_agent(
    agent_name="MyAgent",
    agent_type="opencode",
    capabilities=["python"]
)
agent_id = result["agent_id"]

# Save this ID for future use
```

### "Validation error" on tool parameters

**Problem**: Missing or invalid parameters.

**Solution**:
1. Check API reference for required parameters
2. Verify parameter types
3. Ensure UUIDs are valid format
4. Check string lengths (if using validation)

Example:
```python
# ❌ Missing required parameter
await save_decision(project_id="...")  # Missing title

# ✅ All required parameters
await save_decision(
    project_id="...",
    title="Use FastAPI",  # Required!
    description="...",
    rationale="..."
)
```

### "Tool times out"

**Problem**: Operation takes too long.

**Solution**:
1. Check disk I/O (slow storage)
2. Large data operations may take time
3. Check for deadlocks in file locking
4. Review logs for errors

## Performance Issues

### "Slow response times"

**Problem**: Tools take long to execute.

**Solution**:
```bash
# 1. Check disk performance
dd if=/dev/zero of=~/.coordmcp/test bs=1M count=10

# 2. Reduce log level
export COORDMCP_LOG_LEVEL=WARNING

# 3. Archive old data periodically
# Move old projects to backup
```

### "High memory usage"

**Problem**: CoordMCP using too much memory.

**Solution**:
1. Large data sets may need more memory
2. Restart server periodically
3. Archive old projects
4. Monitor with: `top` or Activity Monitor

## Debugging Tips

### Enable Debug Logging

```bash
export COORDMCP_LOG_LEVEL=DEBUG
python -m coordmcp.main
```

### Check Server Status

```python
# Test basic functionality
import asyncio
from coordmcp.memory.json_store import JSONStorageBackend

async def test():
    storage = JSONStorageBackend()
    await storage.write("test.json", {"status": "ok"})
    result = await storage.read("test.json")
    print(f"Test: {result}")

asyncio.run(test())
```

### View Recent Logs

```bash
# Last 50 lines
tail -n 50 ~/.coordmcp/logs/coordmcp.log

# Search for errors
grep ERROR ~/.coordmcp/logs/coordmcp.log

# Follow logs in real-time
tail -f ~/.coordmcp/logs/coordmcp.log
```

### Reset Everything (Nuclear Option)

⚠️ **WARNING**: This deletes all data!

```bash
# Stop server
# Remove all data
rm -rf ~/.coordmcp/

# Restart server
python -m coordmcp.main
```

## Getting Help

### Before Asking

1. Check this troubleshooting guide
2. Review the logs: `~/.coordmcp/logs/coordmcp.log`
3. Try the debug steps above
4. Search existing [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

### What to Include

When reporting an issue, include:

1. **Error message** (exact text)
2. **Steps to reproduce**
3. **Environment**:
   - Python version: `python --version`
   - OS: Windows/macOS/Linux
   - CoordMCP version
4. **Relevant logs** (last 50 lines)
5. **Configuration** (without sensitive data)

### Support Channels

- 📧 **Email**: support@coordmcp.dev
- 💬 **Discord**: [Join our community](https://discord.gg/coordmcp)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

---

**Still stuck?** Check the [Getting Started](./GETTING_STARTED.md) guide or [API Reference](./API_REFERENCE.md).
