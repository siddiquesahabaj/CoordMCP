# Troubleshooting

Common issues and solutions for CoordMCP.

## Quick Diagnostics

```bash
# Check version
coordmcp --version

# Test server
python -m coordmcp

# Check logs
tail -f ~/.coordmcp/logs/coordmcp.log
```

---

## Installation Issues

### "ModuleNotFoundError: No module named 'coordmcp'"

**Problem:** Python can't find CoordMCP.

**Solution:**
```bash
# 1. Ensure you're in project directory
cd coordmcp

# 2. Install
pip install -e .

# 3. Verify
python -c "import coordmcp; print('OK')"
```

### "pip install fails with permission error"

**Problem:** Permission denied.

**Solution:**
```bash
# Don't use sudo! Use virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
```

### "fastmcp module not found"

**Problem:** Dependencies missing.

**Solution:**
```bash
pip install -e . --force-reinstall
# Or manually
pip install fastmcp pydantic python-dotenv
```

---

## Server Issues

### "Server won't start"

**Problem:** Nothing happens or error on startup.

**Solution:**
```bash
# 1. Check Python version (need 3.10+)
python --version

# 2. Run with debug logging
COORDMCP_LOG_LEVEL=DEBUG python -m coordmcp

# 3. Check for import errors
python -c "from coordmcp.main import main"

# 4. Verify data directory
mkdir -p ~/.coordmcp/data
```

### "Server starts but doesn't respond"

**Problem:** Server running but tools don't work.

**Solution:**
1. Check logs: `cat ~/.coordmcp/logs/coordmcp.log`
2. Look for "CoordMCP server initialized and ready"
3. Look for "All tools registered successfully"
4. Restart the server
5. Restart your AI agent

---

## Agent Integration Issues

### "Tools not appearing in agent"

**Problem:** CoordMCP tools don't show up.

**Solution:**
```bash
# 1. Verify server runs
python -m coordmcp

# 2. Check config syntax
cat opencode.jsonc | python -m json.tool

# 3. Restart agent IDE completely

# 4. Check agent logs for connection errors
```

### "Connection refused" or "Connection error"

**Problem:** Agent can't connect to CoordMCP.

**Solution:**
1. Ensure CoordMCP server is running
2. Check configuration path
3. Use full Python path:
```json
{
  "command": "/full/path/to/python",
  "args": ["-m", "coordmcp"]
}
```

### "Tools appear but don't work"

**Problem:** Tools visible but fail when called.

**Solution:**
```bash
# Check logs
cat ~/.coordmcp/logs/coordmcp.log

# Verify data directory permissions
chmod -R 755 ~/.coordmcp/data
```

---

## Data Issues

### "Data not persisting after restart"

**Problem:** Projects/agents disappear.

**Solution:**
```bash
# 1. Check data directory
echo $COORDMCP_DATA_DIR
ls -la ~/.coordmcp/data/

# 2. Verify files exist
ls ~/.coordmcp/data/memory/

# 3. Check permissions
chmod -R 755 ~/.coordmcp/data
```

### "Permission denied on data directory"

**Problem:** Can't read/write data.

**Solution:**
```bash
# Linux/macOS
mkdir -p ~/.coordmcp/data
chmod 755 ~/.coordmcp/data

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.coordmcp\data"
```

### "JSON decode error"

**Problem:** Corrupted data files.

**Solution:**
```bash
# Check which file is corrupted
python -m json.tool ~/.coordmcp/data/memory/*/decisions.json

# If corrupted, restore from backup or reset
rm -rf ~/.coordmcp/data/
python -m coordmcp  # Will recreate
```

---

## File Locking Issues

### "File already locked by another agent"

**Problem:** Can't edit a locked file.

**Solution:**
```python
# Check who has it locked
locked = await coordmcp_get_locked_files(project_id=project_id)

# Wait for timeout (default: 24 hours)
# Or coordinate with that agent
```

### "Too many files locked"

**Problem:** Hit lock limit.

**Solution:**
```python
# Unlock files you're done with
await coordmcp_unlock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["src/file1.py", "src/file2.py"]
)
```

---

## Tool Issues

### "Project not found"

**Problem:** Referencing non-existent project.

**Solution:**
```python
# Use discover_project first
discovery = await coordmcp_discover_project(path=os.getcwd())
```

### "Agent not found"

**Problem:** Agent ID doesn't exist.

**Solution:**
```python
# Register first
agent = await coordmcp_register_agent(
    agent_name="MyAgent",
    agent_type="opencode",
    capabilities=["python"]
)
```

### "Validation error"

**Problem:** Missing or invalid parameters.

**Solution:**
- Check required parameters in API reference
- Verify parameter types
- Use absolute paths for `workspace_path`

---

## Performance Issues

### "Slow response times"

**Problem:** Tools take too long.

**Solution:**
```bash
# 1. Reduce log level
export COORDMCP_LOG_LEVEL=WARNING

# 2. Archive old projects
mv ~/.coordmcp/data/memory/old-project ~/.coordmcp/archive/
```

### "High memory usage"

**Problem:** Using too much memory.

**Solution:**
1. Restart server periodically
2. Archive old projects
3. Monitor with `top` or Task Manager

---

## Debug Mode

Enable detailed logging:

```bash
export COORDMCP_LOG_LEVEL=DEBUG
python -m coordmcp
```

View logs:
```bash
# Recent logs
tail -n 50 ~/.coordmcp/logs/coordmcp.log

# Search for errors
grep ERROR ~/.coordmcp/logs/coordmcp.log

# Follow in real-time
tail -f ~/.coordmcp/logs/coordmcp.log
```

---

## Reset Everything

**WARNING:** Deletes all data!

```bash
# Stop server
# Remove all data
rm -rf ~/.coordmcp/

# Restart
python -m coordmcp
```

---

## Getting Help

### Before Asking

1. Check this troubleshooting guide
2. Check logs: `~/.coordmcp/logs/coordmcp.log`
3. Try debug mode
4. Search [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

### What to Include

When reporting an issue:

1. **Error message** (exact text)
2. **Steps to reproduce**
3. **Environment:**
   - Python version: `python --version`
   - OS: Windows/macOS/Linux
   - CoordMCP version
4. **Relevant logs** (last 50 lines)

### Support Channels

- Email: support@coordmcp.dev
- Discord: [Join our community](https://discord.gg/coordmcp)
- Issues: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)
