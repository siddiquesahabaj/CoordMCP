# Contributing to CoordMCP

Thank you for your interest in contributing to CoordMCP! This document provides comprehensive guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Code Style](#code-style)
- [Testing](#testing)
- [Making Changes](#making-changes)
- [Submitting Contributions](#submitting-contributions)
- [Release Process](#release-process)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold these standards:

- **Be respectful** - Treat everyone with respect and consideration
- **Be inclusive** - Welcome newcomers and help them learn
- **Be constructive** - Provide helpful feedback and criticism
- **Be patient** - Remember that people have varying levels of experience
- **Be collaborative** - Work together to build something great

## Getting Started

### Prerequisites

Before you begin, ensure you have:

- Python 3.10 or higher
- Git (for version control)
- pip (Python package manager)
- A GitHub account

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/coordmcp.git
   cd coordmcp
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original/coordmcp.git
   git fetch upstream
   ```

## Development Environment

### Option 1: Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Verify installation
python -m coordmcp --version
```

### Option 2: Using Conda

```bash
# Create conda environment
conda create -n coordmcp python=3.11
conda activate coordmcp

# Install in development mode
pip install -e ".[dev]"

# Verify
python -m coordmcp --version
```

## Project Structure

```
coordmcp/
├── src/coordmcp/              # Main source code
│   ├── core/                  # Server initialization, tool/resource registration
│   │   ├── server.py          # FastMCP server setup
│   │   ├── tool_manager.py    # Tool registration
│   │   └── resource_manager.py # Resource registration
│   ├── memory/                # Long-term memory system
│   │   ├── json_store.py      # Project memory storage
│   │   └── models.py          # Data models (Decision, TechStackEntry, etc.)
│   ├── context/               # Agent context and file locking
│   │   ├── manager.py         # Context management
│   │   ├── file_tracker.py    # File locking system
│   │   └── state.py           # State models
│   ├── architecture/          # Architecture tools
│   │   ├── analyzer.py        # Code structure analysis
│   │   ├── patterns.py        # Design pattern library
│   │   └── recommender.py     # Architecture recommendations
│   ├── tools/                 # MCP tool implementations
│   │   ├── memory_tools.py    # Project, decision, tech stack tools
│   │   ├── context_tools.py   # Agent, context, file locking tools
│   │   ├── discovery_tools.py # Project/agent discovery
│   │   └── architecture_tools.py # Architecture analysis tools
│   ├── resources/             # MCP resource implementations
│   ├── storage/               # Storage backends
│   │   └── json_adapter.py    # JSON file storage
│   ├── utils/                 # Utility functions
│   │   ├── validation.py      # Input validation
│   │   └── project_resolver.py # Project lookup utilities
│   └── __init__.py            # Package initialization
├── src/tests/                 # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
├── docs/                      # Documentation
├── pyproject.toml             # Project configuration
└── README.md                  # Main documentation
```

## Code Style

We follow PEP 8 with project-specific conventions:

### Python Style Guide

```python
# 1. Use type hints for all function parameters and return values
async def create_project(
    project_name: str,
    workspace_path: str,
    description: str = ""
) -> Dict[str, Any]:
    """Create a new project.
    
    Args:
        project_name: Name of the project (required)
        workspace_path: Absolute path to project directory (required)
        description: Optional project description
        
    Returns:
        Dictionary with project_id and status
        
    Example:
        >>> result = await create_project("My App", "/path/to/app")
        >>> print(result["project_id"])
    """
    pass

# 2. Maximum line length: 100 characters
# 3. Use double quotes for strings
# 4. Use trailing commas in multi-line structures

# 5. Import order: stdlib, third-party, local
import os
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from coordmcp.config import Config
from coordmcp.memory.models import ProjectInfo
```

### Docstring Standards

Use Google-style docstrings with examples:

```python
async def register_agent(
    agent_name: str,
    agent_type: str,
    capabilities: List[str] = []
) -> Dict[str, Any]:
    """Register a new agent in the global registry.
    
    This function creates or reconnects to an existing agent based on name.
    Agents with the same name will reconnect to their existing identity.
    
    Args:
        agent_name: Name of the agent (e.g., "OpenCode", "Cursor")
        agent_type: Type of agent - "opencode", "cursor", "claude_code", or "custom"
        capabilities: List of agent capabilities (e.g., ["python", "react"])
        
    Returns:
        Dictionary with:
        - success: Boolean indicating success
        - agent_id: Unique agent identifier
        - message: Status message
        
    Raises:
        ValidationError: If agent_type is invalid
        
    Example:
        >>> result = await register_agent("MyAgent", "opencode", ["python"])
        >>> if result["success"]:
        ...     print(f"Agent ID: {result['agent_id']}")
    """
```

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Files | snake_case | `memory_tools.py` |
| Classes | PascalCase | `ProjectInfo` |
| Functions | snake_case | `create_project` |
| Variables | snake_case | `project_id` |
| Constants | UPPER_SNAKE_CASE | `SCHEMA_VERSION` |
| Private | _leading_underscore | `_internal_function` |

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest src/tests/ -v

# Run with coverage
python -m pytest --cov=coordmcp src/tests/ -v

# Run specific test category
python -m pytest src/tests/unit/ -v
python -m pytest src/tests/integration/ -v
python -m pytest src/tests/e2e/ -v

# Run specific test file
python -m pytest src/tests/unit/test_memory/test_json_store.py -v

# Run specific test
python -m pytest src/tests/unit/test_memory/test_json_store.py::TestProjectCreation -v
```

### Writing Tests

```python
# tests/unit/test_memory/test_json_store.py
import pytest
from coordmcp.memory.json_store import JSONStorageBackend

class TestJSONStorageBackend:
    """Test JSON storage backend operations."""
    
    @pytest.fixture
    def storage(self, tmp_path):
        """Create temporary storage for testing."""
        return JSONStorageBackend(base_path=tmp_path)
    
    def test_read_write(self, storage):
        """Test basic read/write operations."""
        data = {"key": "value"}
        storage.write("test.json", data)
        result = storage.read("test.json")
        assert result == data
    
    def test_read_nonexistent(self, storage):
        """Test reading non-existent file returns None."""
        result = storage.read("nonexistent.json")
        assert result is None
    
    def test_atomic_write(self, storage):
        """Test atomic write prevents corruption."""
        data = {"important": "data"}
        storage.write("important.json", data)
        # Verify file exists and is valid JSON
        result = storage.read("important.json")
        assert result == data
```

### Test Categories

- **Unit Tests** (`src/tests/unit/`): Test individual functions/classes
- **Integration Tests** (`src/tests/integration/`): Test component interactions
- **E2E Tests** (`src/tests/e2e/`): Test complete workflows

### Test Markers

```python
@pytest.mark.unit
@pytest.mark.memory
class TestProjectCreation:
    """Test project creation."""
    
    @pytest.mark.asyncio
    async def test_create_project(self):
        """Test creating a project."""
        pass
```

## Making Changes

### Branch Naming

```
feature/description          # New features
bugfix/description           # Bug fixes
docs/description             # Documentation updates
refactor/description         # Code refactoring
test/description             # Test additions
chore/description            # Maintenance tasks
```

Examples:
- `feature/add-discovery-tools`
- `bugfix/fix-workspace-path-validation`
- `docs/update-readme-installation`

### Commit Messages

Follow conventional commits:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, no logic changes)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

**Examples:**
```
feat(tools): add discover_project tool for workspace-based lookup

Implement project discovery by directory path with parent
directory search support. This enables agents to automatically
find projects when working in a directory.

fix(memory): resolve workspace_path validation error

Fix issue where relative paths were accepted when absolute
paths are required. Now properly validates path format.

docs(readme): update installation instructions for pip

Add clear pip installation instructions and troubleshoot
guide for common installation issues.
```

### Adding New Tools

1. **Create tool function** in appropriate file:
   ```python
   # src/coordmcp/tools/memory_tools.py
   
   async def my_new_tool(
       project_id: Optional[str] = None,
       project_name: Optional[str] = None,
       workspace_path: Optional[str] = None,
       **kwargs
   ) -> Dict[str, Any]:
       """Brief description.
       
       Detailed description of what the tool does.
       
       Args:
           project_id: Project identifier (optional)
           project_name: Project name (optional)
           workspace_path: Workspace path (optional)
           
       Returns:
           Dictionary with result
       """
       # Implementation
       pass
   ```

2. **Register in tool_manager.py**:
   ```python
   @server.tool()
   async def my_new_tool(...):
       """Docstring here."""
       return await memory_tools.my_new_tool(...)
   ```

3. **Add tests**:
   ```python
   # tests/unit/test_tools/test_memory_tools.py
   
   @pytest.mark.asyncio
   async def test_my_new_tool():
       """Test my_new_tool."""
       result = await my_new_tool(project_id="test")
       assert result["success"]
   ```

4. **Update documentation**:
   - Add to README.md tool list
   - Update API_REFERENCE.md
   - Add example if needed

### Adding Validation

```python
from coordmcp.utils.validation import (
    validate_required_fields,
    validate_project_id,
    validate_enum_field
)

@validate_required_fields("title", "rationale")
@validate_project_id
async def save_decision(
    project_id: str,
    title: str,
    rationale: str,
    **kwargs
) -> Dict[str, Any]:
    """Save decision with validation."""
    pass
```

## Submitting Contributions

### Pull Request Process

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes** with focused commits

3. **Run tests** locally:
   ```bash
   python -m pytest src/tests/ -v
   ```

4. **Update documentation**:
   - Update README.md if adding features
   - Update CHANGELOG.md
   - Add/update docstrings

5. **Push your branch**:
   ```bash
   git push origin feature/my-feature
   ```

6. **Create Pull Request** on GitHub:
   - Fill out the PR template
   - Link related issues
   - Request review from maintainers

### PR Checklist

Before submitting:

- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (or documented)
- [ ] Commit messages follow conventions
- [ ] PR description is clear

### Review Process

- Maintainers will review within 48 hours
- Address review comments promptly
- Be open to feedback and suggestions
- Ask questions if anything is unclear

## Release Process

### Version Numbering

We follow Semantic Versioning (SemVer):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes

### Creating a Release

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Create git tag**:
   ```bash
   git tag -a v0.2.0 -m "Release version 0.2.0"
   git push origin v0.2.0
   ```
4. **Build package**:
   ```bash
   python -m build
   ```
5. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

## Getting Help

- 📧 Email: support@coordmcp.dev
- 💬 Discord: [Join our community](https://discord.gg/coordmcp)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to CoordMCP! 🎉
