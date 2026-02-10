# CoordMCP - Code Examples & Patterns

## 1. Configuration Pattern

### config.py Template
```python
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from typing import Literal

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

@dataclass
class Config:
    """Global configuration for CoordMCP"""
    
    # Storage
    data_dir: Path = Path.home() / ".coordmcp" / "data"
    
    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_file: Path = Path.home() / ".coordmcp" / "logs" / "coordmcp.log"
    
    # Behavior
    max_file_locks_per_agent: int = 100
    lock_timeout_hours: int = 24
    auto_cleanup_stale_locks: bool = True
    
    # Version
    version: str = "0.1.0"
    
    def __post_init__(self):
        """Create directories if they don't exist"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

_config: Config | None = None

def get_config() -> Config:
    """Get cached config instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config

def set_config(config: Config) -> None:
    """Override config (useful for testing)"""
    global _config
    _config = config
```

---

## 2. Logger Pattern

### logger.py Template
```python
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from coordmcp.config import get_config

def setup_logging(log_file: Optional[Path] = None, level: str = "INFO") -> None:
    """Setup logging for CoordMCP"""
    
    config = get_config()
    log_file = log_file or config.log_file
    
    # Create logger
    logger = logging.getLogger("coordmcp")
    logger.setLevel(getattr(logging, level))
    
    # File handler with rotation
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    
    # Format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    # Add handler
    logger.addHandler(handler)
    
    # Also log to console for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def get_logger(name: str) -> logging.Logger:
    """Get logger instance for a module"""
    return logging.getLogger(f"coordmcp.{name}")
```

---

## 3. Storage Abstraction Pattern

### storage/base.py Template
```python
from abc import ABC, abstractmethod
from typing import Dict, Optional, List

class StorageBackend(ABC):
    """Abstract storage backend"""
    
    @abstractmethod
    def save(self, key: str, data: Dict) -> bool:
        """
        Save data with atomic write
        
        Args:
            key: Storage key (e.g., "memory/proj1/decisions")
            data: Data to save (will be JSON serialized)
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[Dict]:
        """
        Load data from storage
        
        Args:
            key: Storage key
            
        Returns:
            Data dict if exists, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete data from storage"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass
    
    @abstractmethod
    def list_keys(self, prefix: str) -> List[str]:
        """List all keys matching prefix"""
        pass
    
    @abstractmethod
    def batch_save(self, items: Dict[str, Dict]) -> bool:
        """Save multiple items (should be atomic)"""
        pass
```

### storage/json_adapter.py Template
```python
import json
import tempfile
from pathlib import Path
from typing import Dict, Optional, List
from coordmcp.storage.base import StorageBackend
from coordmcp.logger import get_logger

logger = get_logger("storage.json")

class JSONStorageBackend(StorageBackend):
    """JSON file-based storage backend"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_path(self, key: str) -> Path:
        """Convert key to file path"""
        # Replace / with os separator, add .json
        parts = key.split("/")
        file_path = self.base_dir / Path(*parts).with_suffix(".json")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        return file_path
    
    def save(self, key: str, data: Dict) -> bool:
        """Save with atomic write (temp file + rename)"""
        try:
            file_path = self._get_path(key)
            
            # Write to temp file first
            with tempfile.NamedTemporaryFile(
                mode='w',
                dir=file_path.parent,
                delete=False,
                suffix='.tmp'
            ) as tmp:
                json.dump(data, tmp, indent=2)
                tmp_path = tmp.name
            
            # Atomic rename
            Path(tmp_path).replace(file_path)
            logger.debug(f"Saved: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save {key}: {e}")
            return False
    
    def load(self, key: str) -> Optional[Dict]:
        """Load from JSON file"""
        try:
            file_path = self._get_path(key)
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            logger.debug(f"Loaded: {key}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted JSON {key}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete file"""
        try:
            file_path = self._get_path(key)
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self._get_path(key).exists()
    
    def list_keys(self, prefix: str) -> List[str]:
        """List all keys with prefix"""
        try:
            prefix_path = self.base_dir / prefix
            keys = []
            
            if not prefix_path.exists():
                return keys
            
            for file_path in prefix_path.rglob("*.json"):
                # Convert path back to key format
                rel_path = file_path.relative_to(self.base_dir)
                key = str(rel_path).replace("\\", "/").replace(".json", "")
                keys.append(key)
            
            return keys
            
        except Exception as e:
            logger.error(f"Failed to list keys {prefix}: {e}")
            return []
    
    def batch_save(self, items: Dict[str, Dict]) -> bool:
        """Save multiple items"""
        # In simple implementation, save individually
        # For atomic batch, would use transaction-like pattern
        all_success = True
        for key, data in items.items():
            if not self.save(key, data):
                all_success = False
        return all_success
```

---

## 4. Data Models Pattern

### memory/models.py Template
```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Literal
from uuid import uuid4

@dataclass
class Decision:
    """Major technical or architectural decision"""
    
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    title: str = ""
    description: str = ""
    context: str = ""
    rationale: str = ""
    impact: str = ""
    status: Literal["active", "archived", "superseded"] = "active"
    related_files: List[str] = field(default_factory=list)
    author_agent: str = ""
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON"""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "title": self.title,
            "description": self.description,
            "context": self.context,
            "rationale": self.rationale,
            "impact": self.impact,
            "status": self.status,
            "related_files": self.related_files,
            "author_agent": self.author_agent,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Decision":
        """Create from dictionary"""
        return cls(**data)

@dataclass
class Change:
    """Change to project files/architecture"""
    
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    file_path: str = ""
    change_type: Literal["create", "modify", "delete", "refactor"] = "modify"
    description: str = ""
    code_summary: str = ""
    agent_id: str = ""
    architecture_impact: Literal["none", "minor", "significant"] = "none"
    related_decision: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "file_path": self.file_path,
            "change_type": self.change_type,
            "description": self.description,
            "code_summary": self.code_summary,
            "agent_id": self.agent_id,
            "architecture_impact": self.architecture_impact,
            "related_decision": self.related_decision
        }

@dataclass
class LockInfo:
    """File lock information"""
    
    file_path: str = ""
    locked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    locked_by: str = ""  # agent_id
    reason: str = ""
    expected_unlock_time: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "locked_at": self.locked_at,
            "locked_by": self.locked_by,
            "reason": self.reason,
            "expected_unlock_time": self.expected_unlock_time
        }
```

---

## 5. Manager Pattern

### memory/json_store.py Template
```python
from typing import List, Optional, Dict
from pathlib import Path
from coordmcp.storage.base import StorageBackend
from coordmcp.memory.models import Decision, Change
from coordmcp.logger import get_logger

logger = get_logger("memory.store")

class ProjectMemoryStore:
    """Manages long-term memory for a project"""
    
    def __init__(self, storage_backend: StorageBackend):
        self.storage = storage_backend
    
    # ==================== DECISIONS ====================
    
    def save_decision(self, project_id: str, decision: Decision) -> str:
        """Save decision, return decision ID"""
        
        # Validate
        if not decision.title or not decision.rationale:
            raise ValueError("Decision must have title and rationale")
        
        # Load existing decisions
        key = f"memory/{project_id}/decisions"
        data = self.storage.load(key) or {"decisions": []}
        
        # Add new decision
        data["decisions"].append(decision.to_dict())
        
        # Save
        if self.storage.save(key, data):
            logger.info(f"Decision saved: {decision.id}")
            return decision.id
        else:
            raise RuntimeError(f"Failed to save decision")
    
    def get_decision(self, project_id: str, decision_id: str) -> Optional[Decision]:
        """Get specific decision"""
        
        key = f"memory/{project_id}/decisions"
        data = self.storage.load(key)
        
        if not data:
            return None
        
        for decision_dict in data.get("decisions", []):
            if decision_dict.get("id") == decision_id:
                return Decision.from_dict(decision_dict)
        
        return None
    
    def list_decisions(self, project_id: str, status: str = "all") -> List[Decision]:
        """Get all decisions for project"""
        
        key = f"memory/{project_id}/decisions"
        data = self.storage.load(key)
        
        if not data:
            return []
        
        decisions = []
        for decision_dict in data.get("decisions", []):
            decision = Decision.from_dict(decision_dict)
            
            if status == "all" or decision.status == status:
                decisions.append(decision)
        
        return decisions
    
    def search_decisions(
        self,
        project_id: str,
        query: str,
        tags: Optional[List[str]] = None
    ) -> List[Decision]:
        """Search decisions by query and/or tags"""
        
        all_decisions = self.list_decisions(project_id)
        results = []
        
        query_lower = query.lower()
        
        for decision in all_decisions:
            # Match by query (title or description)
            query_match = (
                query_lower in decision.title.lower() or
                query_lower in decision.description.lower()
            )
            
            # Match by tags
            tag_match = True
            if tags:
                tag_match = all(tag in decision.tags for tag in tags)
            
            if query_match and tag_match:
                results.append(decision)
        
        return results
    
    # ==================== CHANGES ====================
    
    def log_change(self, project_id: str, change: Change) -> str:
        """Log a change, return change ID"""
        
        if not change.file_path or not change.description:
            raise ValueError("Change must have file_path and description")
        
        key = f"memory/{project_id}/recent_changes"
        data = self.storage.load(key) or {"changes": []}
        
        data["changes"].append(change.to_dict())
        
        # Keep only last 1000 changes to prevent bloat
        if len(data["changes"]) > 1000:
            data["changes"] = data["changes"][-1000:]
        
        if self.storage.save(key, data):
            logger.info(f"Change logged: {change.id}")
            return change.id
        else:
            raise RuntimeError(f"Failed to log change")
    
    def get_recent_changes(
        self,
        project_id: str,
        limit: int = 20,
        architecture_impact_filter: str = "all"
    ) -> List[Change]:
        """Get recent changes"""
        
        key = f"memory/{project_id}/recent_changes"
        data = self.storage.load(key)
        
        if not data:
            return []
        
        changes = []
        for change_dict in reversed(data.get("changes", [])):
            change = Change.from_dict(change_dict)
            
            if architecture_impact_filter != "all":
                if change.architecture_impact != architecture_impact_filter:
                    continue
            
            changes.append(change)
            
            if len(changes) >= limit:
                break
        
        return changes
```

---

## 6. Tool Implementation Pattern

### tools/memory_tools.py Template
```python
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional, List
from coordmcp.memory.models import Decision
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.logger import get_logger

logger = get_logger("tools.memory")

async def save_decision_handler(
    memory_store: ProjectMemoryStore,
    project_id: str,
    title: str,
    description: str,
    context: str = "",
    rationale: str = "",
    impact: str = "",
    tags: Optional[List[str]] = None
) -> dict:
    """
    Save a major architectural decision
    
    Args:
        memory_store: Instance of ProjectMemoryStore
        project_id: Project ID
        title: Decision title
        description: Detailed description
        context: Context in which decision was made
        rationale: Why this decision was made
        impact: Impact of this decision
        tags: Optional tags for categorization
    
    Returns:
        Response dict with success status and decision_id
    """
    try:
        # Validate inputs
        if not title or not title.strip():
            return {
                "success": False,
                "error": "Title cannot be empty",
                "error_type": "ValidationError"
            }
        
        if not rationale or not rationale.strip():
            return {
                "success": False,
                "error": "Rationale cannot be empty",
                "error_type": "ValidationError"
            }
        
        # Create decision
        decision = Decision(
            title=title.strip(),
            description=description.strip(),
            context=context.strip(),
            rationale=rationale.strip(),
            impact=impact.strip(),
            tags=tags or []
        )
        
        # Save
        decision_id = memory_store.save_decision(project_id, decision)
        
        logger.info(f"Decision saved: {decision_id} in project {project_id}")
        
        return {
            "success": True,
            "decision_id": decision_id,
            "message": f"Decision '{title}' saved successfully",
            "data": {
                "decision_id": decision_id,
                "timestamp": decision.timestamp,
                "title": title
            }
        }
        
    except ValueError as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": "ValidationError"
        }
    except Exception as e:
        logger.error(f"Error saving decision: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError",
            "suggestions": [
                "Check that project_id is valid",
                "Verify all required fields are provided",
                "Check logs for detailed error information"
            ]
        }

async def get_project_decisions_handler(
    memory_store: ProjectMemoryStore,
    project_id: str,
    status: str = "all"
) -> dict:
    """Get all decisions for a project"""
    
    try:
        # Validate status
        if status not in ["all", "active", "archived", "superseded"]:
            return {
                "success": False,
                "error": f"Invalid status: {status}",
                "error_type": "ValidationError"
            }
        
        # Fetch decisions
        decisions = memory_store.list_decisions(project_id, status)
        
        return {
            "success": True,
            "count": len(decisions),
            "data": {
                "decisions": [d.to_dict() for d in decisions],
                "total": len(decisions)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting decisions: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }
```

---

## 7. Error Handling Pattern

### errors/__init__.py Template
```python
class CoordMCPError(Exception):
    """Base exception for CoordMCP"""
    pass

class ProjectNotFoundError(CoordMCPError):
    """Project doesn't exist"""
    def __init__(self, project_id: str):
        super().__init__(f"Project not found: {project_id}")
        self.project_id = project_id

class AgentNotFoundError(CoordMCPError):
    """Agent not registered"""
    def __init__(self, agent_id: str):
        super().__init__(f"Agent not found: {agent_id}")
        self.agent_id = agent_id

class FileLockError(CoordMCPError):
    """File is locked by another agent"""
    def __init__(self, file_path: str, locked_by: str):
        super().__init__(f"File locked: {file_path} (by {locked_by})")
        self.file_path = file_path
        self.locked_by = locked_by

class ContextError(CoordMCPError):
    """Context operation failed"""
    pass

class DataValidationError(CoordMCPError):
    """Data validation failed"""
    pass

class DataCorruptionError(CoordMCPError):
    """Data file is corrupted"""
    def __init__(self, file_path: str):
        super().__init__(f"Data corruption detected: {file_path}")
        self.file_path = file_path
```

---

## 8. FastMCP Tool Registration Pattern

### core/tool_manager.py Template
```python
from mcp.server import Server
from typing import Callable, Dict

class ToolManager:
    """Manages tool registration with FastMCP"""
    
    def __init__(self, server: Server, memory_store, context_manager, arch_analyzer):
        self.server = server
        self.memory_store = memory_store
        self.context_manager = context_manager
        self.arch_analyzer = arch_analyzer
    
    def register_all_tools(self) -> None:
        """Register all tools with the MCP server"""
        
        # Memory tools
        self._register_memory_tools()
        
        # Context tools
        self._register_context_tools()
        
        # Architecture tools
        self._register_architecture_tools()
        
        # Query tools
        self._register_query_tools()
    
    def _register_memory_tools(self) -> None:
        """Register memory management tools"""
        
        self.server.add_tool(
            name="save_decision",
            description="Save a major architectural or technical decision",
            input_schema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "context": {"type": "string"},
                    "rationale": {"type": "string"},
                    "impact": {"type": "string"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["project_id", "title", "rationale"]
            },
            handler=self._make_tool_handler(
                "save_decision",
                self.memory_store
            )
        )
        
        # ... more tool registrations
    
    def _make_tool_handler(self, tool_name: str, store) -> Callable:
        """Create handler function for a tool"""
        
        async def handler(**kwargs):
            # Dispatch to appropriate handler
            if tool_name == "save_decision":
                from coordmcp.tools.memory_tools import save_decision_handler
                return await save_decision_handler(store, **kwargs)
            # ... more dispatches
        
        return handler
```

---

## 9. Testing Pattern

### tests/unit/test_memory_store.py Template
```python
import pytest
import tempfile
from pathlib import Path
from coordmcp.storage.json_adapter import JSONStorageBackend
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.memory.models import Decision

@pytest.fixture
def temp_storage():
    """Create temporary storage for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        backend = JSONStorageBackend(Path(tmpdir))
        yield backend

@pytest.fixture
def memory_store(temp_storage):
    """Create memory store with temporary storage"""
    return ProjectMemoryStore(temp_storage)

class TestProjectMemoryStore:
    
    def test_save_decision(self, memory_store):
        """Test saving a decision"""
        
        decision = Decision(
            title="Use FastAPI",
            description="Selected FastAPI for API layer",
            rationale="Great performance and type safety",
            impact="All API endpoints use FastAPI"
        )
        
        decision_id = memory_store.save_decision("proj1", decision)
        
        assert decision_id is not None
        assert decision_id == decision.id
    
    def test_get_decision(self, memory_store):
        """Test retrieving a decision"""
        
        decision = Decision(
            title="Use Pydantic",
            description="For data validation",
            rationale="Built-in validation",
            impact="All models use Pydantic"
        )
        
        decision_id = memory_store.save_decision("proj1", decision)
        
        retrieved = memory_store.get_decision("proj1", decision_id)
        
        assert retrieved is not None
        assert retrieved.title == decision.title
        assert retrieved.id == decision_id
    
    def test_list_decisions(self, memory_store):
        """Test listing all decisions"""
        
        # Save multiple decisions
        for i in range(3):
            decision = Decision(
                title=f"Decision {i}",
                description=f"Description {i}",
                rationale=f"Rationale {i}",
                impact=f"Impact {i}"
            )
            memory_store.save_decision("proj1", decision)
        
        decisions = memory_store.list_decisions("proj1")
        
        assert len(decisions) == 3
    
    def test_search_decisions(self, memory_store):
        """Test searching decisions"""
        
        decision1 = Decision(
            title="Use FastAPI",
            description="For API layer",
            rationale="Performance",
            impact="All endpoints",
            tags=["backend", "framework"]
        )
        
        decision2 = Decision(
            title="Use PostgreSQL",
            description="For database",
            rationale="Reliability",
            impact="Data storage",
            tags=["backend", "database"]
        )
        
        memory_store.save_decision("proj1", decision1)
        memory_store.save_decision("proj1", decision2)
        
        # Search by query
        results = memory_store.search_decisions("proj1", "FastAPI")
        assert len(results) == 1
        assert results[0].title == "Use FastAPI"
        
        # Search by tags
        results = memory_store.search_decisions("proj1", "", ["backend"])
        assert len(results) == 2
    
    def test_log_change(self, memory_store):
        """Test logging changes"""
        
        from coordmcp.memory.models import Change
        
        change = Change(
            file_path="src/api/main.py",
            change_type="create",
            description="Initial API setup",
            agent_id="agent1"
        )
        
        change_id = memory_store.log_change("proj1", change)
        
        assert change_id is not None
        
        recent = memory_store.get_recent_changes("proj1", limit=10)
        assert len(recent) == 1
        assert recent[0].id == change_id
```

---

## 10. Integration Test Pattern

### tests/integration/test_full_workflow.py Template
```python
import pytest
import tempfile
from pathlib import Path
from coordmcp.storage.json_adapter import JSONStorageBackend
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.context.manager import ContextManager
from coordmcp.context.file_tracker import FileTracker
from coordmcp.memory.models import Decision, Change
from coordmcp.context.models import AgentProfile

@pytest.fixture
def storage_backend():
    """Create temporary storage for integration test"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield JSONStorageBackend(Path(tmpdir))

@pytest.fixture
def memory_store(storage_backend):
    return ProjectMemoryStore(storage_backend)

@pytest.fixture
def file_tracker(storage_backend):
    return FileTracker(storage_backend)

@pytest.fixture
def context_manager(storage_backend, file_tracker):
    return ContextManager(storage_backend, file_tracker)

class TestFullWorkflow:
    
    def test_complete_agent_workflow(
        self,
        memory_store,
        context_manager,
        file_tracker
    ):
        """Test complete workflow: register → start → lock → change → unlock"""
        
        # 1. Register agent
        agent = AgentProfile(
            agent_name="opencode-dev",
            agent_type="opencode",
            capabilities=["write", "refactor"]
        )
        agent_id = context_manager.register_agent(agent)
        assert agent_id is not None
        
        # 2. Start context
        context = context_manager.start_context(
            agent_id=agent_id,
            project_id="proj1",
            objective="Build authentication"
        )
        assert context is not None
        
        # 3. Lock files
        locked = file_tracker.lock_files(
            agent_id=agent_id,
            project_id="proj1",
            files=["src/auth/models.py", "src/auth/service.py"],
            reason="Implementing auth system"
        )
        assert locked is True
        
        # 4. Save decision
        decision = Decision(
            title="Use JWT for authentication",
            description="JWT tokens for stateless auth",
            rationale="Scalable and secure",
            impact="All auth endpoints use JWT"
        )
        decision_id = memory_store.save_decision("proj1", decision)
        assert decision_id is not None
        
        # 5. Log changes
        change = Change(
            file_path="src/auth/models.py",
            change_type="create",
            description="Created User model with password hashing",
            agent_id=agent_id
        )
        change_id = memory_store.log_change("proj1", change)
        assert change_id is not None
        
        # 6. Unlock files
        unlocked = file_tracker.unlock_files(
            agent_id=agent_id,
            project_id="proj1",
            files=["src/auth/models.py", "src/auth/service.py"]
        )
        assert unlocked is True
        
        # 7. Verify state
        locked_files = file_tracker.get_locked_files("proj1")
        assert len(locked_files) == 0
        
        recent_changes = memory_store.get_recent_changes("proj1")
        assert len(recent_changes) == 1
        
        decisions = memory_store.list_decisions("proj1")
        assert len(decisions) == 1
    
    def test_multi_agent_conflict_detection(
        self,
        context_manager,
        file_tracker
    ):
        """Test that system prevents multi-agent file conflicts"""
        
        # Agent 1 registers and starts
        agent1 = AgentProfile(
            agent_name="opencode-1",
            agent_type="opencode"
        )
        agent1_id = context_manager.register_agent(agent1)
        
        # Agent 1 locks file
        file_tracker.lock_files(
            agent_id=agent1_id,
            project_id="proj1",
            files=["shared.py"],
            reason="Agent 1 working"
        )
        
        # Agent 2 registers
        agent2 = AgentProfile(
            agent_name="opencode-2",
            agent_type="opencode"
        )
        agent2_id = context_manager.register_agent(agent2)
        
        # Agent 2 tries to lock same file
        with pytest.raises(FileLockError):
            file_tracker.lock_files(
                agent_id=agent2_id,
                project_id="proj1",
                files=["shared.py"],
                reason="Agent 2 working"
            )
        
        # Verify lock is held by agent 1
        lock_holder = file_tracker.get_lock_holder("proj1", "shared.py")
        assert lock_holder == agent1_id
```

---

## 11. Utility Functions Pattern

### utils/validators.py Template
```python
from typing import List
from coordmcp.errors import DataValidationError

def validate_project_id(project_id: str) -> None:
    """Validate project ID format"""
    if not project_id or not isinstance(project_id, str):
        raise DataValidationError("Project ID must be non-empty string")
    if len(project_id) < 3:
        raise DataValidationError("Project ID too short (min 3 chars)")
    if len(project_id) > 100:
        raise DataValidationError("Project ID too long (max 100 chars)")

def validate_agent_id(agent_id: str) -> None:
    """Validate agent ID (should be UUID)"""
    if not agent_id or not isinstance(agent_id, str):
        raise DataValidationError("Agent ID must be non-empty string")
    # Could add UUID validation here

def validate_file_path(file_path: str) -> None:
    """Validate file path"""
    if not file_path or not isinstance(file_path, str):
        raise DataValidationError("File path must be non-empty string")
    if file_path.startswith("/"):
        raise DataValidationError("File path must be relative (no leading /)")

def validate_non_empty_string(value: str, field_name: str, min_len: int = 1) -> None:
    """Generic string validator"""
    if not isinstance(value, str) or len(value.strip()) < min_len:
        raise DataValidationError(f"{field_name} cannot be empty")
```

---

This provides concrete examples Opencode can follow for consistent implementation!
