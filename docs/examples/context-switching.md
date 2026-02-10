# Context Switching

Learn how to work on multiple projects and switch between tasks seamlessly.

**Difficulty:** ⭐⭐ Medium  
**Time:** 10-15 minutes

## Introduction

As a developer, you often need to work on multiple projects or switch between different tasks. CoordMCP's context switching lets you:

- Maintain separate contexts for different projects
- Automatically manage file locks when switching
- Keep a history of your work sessions
- Resume work exactly where you left off

## Scenario

You're a developer juggling three projects:
- **Project A**: Website redesign (high priority)
- **Project B**: API migration (critical)
- **Project C**: Database optimization (medium priority)

You need to switch between them without losing track of what you were doing.

## Prerequisites

- Completed [Basic Project Setup](./basic-project-setup.md)
- Understanding of file locking (optional)

## Step-by-Step Guide

### Step 1: Create Multiple Projects

First, let's set up the three projects:

```python
# Project A: Website redesign
project_a = await create_project(
    project_name="Website Redesign",
    description="Redesign company website with modern UI"
)
project_a_id = project_a["project_id"]
print(f"✓ Project A: Website Redesign ({project_a_id})")

# Project B: API migration
project_b = await create_project(
    project_name="API Migration",
    description="Migrate legacy API to FastAPI"
)
project_b_id = project_b["project_id"]
print(f"✓ Project B: API Migration ({project_b_id})")

# Project C: Database optimization
project_c = await create_project(
    project_name="Database Optimization",
    description="Optimize database queries and indexes"
)
project_c_id = project_c["project_id"]
print(f"✓ Project C: Database Optimization ({project_c_id})")
```

### Step 2: Register Yourself as an Agent

```python
# Register yourself
agent = await register_agent(
    agent_name="MultiTasker",
    agent_type="opencode",
    capabilities=["frontend", "backend", "database", "devops"]
)
agent_id = agent["agent_id"]
print(f"✓ Agent registered: MultiTasker ({agent_id})")
```

### Step 3: Start Working on Project A

Begin with the website redesign:

```python
# Start context on Project A
context_a = await start_context(
    agent_id=agent_id,
    project_id=project_a_id,
    objective="Implement new homepage design",
    task_description="Create responsive homepage with hero section",
    priority="high",
    current_file="src/pages/Home.tsx"
)

print(f"✓ Context started: {context_a['objective']}")
print(f"  Current file: {context_a.get('current_file', 'N/A')}")
```

### Step 4: Lock Files for Project A

Prevent conflicts while working:

```python
# Lock homepage files
result = await lock_files(
    agent_id=agent_id,
    project_id=project_a_id,
    files=[
        "src/pages/Home.tsx",
        "src/components/Hero.tsx",
        "src/styles/home.css"
    ],
    reason="Implementing homepage redesign"
)

print(f"✓ Locked {len(result['locked_files'])} files")
```

### Step 5: Switch to Project B (Urgent!)

A critical bug needs your attention:

```python
# Switch context to Project B
# Note: This automatically unlocks files from Project A
context_b = await switch_context(
    agent_id=agent_id,
    to_project_id=project_b_id,
    to_objective="Fix authentication bug",
    task_description="Resolve JWT token expiration issue",
    priority="critical"
)

print(f"✓ Switched to Project B")
print(f"  New objective: {context_b['objective']}")
print(f"  Previous files automatically unlocked!")
```

**Key Point:** When you switch context, CoordMCP automatically unlocks files from the previous project!

### Step 6: Lock Files for Project B

```python
# Lock API files
result = await lock_files(
    agent_id=agent_id,
    project_id=project_b_id,
    files=[
        "src/api/auth.py",
        "src/services/auth_service.py"
    ],
    reason="Fixing authentication bug"
)

print(f"✓ Locked {len(result['locked_files'])} files for Project B")
```

### Step 7: View Your Context History

See what you've been working on:

```python
# Get context history
history = await get_context_history(agent_id=agent_id, limit=10)

print(f"\nContext history ({len(history['entries'])} entries):")
for i, entry in enumerate(history['entries'], 1):
    print(f"  {i}. {entry['timestamp']}")
    print(f"     {entry['operation']}: {entry.get('file', 'N/A')}")
```

**Expected Output:**
```
Context history (2 entries):
  1. 2026-02-10T10:30:00Z
     context_started: context session
  2. 2026-02-10T10:45:00Z
     context_switched: Project A -> Project B
```

### Step 8: Switch to Project C

Now let's handle the database work:

```python
# Switch to Project C
context_c = await switch_context(
    agent_id=agent_id,
    to_project_id=project_c_id,
    to_objective="Add performance indexes",
    task_description="Create indexes for frequently queried columns",
    priority="medium"
)

print(f"✓ Switched to Project C")
print(f"  New objective: {context_c['objective']}")
```

### Step 9: View Session Log

Check your complete activity log:

```python
# Get session log
session_log = await get_session_log(agent_id=agent_id, limit=20)

print(f"\nSession log ({len(session_log['entries'])} entries):")
for entry in session_log['entries']:
    emoji = {
        "context_started": "🚀",
        "context_switched": "🔄",
        "files_locked": "🔒",
        "files_unlocked": "🔓"
    }.get(entry['event'], "📌")
    
    print(f"  {emoji} {entry['event']} at {entry['timestamp']}")
```

### Step 10: Check Current Status

What project are you working on now?

```python
# Get current context
current = await get_agent_context(agent_id=agent_id)

if current.get('project_id'):
    print(f"\nCurrent project: {current['project_id']}")
    print(f"Current objective: {current.get('objective', 'N/A')}")
    print(f"Current file: {current.get('current_file', 'N/A')}")
else:
    print("No active context")
```

### Step 11: Switch Back to Project A

Resume the website work:

```python
# Switch back to Project A
context_a2 = await switch_context(
    agent_id=agent_id,
    to_project_id=project_a_id,
    to_objective="Complete homepage footer",
    task_description="Finish implementing footer component",
    priority="high"
)

print(f"✓ Back on Project A")
print(f"  Resumed work: {context_a2['objective']}")
```

### Step 12: End Your Session

When you're done for the day:

```python
# End context
await end_context(agent_id=agent_id)
print("✓ Context ended - see you tomorrow!")
```

## Complete Example Code

```python
# Create multiple projects
project_a = await create_project(name="Website", description="Website redesign")
project_b = await create_project(name="API", description="API migration")
project_c = await create_project(name="Database", description="DB optimization")

# Register agent
agent = await register_agent(name="Dev", agent_type="opencode", capabilities=["python"])

# Work on Project A
await start_context(
    agent_id=agent["agent_id"],
    project_id=project_a["project_id"],
    objective="Homepage design",
    priority="high"
)

await lock_files(
    agent_id=agent["agent_id"],
    project_id=project_a["project_id"],
    files=["src/Home.tsx"]
)

# Switch to urgent Project B
await switch_context(
    agent_id=agent["agent_id"],
    to_project_id=project_b["project_id"],
    to_objective="Fix critical bug",
    priority="critical"
)
# Note: Home.tsx automatically unlocked!

# Check history
history = await get_context_history(agent_id=agent["agent_id"])
print(f"Switched contexts {len(history['entries'])} times today")

# End session
await end_context(agent_id=agent["agent_id"])
```

## Expected Output

```
✓ Project A: Website Redesign (proj-abc-123)
✓ Project B: API Migration (proj-def-456)
✓ Project C: Database Optimization (proj-ghi-789)
✓ Agent registered: MultiTasker (agent-xyz-789)
✓ Context started: Implement new homepage design
  Current file: src/pages/Home.tsx
✓ Locked 3 files

✓ Switched to Project B
  New objective: Fix authentication bug
  Previous files automatically unlocked!

✓ Locked 2 files for Project B

Context history (2 entries):
  1. 2026-02-10T10:30:00Z
     context_started: context session
  2. 2026-02-10T10:45:00Z
     context_switched: Project A -> Project B

✓ Switched to Project C
  New objective: Add performance indexes

Session log (5 entries):
  🚀 context_started at 2026-02-10T10:30:00Z
  🔒 files_locked at 2026-02-10T10:32:00Z
  🔄 context_switched at 2026-02-10T10:45:00Z
  🔒 files_locked at 2026-02-10T10:47:00Z
  🔄 context_switched at 2026-02-10T11:00:00Z

Current project: proj-ghi-789
Current objective: Add performance indexes

✓ Back on Project A
  Resumed work: Complete homepage footer

✓ Context ended - see you tomorrow!
```

## Key Concepts Learned

1. **Context Switching** - Seamlessly move between projects
2. **Automatic Unlock** - Files unlock when you switch away
3. **History Tracking** - Full audit trail of context changes
4. **Session Logging** - Complete activity record

## Benefits

- ✅ **No lost work** - Resume exactly where you left off
- ✅ **No conflicts** - Automatic file management
- ✅ **Full transparency** - See your work history
- ✅ **Multi-project** - Juggle multiple initiatives

## Common Patterns

### The "Hotfix" Pattern

```python
# Working on feature
await start_context(agent_id=aid, project_id=feature_proj, objective="Implement X")

# URGENT: Production bug!
await switch_context(
    agent_id=aid,
    to_project_id=prod_proj,
    to_objective="Fix critical bug",
    priority="critical"
)
# Fix the bug...

# Return to feature work
await switch_context(
    agent_id=aid,
    to_project_id=feature_proj,
    to_objective="Continue implementing X"
)
```

### The "Code Review" Pattern

```python
# Finish your work
await end_context(agent_id=aid)

# Switch to review someone else's work
await start_context(agent_id=aid, project_id=other_proj, objective="Review PR #123")

# After review, go back to your work
await switch_context(agent_id=aid, to_project_id=my_proj, to_objective="Continue feature")
```

## Troubleshooting

### "Cannot switch context"
- Ensure you have an active context
- Check agent_id is correct
- Verify project exists

### "Files still locked after switch"
- File unlock is automatic, but may have a delay
- Manually unlock if needed: `unlock_files(...)`
- Check with: `get_locked_files(project_id=...)`

## Next Steps

Ready for more advanced coordination?

**Next Example:** [Multi-Agent Workflow](./multi-agent-workflow.md) - Coordinate multiple agents on the same project

---

**Excellent!** You can now manage multiple projects with ease. 🎉

Next: Learn about [Multi-Agent Workflows](./multi-agent-workflow.md)
