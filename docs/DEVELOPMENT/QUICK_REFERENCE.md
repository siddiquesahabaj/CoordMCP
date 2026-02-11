# CoordMCP - Quick Reference for Opencode

## 🚀 Quick Start Commands

```bash
# Initialize project
opencode> Create CoordMCP project with directory structure from coordmcp/

# Day 1 - Foundation
opencode> Implement config.py, logger.py, and storage abstraction layer

# Day 2 - Memory
opencode> Implement all memory models and ProjectMemoryStore with 8 tools

# Day 3 - Context
opencode> Implement ContextManager and FileTracker with 8 tools

# Day 4 - Architecture
opencode> Implement architecture analyzer and recommender with 5 tools

# Day 5 - Polish
opencode> Implement all resources, tests, documentation, and examples
```

---

## 📋 Module Dependencies

```
FastMCP Server
    ├── Tool Manager
    │   └── All 25 Tools
    ├── Resource Manager
    │   └── All Resources
    └── Core Server Setup

Tools (25 total)
    ├── Memory Tools (8)
    │   └── ProjectMemoryStore
    │       └── JSONStorageBackend
    ├── Context Tools (8)
    │   ├── ContextManager
    │   ├── FileTracker
    │   └── ChangeLog
    ├── Architecture Tools (5)
    │   ├── ArchitectureAnalyzer
    │   └── ArchitectureRecommender
    └── Context Tools (13)
        └── All of the above

Resources (6 types)
    ├── Project Resources
    ├── Agent Resources
    └── Architecture Resources
```

---

## 🔧 Class Hierarchy Quick View

```
StorageBackend (ABC)
└── JSONStorageBackend (implements all methods)

ProjectMemoryStore
├── save_decision()
├── get_decision()
├── list_decisions()
├── search_decisions()
├── update_tech_stack()
├── get_tech_stack()
├── log_change()
├── get_recent_changes()
├── update_file_metadata()
└── get_file_metadata()

ContextManager
├── register_agent()
├── start_context()
├── get_current_context()
├── switch_context()
└── get_context_history()

FileTracker
├── lock_files()
├── unlock_files()
├── get_locked_files()
├── is_locked()
└── cleanup_stale_locks()

ArchitectureAnalyzer
├── analyze_project()
├── check_modularity()
└── assess_scalability()

ArchitectureRecommender
├── recommend_structure()
└── get_pattern_for_feature()

CodeStructureValidator
├── validate()
├── check_naming_conventions()
├── check_layer_separation()
├── check_circular_dependencies()
└── check_modularity()
```

---

## 📦 Data Models (Pydantic/Dataclass)

```python
Decision
├── id: str
├── timestamp: datetime
├── title: str
├── description: str
├── context: str
├── rationale: str
├── impact: str
├── status: "active|archived|superseded"
├── related_files: List[str]
├── author_agent: str
└── tags: List[str]

TechStackEntry
├── category: str
├── technology: str
├── version: str
├── rationale: str
└── decision_ref: Optional[str]

ArchitectureModule
├── name: str
├── purpose: str
├── files: List[str]
├── dependencies: List[str]
└── responsibilities: List[str]

FileMetadata
├── path: str
├── type: "source|test|config|doc"
├── last_modified: datetime
├── last_modified_by: str
├── module: str
├── purpose: str
├── dependencies: List[str]
├── dependents: List[str]
├── lines_of_code: int
└── complexity: "low|medium|high"

AgentProfile
├── agent_id: str
├── agent_name: str
├── agent_type: "opencode|cursor|claude_code|custom"
├── capabilities: List[str]
└── status: "active|inactive"

Context
├── agent_id: str
├── project_id: str
├── objective: str
├── task_description: str
├── priority: "critical|high|medium|low"
├── started_at: datetime
└── current_file: str

LockInfo
├── file_path: str
├── locked_at: datetime
├── locked_by: str (agent_id)
├── reason: str
└── expected_unlock_time: datetime
```

---

## 🛠️ Memory Tools (8)

```python
1. save_decision(project_id, title, description, context, rationale, impact?, tags?)
   → {success, decision_id}

2. get_project_decisions(project_id, status?, tags?)
   → {success, decisions: List[Decision]}

3. update_tech_stack(project_id, category, technology, version, rationale?, decision_ref?)
   → {success}

4. get_tech_stack(project_id, category?)
   → {success, tech_stack: Dict}

5. log_change(project_id, file_path, change_type, description, code_summary?, architecture_impact?, related_decision?)
   → {success, change_id}

6. get_recent_changes(project_id, limit?, architecture_impact_filter?)
   → {success, changes: List[Change]}

7. update_file_metadata(project_id, file_path, type?, purpose?, module?, complexity?)
   → {success}

8. search_decisions(project_id, query, tags?)
   → {success, results: List[Decision]}

9. get_project_info(project_id)
   → {success, project: ProjectInfo}

10. get_file_dependencies(project_id, file_path, direction?)
    → {success, dependencies: List[DependencyInfo]}

11. get_module_info(project_id, module_name)
    → {success, module: ArchitectureModule}
```

---

## 🔄 Context Tools (13)

```python
1. register_agent(agent_name, agent_type, capabilities?)
   → {success, agent_id}

2. start_context(agent_id, project_id, objective, task_description?, priority?)
   → {success, context: Context}

3. lock_files(agent_id, project_id, files, reason, expected_duration_minutes?)
   → {success, locked_files: List}

4. unlock_files(agent_id, project_id, files)
   → {success, unlocked_count: int}

5. get_locked_files(project_id)
   → {success, locked_files: Dict[file → LockInfo]}

6. switch_context(agent_id, to_project_id, to_objective, task_description?, priority?)
   → {success, new_context: Context}

7. get_agent_context(agent_id)
   → {success, context: Context}

8. get_agents_list()
   → {success, agents: List[AgentProfile]}

9. get_agent_profile(agent_id)
   → {success, agent: AgentProfile}

10. end_context(agent_id)
    → {success}

11. get_context_history(agent_id, limit?)
    → {success, history: List[ContextEntry]}

12. get_session_log(agent_id, limit?)
    → {success, log: List[SessionLogEntry]}

13. get_agents_in_project(project_id)
    → {success, agents: List[AgentProfile]}
```

---

## 🏗️ Architecture Tools (5)

```python
1. analyze_architecture(project_id)
   → {success, analysis: ArchitectureAnalysis}

2. get_architecture_recommendation(
     project_id, 
     feature_description, 
     context?, 
     constraints?, 
     implementation_style?)
   → {success, recommendation: Recommendation}

3. validate_code_structure(project_id, file_path, code_structure, strict_mode?)
   → {success, issues: List[ValidationIssue]}

4. update_architecture(project_id, recommendation_id, implementation_summary?, actual_files_created?, actual_files_modified?)
   → {success}

5. get_design_patterns()
   → {success, patterns: Dict[pattern_name → DesignPattern]}
```

---

## 📊 Tool Summary

**Total: 29 Tools**
- Memory Tools: 11
- Context Tools: 13
- Architecture Tools: 5

---

## 📚 Resources (6 Types)

```
project://{project_id}
├── Returns: Full project overview

project://{project_id}/decisions
├── Returns: All decisions for project

project://{project_id}/tech-stack
├── Returns: Technology stack

project://{project_id}/architecture
├── Returns: Architecture definition

project://{project_id}/modules/{module_name}
├── Returns: Specific module details

project://{project_id}/recent-changes
├── Returns: Recent changes

agent://{agent_id}
├── Returns: Agent profile

agent://{agent_id}/context
├── Returns: Current context

agent://{agent_id}/locked-files
├── Returns: Files locked by agent

agent://{agent_id}/session-log
├── Returns: Activity log

design-patterns://list
├── Returns: All patterns

design-patterns://{pattern_name}
├── Returns: Specific pattern details
```

---

## 📂 File Layout Checklist

```
coordmcp/
├── src/coordmcp/
│   ├── __init__.py ✓
│   ├── main.py (FastMCP entry point) ✓
│   ├── config.py ✓
│   ├── logger.py ✓
│   ├── core/
│   │   ├── __init__.py ✓
│   │   ├── server.py ✓
│   │   ├── resource_manager.py ✓
│   │   └── tool_manager.py ✓
│   ├── memory/
│   │   ├── __init__.py ✓
│   │   ├── base.py ✓
│   │   ├── json_store.py ✓
│   │   ├── models.py ✓
│   │   └── utils.py ✓
│   ├── context/
│   │   ├── __init__.py ✓
│   │   ├── manager.py ✓
│   │   ├── state.py ✓
│   │   ├── file_tracker.py ✓
│   │   └── change_log.py ✓
│   ├── architecture/
│   │   ├── __init__.py ✓
│   │   ├── analyzer.py ✓
│   │   ├── recommender.py ✓
│   │   ├── validators.py ✓
│   │   └── patterns.py ✓
  │   ├── tools/
│   │   ├── __init__.py ✓
│   │   ├── memory_tools.py (11 tools) ✓
│   │   ├── context_tools.py (13 tools) ✓
│   │   └── architecture_tools.py (5 tools) ✓
│   ├── resources/
│   │   ├── __init__.py ✓
│   │   ├── project_resources.py ✓
│   │   ├── agent_resources.py ✓
│   │   └── architecture_resources.py ✓
│   ├── storage/
│   │   ├── __init__.py ✓
│   │   ├── base.py ✓
│   │   ├── json_adapter.py ✓
│   │   └── utils.py ✓
│   └── errors/
│       └── __init__.py (7 exception classes) ✓
├── data/ (auto-created at runtime) ✓
├── tests/
│   ├── unit/
│   │   ├── test_memory_store.py ✓
│   │   ├── test_context_manager.py ✓
│   │   ├── test_file_tracker.py ✓
│   │   └── test_architecture.py ✓
│   └── integration/
│       ├── test_full_workflow.py ✓
│       └── test_tools_integration.py ✓
├── docs/
│   ├── README.md ✓
│   ├── ARCHITECTURE.md ✓
│   ├── API_REFERENCE.md ✓
│   ├── SETUP.md ✓
│   ├── USAGE_EXAMPLES.md ✓
│   └── EXTENDING.md ✓
├── examples/
│   ├── basic_project_setup.py ✓
│   ├── multi_agent_workflow.py ✓
│   └── context_switching.py ✓
├── pyproject.toml ✓
├── requirements.txt ✓
└── .env.example ✓
```

---

## ⏱️ Time Allocation Guide

### Day 1 (6 hours) - Foundation
- Setup & config: 1h
- Logger: 30m
- Storage base: 1h
- JSON adapter: 1h
- Data dir init: 30m
- Testing/validation: 1h

### Day 2 (6 hours) - Memory
- Models: 1h
- ProjectMemoryStore: 2h
- Memory tools: 2h
- Testing: 1h

### Day 3 (6 hours) - Context
- Context models: 1h
- ContextManager: 1.5h
- FileTracker: 1.5h
- Context tools: 1h
- Testing: 1h

### Day 4 (6 hours) - Architecture
- Analyzer: 1.5h
- Recommender: 1.5h
- Validators: 1h
- Architecture tools: 1h
- Testing: 1h

### Day 5 (6 hours) - Polish
- Resources: 1.5h
- Full integration tests: 1.5h
- Documentation: 2h
- Examples & demo: 1h

---

## 🧪 Minimal Test Cases Per Module

```python
# Memory
- Create decision, retrieve decision, list decisions
- Update tech stack, get tech stack
- Log change, get recent changes
- Search decisions by query

# Context
- Register agent, get agent
- Start context, switch context
- Lock files, unlock files, get locked
- Get context history

# Architecture
- Analyze project architecture
- Get recommendation for new feature
- Validate code structure
- Get design patterns

# Integration
- Full workflow: register → start → lock → change → unlock
- Multi-agent conflict detection
- Architecture recommendation implementation
```

---

## 🎯 Success Criteria (Day 5)

✅ All 29 tools fully implemented and functional
✅ All 6 resource types working
✅ JSON storage working reliably
✅ No data corruption on failures
✅ Comprehensive error handling
✅ Unit tests pass
✅ Integration tests pass
✅ Examples run without errors
✅ Documentation complete
✅ README with quick start
✅ Can be integrated with Opencode immediately

---

## 🔧 Debugging Tips

### If tools don't work:
1. Check tool registration in tool_manager.py
2. Verify schema matches tool implementation
3. Check error handling in tool handler
4. Look at logs in `~/.coordmcp/logs/`

### If data isn't persisting:
1. Check JSONStorageBackend paths
2. Verify data directory exists
3. Check file permissions
4. Ensure JSON is valid (use `json.tool`)

### If agents can't find context:
1. Verify agent registered first
2. Check agent_id is correct UUID
3. Verify context was started
4. Check session_id matches

### If file locks fail:
1. Check if file already locked
2. Verify lock holder exists
3. Check lock timeout (24h default)
4. Use cleanup_stale_locks() if needed

---

## 📝 Important Notes for Opencode

1. **Use UUID for IDs**: `from uuid import uuid4`; `id = str(uuid4())`
2. **Use ISO timestamps**: `datetime.now(timezone.utc).isoformat()`
3. **Atomic writes**: Always write to temp file first, then rename
4. **Validate early**: Check all inputs at function start
5. **Log decisions**: Every create/update/delete should be logged
6. **Type hints**: Use them everywhere for IDE support
7. **Error handling**: Catch specific exceptions, provide suggestions
8. **No LLM calls**: All recommendations are rule-based logic

---

This quick reference should help Opencode navigate the codebase efficiently!
