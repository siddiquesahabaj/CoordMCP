# Onboarding Tools

Detailed documentation for CoordMCP's onboarding and workflow guidance tools.

## Overview

Onboarding tools help agents quickly understand the current state of a project and follow the correct workflow. They provide:

- **Context at Session Start**: Complete situation report when entering a project
- **Workflow Guidance**: Step-by-step instructions for common tasks
- **Validation**: Check if required workflow steps were followed
- **System Prompts**: Instructions for proper CoordMCP integration

## Tools

### get_project_onboarding_context

Get a comprehensive "situation report" when entering a project.

#### When to Use

- **Every session start**: Call this after registering your agent
- **After switching projects**: When moving to a different project
- **When resuming work**: After being away from a project

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Your agent ID |
| `project_id` | string | Yes | Project ID |

#### Returns

```json
{
  "success": true,
  "project_info": {
    "project_id": "proj-123",
    "project_name": "My App",
    "description": "A task management application",
    "workspace_path": "/home/user/projects/myapp",
    "project_type": "webapp",
    "tech_stack": [
      {"category": "backend", "technology": "FastAPI", "version": "0.104.0"},
      {"category": "frontend", "technology": "React", "version": "18.2.0"}
    ],
    "architecture": {
      "module_count": 5,
      "modules": ["auth", "api", "models", "services", "utils"]
    },
    "recommended_workflows": ["test-first"]
  },
  "agent_context": {
    "agent_id": "agent-456",
    "agent_name": "DevBot",
    "is_returning": true,
    "previous_sessions_in_project": 3,
    "last_session_in_project": "2024-01-19T15:30:00",
    "total_sessions_all_projects": 12,
    "capabilities": ["python", "javascript", "testing"]
  },
  "active_agents": [
    {
      "agent_id": "agent-789",
      "agent_name": "TestBot",
      "current_objective": "Writing integration tests"
    }
  ],
  "recent_changes": [
    {
      "change_id": "change-001",
      "file_path": "src/auth/login.py",
      "change_type": "modify",
      "description": "Added JWT validation",
      "created_at": "2024-01-20T10:00:00"
    }
  ],
  "key_decisions": [
    {
      "decision_id": "dec-001",
      "title": "Use JWT for authentication",
      "description": "JWT tokens for stateless auth...",
      "tags": ["security", "backend"]
    }
  ],
  "locked_files": [
    {
      "file_path": "src/api/routes.py",
      "locked_by": "agent-789",
      "reason": "Adding new endpoints",
      "expected_unlock_time": "2024-01-20T12:00:00"
    }
  ],
  "recommended_next_steps": [
    "Review recent changes to understand current state",
    "Note: 1 file is currently locked by another agent",
    "There are 3 pending task(s) available to work on"
  ]
}
```

#### Example Usage

```python
# After registering and discovering project
agent = await register_agent(agent_name="DevBot", agent_type="opencode")
agent_id = agent["agent_id"]

project = await discover_project(path=os.getcwd())
project_id = project["project"]["project_id"]

# Get full onboarding context
onboarding = await get_project_onboarding_context(
    agent_id=agent_id,
    project_id=project_id
)

# Check recommendations
for step in onboarding["recommended_next_steps"]:
    print(f"Next: {step}")

# Check if files are locked
if onboarding["locked_files"]:
    print("Warning: Some files are locked")
```

---

### get_workflow_guidance

Get step-by-step workflow instructions for working on a project.

#### When to Use

- **New to CoordMCP**: Learn the correct workflow
- **Starting a new type of work**: Different workflows for different tasks
- **Need reminders**: Quick reference for workflow steps

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_id` | string | No | Project ID (for project-specific workflows) |
| `workflow_name` | string | No | Specific workflow to use |

#### Available Workflows

| Workflow | Name | Description |
|----------|------|-------------|
| `default` | Standard Development Workflow | Basic workflow for any development task |
| `test-first` | Test-First Development | Write tests before implementing code |
| `feature-branch` | Feature Branch Workflow | Work on feature branches with code review |
| `review-then-commit` | Review Then Commit | Peer review before committing changes |

#### Returns

```json
{
  "success": true,
  "workflow_name": "test-first",
  "workflow_display_name": "Test-First Development",
  "description": "Write tests before implementing code",
  "phases": [
    {"step": 1, "action": "register_agent", "tool": "register_agent", "description": "Register your agent identity"},
    {"step": 2, "action": "start_context", "tool": "start_context", "description": "Start a work context for this project"},
    {"step": 3, "action": "create_task", "tool": "create_task", "description": "Create a task for the feature"},
    {"step": 4, "action": "write_test", "tool": "N/A", "description": "Write failing test first"},
    {"step": 5, "action": "implement", "tool": "N/A", "description": "Implement code to pass test"},
    {"step": 6, "action": "lock_files", "tool": "lock_files", "description": "Lock files before editing"},
    {"step": 7, "action": "log_change", "tool": "log_change", "description": "Log the change with description"},
    {"step": 8, "action": "unlock_files", "tool": "unlock_files", "description": "Unlock files after editing"},
    {"step": 9, "action": "complete_task", "tool": "update_task", "description": "Mark task as completed"},
    {"step": 10, "action": "end_context", "tool": "end_context", "description": "End work context"}
  ],
  "project_workflows_available": ["test-first", "feature-branch"],
  "is_default": false,
  "project_id": "proj-123",
  "project_name": "My App"
}
```

#### Example Usage

```python
# Get default workflow
workflow = await get_workflow_guidance()

# Get specific workflow
workflow = await get_workflow_guidance(workflow_name="test-first")

# Get project-specific workflow
workflow = await get_workflow_guidance(
    project_id="proj-123",
    workflow_name="feature-branch"
)

# Print steps
for phase in workflow["phases"]:
    print(f"Step {phase['step']}: {phase['description']}")
```

---

### validate_workflow_state

Check if you've followed the required workflow steps.

#### When to Use

- **Before ending a session**: Verify all steps completed
- **When confused**: Check what steps you might have missed
- **During work**: Get reminders about pending steps

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | string | Yes | Your agent ID |

#### Returns

```json
{
  "success": true,
  "current_state": "working",
  "workflow_progress": ["register_agent", "start_context", "lock_files"],
  "warnings": [
    "⚠️ You have 2 locked file(s) - unlock them when done"
  ],
  "completed_steps": ["register_agent", "start_context", "lock_files"],
  "missing_steps": ["make_changes", "log_change", "unlock_files", "end_context"],
  "has_active_context": true
}
```

#### Possible States

| State | Description |
|-------|-------------|
| `unregistered` | Agent not registered |
| `registered` | Registered but no active context |
| `context_started` | Context started, no files locked |
| `files_locked` | Files locked, ready to work |
| `working` | Actively working on files |
| `changes_logged` | Changes documented |
| `files_unlocked` | Files released |
| `context_ended` | Session complete |

#### Example Usage

```python
# Check workflow state
state = await validate_workflow_state(agent_id="agent-123")

# Handle warnings
if state["warnings"]:
    for warning in state["warnings"]:
        print(f"Warning: {warning}")

# Check what's missing
if state["missing_steps"]:
    print(f"Missing steps: {', '.join(state['missing_steps'])}")
```

---

### get_system_prompt

Get the complete CoordMCP system prompt.

#### When to Use

- **New agent setup**: Get full instructions for CoordMCP integration
- **Reference**: Look up workflow rules and patterns
- **Debugging**: Understand expected behavior

#### Parameters

None

#### Returns

```json
{
  "success": true,
  "system_prompt": "# CoordMCP System Prompt\n\nYou are an intelligent coding assistant...",
  "version": "1.0.0"
}
```

#### Example Usage

```python
# Get system prompt
prompt = await get_system_prompt()
print(prompt["system_prompt"])
```

## Workflow Integration

### Recommended Session Flow

```
1. discover_project() or create_project()
2. register_agent()
3. get_project_onboarding_context()  ← Onboarding tools start here
4. validate_workflow_state()         ← Check previous session state
5. get_workflow_guidance()           ← Get step-by-step guide
6. start_context()
7. lock_files()
8. [DO WORK]
9. log_change()
10. unlock_files()
11. end_context()
12. validate_workflow_state()        ← Verify all steps completed
```

### Example: Complete Session

```python
import os

# 1. Discover project
discovery = await discover_project(path=os.getcwd())
if not discovery["found"]:
    project = await create_project(
        project_name="My App",
        workspace_path=os.getcwd()
    )
    project_id = project["project_id"]
else:
    project_id = discovery["project"]["project_id"]

# 2. Register agent
agent = await register_agent(
    agent_name="DevBot",
    agent_type="opencode",
    capabilities=["python", "testing"]
)
agent_id = agent["agent_id"]

# 3. Get onboarding context
onboarding = await get_project_onboarding_context(
    agent_id=agent_id,
    project_id=project_id
)

# Check for important info
if onboarding["locked_files"]:
    print("Warning: Some files are locked")
    for lock in onboarding["locked_files"]:
        print(f"  - {lock['file_path']} locked by {lock['locked_by']}")

# 4. Get workflow guidance
workflow = await get_workflow_guidance(
    project_id=project_id,
    workflow_name="test-first"
)

# 5. Validate current state
state = await validate_workflow_state(agent_id=agent_id)
if state["warnings"]:
    for warning in state["warnings"]:
        print(f"Note: {warning}")

# 6. Start work
await start_context(
    agent_id=agent_id,
    project_id=project_id,
    objective="Add user authentication"
)

# 7. Lock files
await lock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["src/auth.py", "src/models/user.py"],
    reason="Implementing JWT authentication"
)

# 8. [DO YOUR WORK HERE]

# 9. Log changes
await log_change(
    project_id=project_id,
    file_path="src/auth.py",
    change_type="modify",
    description="Added JWT token validation",
    architecture_impact="significant"
)

# 10. Unlock files
await unlock_files(
    agent_id=agent_id,
    project_id=project_id,
    files=["src/auth.py", "src/models/user.py"]
)

# 11. End context
await end_context(agent_id=agent_id)

# 12. Validate workflow completion
final_state = await validate_workflow_state(agent_id=agent_id)
print(f"Session complete. State: {final_state['current_state']}")
```

## See Also

- [API Reference](api-reference.md) - All 52 tools
- [System Prompt](../../SYSTEM_PROMPT.md) - Full system instructions
- [How It Works](../user-guide/how-it-works.md) - Behind the scenes
