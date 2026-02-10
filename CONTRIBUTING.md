# Contributing to CoordMCP

Thank you for your interest in contributing to CoordMCP! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Project Structure](#project-structure)
- [Architecture Guidelines](#architecture-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip

### Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/coordmcp.git
cd coordmcp

# Add upstream remote
git remote add upstream https://github.com/original/coordmcp.git
```

## Development Setup

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Verify installation
python -m coordmcp.main --version
```

## Code Style

We follow PEP 8 with some project-specific conventions:

### Python Style

```python
# Use type hints
def create_project(project_name: str, description: str = "") -> dict:
    """Create a new project.
    
    Args:
        project_name: Name of the project (required)
        description: Optional project description
        
    Returns:
        Dictionary with project_id and status
        
    Example:
        >>> result = await create_project("My Project", "Description")
        >>> print(result["project_id"])
    """
    pass

# Maximum line length: 100 characters
# Use black for formatting
black src/coordmcp/

# Import order: stdlib, third-party, local
import os
from typing import Dict, List

from pydantic import BaseModel

from coordmcp.config import Config
```

### Documentation

- All public functions must have docstrings
- Use Google-style docstrings
- Include examples in docstrings for complex functions
- Keep README.md updated with new features

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest src/tests/ -v

# Run specific test category
python -m pytest src/tests/unit/ -v
python -m pytest src/tests/integration/ -v

# Run with coverage
python -m pytest --cov=coordmcp src/tests/

# Run specific test file
python -m pytest src/tests/unit/test_memory/test_json_store.py -v
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
```

### Test Categories

- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete workflows

## Submitting Changes

### Branch Naming

```
feature/description    # New features
bugfix/description     # Bug fixes
docs/description       # Documentation updates
refactor/description   # Code refactoring
test/description       # Test additions/improvements
```

### Commit Messages

Follow conventional commits:

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style (formatting, missing semi colons, etc)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Build process or auxiliary tool changes

Examples:
```
feat(memory): add search functionality to decisions

Implement full-text search for architectural decisions
with support for filtering by date, author, and tags.

fix(context): resolve race condition in file locking

Prevent multiple agents from simultaneously locking
the same file by adding atomic check-and-set operation.

docs(api): update tool descriptions in API_REFERENCE

Add missing parameter descriptions and examples for
context management tools.
```

### Pull Request Process

1. **Create a branch** from `main`
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes** with clear, focused commits

3. **Test your changes**
   ```bash
   python -m pytest src/tests/ -v
   ```

4. **Update documentation** if needed

5. **Push your branch**
   ```bash
   git push origin feature/my-feature
   ```

6. **Create Pull Request** on GitHub
   - Fill out the PR template
   - Link related issues
   - Request review from maintainers

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (or documented)
- [ ] Commit messages are clear

## Project Structure

```
coordmcp/
├── src/coordmcp/              # Main source code
│   ├── core/                  # Server and tool management
│   ├── memory/                # Long-term memory system
│   ├── context/               # Context and file locking
│   ├── architecture/          # Architecture tools
│   ├── tools/                 # MCP tool implementations
│   ├── resources/             # MCP resource implementations
│   ├── storage/               # Storage backends
│   ├── errors/                # Exception classes
│   └── utils/                 # Utility functions
├── src/tests/                 # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
├── docs/                      # Documentation
│   ├── INTEGRATIONS/          # Agent integration guides
│   ├── DEVELOPMENT/           # Developer documentation
│   └── examples/              # Example walkthroughs
└── examples/                  # Runnable example scripts
```

## Architecture Guidelines

### Adding New Tools

1. Create tool function in appropriate `tools/` file
2. Add comprehensive docstring with examples
3. Register in `tool_manager.py`
4. Add unit tests
5. Update API_REFERENCE.md

Example:

```python
# src/coordmcp/tools/memory_tools.py

@mcp.tool()
async def my_new_tool(
    project_id: str,
    data: str,
    config: Config = Depends(get_config)
) -> dict:
    """Brief description of what the tool does.
    
    Args:
        project_id: The project identifier
        data: Description of the data parameter
        
    Returns:
        Dictionary with operation result
        
    Raises:
        ProjectNotFoundError: If project doesn't exist
        
    Example:
        >>> result = await my_new_tool("proj-123", "example data")
        >>> print(result["status"])
        'success'
    """
    # Implementation here
    pass
```

### Adding New Resources

1. Create resource function in appropriate `resources/` file
2. Define URI pattern
3. Register in `resource_manager.py`
4. Add tests

### Adding Validation

Use the validation decorators:

```python
from coordmcp.utils.validation import (
    validate_required_fields,
    validate_project_id,
    validate_enum_field
)

@validate_required_fields("project_id", "title")
@validate_project_id
@validate_enum_field("priority", ["low", "medium", "high"])
async def save_decision(
    project_id: str,
    title: str,
    priority: str = "medium",
    **kwargs
) -> dict:
    """Save a decision with validation."""
    pass
```

### Error Handling

Always use custom exceptions:

```python
from coordmcp.errors import ProjectNotFoundError, ValidationError

async def get_project(project_id: str) -> dict:
    project = await storage.read(f"projects/{project_id}.json")
    if not project:
        raise ProjectNotFoundError(f"Project {project_id} not found")
    return project
```

## Questions?

- 📧 Email: support@coordmcp.dev
- 💬 Discord: [Join our community](https://discord.gg/coordmcp)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to CoordMCP! 🎉
