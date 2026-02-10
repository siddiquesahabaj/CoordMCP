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

## Scenario

Three agents are building an e-commerce platform:

- **FrontendAgent** (React/TypeScript) - Building UI components
- **BackendAgent** (Python/FastAPI) - Building API endpoints
- **DatabaseAgent** (SQL) - Designing schema and migrations

They need to work simultaneously without stepping on each other's toes.

## Prerequisites

- Completed [Context Switching](./context-switching.md)
- Understanding of file locking concepts

## Step-by-Step Guide

### Step 1: Create the Project

First, create a shared project:

```python
# Create project
project = await create_project(
    project_name="E-Commerce Platform",
    description="Multi-agent collaboration on e-commerce platform"
)
project_id = project["project_id"]
print(f"✓ Project created: {project_id}")
```

### Step 2: Register All Agents

Register each team member:

```python
# Frontend Agent
frontend_agent = await register_agent(
    agent_name="FrontendAgent",
    agent_type="opencode",
    capabilities=["react", "typescript", "css", "ui-design"]
)
frontend_id = frontend_agent["agent_id"]
print(f"✓ Frontend Agent: {frontend_id}")

# Backend Agent
backend_agent = await register_agent(
    agent_name="BackendAgent",
    agent_type="cursor",
    capabilities=["python", "fastapi", "postgresql", "api-design"]
)
backend_id = backend_agent["agent_id"]
print(f"✓ Backend Agent: {backend_id}")

# Database Agent
database_agent = await register_agent(
    agent_name="DatabaseAgent",
    agent_type="claude_code",
    capabilities=["sql", "postgresql", "database-design", "migrations"]
)
database_id = database_agent["agent_id"]
print(f"✓ Database Agent: {database_id}")
```

### Step 3: Start Contexts for Each Agent

Each agent starts working on their part:

```python
# Frontend starts
await start_context(
    agent_id=frontend_id,
    project_id=project_id,
    objective="Implement user authentication UI",
    task_description="Create login, register, and password reset pages",
    priority="high",
    current_file="src/components/Auth/Login.tsx"
)
print("✓ Frontend context: Authentication UI")

# Backend starts
await start_context(
    agent_id=backend_id,
    project_id=project_id,
    objective="Implement authentication API",
    task_description="Create login, register, and JWT token endpoints",
    priority="high",
    current_file="src/api/auth.py"
)
print("✓ Backend context: Authentication API")

# Database starts
await start_context(
    agent_id=database_id,
    project_id=project_id,
    objective="Design user schema",
    task_description="Create users table and authentication tables",
    priority="high",
    current_file="migrations/001_users.sql"
)
print("✓ Database context: User schema")
```

### Step 4: Lock Files for Each Agent

Each agent locks the files they're working on:

```python
# Frontend locks UI files
frontend_locks = await lock_files(
    agent_id=frontend_id,
    project_id=project_id,
    files=[
        "src/components/Auth/Login.tsx",
        "src/components/Auth/Register.tsx",
        "src/styles/auth.css"
    ],
    reason="Working on authentication UI"
)
print(f"✓ Frontend locked {len(frontend_locks['locked_files'])} files")

# Backend locks API files
backend_locks = await lock_files(
    agent_id=backend_id,
    project_id=project_id,
    files=[
        "src/api/auth.py",
        "src/services/auth_service.py"
    ],
    reason="Implementing authentication API"
)
print(f"✓ Backend locked {len(backend_locks['locked_files'])} files")

# Database locks schema files
database_locks = await lock_files(
    agent_id=database_id,
    project_id=project_id,
    files=[
        "migrations/001_users.sql",
        "schema/users.er"
    ],
    reason="Designing user database schema"
)
print(f"✓ Database locked {len(database_locks['locked_files'])} files")
```

### Step 5: Conflict Detection

Let's see what happens when Backend tries to access Frontend's file:

```python
# Backend tries to lock a frontend file (simulating confusion)
try:
    await lock_files(
        agent_id=backend_id,
        project_id=project_id,
        files=["src/components/Auth/Login.tsx"],  # Frontend's file!
        reason="Need to check the UI structure"
    )
    print("✗ ERROR: Should have raised an error!")
except Exception as e:
    print(f"✓ Conflict detected correctly!")
    print(f"  File 'Login.tsx' is locked by FrontendAgent")
    print(f"  Backend cannot modify it")
```

**Key Point:** CoordMCP automatically prevents file conflicts!

### Step 6: Check Active Agents

See who's working on the project:

```python
# Get active agents
agents = await get_agents_in_project(project_id=project_id)

print(f"\nActive agents: {len(agents['agents'])}")
for agent_info in agents['agents']:
    print(f"  - {agent_info['agent_name']}: {agent_info.get('current_objective', 'No objective')}")
```

**Expected Output:**
```
Active agents: 3
  - FrontendAgent: Implement user authentication UI
  - BackendAgent: Implement authentication API
  - DatabaseAgent: Design user schema
```

### Step 7: Check All Locked Files

See what files are locked and by whom:

```python
# Get all locked files
locked = await get_locked_files(project_id=project_id)

print(f"\nTotal locked files: {locked['total_locked']}")
for agent_id, files in locked['by_agent'].items():
    # Get agent name
    agent_info = await get_agent_profile(agent_id=agent_id)
    agent_name = agent_info.get('agent_name', agent_id[:8])
    print(f"  {agent_name}: {len(files)} files")
```

**Expected Output:**
```
Total locked files: 7
  FrontendAgent: 3 files
  BackendAgent: 2 files
  DatabaseAgent: 2 files
```

### Step 8: Log Changes

Each agent logs their work:

```python
# Frontend logs UI work
await log_change(
    project_id=project_id,
    file_path="src/components/Auth/Login.tsx",
    change_type="create",
    description="Created login component with email/password fields",
    agent_id=frontend_id,
    architecture_impact="minor"
)
print("✓ Frontend logged: Login component created")

# Backend logs API work
await log_change(
    project_id=project_id,
    file_path="src/api/auth.py",
    change_type="create",
    description="Created authentication endpoints",
    agent_id=backend_id,
    architecture_impact="significant"
)
print("✓ Backend logged: Auth endpoints created")

# Database logs schema work
await log_change(
    project_id=project_id,
    file_path="migrations/001_users.sql",
    change_type="create",
    description="Created users table with indexes",
    agent_id=database_id,
    architecture_impact="significant"
)
print("✓ Database logged: Users table created")
```

### Step 9: Unlock Files When Done

When agents finish their work:

```python
# Frontend unlocks
await unlock_files(
    agent_id=frontend_id,
    project_id=project_id,
    files=[
        "src/components/Auth/Login.tsx",
        "src/components/Auth/Register.tsx",
        "src/styles/auth.css"
    ]
)
print("✓ Frontend files unlocked")

# Backend unlocks
await unlock_files(
    agent_id=backend_id,
    project_id=project_id,
    files=[
        "src/api/auth.py",
        "src/services/auth_service.py"
    ]
)
print("✓ Backend files unlocked")

# Database unlocks
await unlock_files(
    agent_id=database_id,
    project_id=project_id,
    files=[
        "migrations/001_users.sql",
        "schema/users.er"
    ]
)
print("✓ Database files unlocked")
```

### Step 10: End Sessions

All agents end their contexts:

```python
# End all contexts
await end_context(agent_id=frontend_id)
await end_context(agent_id=backend_id)
await end_context(agent_id=database_id)
print("✓ All agent sessions ended")
```

## Complete Example Code

```python
# Setup
project = await create_project(name="E-Commerce", description="Multi-agent project")
project_id = project["project_id"]

# Register agents
frontend = await register_agent(name="Frontend", capabilities=["react"])
backend = await register_agent(name="Backend", capabilities=["python"])
database = await register_agent(name="Database", capabilities=["sql"])

# Start contexts
await start_context(agent_id=frontend["agent_id"], project_id=project_id, objective="Build UI")
await start_context(agent_id=backend["agent_id"], project_id=project_id, objective="Build API")
await start_context(agent_id=database["agent_id"], project_id=project_id, objective="Design DB")

# Lock files
await lock_files(agent_id=frontend["agent_id"], project_id=project_id, files=["src/App.tsx"])
await lock_files(agent_id=backend["agent_id"], project_id=project_id, files=["src/api.py"])

# Try conflict (will fail)
try:
    await lock_files(agent_id=backend["agent_id"], project_id=project_id, files=["src/App.tsx"])
except:
    print("Conflict prevented!")

# Check status
agents = await get_agents_in_project(project_id=project_id)
print(f"{len(agents['agents'])} agents working")

# Log changes
await log_change(project_id=project_id, file_path="src/App.tsx", change_type="create", agent_id=frontend["agent_id"])

# Unlock
await unlock_files(agent_id=frontend["agent_id"], project_id=project_id, files=["src/App.tsx"])

# End sessions
await end_context(agent_id=frontend["agent_id"])
await end_context(agent_id=backend["agent_id"])
await end_context(agent_id=database["agent_id"])
```

## Expected Output

```
✓ Project created: proj-ecommerce-123
✓ Frontend Agent: agent-fe-456
✓ Backend Agent: agent-be-789
✓ Database Agent: agent-db-012
✓ Frontend context: Authentication UI
✓ Backend context: Authentication API
✓ Database context: User schema
✓ Frontend locked 3 files
✓ Backend locked 2 files
✓ Database locked 2 files

✓ Conflict detected correctly!
  File 'Login.tsx' is locked by FrontendAgent
  Backend cannot modify it

Active agents: 3
  - FrontendAgent: Implement user authentication UI
  - BackendAgent: Implement authentication API
  - DatabaseAgent: Design user schema

Total locked files: 7
  FrontendAgent: 3 files
  BackendAgent: 2 files
  DatabaseAgent: 2 files

✓ Frontend logged: Login component created
✓ Backend logged: Auth endpoints created
✓ Database logged: Users table created

✓ Frontend files unlocked
✓ Backend files unlocked
✓ Database files unlocked

✓ All agent sessions ended
```

## Key Concepts Learned

1. **Multi-Agent Registration** - Multiple agents on one project
2. **File Locking** - Prevent conflicts automatically
3. **Conflict Detection** - System prevents overwrites
4. **Change Logging** - Track who did what
5. **Agent Coordination** - Work together seamlessly

## Best Practices

### For Multi-Agent Projects

1. **Lock early** - Before making changes
2. **Communicate** - Tell others what you're working on
3. **Unlock promptly** - When done with files
4. **Log changes** - Keep audit trail
5. **Check locks** - Before starting work

### Communication Patterns

```python
# Before starting work
locked = await get_locked_files(project_id=project_id)
print(f"Currently locked: {locked['total_locked']} files")

# After finishing
await log_change(
    project_id=project_id,
    file_path="src/feature.py",
    change_type="create",
    description="Implemented feature X",
    architecture_impact="significant"
)
print("✓ Changes logged for team visibility")
```

## Real-World Scenarios

### Scenario 1: Frontend & Backend Coordination

```python
# Frontend starts
create_context(frontend_id, "Build login form")
lock_files(frontend_id, ["Login.tsx"])

# Backend needs to know the API contract
# Checks what frontend is doing
agents = get_agents_in_project(project_id)
print(f"Frontend is working on: {get_objective(frontend_id)}")

# Backend implements API accordingly
create_context(backend_id, "Build login API")
lock_files(backend_id, ["auth.py"])
```

### Scenario 2: Code Review Workflow

```python
# Agent 1 finishes and unlocks
unlock_files(agent1_id, files)

# Agent 2 reviews
locked = get_locked_files(project_id)
if not locked['total_locked']:
    print("Files free for review!")
    lock_files(agent2_id, files)  # Lock for review
    # Review code...
    unlock_files(agent2_id, files)
```

## Troubleshooting

### "Cannot lock file"
- Check if another agent has it locked
- Use `get_locked_files()` to see status
- Contact the other agent or wait

### "Agent not found"
- Ensure agent is registered
- Check agent_id is correct
- Use `get_agents_list()` to verify

### "Too many conflicts"
- Plan work better with team
- Use smaller, focused tasks
- Communicate before locking

## Summary

**What You Learned:**
- ✅ Register multiple agents
- ✅ Coordinate file locking
- ✅ Prevent conflicts automatically
- ✅ Track all changes
- ✅ View agent activity

**Benefits:**
- **No overwrites** - Automatic conflict prevention
- **Transparency** - See who's doing what
- **Audit trail** - Complete change history
- **Team coordination** - Work together smoothly

---

**Congratulations!** You're now a multi-agent coordination expert! 🎉

**Next Steps:**
- Explore the [API Reference](../API_REFERENCE.md)
- Read about [Extending CoordMCP](../EXTENDING.md)
- Check [Troubleshooting](../TROUBLESHOOTING.md) for common issues
