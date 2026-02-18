# Testing

How to run and write tests for CoordMCP.

## Test Structure

```
src/tests/
├── unit/               # Unit tests
│   ├── test_memory/    # Memory system tests
│   ├── test_context/   # Context system tests
│   └── test_architecture/  # Architecture tests
├── integration/        # Integration tests
├── e2e/               # End-to-end tests
├── utils/             # Test utilities
│   ├── factories.py   # Test data factories
│   └── assertions.py  # Custom assertions
├── fixtures/          # Test fixtures
└── conftest.py        # Pytest configuration
```

## Running Tests

### All Tests

```bash
python -m pytest src/tests/ -v
```

### By Category

```bash
# Unit tests
python -m pytest src/tests/unit/ -v

# Integration tests
python -m pytest src/tests/integration/ -v

# E2E tests
python -m pytest src/tests/e2e/ -v
```

### Specific Test File

```bash
python -m pytest src/tests/unit/test_memory/test_json_store.py -v
```

### Specific Test

```bash
python -m pytest src/tests/unit/test_memory/test_json_store.py::TestProjectCreation -v
```

### With Coverage

```bash
python -m pytest src/tests/ --cov=coordmcp --cov-report=html
```

Coverage report generated in `htmlcov/index.html`.

## Writing Tests

### Test Structure

```python
import pytest
from coordmcp.memory.json_store import ProjectMemoryStore

class TestFeature:
    """Tests for Feature X."""
    
    @pytest.fixture
    def store(self, tmp_path):
        """Create a test store."""
        return ProjectMemoryStore(storage=tmp_path)
    
    def test_basic_operation(self, store):
        """Test basic operation."""
        # Arrange
        project_name = "Test Project"
        
        # Act
        result = store.create_project(project_name)
        
        # Assert
        assert result is not None
        assert "project_id" in result
```

### Using Fixtures

```python
# In conftest.py
import pytest
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.storage.json_adapter import JSONStorageBackend

@pytest.fixture
def storage(tmp_path):
    """Create test storage."""
    return JSONStorageBackend(data_dir=str(tmp_path))

@pytest.fixture
def memory_store(storage):
    """Create test memory store."""
    return ProjectMemoryStore(storage)
```

### Test Markers

```python
import pytest

@pytest.mark.unit
def test_unit_function():
    """Unit test."""
    pass

@pytest.mark.integration
def test_integration():
    """Integration test."""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Slow test."""
    pass
```

Run by marker:
```bash
python -m pytest -m unit
python -m pytest -m "not slow"
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    """Test async function."""
    result = await some_async_function()
    assert result.success
```

## Test Utilities

### Factories

```python
# In tests/utils/factories.py
from coordmcp.memory.models import Decision

def create_decision(**kwargs):
    """Create test decision."""
    defaults = {
        "id": "test-decision-id",
        "title": "Test Decision",
        "description": "Test description",
        "rationale": "Test rationale",
    }
    defaults.update(kwargs)
    return Decision(**defaults)
```

### Custom Assertions

```python
# In tests/utils/assertions.py
def assert_successful(response):
    """Assert response is successful."""
    assert response["success"] is True
    assert "error" not in response

def assert_error(response, error_type):
    """Assert response has specific error."""
    assert response["success"] is False
    assert response["error_type"] == error_type
```

## Test Categories

### Unit Tests

Test individual functions in isolation.

```python
class TestDecisionModel:
    def test_create_decision(self):
        decision = Decision(
            id="test-id",
            title="Test",
            description="Desc",
            rationale="Why"
        )
        assert decision.title == "Test"
```

### Integration Tests

Test component interactions.

```python
class TestMemoryIntegration:
    def test_save_and_retrieve(self, memory_store):
        # Create project
        project_id = memory_store.create_project("Test")
        
        # Save decision
        decision = create_decision()
        memory_store.save_decision(project_id, decision)
        
        # Retrieve
        decisions = memory_store.get_all_decisions(project_id)
        assert len(decisions) == 1
```

### E2E Tests

Test complete workflows.

```python
class TestCompleteWorkflow:
    @pytest.mark.asyncio
    async def test_project_lifecycle(self):
        # Discover
        result = await discover_project()
        
        # Create if needed
        if not result["found"]:
            result = await create_project(...)
        
        # Register agent
        agent = await register_agent(...)
        
        # Complete workflow
        # ...
```

## Best Practices

1. **One assertion per test** - Keep tests focused
2. **Descriptive names** - `test_create_project_with_valid_data`
3. **Arrange-Act-Assert** - Clear test structure
4. **Use fixtures** - Avoid duplication
5. **Test edge cases** - Empty inputs, errors, boundaries
6. **Keep tests fast** - Use mocks for slow operations

## Continuous Integration

Tests run automatically on:
- Push to main
- Pull requests

Configuration in `.github/workflows/test.yml`.

## Next Steps

- [Architecture](architecture.md) - Understand the system
- [Extending](extending.md) - Add new features
