# Basic Project Setup Example

Learn how to create your first project and record architectural decisions with CoordMCP.

**Difficulty:** ⭐ Easy  
**Time:** 5-10 minutes

## Introduction

This example demonstrates the fundamental workflow for setting up a project and recording key architectural decisions. By the end, you'll understand how to:

- Create a new project with workspace_path
- Register as an agent with session persistence
- Record architectural decisions with context
- Update your technology stack
- Log changes for audit trail
- Query project information

## Scenario

You're starting a new REST API project and want to track your decisions from day one using CoordMCP.

## Prerequisites

- CoordMCP installed and running (`pip install coordmcp`)
- Your agent (OpenCode, Cursor, etc.) configured with CoordMCP
- CoordMCP server started (`python -m coordmcp` or `coordmcp`)

## Step-by-Step Guide

### Step 1: Discover or Create Project

**Always** try to discover an existing project first before creating a new one:

```python
import os

# Try to discover existing project in current directory
discovery = await coordmcp_discover_project(path=os.getcwd())

if discovery["found"]:
    project_id = discovery["project"]["project_id"]
    print(f"✓ Found existing project: {discovery['project']['project_name']}")
    print(f"  Project ID: {project_id}")
else:
    # Create new project (requires workspace_path)
    result = await coordmcp_create_project(
        project_name="My Awesome API",
        workspace_path=os.getcwd(),  # REQUIRED: Absolute path
        description="A RESTful API service built with FastAPI"
    )
    project_id = result["project_id"]
    print(f"✓ Project created: {result['project_name']}")
    print(f"  Project ID: {project_id}")
```

**Key Points:**
- `workspace_path` is **required** when creating a project (use `os.getcwd()`)
- `workspace_path` must be an absolute path
- Discovery checks current directory and up to 3 parent directories

### Step 2: Register as an Agent

Register yourself to enable multi-agent coordination and session persistence:

```python
# Register as an agent (use SAME name across sessions!)
agent = await coordmcp_register_agent(
    agent_name="DevTeam_Member1",  # Use consistent name
    agent_type="opencode",         # or "cursor", "claude_code", "custom"
    capabilities=["python", "fastapi", "postgresql"]
)
agent_id = agent["agent_id"]
print(f"✓ Agent registered: {agent['message']}")
print(f"  Agent ID: {agent_id}")
```

**Important:**
- Use the same `agent_name` across sessions to reconnect to the same identity
- If an agent with the same name exists, you'll reconnect to it
- Capabilities help other agents understand what you can do

### Step 3: Start Your Work Context

Establish what you're working on:

```python
# Start a work context
await coordmcp_start_context(
    agent_id=agent_id,
    project_id=project_id,
    objective="Set up FastAPI project foundation",
    task_description="Initialize project structure, dependencies, and basic configuration",
    priority="high",
    current_file="main.py"
)
print("✓ Work context started")
```

**Priority Levels:**
- `critical` - Production outage, security vulnerability
- `high` - Important features, significant refactoring
- `medium` - Standard development work (default)
- `low` - Documentation, minor optimizations

### Step 4: Record Your First Decision

Document your technology choices with full context:

```python
# Save an architectural decision
await coordmcp_save_decision(
    project_id=project_id,
    title="Use FastAPI for API Framework",
    description="FastAPI will be our primary web framework for building REST APIs",
    rationale="FastAPI offers excellent performance, automatic validation via Pydantic, async support, and automatic OpenAPI documentation generation. Team is already familiar with it.",
    impact="All API endpoints will be built with FastAPI. Affects routing, validation, and documentation.",
    tags=["backend", "framework", "api", "fastapi"],
    related_files=["requirements.txt", "main.py", "src/api/routes.py"],
    author_agent=agent_id
)
print("✓ Decision recorded: Framework choice")
```

**Key Fields:**
- **title** - Short, clear decision name
- **description** - What was decided
- **rationale** - WHY this decision was made (crucial for future reference)
- **impact** - What this affects
- **tags** - Categories for searching
- **related_files** - Files affected by this decision

### Step 5: Record More Decisions

Let's document the database choice:

```python
await coordmcp_save_decision(
    project_id=project_id,
    title="Use PostgreSQL for Primary Database",
    description="PostgreSQL will be our main data store with SQLAlchemy as ORM",
    rationale="ACID compliance, excellent Python support via SQLAlchemy, battle-tested for production, JSON support for flexible schemas when needed",
    impact="All data persistence will use PostgreSQL. Requires setting up database migrations.",
    tags=["database", "postgresql", "sqlalchemy", "storage"],
    related_files=["src/models/", "migrations/", "docker-compose.yml"],
    author_agent=agent_id
)
print("✓ Decision recorded: Database choice")
```

### Step 6: Update Technology Stack

Record your technology choices with versions:

```python
# Update tech stack
await coordmcp_update_tech_stack(
    project_id=project_id,
    category="backend",
    technology="FastAPI",
    version="0.104.0",
    rationale="High performance, async support, automatic API documentation"
)

await coordmcp_update_tech_stack(
    project_id=project_id,
    category="database",
    technology="PostgreSQL",
    version="15",
    rationale="ACID compliance, reliability, JSON support"
)

await coordmcp_update_tech_stack(
    project_id=project_id,
    category="infrastructure",
    technology="Docker",
    version="24.0",
    rationale="Containerization for consistent deployments"
)

print("✓ Technology stack updated")
```

**Categories:**
- `backend` - Server frameworks, languages
- `frontend` - UI frameworks, CSS libraries
- `database` - Databases, ORMs
- `infrastructure` - Docker, Kubernetes, cloud services
- `testing` - Test frameworks
- `devops` - CI/CD tools

### Step 7: Log Your Changes

Record what you've done for audit trail:

```python
# Log file creation
await coordmcp_log_change(
    project_id=project_id,
    file_path="requirements.txt",
    change_type="create",
    description="Created requirements file with FastAPI, SQLAlchemy, and PostgreSQL dependencies",
    agent_id=agent_id,
    architecture_impact="significant",
    code_summary="Added fastapi==0.104.0, sqlalchemy==2.0, psycopg2-binary==2.9",
    related_decision=None
)

await coordmcp_log_change(
    project_id=project_id,
    file_path="main.py",
    change_type="create",
    description="Created main FastAPI application entry point with basic routes",
    agent_id=agent_id,
    architecture_impact="significant",
    code_summary="Initialized FastAPI app with health check endpoint"
)

await coordmcp_log_change(
    project_id=project_id,
    file_path="docker-compose.yml",
    change_type="create",
    description="Set up Docker Compose with PostgreSQL service",
    agent_id=agent_id,
    architecture_impact="minor"
)

print("✓ Changes logged")
```

**Change Types:**
- `create` - New files
- `modify` - Updates to existing files
- `delete` - File deletions
- `refactor` - Restructuring without behavior changes

**Architecture Impact:**
- `none` - Simple changes, bug fixes
- `minor` - Small API changes, config updates
- `significant` - New patterns, major refactoring

### Step 8: Verify Your Work

Check what you've recorded:

```python
# Get project info
info = await coordmcp_get_project_info(project_id=project_id)
print(f"\n📋 Project: {info['project']['project_name']}")
print(f"   Created: {info['project']['created_at']}")
print(f"   Workspace: {info['project']['workspace_path']}")

# Get tech stack
tech = await coordmcp_get_tech_stack(project_id=project_id)
print(f"\n🛠️  Tech Stack:")
for category, entries in tech['tech_stack'].items():
    if entries:
        techs = ', '.join(f"{e['technology']} ({e['version']})" for e in entries)
        print(f"   {category}: {techs}")

# Get decisions
decisions = await coordmcp_get_project_decisions(project_id=project_id)
print(f"\n📊 Decisions: {decisions['count']}")
for d in decisions['decisions']:
    print(f"   • {d['title']} ({d['status']})")
    print(f"     Tags: {', '.join(d['tags'])}")

# Get recent changes
changes = await coordmcp_get_recent_changes(project_id=project_id, limit=5)
print(f"\n📝 Recent Changes: {changes['count']}")
for c in changes['changes']:
    impact_icon = "🔴" if c['architecture_impact'] == 'significant' else "🟡" if c['architecture_impact'] == 'minor' else "⚪"
    print(f"   {impact_icon} {c['file_path']}: {c['description']}")
```

**Expected Output:**
```
📋 Project: My Awesome API
   Created: 2026-02-14T10:30:00
   Workspace: /home/user/projects/my-api

🛠️  Tech Stack:
   backend: FastAPI (0.104.0)
   database: PostgreSQL (15)
   infrastructure: Docker (24.0)

📊 Decisions: 2
   • Use FastAPI for API Framework (active)
     Tags: backend, framework, api, fastapi
   • Use PostgreSQL for Primary Database (active)
     Tags: database, postgresql, sqlalchemy, storage

📝 Recent Changes: 3
   🔴 requirements.txt: Created requirements file...
   🔴 main.py: Created main FastAPI application...
   🟡 docker-compose.yml: Set up Docker Compose...
```

### Step 9: Search Decisions

Find decisions related to specific topics:

```python
# Search for database-related decisions
results = await coordmcp_search_decisions(
    project_id=project_id,
    query="database"
)

print(f"\n🔍 Search 'database': {results['count']} results")
for d in results['decisions']:
    print(f"   • {d['title']}")

# Search by tags
db_decisions = await coordmcp_get_project_decisions(
    project_id=project_id,
    tags=["database"]
)
print(f"\n🏷️  Tagged 'database': {db_decisions['count']} decisions")
```

### Step 10: Clean Up

End your session properly:

```python
# End context
await coordmcp_end_context(agent_id=agent_id)
print("\n✅ Session ended successfully")
```

## Complete Example Code

Here's the complete example in one block:

```python
import os

# 1. Discover or create project
discovery = await coordmcp_discover_project(path=os.getcwd())

if discovery["found"]:
    project_id = discovery["project"]["project_id"]
    print(f"Found existing project: {discovery['project']['project_name']}")
else:
    result = await coordmcp_create_project(
        project_name="My Awesome API",
        workspace_path=os.getcwd(),
        description="A RESTful API service built with FastAPI"
    )
    project_id = result["project_id"]
    print(f"Created project: {result['project_name']}")

# 2. Register as agent
agent = await coordmcp_register_agent(
    agent_name="DevTeam_Member1",
    agent_type="opencode",
    capabilities=["python", "fastapi", "postgresql"]
)
agent_id = agent["agent_id"]

# 3. Start context
await coordmcp_start_context(
    agent_id=agent_id,
    project_id=project_id,
    objective="Set up FastAPI project foundation",
    priority="high"
)

# 4. Save decisions
await coordmcp_save_decision(
    project_id=project_id,
    title="Use FastAPI for API Framework",
    description="FastAPI will be our primary web framework",
    rationale="High performance, async support, automatic docs",
    tags=["backend", "api"],
    author_agent=agent_id
)

await coordmcp_save_decision(
    project_id=project_id,
    title="Use PostgreSQL for Primary Database",
    description="PostgreSQL with SQLAlchemy ORM",
    rationale="ACID compliance, reliability",
    tags=["database"],
    author_agent=agent_id
)

# 5. Update tech stack
await coordmcp_update_tech_stack(
    project_id=project_id,
    category="backend",
    technology="FastAPI",
    version="0.104.0"
)

await coordmcp_update_tech_stack(
    project_id=project_id,
    category="database",
    technology="PostgreSQL",
    version="15"
)

# 6. Log changes
await coordmcp_log_change(
    project_id=project_id,
    file_path="requirements.txt",
    change_type="create",
    description="Created requirements file",
    agent_id=agent_id,
    architecture_impact="significant"
)

await coordmcp_log_change(
    project_id=project_id,
    file_path="main.py",
    change_type="create",
    description="Created main FastAPI app",
    agent_id=agent_id,
    architecture_impact="significant"
)

# 7. Verify
info = await coordmcp_get_project_info(project_id=project_id)
print(f"\n✅ Project setup complete!")
print(f"   Name: {info['project']['project_name']}")
print(f"   ID: {project_id}")
print(f"   Agent: {agent_id}")

# 8. End session
await coordmcp_end_context(agent_id=agent_id)
```

## Key Concepts

1. **Project Discovery** - Always try to discover before creating to prevent duplicates
2. **Workspace Path** - Must be an absolute path when creating projects (use `os.getcwd()`)
3. **Agent Persistence** - Same name = same agent ID across sessions, preserving history
4. **Decisions** - Record WHY you made choices, not just WHAT. Future you will thank you!
5. **Tech Stack** - Track versions for future reference and compatibility checks
6. **Changes** - Log all significant modifications for a complete audit trail
7. **Flexible Lookup** - Use project_id, project_name, or workspace_path interchangeably

## Next Steps

- Try [Context Switching](./context-switching.md) to work on multiple projects
- Learn about [Architecture Recommendations](./architecture-recommendation.md)
- Explore [Multi-Agent Workflow](./multi-agent-workflow.md)

## Troubleshooting

### "Project not found"
```python
# Always use discover_project first
discovery = await coordmcp_discover_project(path=os.getcwd())
if discovery["found"]:
    project_id = discovery["project"]["project_id"]
```

### "Invalid workspace_path"
```python
# Must be absolute path
import os
await coordmcp_create_project(
    project_name="My App",
    workspace_path=os.getcwd()  # ✓ Correct
)
```

### "Agent already exists"
```python
# This is expected! Same name reconnects to existing agent
agent = await coordmcp_register_agent(
    agent_name="DevTeam_Member1",  # Same name = reconnect
    agent_type="opencode",
    capabilities=["python"]
)
# Check agent['message'] to see if it was a reconnection
```

### "Missing required parameter: workspace_path"
```python
# You forgot to include workspace_path when creating project
result = await coordmcp_create_project(
    project_name="My App",
    workspace_path=os.getcwd(),  # REQUIRED parameter
    description="..."
)
```

## Tips for Success

- ✅ Always call `discover_project` first before creating
- ✅ Use `os.getcwd()` for workspace_path parameter
- ✅ Use consistent agent_name across sessions for persistence
- ✅ Be specific in decision titles and descriptions
- ✅ Always explain the rationale - this is the most valuable part
- ✅ Log changes after completing significant work
- ✅ Use tags to categorize decisions for easier searching
- ✅ Check the `message` field in responses for helpful info

---

**Congratulations!** You've successfully created your first CoordMCP project with proper documentation and tracking. 🎉

Next: Learn how to get [Architecture Recommendations](./architecture-recommendation.md)
