# CoordMCP - Visual Architecture & System Flows

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL AGENTS                                  │
│  (Opencode, Cursor, Claude Code, Custom Agents)                         │
└────────────────────┬────────────────────────────────────────────────────┘
                     │
                     │ FastMCP Protocol
                     │
┌────────────────────▼────────────────────────────────────────────────────┐
│                      FastMCP SERVER (main.py)                            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐                    │
│  │   TOOL MANAGER       │  │ RESOURCE MANAGER     │                    │
│  ├──────────────────────┤  ├──────────────────────┤                    │
│  │ 25 Tools:           │  │ 6 Resource Types:    │                    │
│  │ - Memory (8)        │  │ - Project (5)        │                    │
│  │ - Context (8)       │  │ - Agent (3)          │                    │
│  │ - Architecture (5)  │  │ - Architecture (2)   │                    │
│  │ - Query (4)         │  │ - Patterns (2)       │                    │
│  └──────────────────────┘  └──────────────────────┘                    │
│                                                                          │
└──────────────────────┬────────────────────┬──────────────────────────────┘
                       │                    │
        ┌──────────────▼──────┐   ┌─────────▼─────────┐
        │  CORE SERVICES      │   │  MANAGERS         │
        ├─────────────────────┤   ├───────────────────┤
        │ - Config            │   │ ProjectMemory     │
        │ - Logger            │   │ ContextManager    │
        │ - Error Handler     │   │ FileTracker       │
        └──────────────────────┘   └─────────┬─────────┘
                                             │
        ┌────────────────────────────────────▼──────────────────────┐
        │           BUSINESS LOGIC LAYER                            │
        ├──────────────────────────────────────────────────────────┤
        │                                                          │
        │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
        │  │   Memory     │ │   Context    │ │ Architecture │    │
        │  │   System     │ │   System     │ │   System     │    │
        │  ├──────────────┤ ├──────────────┤ ├──────────────┤    │
        │  │ - Decisions  │ │ - Agents     │ │ - Analyzer   │    │
        │  │ - Tech Stack │ │ - Contexts   │ │ - Recommender│   │
        │  │ - Changes    │ │ - File Locks │ │ - Validators │    │
        │  │ - Files      │ │ - Sessions   │ │ - Patterns   │    │
        │  └──────────────┘ └──────────────┘ └──────────────┘    │
        │                                                          │
        └──────────────────────────────┬──────────────────────────┘
                                       │
        ┌──────────────────────────────▼──────────────────────────┐
        │        STORAGE ABSTRACTION LAYER                        │
        ├──────────────────────────────────────────────────────────┤
        │                                                          │
        │     interface StorageBackend:                           │
        │         save(key, data)                                 │
        │         load(key)                                       │
        │         delete(key)                                     │
        │         exists(key)                                     │
        │         list_keys(prefix)                               │
        │         batch_save(items)                               │
        │                                                          │
        └──────────────────┬───────────────────────────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │   JSONStorageBackend (Current)      │
        ├────────────────────────────────────┤
        │ Implements all abstract methods     │
        │ with JSON file I/O                  │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │   DATA STORAGE (~/.coordmcp/data)   │
        ├────────────────────────────────────┤
        │                                    │
        │  memory/                           │
        │  ├── proj1/                        │
        │  │   ├── decisions.json            │
        │  │   ├── tech_stack.json           │
        │  │   ├── architecture.json         │
        │  │   ├── recent_changes.json       │
        │  │   └── file_metadata.json        │
        │  │                                 │
        │  agents/                           │
        │  ├── agent1/                       │
        │  │   ├── profile.json              │
        │  │   ├── context.json              │
        │  │   ├── locked_files.json         │
        │  │   └── session_log.json          │
        │  │                                 │
        │  recommendations/                  │
        │  ├── rec1/                         │
        │  │   └── recommendation.json       │
        │  │                                 │
        │  global/                           │
        │  ├── agent_registry.json           │
        │  └── project_registry.json         │
        │                                    │
        └────────────────────────────────────┘
```

---

## Data Flow Diagrams

### Flow 1: Save Decision (Memory System)

```
Agent                FastMCP              Tool Handler         Store         JSON File
  │                   │                      │                  │              │
  ├─save_decision────>│                      │                  │              │
  │                   │─route to handler────>│                  │              │
  │                   │                      ├─validate input    │              │
  │                   │                      ├─create Decision   │              │
  │                   │                      │  with UUID        │              │
  │                   │                      ├─save_decision────>│              │
  │                   │                      │                  ├─temp file───>│
  │                   │                      │                  ├─atomicwrite  │
  │                   │                      │                  │<─success     │
  │                   │<──────response──────<├─return {success} │              │
  │<───response───────│                      │                  │              │
```

### Flow 2: Lock Files (Context System)

```
Agent1              Agent2           FileTracker        Locked Files      Agent Registry
  │                  │                   │                   │                │
  ├─lock_files──────>│ (via MCP)        │                   │                │
  │                  │                   ├─check if free      │                │
  │                  │                   ├─read lock file────>│                │
  │                  │                   │                   ├─no conflicts   │
  │                  │                   │<─return status     │                │
  │                  │                   ├─add lock entry     │                │
  │                  │                   ├─write lock────────>│                │
  │                  │                   │                   │                │
  │<──success────────┤                   │                   │                │
  │ locked = true    │                   │                   │                │
  │                  │ ├─lock_files──────>│                  │                │
  │                  │ (same files)       ├─check if free     │                │
  │                  │                   ├─read lock file───>│                │
  │                  │                   │                   │<─locked by A1   │
  │                  │                   ├─file in use!      │                │
  │                  │<──error──────────<├─return error      │                │
  │                  │ locked = false     │                   │                │
```

### Flow 3: Architecture Recommendation (No LLM)

```
Agent           Tool Handler        Analyzer          Recommender        Patterns
  │                  │                  │                  │                │
  ├─get_arch_rec────>│                  │                  │                │
  │ (feature desc)   │                  │                  │                │
  │                  ├─analyze_project─>│                  │                │
  │                  │                  ├─read memory      │                │
  │                  │                  ├─current modules  │                │
  │                  │<─analysis────────┤                  │                │
  │                  │                  │                  │                │
  │                  ├─match_pattern────────────────────>│                │
  │                  │ (feature type)                      ├─lookup pattern│
  │                  │                  │<─pattern config──┤                │
  │                  │                  │                  │                │
  │                  ├─recommend────────────────────────>│                │
  │                  │ (apply SOLID)    │                  ├─file structure│
  │                  │                  │                  ├─code structure│
  │                  │                  │                  ├─impl steps    │
  │                  │<─recommendation──<─────────────────┤                │
  │<──full_rec───────┤                  │                  │                │
  │ (ready to code)  │                  │                  │                │
```

### Flow 4: Multi-Agent Context Switch

```
Agent1              Agent2           ContextManager      File Tracker      Memory
  │                  │                   │                   │              │
  ├─start_context────────────────────────>│                   │              │
  │ (proj1, obj1)    │                   ├─save context       │              │
  │                  │                   ├─lock files────────>│              │
  │<─context────────<┤                   │                   │              │
  │ working...       │                   │                   │              │
  │                  │                   │                   │              │
  │                  │ ├─start_context──>│                   │              │
  │                  │ │(proj2, obj2)    ├─different files   │              │
  │                  │ │                 ├─lock files────────>│              │
  │                  │ │<─context───────<├─no conflict!      │              │
  │                  │ │ working...      │                   │              │
  │                  │                   │                   │              │
  ├─switch_context───────────────────────>│                   │              │
  │ (to proj2, obj2) │                   ├─save context from  │              │
  │                  │                   │ previous session   │              │
  │                  │                   ├─load new context  ├─query state ─>│
  │<─new_context─────┤                   │                   │              │
  │ working on proj2 │                   │                   │              │
  │                  │                   │                   │              │
  │                  │ ├─switch_context──>│                   │              │
  │                  │ │(back to proj1)  ├─restore context   ├─query state ─>│
  │                  │ │<─new_context──<─├─re-acquire locks  │              │
  │                  │ │ back to proj1   │                   │              │
```

---

## Module Interaction Diagram

```
                    ┌──────────────────────┐
                    │   FastMCP Server     │
                    │   (Tool Registry)    │
                    └──────────┬───────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
    ┌────▼────┐         ┌──────▼──────┐        ┌────▼─────┐
    │ Memory  │         │  Context    │        │Architecture
    │ Tools   │         │   Tools     │        │   Tools
    └────┬────┘         └──────┬──────┘        └────┬──────┘
         │                     │                    │
         │              ┌──────┴─────┐              │
         │              │            │              │
    ┌────▼────────┐  ┌──▼──┐    ┌───▼──┐     ┌─────▼──────┐
    │ProjectMemory│  │Context  │FileTracker  │ArchAnalyzer│
    │Store        │  │Manager  │            │ ArchRecommend
    └────┬────────┘  └──┬──┬───┘            └──────┬──────┘
         │              │  │                       │
         └──────────────┼──┼───────────────────────┘
                        │  │
                   ┌────▼──▼────────┐
                   │ Storage Backend │
                   │ (Abstract)      │
                   └────┬───────────┘
                        │
                   ┌────▼──────────┐
                   │JSONStorageBknd│
                   └────┬──────────┘
                        │
                   ┌────▼────────────┐
                   │ JSON Files on   │
                   │ Disk (~/.coord) │
                   └─────────────────┘
```

---

## Tool Dependency Graph

```
Memory Tools
├── save_decision ──────┐
├── get_project_decisions
├── search_decisions ───├── ProjectMemoryStore ──┐
├── update_tech_stack ─┤                        │
├── get_tech_stack ────┤                        │
├── log_change ────────┤                        │
├── get_recent_changes─┤                        │
└── update_file_metadata                        │
                                               │
Context Tools                                  │
├── register_agent ────┐                       │
├── start_context ─────├── ContextManager ─────┼── JSONStorageBackend
├── get_agent_context ─┤                       │
├── switch_context ────┤                       │
├── lock_files ────────├── FileTracker ───────┤
├── unlock_files ──────┤                       │
├── get_locked_files ──┤                       │
└── get_agents_list ───┘                       │
                                               │
Architecture Tools                             │
├── analyze_architecture ──┐                   │
├── get_arch_recommendation├── Analyzer ──┐    │
├── validate_code_structure├── Recommender├────┘
├── update_architecture ───┤
└── get_design_patterns ───┘
                           │
Query Tools               │
├── search_decisions ──────┼── Combined access to all above
├── get_module_info ───────┤
├── get_file_dependencies ─┤
└── get_agent_activity ────┘
```

---

## State Machine: Agent Context

```
                    ┌──────────────┐
                    │   INIT       │
                    │  (Registered)│
                    └──────┬───────┘
                           │
                    register_agent()
                           │
                    ┌──────▼─────────┐
                    │  REGISTERED    │
                    │  (No context)  │
                    └──────┬─────────┘
                           │
                    start_context()
                           │
                    ┌──────▼──────────┐
    ┌───────────────│  ACTIVE         │
    │               │  (In progress)  │
    │               └──────┬──────────┘
    │                      │
    │              switch_context() or
    │              end_context()
    │                      │
    │              ┌───────▼─────────┐
    │              │  PAUSED         │
    │              │  (session saved)│
    │              └───────┬─────────┘
    │                      │
    │            start_context() (resume)
    │                      │
    └──────────────────────┘
```

---

## File Locking State Machine

```
              ┌──────────────┐
              │   UNLOCKED   │
              │  (available) │
              └──────┬───────┘
                     │
              lock_files()
                     │
         ┌───────────▼──────────┐
         │   LOCKED             │
         │   (agent_id, reason) │
         └───────────┬──────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
 unlock_files()  cleanup_stale   force_unlock()
  (normal)       (24h timeout)    (override)
      │              │              │
      └──────────────┴──────────────┘
              │
         ┌────▼────────┐
         │  UNLOCKED   │
         │ (available) │
         └─────────────┘
```

---

## Data Schema Relationships

```
Project
├── Decisions (many)
│   ├── tags (array)
│   ├── related_files (array)
│   └── status: active|archived|superseded
│
├── Tech Stack (dict)
│   ├── backend (category)
│   ├── frontend (category)
│   ├── database (category)
│   └── infrastructure (category)
│
├── Architecture (dict)
│   ├── overview (string)
│   ├── modules (many)
│   │   ├── files (array)
│   │   ├── dependencies (array)
│   │   └── responsibilities (array)
│   └── design_patterns (array)
│
├── File Metadata (dict of files)
│   ├── type: source|test|config|doc
│   ├── module: string
│   ├── dependencies (array)
│   ├── dependents (array)
│   └── complexity: low|medium|high
│
└── Recent Changes (array)
    ├── file_path: string
    ├── change_type: create|modify|delete|refactor
    ├── architecture_impact: none|minor|significant
    ├── agent_id: string
    └── related_decision: optional

Agent
├── Profile (metadata)
├── Current Context (session)
│   ├── project_id
│   ├── objective
│   └── locked_files
├── Locked Files (array)
└── Session Log (array)

Recommendation
├── Request (input)
├── Recommendation
│   ├── file_structure
│   ├── code_structure
│   ├── architecture_impact
│   └── design_principles
├── Implementation Guide
└── Status: pending|approved|implemented
```

---

## API Call Sequence: Complete Workflow

```
Time  Agent                           System                            Storage
T0    register_agent()────────────────>
      "opencode-dev"                  Generate UUID
                                      Save profile
                                      ├─────────────────────────────────>
                                      │ agents/agent1/profile.json
      <────agent_id(agent-001)────────
                                      
T1    create_project()────────────────>
      "MyProject"                     Generate UUID
                                      Create directories
                                      ├─────────────────────────────────>
                                      │ projects.json
                                      │ memory/proj1/*
      <────project_id(proj-001)───────

T2    start_context()───────────────>
      (agent-001, proj-001,            Save context
      "Build Auth")                   ├─────────────────────────────────>
                                      │ agents/agent-001/context.json
      <────context────────────────────

T3    lock_files()─────────────────────>
      (agent-001, proj-001,           Check availability
      ["src/auth/models.py"])         Save locks
                                      ├─────────────────────────────────>
                                      │ agents/agent-001/locked_files.json
      <────{locked: true}──────────────

T4    save_decision()─────────────────>
      (proj-001, "Use Pydantic...")   Create Decision
                                      Save to memory
                                      ├─────────────────────────────────>
                                      │ memory/proj1/decisions.json
      <────decision_id────────────────

T5    get_arch_recommendation()───────>
      (proj-001,                      Analyze project
      "User Authentication")          Match patterns
                                      Generate structure
                                      Recommend files
      <────recommendation──────────────

T6    log_change()──────────────────────>
      (proj-001, "src/auth/models.py" Create Change entry
      "create", "Added User model")   Save to changes
                                      ├─────────────────────────────────>
                                      │ memory/proj1/recent_changes.json
      <────change_id────────────────────

T7    unlock_files()──────────────────>
      (agent-001, proj-001,           Remove locks
      ["src/auth/models.py"])         ├─────────────────────────────────>
                                      │ agents/agent-001/locked_files.json
      <────{unlocked: true}───────────

T8    switch_context()────────────────>
      (agent-001, to_proj_id,         Save current session
      "API Endpoints")                Load new context
                                      ├─────────────────────────────────>
                                      │ agents/agent-001/session_log.json
      <────new_context────────────────
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              HOST MACHINE                                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ~/.coordmcp/                                                │
│  ├── data/                   (persistent storage)           │
│  │   ├── memory/                                            │
│  │   ├── agents/                                            │
│  │   ├── recommendations/                                   │
│  │   └── global/                                            │
│  │                                                          │
│  └── logs/                   (activity logs)                │
│      └── coordmcp.log                                       │
│                                                              │
│  Python Virtual Environment (optional)                      │
│  ├── python 3.9+                                            │
│  ├── fastmcp                                                │
│  ├── pydantic                                               │
│  └── other dependencies                                     │
│                                                              │
│  CoordMCP Package                                           │
│  └── src/coordmcp/                                          │
│      ├── main.py (FastMCP server startup)                   │
│      └── (all modules)                                      │
│                                                              │
│  MCP Socket/Stdio                                           │
│  └── Agents connect here (Opencode, Cursor, Claude Code)   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Extension Points for Future Enhancements

```
Current Implementation         Future Enhancement Point
─────────────────────────────────────────────────────────────

JSONStorageBackend         → PostgreSQL Backend
                           → MongoDB Backend
                           → Vector DB Backend

Local File Locking         → Redis Distributed Locking
                           → Real-time conflict resolution

Rule-Based Recommendations → ML Model Recommendations
                           → Embedding-based search

Single Server              → Distributed System
                           → Load balancing

Manual Backups             → Automated Backup System
                           → Cloud Storage Integration

Text Search (decisions)     → Vector Search (semantics)
                           → Full-text Search Index

Simple Metrics             → Advanced Analytics
                           → Performance Dashboard

CLI Only                   → Web UI Dashboard
                           → Mobile App

Offline Only               → Git Integration
                           → Live Team Collaboration
```

---

This visual architecture should help Opencode understand how all components fit together!
