# Context Switching

Learn how to work on multiple projects and switch between tasks seamlessly.

**Difficulty:** ⭐⭐ Medium  
**Time:** 10-15 minutes

## Introduction

As a developer, you often need to work on multiple projects or switch between different tasks. CoordMCP's context switching lets you:

- Maintain separate contexts for different projects
- Track what you were working on
- Keep a history of your work sessions
- Resume work exactly where you left off
- Manually manage file locks when switching

## Scenario

You're a developer juggling three projects:
- **Project A**: Website redesign (high priority)
- **Project B**: API migration (critical)
- **Project C**: Database optimization (medium priority)

You need to switch between them without losing track of what you were doing.

## Prerequisites

- Completed [Basic Project Setup](./basic-project-setup.md)
- Understanding of file locking (optional)
- CoordMCP server running

## Step-by-Step Guide

### Step 1: Create Multiple Projects

First, let's set up three projects in different directories:

```python
import os

# Create projects in different directories
# (In real usage, these would be in different workspace folders)

# Project A: Website redesign
os.makedirs("/tmp/website-redesign", exist_ok=True)
project_a = await coordmcp_create_project(
    project_name="Website Redesign",
    workspace_path="/tmp/website-redesign",
    description="Redesign company website with modern UI and responsive design"
)
project_a_id = project_a["project_id"]
print(f"✓ Project A: Website Redesign ({project_a_id})")

# Project B: API migration
os.makedirs("/tmp/api-migration", exist_ok=True)
project_b = await coordmcp_create_project(
    project_name="API Migration",
    workspace_path="/tmp/api-migration",
    description="Migrate legacy API to FastAPI"
)
project_b_id = project_b["project_id"]
print(f"✓ Project B: API Migration ({project_b_id})")

# Project C: Database optimization
os.makedirs("/tmp/db-optimization", exist_ok=True)
project_c = await coordmcp_create_project(
    project_name="Database Optimization",
    workspace_path="/tmp/db-optimization",
    description="Optimize database queries and indexes"
)
project_c_id = project_c["project_id"]
print(f"✓ Project C: Database Optimization ({project_c_id})")
```

### Step 2: Register Yourself as an Agent

```python
# Register yourself with comprehensive capabilities
agent = await coordmcp_register_agent(
    agent_name="MultiTasker",
    agent_type="opencode",
    capabilities=["frontend", "backend", "database", "devops", "react", "fastapi"]
)
agent_id = agent["agent_id"]
print(f"✓ Agent registered: MultiTasker ({agent_id})")
print(f"  Message: {agent['message']}")
```

### Step 3: Start Working on Project A

Begin with the website redesign:

```python
# Start context on Project A
await coordmcp_start_context(
    agent_id=agent_id,
    project_id=project_a_id,
    objective="Implement new homepage design",
    task_description="Create responsive homepage with hero section, feature cards, and call-to-action",
    priority="high",
    current_file="src/pages/Home.tsx"
)

# Verify context
context = await coordmcp_get_agent_context(agent_id=agent_id)
print(f"✓ Context started on Project A")
print(f"  Project: {context['current_context']['project_id']}")
print(f"  Objective: {context['current_context']['current_objective']}")
print(f"  Priority: {context['current_context']['priority']}")
print(f"  Current file: {context['current_context']['current_file']}")
```

### Step 4: Lock Files for Project A

Prevent conflicts while working:

```python
# Lock homepage files
result = await coordmcp_lock_files(
    agent_id=agent_id,
    project_id=project_a_id,
    files=[
        "src/pages/Home.tsx",
        "src/components/Hero.tsx",
        "src/components/FeatureCards.tsx",
        "src/styles/home.css"
    ],
    reason="Implementing homepage redesign - hero section and feature cards",
    expected_duration_minutes=120
)

print(f"✓ Locked {result['count']} files")
for f in result['locked_files']:
    print(f"  • {f}")

# Check locked files
locked = await coordmcp_get_locked_files(agent_id=agent_id)
print(f"\n  Total locked: {locked['count']} files")
```

### Step 5: Save Progress on Project A

Document what you've done:

```python
# Log changes
await coordmcp_log_change(
    project_id=project_a_id,
    file_path="src/pages/Home.tsx",
    change_type="modify",
    description="Updated homepage layout with new hero section",
    agent_id=agent_id,
    architecture_impact="minor"
)

# Save a decision
await coordmcp_save_decision(
    project_id=project_a_id,
    title="Use CSS Grid for Homepage Layout",
    description="Implement homepage using CSS Grid for better responsive behavior",
    rationale="CSS Grid provides more control over 2D layouts than Flexbox, making responsive design easier",
    tags=["frontend", "css", "responsive-design"],
    author_agent=agent_id
)

print("✓ Progress saved on Project A")
```

### Step 6: Switch to Project B (Urgent!)

A critical bug needs your attention:

```python
# IMPORTANT: Unlock files from Project A first!
await coordmcp_unlock_files(
    agent_id=agent_id,
    project_id=project_a_id,
    files=["src/pages/Home.tsx", "src/components/Hero.tsx", 
           "src/components/FeatureCards.tsx", "src/styles/home.css"]
)
print("✓ Unlocked files from Project A")

# Now switch context to Project B
await coordmcp_switch_context(
    agent_id=agent_id,
    to_project_id=project_b_id,
    to_objective="Fix authentication bug",
    task_description="Resolve JWT token expiration issue causing 401 errors",
    priority="critical",
    current_file="src/api/auth.py"
)

print(f"✓ Switched to Project B")

# Verify new context
context = await coordmcp_get_agent_context(agent_id=agent_id)
print(f"  New project: {context['current_context']['project_id']}")
print(f"  New objective: {context['current_context']['current_objective']}")
print(f"  Priority: {context['current_context']['priority']}")
```

**Important:** Always unlock files when switching away from a project to allow others to work on them!

### Step 7: Lock Files for Project B

```python
# Lock API files
result = await coordmcp_lock_files(
    agent_id=agent_id,
    project_id=project_b_id,
    files=[
        "src/api/auth.py",
        "src/services/auth_service.py",
        "src/middleware/jwt.py"
    ],
    reason="Fixing JWT token expiration bug",
    expected_duration_minutes=60
)

print(f"✓ Locked {result['count']} files for Project B")
```

### Step 8: View Your Context History

See what you've been working on:

```python
# Get context history
history = await coordmcp_get_context_history(agent_id=agent_id, limit=10)

print(f"\n📜 Context History ({history['count']} entries):")
for i, entry in enumerate(history['entries'], 1):
    print(f"\n  {i}. {entry['timestamp']}")
    print(f"     Operation: {entry['operation']}")
    if entry.get('from_project'):
        print(f"     From: {entry['from_project']}")
    if entry.get('to_project'):
        print(f"     To: {entry['to_project']}")
    if entry.get('objective'):
        print(f"     Objective: {entry['objective']}")
```

**Expected Output:**
```
📜 Context History (2 entries):

  1. 2026-02-14T10:30:00
     Operation: context_started
     Objective: Implement new homepage design

  2. 2026-02-14T10:45:00
     Operation: context_switched
     From: Website Redesign
     To: API Migration
     Objective: Fix authentication bug
```

### Step 9: Switch to Project C

Now let's handle the database work:

```python
# First, unlock Project B files
await coordmcp_unlock_files(
    agent_id=agent_id,
    project_id=project_b_id,
    files=["src/api/auth.py", "src/services/auth_service.py", "src/middleware/jwt.py"]
)

# Log the fix
await coordmcp_log_change(
    project_id=project_b_id,
    file_path="src/services/auth_service.py",
    change_type="modify",
    description="Fixed JWT token expiration by adding proper refresh logic",
    agent_id=agent_id,
    architecture_impact="significant",
    code_summary="Updated token validation to check expiration with buffer time"
)

# Save decision
await coordmcp_save_decision(
    project_id=project_b_id,
    title="Add 5-Minute Buffer to JWT Validation",
    description="JWT tokens now validated with a 5-minute buffer to prevent edge-case expiration issues",
    rationale="Prevents race conditions where token expires between validation and usage",
    tags=["security", "jwt", "authentication"],
    author_agent=agent_id
)

# Switch to Project C
await coordmcp_switch_context(
    agent_id=agent_id,
    to_project_id=project_c_id,
    to_objective="Add performance indexes",
    task_description="Create indexes for frequently queried columns to improve API response times",
    priority="medium",
    current_file="migrations/add_indexes.sql"
)

print(f"✓ Switched to Project C")
context = await coordmcp_get_agent_context(agent_id=agent_id)
print(f"  New objective: {context['current_context']['current_objective']}")
```

### Step 10: View Session Log

Check your complete activity log:

```python
# Get session log
session_log = await coordmcp_get_session_log(agent_id=agent_id, limit=20)

print(f"\n📋 Session Log ({session_log['count']} entries):")
for entry in session_log['entries']:
    emoji = {
        "context_started": "🚀",
        "context_switched": "🔄",
        "context_ended": "🏁",
        "files_locked": "🔒",
        "files_unlocked": "🔓",
        "decision_saved": "📊",
        "change_logged": "📝"
    }.get(entry['event'], "📌")
    
    print(f"  {emoji} {entry['event']} at {entry['timestamp']}")
    if entry.get('details'):
        print(f"     Details: {entry['details']}")
```

### Step 11: Check Current Status

What project are you working on now?

```python
# Get current context
current = await coordmcp_get_agent_context(agent_id=agent_id)

if current.get('current_context'):
    ctx = current['current_context']
    print(f"\n🎯 Current Status:")
    print(f"   Project ID: {ctx['project_id']}")
    print(f"   Objective: {ctx['current_objective']}")
    print(f"   Priority: {ctx['priority']}")
    print(f"   Current File: {ctx.get('current_file', 'N/A')}")
    print(f"   Started At: {ctx['started_at']}")
    
    # Check locked files
    locked = await coordmcp_get_locked_files(agent_id=agent_id)
    if locked['count'] > 0:
        print(f"\n   🔒 Locked Files ({locked['count']}):")
        for f in locked['locked_files'][:5]:  # Show first 5
            print(f"      • {f['file_path']}")
else:
    print("No active context")
```

### Step 12: Switch Back to Project A

Resume the website work:

```python
# Switch back to Project A
await coordmcp_switch_context(
    agent_id=agent_id,
    to_project_id=project_a_id,
    to_objective="Complete homepage footer",
    task_description="Finish implementing footer component with social links and copyright",
    priority="high",
    current_file="src/components/Footer.tsx"
)

print(f"✓ Back on Project A")
context = await coordmcp_get_agent_context(agent_id=agent_id)
print(f"  Resumed work: {context['current_context']['current_objective']}")

# Lock new files for Project A
await coordmcp_lock_files(
    agent_id=agent_id,
    project_id=project_a_id,
    files=["src/components/Footer.tsx", "src/styles/footer.css"],
    reason="Implementing footer component",
    expected_duration_minutes=90
)
print(f"✓ Locked footer files")
```

### Step 13: List All Projects

See all your projects:

```python
# List all projects
projects = await coordmcp_list_projects()

print(f"\n📁 All Projects ({projects['total_count']}):")
for p in projects['projects']:
    # Check if this is the current project
    is_current = current.get('current_context', {}).get('project_id') == p['project_id']
    marker = "👉" if is_current else "  "
    print(f"{marker} {p['project_name']} ({p['project_id']})")
    print(f"     Workspace: {p.get('workspace_path', 'N/A')}")
    print(f"     Updated: {p.get('updated_at', 'N/A')}")
```

### Step 14: End Your Session

When you're done for the day:

```python
# Unlock all files first
await coordmcp_unlock_files(
    agent_id=agent_id,
    project_id=project_a_id,
    files=["src/components/Footer.tsx", "src/styles/footer.css"]
)

# Log final change
await coordmcp_log_change(
    project_id=project_a_id,
    file_path="src/components/Footer.tsx",
    change_type="create",
    description="Created footer component with social links",
    agent_id=agent_id,
    architecture_impact="minor"
)

# End context
await coordmcp_end_context(
    agent_id=agent_id,
    summary="Made progress on homepage redesign (hero + footer) and fixed critical JWT bug",
    outcome="success"
)

print("\n✅ Context ended - see you tomorrow!")
print("   Summary: Made progress on multiple projects")
```

## Complete Example Code

Here's the complete example:

```python
import os

# Create multiple projects in different directories
os.makedirs("/tmp/website-redesign", exist_ok=True)
project_a = await coordmcp_create_project(
    project_name="Website Redesign",
    workspace_path="/tmp/website-redesign",
    description="Website redesign project"
)

os.makedirs("/tmp/api-migration", exist_ok=True)
project_b = await coordmcp_create_project(
    project_name="API Migration",
    workspace_path="/tmp/api-migration",
    description="API migration project"
)

# Register agent
agent = await coordmcp_register_agent(
    agent_name="MultiTasker",
    agent_type="opencode",
    capabilities=["python", "react"]
)
agent_id = agent["agent_id"]

# Work on Project A
await coordmcp_start_context(
    agent_id=agent_id,
    project_id=project_a["project_id"],
    objective="Homepage design",
    priority="high"
)

await coordmcp_lock_files(
    agent_id=agent_id,
    project_id=project_a["project_id"],
    files=["src/Home.tsx"],
    reason="Working on homepage"
)

# Switch to urgent Project B
await coordmcp_unlock_files(
    agent_id=agent_id,
    project_id=project_a["project_id"],
    files=["src/Home.tsx"]
)

await coordmcp_switch_context(
    agent_id=agent_id,
    to_project_id=project_b["project_id"],
    to_objective="Fix critical bug",
    priority="critical"
)

# Check history
history = await coordmcp_get_context_history(agent_id=agent_id)
print(f"Switched contexts {history['count']} times today")

# End session
await coordmcp_end_context(agent_id=agent_id)
```

## Key Concepts Learned

1. **Context Switching** - Seamlessly move between projects while maintaining state
2. **Manual File Management** - Unlock files when switching (good practice!)
3. **History Tracking** - Full audit trail of context changes and work sessions
4. **Session Logging** - Complete activity record for productivity tracking
5. **Progress Documentation** - Save decisions and log changes at each step

## Best Practices

### ✅ DO:
- Always unlock files when switching away from a project
- Document your progress with decisions and change logs
- Use descriptive objectives and task descriptions
- Check context history to track your work
- End context at the end of your work day

### ❌ DON'T:
- Leave files locked when not actively working on them
- Switch contexts without updating your objective
- Forget to log significant changes
- Use vague task descriptions

## Common Patterns

### The "Hotfix" Pattern

```python
# Working on feature
await coordmcp_start_context(
    agent_id=aid, 
    project_id=feature_proj, 
    objective="Implement user dashboard"
)

# URGENT: Production bug!
# 1. Save progress
await coordmcp_save_decision(
    project_id=feature_proj,
    title="Dashboard Layout Decision",
    description="Use grid layout",
    rationale="Better responsive behavior"
)

# 2. Unlock current files
await coordmcp_unlock_files(agent_id=aid, project_id=feature_proj, files=["..."])

# 3. Switch to production
await coordmcp_switch_context(
    agent_id=aid,
    to_project_id=prod_proj,
    to_objective="Fix critical bug",
    priority="critical"
)

# Fix the bug...

# 4. Return to feature work
await coordmcp_switch_context(
    agent_id=aid,
    to_project_id=feature_proj,
    to_objective="Continue user dashboard"
)
```

### The "Code Review" Pattern

```python
# Finish your work
await coordmcp_save_decision(...)
await coordmcp_log_change(...)
await coordmcp_unlock_files(...)
await coordmcp_end_context(agent_id=aid)

# Switch to review someone else's work
await coordmcp_start_context(
    agent_id=aid, 
    project_id=other_proj, 
    objective="Review PR #123 - Add authentication"
)

# After review, go back to your work
await coordmcp_switch_context(
    agent_id=aid, 
    to_project_id=my_proj, 
    to_objective="Continue feature X"
)
```

## Troubleshooting

### "Cannot switch context"
```python
# Ensure you have an active context
current = await coordmcp_get_agent_context(agent_id=agent_id)
if not current.get('current_context'):
    print("No active context. Start one first with start_context()")
```

### "Files still locked after switch"
```python
# File unlock is NOT automatic - always unlock manually!
await coordmcp_unlock_files(
    agent_id=agent_id,
    project_id=old_project_id,
    files=["file1.py", "file2.py"]
)

# Check locked files
locked = await coordmcp_get_locked_files(agent_id=agent_id)
print(f"Still locked: {locked['count']} files")
```

### "Cannot find project"
```python
# Use flexible project lookup
project = await coordmcp_get_project(project_id=project_id)
# or
project = await coordmcp_get_project(project_name="My Project")
# or
project = await coordmcp_get_project(workspace_path=os.getcwd())
```

## Next Steps

Ready for more advanced coordination?

**Next Example:** [Multi-Agent Workflow](./multi-agent-workflow.md) - Coordinate multiple agents on the same project

---

**Excellent!** You can now manage multiple projects with ease. 🎉

Next: Learn about [Multi-Agent Workflows](./multi-agent-workflow.md)
