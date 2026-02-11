# CoordMCP - Detailed API Specification & Implementation Guidelines

## 1. Core Modules Implementation Details

### 1.1 `config.py` - Configuration Management

```python
# Structure:
- class Config:
  - data_dir: str = Path to data storage
  - log_level: str = "INFO"
  - max_file_locks_per_agent: int = 100
  - lock_timeout_hours: int = 24
  - enable_compression: bool = False
  - version: str = "0.1.0"

- load_config() -> Config
- get_config() -> Config (cached)
- validate_config(config: Config) -> bool
```

### 1.2 `logger.py` - Logging Setup

```python
# Structure:
- class CoordLogger:
  - setup_logging(log_level: str, log_file: Optional[str]) -> None
  - get_logger(name: str) -> logging.Logger
  
- Logs to: {data_dir}/logs/coordmcp.log
- Rotation: 10MB per file, keep 5 files
- Format: %(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### 1.3 Storage Architecture

```python
# storage/base.py - Abstract Interface
class StorageBackend(ABC):
    @abstractmethod
    def save(self, key: str, data: Dict) -> bool
    
    @abstractmethod
    def load(self, key: str) -> Optional[Dict]
    
    @abstractmethod
    def delete(self, key: str) -> bool
    
    @abstractmethod
    def exists(self, key: str) -> bool
    
    @abstractmethod
    def list_keys(self, prefix: str) -> List[str]
    
    @abstractmethod
    def batch_save(self, items: Dict[str, Dict]) -> bool

# storage/json_adapter.py - JSON Implementation
class JSONStorageBackend(StorageBackend):
    def __init__(self, base_dir: Path)
    
    # Each key maps to a JSON file
    # Nested keys use directory structure
    # Example: "projects/proj1/decisions" → projects/proj1/decisions.json
    
    def save() -> Implements atomic writes with temp files
    def load() -> Handles missing files gracefully
    def list_keys() -> Traverses directory structure
```

### 1.4 Memory System Architecture

```python
# memory/models.py - Data Models
@dataclass
class Decision:
    id: str
    timestamp: datetime
    title: str
    description: str
    context: str
    rationale: str
    impact: str
    status: Literal["active", "archived", "superseded"]
    related_files: List[str]
    author_agent: str
    tags: List[str]

@dataclass
class TechStackEntry:
    category: str
    technology: str
    version: str
    rationale: str
    decision_ref: Optional[str]

@dataclass
class ArchitectureModule:
    name: str
    purpose: str
    files: List[str]
    dependencies: List[str]
    responsibilities: List[str]

@dataclass
class ProjectMemory:
    project_id: str
    project_name: str
    created_at: datetime
    decisions: Dict[str, Decision]
    tech_stack: Dict[str, TechStackEntry]
    architecture: Dict[str, ArchitectureModule]
    recent_changes: List[Change]
    file_metadata: Dict[str, FileMetadata]

# memory/json_store.py - JSON Storage Implementation
class ProjectMemoryStore:
    def __init__(self, storage_backend: StorageBackend)
    
    # Core operations
    def save_decision(project_id: str, decision: Decision) -> str
    def get_decision(project_id: str, decision_id: str) -> Decision
    def list_decisions(project_id: str, status: str = "all") -> List[Decision]
    def search_decisions(project_id: str, query: str, tags: List[str]) -> List[Decision]
    
    def update_tech_stack(project_id: str, entry: TechStackEntry) -> None
    def get_tech_stack(project_id: str) -> Dict[str, TechStackEntry]
    
    def log_change(project_id: str, change: Change) -> str
    def get_recent_changes(project_id: str, limit: int = 20) -> List[Change]
    
    def update_file_metadata(project_id: str, file_path: str, metadata: FileMetadata) -> None
    def get_file_metadata(project_id: str, file_path: str) -> FileMetadata
    
    def update_architecture(project_id: str, arch: Dict) -> None
    def get_architecture(project_id: str) -> Dict
```

### 1.5 Context Management Architecture

```python
# context/manager.py - Context Manager
class ContextManager:
    def __init__(self, storage_backend: StorageBackend, file_tracker: FileTracker)
    
    def register_agent(agent: AgentProfile) -> str
    def get_agent(agent_id: str) -> AgentProfile
    
    def start_context(agent_id: str, project_id: str, objective: str) -> Context
    def get_current_context(agent_id: str) -> Context
    def end_context(agent_id: str) -> None
    
    def switch_context(agent_id: str, to_project: str, to_objective: str) -> Context
    def get_context_history(agent_id: str, limit: int = 10) -> List[Context]

# context/file_tracker.py - File Locking System
class FileTracker:
    def __init__(self, storage_backend: StorageBackend)
    
    def lock_files(agent_id: str, project_id: str, files: List[str], reason: str) -> bool
    def unlock_files(agent_id: str, project_id: str, files: List[str]) -> bool
    def get_locked_files(project_id: str) -> Dict[str, LockInfo]
    def is_locked(project_id: str, file_path: str) -> bool
    def get_lock_holder(project_id: str, file_path: str) -> Optional[str]
    
    # Auto-unlock stale locks (> 24 hours)
    def cleanup_stale_locks() -> int

# context/change_log.py - Change Tracking
class ChangeLog:
    def __init__(self, storage_backend: StorageBackend)
    
    def add_entry(project_id: str, agent_id: str, file: str, op: str) -> None
    def get_recent(project_id: str, limit: int = 20) -> List[ContextEntry]
```

### 1.6 Architecture System Architecture

```python
# architecture/analyzer.py - Architecture Analysis
class ArchitectureAnalyzer:
    def __init__(self, memory_store: ProjectMemoryStore)
    
    def analyze_project(project_id: str) -> ArchitectureAnalysis
    # Returns: current modules, patterns, dependencies, complexity assessment
    
    def check_modularity(project_id: str) -> ModularityReport
    # Analyzes: coupling, cohesion, circular dependencies
    
    def assess_scalability(project_id: str) -> ScalabilityReport
    # Analyzes: growth paths, bottlenecks, expansion points

# architecture/recommender.py - Recommendation Engine (NO LLM CALLS)
class ArchitectureRecommender:
    def __init__(self, memory_store: ProjectMemoryStore, analyzer: ArchitectureAnalyzer)
    
    def recommend_structure(
        project_id: str,
        feature_description: str,
        context: str,
        constraints: List[str]
    ) -> Recommendation
    
    # Logic:
    # 1. Analyze current architecture
    # 2. Match against design patterns
    # 3. Apply SOLID principles
    # 4. Check existing modules for extensions
    # 5. Generate file/code structure
    # 6. Suggest implementation steps
    
    def get_pattern_for_feature(feature_type: str) -> DesignPattern
    # Patterns: CRUD (separate model/controller/service)
    #          Validator (dedicated validation layer)
    #          Query (separate query classes)
    #          Factory (creation logic)
    #          etc.

# architecture/validators.py - Structure Validation
class CodeStructureValidator:
    def __init__(self, memory_store: ProjectMemoryStore)
    
    def validate(project_id: str, structure: Dict, strict: bool = False) -> ValidationReport
    
    def check_naming_conventions(structure: Dict) -> List[Issue]
    def check_layer_separation(project_id: str, structure: Dict) -> List[Issue]
    def check_circular_dependencies(structure: Dict) -> List[Issue]
    def check_modularity(structure: Dict) -> List[Issue]

# architecture/patterns.py - Design Patterns Reference
DESIGN_PATTERNS = {
    "CRUD": {
        "description": "Basic create, read, update, delete",
        "structure": {...},
        "best_for": ["simple data models"],
        "modules": ["models", "repositories", "services"]
    },
    "MVC": {
        "description": "Model-View-Controller",
        "structure": {...},
        ...
    },
    "Repository": {
        "description": "Data access abstraction",
        "structure": {...},
        ...
    },
    "Service": {
        "description": "Business logic layer",
        "structure": {...},
        ...
    },
    "Factory": {
        "description": "Object creation pattern",
        "structure": {...},
        ...
    },
    "Observer": {
        "description": "Event-driven architecture",
        "structure": {...},
        ...
    },
    "Adapter": {
        "description": "Interface adaptation",
        "structure": {...},
        ...
    }
}
```

## 2. FastMCP Tool Implementation Details

### 2.1 Tool Registration Pattern

```python
# In tools/__init__.py
def register_tools(server):
    # Memory tools
    server.add_tool("save_decision", save_decision_handler, SAVE_DECISION_SCHEMA)
    server.add_tool("get_project_decisions", get_decisions_handler, GET_DECISIONS_SCHEMA)
    # ... more tools
    
    return server

# Each tool file (e.g., memory_tools.py)
async def save_decision_handler(project_id: str, title: str, ...) -> Dict:
    """
    1. Validate inputs
    2. Create Decision object with UUID
    3. Add timestamp
    4. Save via memory_store
    5. Return success + decision_id
    """
    try:
        decision = Decision(
            id=str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            title=title,
            # ... other fields
        )
        decision_id = memory_store.save_decision(project_id, decision)
        logger.info(f"Decision saved: {decision_id}")
        return {
            "success": True,
            "decision_id": decision_id,
            "message": f"Decision '{title}' saved successfully"
        }
    except ProjectNotFoundError as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": "ProjectNotFound"
        }
    except Exception as e:
        logger.error(f"Error saving decision: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "InternalError"
        }
```

### 2.2 Tool Categories & Count

**Memory Tools (8 tools)**
1. save_decision
2. get_project_decisions
3. update_tech_stack
4. get_tech_stack
5. log_change
6. get_recent_changes
7. update_file_metadata
8. search_decisions

**Context Tools (8 tools)**
1. register_agent
2. start_context
3. lock_files
4. unlock_files
5. get_locked_files
6. switch_context
7. get_agent_context
8. get_agents_list

**Architecture Tools (5 tools)**
1. analyze_architecture
2. get_architecture_recommendation
3. validate_code_structure
4. update_architecture
5. get_design_patterns

**Actual Tool Count:**
- Memory Tools: 11 tools
- Context Tools: 13 tools
- Architecture Tools: 5 tools
- **Total: 29 tools**

## 3. FastMCP Resource Implementation Details

### 3.1 Resource URI Patterns

```
# Project Resources
project://{project_id}
project://{project_id}/decisions
project://{project_id}/decisions/{decision_id}
project://{project_id}/tech-stack
project://{project_id}/architecture
project://{project_id}/modules/{module_name}
project://{project_id}/recent-changes

# Agent Resources
agent://{agent_id}
agent://{agent_id}/context
agent://{agent_id}/locked-files
agent://{agent_id}/session-log

# Architecture Resources
design-patterns://list
design-patterns://{pattern_name}
```

### 3.2 Resource Implementation Pattern

```python
# In resources/project_resources.py
def register_project_resources(server):
    server.add_resource("project", handle_project_resource)
    server.add_resource("design-patterns", handle_patterns_resource)

async def handle_project_resource(uri: str) -> str:
    """
    Parse URI: project://{project_id}/{resource_type}
    Return formatted content based on resource type
    """
    parts = uri.split("://")[1].split("/")
    project_id = parts[0]
    resource_type = parts[1] if len(parts) > 1 else "overview"
    
    if resource_type == "overview":
        data = memory_store.get_project_overview(project_id)
    elif resource_type == "decisions":
        data = memory_store.list_decisions(project_id)
    # ... more types
    
    return format_as_markdown(data)
```

## 4. Data File Structure Examples

### 4.1 File Organization

```
data/
├── projects.json
│   └── {
│       "projects": [
│         {"id": "proj1", "name": "MyProject", "created": "...", "last_updated": "..."}
│       ]
│     }
│
├── memory/
│   └── proj1/
│       ├── decisions.json       # All decisions for project
│       ├── tech_stack.json      # Tech stack config
│       ├── architecture.json    # Architecture definition
│       ├── recent_changes.json  # Change log
│       └── file_metadata.json   # File metadata
│
├── agents/
│   └── agent1/
│       ├── profile.json         # Agent info
│       ├── context.json         # Current context
│       ├── locked_files.json    # Files locked by agent
│       └── session_log.json     # Activity log
│
├── recommendations/
│   └── rec1/
│       └── recommendation.json  # Full recommendation
│
└── global/
    ├── agent_registry.json      # All agents
    └── project_registry.json    # All projects
```

### 4.2 Example JSON Files

```json
// memory/proj1/decisions.json
{
  "decisions": [
    {
      "id": "dec-001",
      "timestamp": "2024-02-09T10:30:00Z",
      "title": "Use FastAPI for API layer",
      "description": "We decided to use FastAPI...",
      "context": "Building REST API",
      "rationale": "Performance, type safety, auto-docs",
      "impact": "All API endpoints use FastAPI",
      "status": "active",
      "related_files": ["src/api/main.py"],
      "author_agent": "opencode-001",
      "tags": ["backend", "framework"]
    }
  ]
}

// memory/proj1/tech_stack.json
{
  "backend": {
    "language": {
      "technology": "python",
      "version": "3.11",
      "rationale": "Rapid development, type safety"
    },
    "framework": {
      "technology": "fastapi",
      "version": "0.100.0",
      "rationale": "Built-in validation, async support"
    }
  },
  "frontend": {...}
}

// agents/agent1/context.json
{
  "agent_id": "agent-001",
  "agent_name": "opencode-dev",
  "session_id": "sess-001",
  "current_context": {
    "project_id": "proj1",
    "current_objective": "Implement user authentication",
    "current_file": "src/auth/models.py",
    "task_description": "Create User model with password hashing",
    "priority": "high",
    "started_at": "2024-02-09T10:00:00Z"
  },
  "locked_files": [
    {
      "file_path": "src/auth/models.py",
      "locked_at": "2024-02-09T10:00:00Z",
      "locked_by": "agent-001",
      "reason": "Adding password hashing implementation"
    }
  ]
}
```

## 5. Error Handling Strategy

### 5.1 Custom Exceptions

```python
# errors/__init__.py
class CoordMCPError(Exception):
    """Base exception"""
    pass

class ProjectNotFoundError(CoordMCPError):
    """Project doesn't exist"""
    pass

class AgentNotFoundError(CoordMCPError):
    """Agent not registered"""
    pass

class FileLockError(CoordMCPError):
    """File is locked by another agent"""
    pass

class ContextError(CoordMCPError):
    """Context operation failed"""
    pass

class DataValidationError(CoordMCPError):
    """Data validation failed"""
    pass

class DataCorruptionError(CoordMCPError):
    """Data file is corrupted"""
    pass
```

### 5.2 Error Response Format

```python
# All tool handlers return:
{
    "success": True|False,
    "data": {...},           # Only if success
    "error": "error message", # Only if fail
    "error_type": "ErrorType",
    "error_code": "ERR_001",
    "suggestions": ["suggestion1", "suggestion2"]  # How to fix
}
```

## 6. Implementation Order for Opencode

**Recommended sequence for Opencode to follow:**

```
1. Create directory structure & __init__.py files
2. Implement config.py & logger.py
3. Implement storage/base.py & storage/json_adapter.py
4. Implement memory/models.py
5. Implement memory/json_store.py (ProjectMemoryStore)
6. Create memory_tools.py with all 11 memory tools
7. Register tools in core/tool_manager.py
8. Test memory system thoroughly
9. Implement context/manager.py & context/file_tracker.py
10. Create context_tools.py with all 13 context tools
11. Implement architecture/analyzer.py & recommender.py
12. Create architecture_tools.py with 5 architecture tools
13. Implement all resources
14. Create test suite
15. Write documentation & examples
```

## 7. Key Implementation Tips for Opencode

### Tip 1: Use Dependency Injection
```python
class ProjectMemoryStore:
    def __init__(self, storage_backend: StorageBackend):
        self.backend = storage_backend
        # This makes testing easy
```

### Tip 2: Atomic Operations
```python
# For JSON writes, use temp file then rename
# Prevents corruption if write fails
def save(self, key: str, data: Dict):
    temp_path = self.base_dir / f"{key}.tmp"
    with open(temp_path, 'w') as f:
        json.dump(data, f)
    (self.base_dir / f"{key}.json").replace(temp_path)
```

### Tip 3: Validation First
```python
# Always validate before processing
def save_decision(self, project_id: str, decision: Decision):
    if not self.project_exists(project_id):
        raise ProjectNotFoundError(f"Project {project_id} not found")
    # Now proceed with save
```

### Tip 4: Logging Everywhere
```python
# Log at decision points
logger.info(f"Decision saved: {decision_id} in project {project_id}")
logger.debug(f"Decision details: {decision}")
logger.warning(f"Overwriting existing decision: {existing_id}")
```

### Tip 5: Type Hints
```python
# Use type hints for clarity and IDE support
def lock_files(
    self,
    agent_id: str,
    project_id: str,
    files: List[str],
    reason: str
) -> bool:
    # IDE will autocomplete, type checking catches errors
```

## 8. Testing Strategy Details

### Unit Test Structure
```python
# tests/unit/test_memory_store.py
class TestProjectMemoryStore:
    @pytest.fixture
    def memory_store(self):
        # Create temp storage for test
        return ProjectMemoryStore(JSONStorageBackend(temp_dir))
    
    def test_save_decision(self, memory_store):
        # Test single decision save
        
    def test_save_multiple_decisions(self, memory_store):
        # Test multiple saves
        
    def test_retrieve_decision(self, memory_store):
        # Test retrieval
    
    def test_decision_not_found(self, memory_store):
        # Test error handling
```

### Integration Test Structure
```python
# tests/integration/test_full_workflow.py
class TestFullWorkflow:
    def test_agent_workflow(self):
        # 1. Register agent
        # 2. Create project
        # 3. Start context
        # 4. Lock files
        # 5. Log change
        # 6. Get architecture recommendation
        # 7. Unlock files
        # Verify each step
```

---

## 9. Performance Considerations

### For 5-Day Timeline
- JSON files should be reasonable size (< 10MB)
- In-memory caching of project metadata
- Lazy loading for large change logs
- Simple direct file I/O (no optimization needed yet)

### For Production (Future)
- Implement LRU cache
- Use pagination for large datasets
- Consider batch operations
- Profile and optimize hot paths

## 10. Configuration Defaults

```python
# config.py defaults
DATA_DIR = Path.home() / ".coordmcp" / "data"
LOG_LEVEL = "INFO"
MAX_FILE_LOCKS_PER_AGENT = 100
LOCK_TIMEOUT_HOURS = 24
AUTO_CLEANUP_STALE_LOCKS = True
ENABLE_COMPRESSION = False  # For future use
VERSION = "0.1.0"
```

This completes the detailed implementation specification. Opencode can use this as a step-by-step guide to implement each module.
