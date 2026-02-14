# Multi-Agent Workflow

Learn how multiple agents can collaborate on the same project without conflicts.

**Difficulty:** ⭐⭐⭐ Advanced  
**Time:** 15-20 minutes

## Introduction

Modern development often involves multiple agents (or developers) working simultaneously. CoordMCP provides sophisticated coordination mechanisms:

- **File Locking** - Prevent conflicts between agents
- **Context Awareness** - Know who's working on what
- **Change Logging** - Track all modifications
- **Conflict Detection** - Automatic prevention of overwrites
- **Agent Discovery** - See which agents are active

## Scenario

Three agents are building an e-commerce platform:

- **FrontendAgent** (React/TypeScript) - Building UI components
- **BackendAgent** (Python/FastAPI) - Building API endpoints
- **DatabaseAgent** (SQL) - Designing schema and migrations

They need to work simultaneously without stepping on each other's toes.

## Prerequisites

- Completed [Context Switching](./context-switching.md)
- Understanding of file locking concepts
- CoordMCP server running

## Step-by-Step Guide

### Step 1: Create the Project

First, create a shared project:

```python
import os

# Create project in a shared workspace
project = await coordmcp_create_project(
    project_name="E-Commerce Platform",
    workspace_path=os.getcwd(),
    description="Multi-agent collaboration on e-commerce platform with React frontend, FastAPI backend, and PostgreSQL database"
)
project_id = project["project_id"]
print(f"✓ Project created: {project['project_name']} ({project_id})")
```

### Step 2: Register All Agents

Register each team member with their specific capabilities:

```python
# Frontend Agent
frontend_agent = await coordmcp_register_agent(
    agent_name="FrontendAgent",
    agent_type="opencode",
    capabilities=["react", "typescript", "css", "ui-design", "frontend"]
)
frontend_id = frontend_agent["agent_id"]
print(f"✓ Frontend Agent: {frontend_id}")
print(f"  Capabilities: {frontend_agent.get('capabilities', [])}")

# Backend Agent
backend_agent = await coordmcp_register_agent(
    agent_name="BackendAgent",
    agent_type="cursor",
    capabilities=["python", "fastapi", "postgresql", "api-design", "backend"]
)
backend_id = backend_agent["agent_id"]
print(f"✓ Backend Agent: {backend_id}")

# Database Agent
database_agent = await coordmcp_register_agent(
    agent_name="DatabaseAgent",
    agent_type="claude_code",
    capabilities=["sql", "postgresql", "database-design", "migrations", "optimization"]
)
database_id = database_agent["agent_id"]
print(f"✓ Database Agent: {database_id}")

print(f"\n👥 Total agents registered: 3")
```

### Step 3: Start Contexts for Each Agent

Each agent starts working on their part:

```python
# Frontend starts
await coordmcp_start_context(
    agent_id=frontend_id,
    project_id=project_id,
    objective="Implement user authentication UI",
    task_description="Create login, register, and password reset pages with form validation and error handling",
    priority="high",
    current_file="src/components/Auth/Login.tsx"
)
print("✓ Frontend context: Authentication UI")

# Backend starts
await coordmcp_start_context(
    agent_id=backend_id,
    project_id=project_id,
    objective="Implement authentication API",
    task_description="Create login, register, JWT token endpoints, and password reset functionality",
    priority="high",
    current_file="src/api/auth.py"
)
print("✓ Backend context: Authentication API")

# Database starts
await coordmcp_start_context(
    agent_id=database_id,
    project_id=project_id,
    objective="Design user schema",
    task_description="Create users table, authentication tables, and proper indexes for performance",
    priority="high",
    current_file="migrations/001_users.sql"
)
print("✓ Database context: User schema")

# Verify all contexts
print("\n📋 Active Contexts:")
for agent_id, name in [(frontend_id, "Frontend"), (backend_id, "Backend"), (database_id, "Database")]:
    ctx = await coordmcp_get_agent_context(agent_id=agent_id)
    if ctx.get('current_context'):
        print(f"  • {name}: {ctx['current_context']['current_objective']}")
```

### Step 4: Lock Files for Each Agent

Each agent locks the files they're working on:

```python
# Frontend locks UI files
frontend_locks = await coordmcp_lock_files(
    agent_id=frontend_id,
    project_id=project_id,
    files=[
        "src/components/Auth/Login.tsx",
        "src/components/Auth/Register.tsx",
        "src/components/Auth/PasswordReset.tsx",
        "src/styles/auth.css",
        "src/types/auth.ts"
    ],
    reason="Working on authentication UI components",
    expected_duration_minutes=180
)
print(f"✓ Frontend locked {frontend_locks['count']} files")
for f in frontend_locks['locked_files']:
    print(f"  • {f}")

# Backend locks API files
backend_locks = await coordmcp_lock_files(
    agent_id=backend_id,
    project_id=project_id,
    files=[
        "src/api/auth.py",
        "src/services/auth_service.py",
        "src/models/user.py",
        "src/schemas/auth.py"
    ],
    reason="Implementing authentication API endpoints",
    expected_duration_minutes=240
)
print(f"✓ Backend locked {backend_locks['count']} files")

# Database locks schema files
database_locks = await coordmcp_lock_files(
    agent_id=database_id,
    project_id=project_id,
    files=[
        "migrations/001_users.sql",
        "migrations/002_auth_tables.sql",
        "schema/users.er",
        "schema/auth.dbml"
    ],
    reason="Designing user database schema and authentication tables",
    expected_duration_minutes=120
)
print(f"✓ Database locked {database_locks['count']} files")
```

### Step 5: Check File Locks

See what files are locked and by whom:

```python
# Get all locked files
locked = await coordmcp_get_locked_files(project_id=project_id)

print(f"\n🔒 Total locked files: {locked['total_locked']}")
print(f"\nBy Agent:")
for agent_id_key, files in locked['by_agent'].items():
    # Get agent name
    agent_info = await coordmcp_get_agent_profile(agent_id=agent_id_key)
    agent_name = agent_info.get('agent_name', agent_id_key[:8])
    print(f"  {agent_name}: {len(files)} files")
    for f in files[:3]:  # Show first 3
        print(f"    • {f['file_path']}")
```

**Expected Output:**
```
🔒 Total locked files: 13

By Agent:
  FrontendAgent: 5 files
    • src/components/Auth/Login.tsx
    • src/components/Auth/Register.tsx
    • src/components/Auth/PasswordReset.tsx
  BackendAgent: 4 files
    • src/api/auth.py
    • src/services/auth_service.py
    • src/models/user.py
  DatabaseAgent: 4 files
    • migrations/001_users.sql
    • migrations/002_auth_tables.sql
    • schema/users.er
```

### Step 6: Conflict Detection

CoordMCP automatically prevents file conflicts. Let's demonstrate what happens when Backend tries to access Frontend's file:

```python
# Backend tries to check what frontend is doing
# (In a real scenario, Backend would coordinate with Frontend instead of trying to lock)

# Check if a file is locked
locked_files = await coordmcp_get_locked_files(project_id=project_id)
login_file_locked = False
locked_by = None

for agent_id_key, files in locked_files['by_agent'].items():
    for f in files:
        if f['file_path'] == 'src/components/Auth/Login.tsx':
            login_file_locked = True
            agent_info = await coordmcp_get_agent_profile(agent_id=agent_id_key)
            locked_by = agent_info.get('agent_name', agent_id_key[:8])
            break

if login_file_locked:
    print(f"✓ Conflict prevention working!")
    print(f"  File 'Login.tsx' is locked by {locked_by}")
    print(f"  Backend should coordinate with Frontend before making changes")
else:
    print("File is available")

# Backend can safely work on their own files
print(f"\n✓ Backend can safely work on:")
for f in backend_locks['locked_files']:
    print(f"  • {f}")
```

**Key Point:** CoordMCP prevents conflicts through explicit file locking - always check locks before working on files!

### Step 7: Check Active Agents

See who's working on the project:

```python
# Get active agents
agents = await coordmcp_get_active_agents(project_id=project_id)

print(f"\n👥 Active agents: {agents['total_count']}")
for agent_info in agents['agents']:
    print(f"\n  • {agent_info['agent_name']} ({agent_info['agent_type']})")
    print(f"    Current Objective: {agent_info.get('current_objective', 'No objective')}")
    print(f"    Locked Files: {agent_info.get('locked_files_count', 0)}")
    print(f"    Last Active: {agent_info.get('last_active', 'N/A')}")
    print(f"    Capabilities: {', '.join(agent_info.get('capabilities', [])[:5])}")
```

**Expected Output:**
```
👥 Active agents: 3

  • FrontendAgent (opencode)
    Current Objective: Implement user authentication UI
    Locked Files: 5
    Last Active: 2026-02-14T10:30:00
    Capabilities: react, typescript, css, ui-design, frontend

  • BackendAgent (cursor)
    Current Objective: Implement authentication API
    Locked Files: 4
    Last Active: 2026-02-14T10:30:00
    Capabilities: python, fastapi, postgresql, api-design, backend

  • DatabaseAgent (claude_code)
    Current Objective: Design user schema
    Locked Files: 4
    Last Active: 2026-02-14T10:30:00
    Capabilities: sql, postgresql, database-design, migrations, optimization
```

### Step 8: Coordinate Through Decisions

Agents can communicate through architectural decisions:

```python
# Frontend documents their API requirements
await coordmcp_save_decision(
    project_id=project_id,
    title="Authentication API Requirements",
    description="Frontend needs the following endpoints: POST /auth/login, POST /auth/register, POST /auth/forgot-password",
    rationale="These endpoints are required for the authentication flow UI. JWT tokens should be returned on successful login.",
    impact="Backend needs to implement these endpoints",
    tags=["api", "authentication", "frontend-requirements"],
    related_files=["src/components/Auth/Login.tsx", "src/components/Auth/Register.tsx"],
    author_agent=frontend_id
)
print("✓ Frontend documented API requirements")

# Backend acknowledges and designs API
await coordmcp_save_decision(
    project_id=project_id,
    title="Authentication API Design",
    description="Implementing RESTful auth endpoints with JWT tokens. Login returns access_token and refresh_token.",
    rationale="Following REST conventions with stateless JWT authentication. Access tokens expire in 15 minutes, refresh in 7 days.",
    impact="Defines the API contract for frontend integration",
    tags=["api", "authentication", "jwt", "backend-design"],
    related_files=["src/api/auth.py", "src/schemas/auth.py"],
    author_agent=backend_id
)
print("✓ Backend documented API design")

# Database documents schema
await coordmcp_save_decision(
    project_id=project_id,
    title="User Schema Design",
    description="Users table with: id, email, password_hash, created_at, updated_at. Separate auth_tokens table for refresh tokens.",
    rationale="Normalized schema with separate token table for security. Passwords hashed with bcrypt. Indexes on email for lookups.",
    impact="Backend must use this schema. Migration files will be provided.",
    tags=["database", "schema", "users", "security"],
    related_files=["migrations/001_users.sql", "migrations/002_auth_tables.sql"],
    author_agent=database_id
)
print("✓ Database documented schema design")
```

### Step 9: Log Changes

Each agent logs their work:

```python
# Frontend logs UI work
await coordmcp_log_change(
    project_id=project_id,
    file_path="src/components/Auth/Login.tsx",
    change_type="create",
    description="Created login component with email/password fields, validation, and error handling",
    agent_id=frontend_id,
    architecture_impact="minor",
    code_summary="React component with useState for form state, Yup validation, error display"
)
print("✓ Frontend logged: Login component created")

# Backend logs API work
await coordmcp_log_change(
    project_id=project_id,
    file_path="src/api/auth.py",
    change_type="create",
    description="Created authentication endpoints: login, register, forgot-password",
    agent_id=backend_id,
    architecture_impact="significant",
    code_summary="FastAPI routes with JWT token generation, bcrypt password hashing"
)
print("✓ Backend logged: Auth endpoints created")

# Database logs schema work
await coordmcp_log_change(
    project_id=project_id,
    file_path="migrations/001_users.sql",
    change_type="create",
    description="Created users table with proper indexes and constraints",
    agent_id=database_id,
    architecture_impact="significant",
    code_summary="PostgreSQL table: id (UUID), email (unique), password_hash, timestamps"
)
print("✓ Database logged: Users table created")

# Get recent changes
changes = await coordmcp_get_recent_changes(project_id=project_id, limit=10)
print(f"\n📝 Recent changes ({changes['count']}):")
for c in changes['changes']:
    impact_icon = "🔴" if c['architecture_impact'] == 'significant' else "🟡" if c['architecture_impact'] == 'minor' else "⚪"
    print(f"  {impact_icon} {c['file_path']}: {c['description']}")
```

### Step 10: Monitor Progress

Check the overall project status:

```python
# Get project info
info = await coordmcp_get_project_info(project_id=project_id)
print(f"\n📊 Project Status: {info['project']['project_name']}")

# Get all decisions
decisions = await coordmcp_get_project_decisions(project_id=project_id)
print(f"   Decisions: {decisions['count']}")

# Get tech stack
tech = await coordmcp_get_tech_stack(project_id=project_id)
print(f"   Technologies: {sum(len(v) for v in tech['tech_stack'].values())}")

# Get active agents
agents = await coordmcp_get_active_agents(project_id=project_id)
print(f"   Active Agents: {agents['total_count']}")

# Get locked files
locked = await coordmcp_get_locked_files(project_id=project_id)
print(f"   Locked Files: {locked['total_locked']}")

# Get recent changes
changes = await coordmcp_get_recent_changes(project_id=project_id)
print(f"   Recent Changes: {changes['count']}")
```

### Step 11: Unlock Files When Done

When agents finish their work, they unlock files for others:

```python
# Frontend unlocks
await coordmcp_unlock_files(
    agent_id=frontend_id,
    project_id=project_id,
    files=[
        "src/components/Auth/Login.tsx",
        "src/components/Auth/Register.tsx",
        "src/components/Auth/PasswordReset.tsx",
        "src/styles/auth.css",
        "src/types/auth.ts"
    ]
)
print("✓ Frontend files unlocked - available for review/modification")

# Backend unlocks
await coordmcp_unlock_files(
    agent_id=backend_id,
    project_id=project_id,
    files=[
        "src/api/auth.py",
        "src/services/auth_service.py",
        "src/models/user.py",
        "src/schemas/auth.py"
    ]
)
print("✓ Backend files unlocked - available for integration testing")

# Database unlocks
await coordmcp_unlock_files(
    agent_id=database_id,
    project_id=project_id,
    files=[
        "migrations/001_users.sql",
        "migrations/002_auth_tables.sql",
        "schema/users.er",
        "schema/auth.dbml"
    ]
)
print("✓ Database files unlocked - ready for execution")

# Verify all unlocked
locked = await coordmcp_get_locked_files(project_id=project_id)
print(f"\n🔓 Remaining locked files: {locked['total_locked']}")
```

### Step 12: End Sessions

All agents end their contexts:

```python
# Frontend ends
await coordmcp_end_context(
    agent_id=frontend_id,
    summary="Completed authentication UI: login, register, and password reset forms with validation",
    outcome="success"
)
print("✓ Frontend session ended")

# Backend ends
await coordmcp_end_context(
    agent_id=backend_id,
    summary="Completed authentication API: login, register, forgot-password endpoints with JWT tokens",
    outcome="success"
)
print("✓ Backend session ended")

# Database ends
await coordmcp_end_context(
    agent_id=database_id,
    summary="Completed user schema: users table, auth tables, indexes, and migration files",
    outcome="success"
)
print("✓ Database session ended")

print("\n🎉 All agent sessions completed successfully!")
```

## Complete Example Code

Here's the complete example:

```python
import os

# Setup
project = await coordmcp_create_project(
    project_name="E-Commerce Platform",
    workspace_path=os.getcwd(),
    description="Multi-agent project"
)
project_id = project["project_id"]

# Register agents
frontend = await coordmcp_register_agent(
    name="Frontend",
    agent_type="opencode",
    capabilities=["react"]
)
backend = await coordmcp_register_agent(
    name="Backend",
    agent_type="cursor",
    capabilities=["python"]
)
database = await coordmcp_register_agent(
    name="Database",
    agent_type="claude_code",
    capabilities=["sql"]
)

# Start contexts
await coordmcp_start_context(
    agent_id=frontend["agent_id"],
    project_id=project_id,
    objective="Build UI",
    priority="high"
)
await coordmcp_start_context(
    agent_id=backend["agent_id"],
    project_id=project_id,
    objective="Build API",
    priority="high"
)
await coordmcp_start_context(
    agent_id=database["agent_id"],
    project_id=project_id,
    objective="Design DB",
    priority="high"
)

# Lock files
await coordmcp_lock_files(
    agent_id=frontend["agent_id"],
    project_id=project_id,
    files=["src/App.tsx"],
    reason="Building UI"
)
await coordmcp_lock_files(
    agent_id=backend["agent_id"],
    project_id=project_id,
    files=["src/api.py"],
    reason="Building API"
)

# Check status
agents = await coordmcp_get_active_agents(project_id=project_id)
print(f"{agents['total_count']} agents working")

# Log changes
await coordmcp_log_change(
    project_id=project_id,
    file_path="src/App.tsx",
    change_type="create",
    description="Created UI",
    agent_id=frontend["agent_id"]
)

# Unlock
await coordmcp_unlock_files(
    agent_id=frontend["agent_id"],
    project_id=project_id,
    files=["src/App.tsx"]
)

# End sessions
await coordmcp_end_context(agent_id=frontend["agent_id"])
await coordmcp_end_context(agent_id=backend["agent_id"])
await coordmcp_end_context(agent_id=database["agent_id"])

print("Multi-agent workflow complete!")
```

## Key Concepts Learned

1. **Multi-Agent Registration** - Multiple agents on one project
2. **File Locking** - Prevent conflicts through explicit locks
3. **Conflict Detection** - Check locks before working on files
4. **Change Logging** - Track who did what
5. **Agent Coordination** - Work together through decisions and communication
6. **Progress Monitoring** - Track project status across agents

## Best Practices

### For Multi-Agent Projects

1. **Lock early** - Before making changes, lock the files
2. **Communicate** - Use decisions to document requirements and designs
3. **Unlock promptly** - When done with files, unlock them
4. **Log changes** - Keep audit trail of all modifications
5. **Check locks** - Before starting work, see what's locked
6. **Save decisions** - Document API contracts and schema designs
7. **Monitor** - Regularly check project status and agent activity

### Communication Patterns

```python
# Before starting work
discovery = await coordmcp_discover_project(path=os.getcwd())
if discovery["found"]:
    project_id = discovery["project"]["project_id"]
    
    # Check what's locked
    locked = await coordmcp_get_locked_files(project_id=project_id)
    print(f"Currently locked: {locked['total_locked']} files")
    
    # See who's working
    agents = await coordmcp_get_active_agents(project_id=project_id)
    print(f"Active agents: {agents['total_count']}")
    for a in agents['agents']:
        print(f"  - {a['agent_name']}: {a.get('current_objective', 'N/A')}")

# After finishing
await coordmcp_log_change(
    project_id=project_id,
    file_path="src/feature.py",
    change_type="create",
    description="Implemented feature X",
    agent_id=agent_id,
    architecture_impact="significant"
)
print("✓ Changes logged for team visibility")

# Unlock for others
await coordmcp_unlock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["src/feature.py"]
)
```

## Real-World Scenarios

### Scenario 1: Frontend & Backend Coordination

```python
# Frontend starts and documents requirements
await coordmcp_start_context(
    frontend_id,
    project_id=project_id,
    objective="Build user profile page",
    task_description="Need user data endpoint with email, name, avatar"
)

await coordmcp_save_decision(
    project_id=project_id,
    title="User Profile API Requirements",
    description="GET /api/users/me returns {id, email, name, avatar_url}",
    rationale="Frontend profile page needs these fields",
    author_agent=frontend_id
)

# Backend implements based on requirements
await coordmcp_start_context(
    backend_id,
    project_id=project_id,
    objective="Implement user profile endpoint"
)

# Backend checks requirements
decisions = await coordmcp_get_project_decisions(
    project_id=project_id,
    tags=["api-requirements"]
)
print(f"Found {decisions['count']} requirement decisions")

# Backend implements accordingly
await coordmcp_log_change(
    project_id=project_id,
    file_path="src/api/users.py",
    change_type="create",
    description="Implemented GET /api/users/me endpoint",
    agent_id=backend_id
)
```

### Scenario 2: Code Review Workflow

```python
# Agent 1 finishes and unlocks
await coordmcp_unlock_files(
    agent_id=agent1_id,
    project_id=project_id,
    files=["src/feature.py"]
)

# Log completion
await coordmcp_log_change(
    project_id=project_id,
    file_path="src/feature.py",
    change_type="create",
    description="Feature implementation complete",
    agent_id=agent1_id
)

# Agent 2 reviews
locked = await coordmcp_get_locked_files(project_id=project_id)
if "src/feature.py" not in [f['file_path'] for files in locked['by_agent'].values() for f in files]:
    print("Files free for review!")
    await coordmcp_lock_files(
        agent_id=agent2_id,
        project_id=project_id,
        files=["src/feature.py"],
        reason="Code review"
    )
    # Review code...
    await coordmcp_save_decision(
        project_id=project_id,
        title="Code Review: Feature Implementation",
        description="Reviewed feature.py - approved with minor suggestions",
        rationale="Code quality is good, follows standards",
        author_agent=agent2_id
    )
    await coordmcp_unlock_files(
        agent_id=agent2_id,
        project_id=project_id,
        files=["src/feature.py"]
    )
```

## Troubleshooting

### "Cannot lock file - already locked"
```python
# Check who has it locked
locked = await coordmcp_get_locked_files(project_id=project_id)
for agent_id_key, files in locked['by_agent'].items():
    for f in files:
        if f['file_path'] == 'src/file.py':
            agent_info = await coordmcp_get_agent_profile(agent_id=agent_id_key)
            print(f"File locked by: {agent_info['agent_name']}")
            print(f"Reason: {f.get('reason', 'N/A')}")
            print(f"Locked at: {f.get('locked_at', 'N/A')}")
            
# Contact the agent or wait
# Or use get_active_agents to see if they're online
```

### "Agent not found"
```python
# Ensure agent is registered
agent = await coordmcp_register_agent(
    agent_name="MyAgent",
    agent_type="opencode",
    capabilities=["python"]
)
agent_id = agent["agent_id"]

# Or check existing agents
agents = await coordmcp_get_agents_list()
print(f"Registered agents: {len(agents['agents'])}")
```

### "Too many conflicts"
```python
# Plan work better with team
# Use architecture recommendations to split work
rec = await coordmcp_get_architecture_recommendation(
    project_id=project_id,
    feature_description="Add user management system",
    implementation_style="modular"
)

print("Split work by module:")
for file_info in rec['file_structure']['new_files']:
    print(f"  - {file_info['path']}: {file_info['type']}")
    # Assign to different agents based on type
```

## Summary

**What You Learned:**
- ✅ Register multiple agents with specific capabilities
- ✅ Coordinate file locking across agents
- ✅ Prevent conflicts through lock checking
- ✅ Track all changes with detailed logging
- ✅ View agent activity and project status
- ✅ Communicate through architectural decisions
- ✅ Monitor project progress across all agents

**Benefits:**
- **No overwrites** - Explicit lock-based conflict prevention
- **Transparency** - See who's doing what in real-time
- **Audit trail** - Complete change history
- **Team coordination** - Work together smoothly through decisions
- **Progress tracking** - Monitor project status across agents

---

**Congratulations!** You're now a multi-agent coordination expert! 🎉

**Next Steps:**
- Explore the [API Reference](../API_REFERENCE.md)
- Read about [Extending CoordMCP](../EXTENDING.md)
- Check [Troubleshooting](../TROUBLESHOOTING.md) for common issues
