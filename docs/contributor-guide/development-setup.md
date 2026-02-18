# Development Setup

Set up your development environment for CoordMCP.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- git

## Setup Steps

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp
```

### 2. Create Virtual Environment

```bash
# Create
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install in development mode
pip install -e ".[dev]"
```

### 4. Verify Installation

```bash
# Run tests
python -m pytest src/tests/ -v

# Start server
python -m coordmcp
```

## Project Structure

```
coordmcp/
├── src/
│   ├── coordmcp/         # Source code
│   └── tests/            # Test suite
├── docs/                 # Documentation
├── pyproject.toml        # Project config
└── README.md
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `COORDMCP_DATA_DIR` | `~/.coordmcp/data` | Data storage |
| `COORDMCP_LOG_LEVEL` | `INFO` | Log level |
| `COORDMCP_LOG_FILE` | `~/.coordmcp/logs/coordmcp.log` | Log file |
| `COORDMCP_LOCK_TIMEOUT_HOURS` | `24` | Lock timeout |
| `COORDMCP_MAX_FILE_LOCKS_PER_AGENT` | `100` | Max locks |

### Setting Variables

```bash
# Linux/macOS
export COORDMCP_LOG_LEVEL=DEBUG

# Windows
set COORDMCP_LOG_LEVEL=DEBUG

# Or create .env file
echo "COORDMCP_LOG_LEVEL=DEBUG" > .env
```

## Development Workflow

### Running the Server

```bash
# Normal mode
python -m coordmcp

# Debug mode
COORDMCP_LOG_LEVEL=DEBUG python -m coordmcp
```

### Running Tests

```bash
# All tests
python -m pytest src/tests/ -v

# Unit tests only
python -m pytest src/tests/unit/ -v

# Integration tests
python -m pytest src/tests/integration/ -v

# With coverage
python -m pytest src/tests/ --cov=coordmcp --cov-report=html
```

### Code Style

```bash
# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

## IDE Setup

### VS Code

1. Install Python extension
2. Select virtual environment interpreter
3. Recommended settings:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black"
}
```

### PyCharm

1. Open project directory
2. Set Python interpreter to venv
3. Enable pytest as test runner

## Debugging

### Enable Debug Logging

```bash
export COORDMCP_LOG_LEVEL=DEBUG
python -m coordmcp
```

### View Logs

```bash
# Tail logs
tail -f ~/.coordmcp/logs/coordmcp.log

# Search for errors
grep ERROR ~/.coordmcp/logs/coordmcp.log
```

### Debug in Code

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Common Issues

### Import Errors

```bash
# Ensure you're in the project root
cd coordmcp

# Reinstall
pip install -e . --force-reinstall
```

### Test Failures

```bash
# Clear cache
rm -rf .pytest_cache __pycache__

# Run specific test
python -m pytest src/tests/unit/test_memory/test_json_store.py -v
```

### Permission Errors

```bash
# Fix data directory permissions
chmod -R 755 ~/.coordmcp/data
```

## Next Steps

- [Architecture](architecture.md) - Understand the system
- [Testing](testing.md) - Write and run tests
- [Extending](extending.md) - Add new features
