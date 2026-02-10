# Installation Guide

Complete installation instructions for CoordMCP.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Virtual Environment Setup](#virtual-environment-setup)
- [Verification](#verification)
- [Next Steps](#next-steps)

## Prerequisites

Before installing CoordMCP, ensure you have:

- **Python 3.8 or higher**
  ```bash
  python --version  # Should show 3.8 or higher
  ```

- **pip** (Python package manager)
  ```bash
  pip --version
  ```

- **Git** (for cloning)
  ```bash
  git --version
  ```

## Installation Methods

### Method 1: Install from Source (Recommended)

This is the recommended method for development and testing.

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp

# 2. (Optional but recommended) Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 4. Install CoordMCP
pip install -e .

# 5. Verify installation
python -c "import coordmcp; print('CoordMCP installed successfully')"
```

### Method 2: Install via pip (Coming Soon)

When CoordMCP is published to PyPI:

```bash
pip install coordmcp
```

### Method 3: Development Install

For contributing to CoordMCP:

```bash
# Clone and setup
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install with development dependencies
pip install -e ".[dev]"

# Run tests to verify
python -m pytest src/tests/ -v
```

## Virtual Environment Setup

Using a virtual environment is strongly recommended to avoid conflicts with other Python packages.

### Why Use Virtual Environments?

- **Isolation**: Keeps CoordMCP dependencies separate
- **Reproducibility**: Ensures consistent environment
- **No conflicts**: Won't interfere with system Python

### Creating a Virtual Environment

**Option 1: Using venv (built-in)**

```bash
# Create
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Deactivate when done
deactivate
```

**Option 2: Using conda**

```bash
# Create
conda create -n coordmcp python=3.10

# Activate
conda activate coordmcp

# Deactivate
conda deactivate
```

**Option 3: Using pipenv**

```bash
# Install pipenv if not present
pip install pipenv

# Create environment
pipenv install

# Activate
pipenv shell
```

### Virtual Environment Best Practices

1. **Always activate** before working on CoordMCP
2. **Never commit** the venv folder (it's in .gitignore)
3. **Recreate** if you encounter dependency issues:
   ```bash
   rm -rf venv
   python -m venv venv
   pip install -e .
   ```

## Verification

After installation, verify everything is working:

### Test 1: Import Test

```bash
python -c "from coordmcp.main import main; print('Import successful')"
```

### Test 2: Server Start Test

```bash
python -m coordmcp.main
```

Expected output:
```
INFO - Starting CoordMCP server...
INFO - Storage backend initialized
INFO - CoordMCP server v0.1.0 created
INFO - Registering tools...
INFO - All tools registered successfully
INFO - CoordMCP server initialized and ready
```

Press Ctrl+C to stop the server.

### Test 3: Run Test Suite

```bash
# Run all tests
python -m pytest src/tests/ -v

# Or run specific test
python -m pytest src/tests/integration/test_full_integration.py -v
```

Expected: All tests should pass.

### Test 4: Tool Test

Create a test script:

```python
# test_installation.py
import asyncio
from coordmcp.memory.json_store import JSONStorageBackend
from coordmcp.memory.models import Project

async def test():
    storage = JSONStorageBackend()
    
    # Test write
    await storage.write("test.json", {"status": "ok"})
    
    # Test read
    data = await storage.read("test.json")
    assert data["status"] == "ok"
    
    print("✅ Installation verified!")

asyncio.run(test())
```

Run it:
```bash
python test_installation.py
```

## Platform-Specific Notes

### Windows

- Use `venv\Scripts\activate` to activate
- Use forward slashes or escaped backslashes in paths
- Python might be `py` instead of `python`

### macOS

- May need to use `python3` instead of `python`
- Xcode command line tools required: `xcode-select --install`

### Linux

- May need python3-dev: `sudo apt-get install python3-dev`
- Use `python3` and `pip3` if Python 2 is also installed

## Troubleshooting Installation

### "pip not found"

```bash
# Install pip
python -m ensurepip --upgrade
# or
curl https://bootstrap.pypa.io/get-pip.py | python
```

### "Permission denied"

```bash
# Don't use sudo with pip
# Instead, use virtual environment
python -m venv venv
source venv/bin/activate
pip install -e .
```

### "ModuleNotFoundError after installation"

```bash
# Make sure you're in the project root
cd coordmcp

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall
pip install -e . --force-reinstall
```

### "No module named 'fastmcp'"

```bash
# Install dependencies manually
pip install fastmcp>=0.4.0 pydantic>=2.0.0 python-dotenv>=1.0.0

# Or reinstall
pip install -e . --force-reinstall
```

## Data Directory

After first run, CoordMCP creates a data directory:

```
~/.coordmcp/
├── data/              # Project and agent data
└── logs/              # Log files
```

You can change this location with the `COORDMCP_DATA_DIR` environment variable.

## Next Steps

After successful installation:

1. **[Configuration](./CONFIGURATION.md)** - Set up environment variables
2. **[Getting Started](./GETTING_STARTED.md)** - Create your first project
3. **[Integrations](./INTEGRATIONS/)** - Connect to your coding agent
4. **[API Reference](./API_REFERENCE.md)** - Learn the tools

## Uninstallation

If you need to remove CoordMCP:

```bash
# Uninstall package
pip uninstall coordmcp

# Remove data (optional)
rm -rf ~/.coordmcp

# Remove virtual environment (optional)
rm -rf venv
```

## Getting Help

- 📧 **Email**: support@coordmcp.dev
- 💬 **Discord**: [Join our community](https://discord.gg/coordmcp)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

---

**Installation complete!** Continue to [Configuration](./CONFIGURATION.md) or [Getting Started](./GETTING_STARTED.md).
