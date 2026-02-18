# Basic Workflow Example

A complete example showing natural language usage and what happens behind the scenes.

## Scenario: Building a Todo App

### You Say

> "Create a todo app with React frontend and FastAPI backend"

### What Happens Automatically

#### Step 1: Project Discovery

CoordMCP checks if a project exists in your current directory.

**Behind the Scenes:**
```
discover_project(path=os.getcwd())
```

**Result:**
- If found: Uses existing project
- If not found: Creates new project

---

#### Step 2: Agent Registration

Your AI agent registers itself with CoordMCP.

**Behind the Scenes:**
```
register_agent(
    agent_name="OpenCodeDev",
    agent_type="opencode",
    capabilities=["javascript", "python"]
)
```

**Result:** Agent gets unique ID (same ID on reconnection)

---

#### Step 3: Context Start

Agent starts tracking the current task.

**Behind the Scenes:**
```
start_context(
    agent_id="agent-123",
    project_id="proj-456",
    objective="Create todo app with React and FastAPI",
    priority="high"
)
```

**Result:** Task is tracked for this session

---

#### Step 4: Architecture Recommendation

CoordMCP suggests appropriate patterns.

**Behind the Scenes:**
```
get_architecture_recommendation(
    project_id="proj-456",
    feature_description="Todo app with React frontend and FastAPI backend"
)
```

**Result:**
```json
{
  "recommended_pattern": {
    "pattern": "MVC",
    "confidence": 90
  },
  "file_structure": {
    "new_files": [
      "frontend/src/components/TodoList.jsx",
      "backend/api/routes.py",
      "backend/models/todo.py"
    ]
  }
}
```

---

#### Step 5: File Locking

Before editing, files are locked to prevent conflicts.

**Behind the Scenes:**
```
lock_files(
    agent_id="agent-123",
    project_id="proj-456",
    files=[
        "frontend/src/App.jsx",
        "backend/main.py"
    ],
    reason="Creating todo app"
)
```

**Result:** Other agents see these files are in use

---

#### Step 6: Technology Decisions

Framework choices are recorded.

**Behind the Scenes:**
```
update_tech_stack(
    project_id="proj-456",
    category="frontend",
    technology="React",
    version="18.2.0",
    rationale="Component-based, large ecosystem"
)

update_tech_stack(
    project_id="proj-456",
    category="backend",
    technology="FastAPI",
    version="0.104.0",
    rationale="Async, type hints, automatic docs"
)
```

**Result:** Tech stack is tracked for future reference

---

#### Step 7: Decision Recording

Major decisions are saved with rationale.

**Behind the Scenes:**
```
save_decision(
    project_id="proj-456",
    title="Use separate frontend and backend",
    description="React SPA with FastAPI REST API",
    rationale="Clear separation, scalable, independent deployment",
    tags=["architecture", "frontend", "backend"]
)
```

**Result:** Decision remembered across sessions

---

#### Step 8: Change Logging

All file changes are tracked.

**Behind the Scenes:**
```
log_change(
    project_id="proj-456",
    file_path="frontend/src/App.jsx",
    change_type="create",
    description="Created main React app component",
    architecture_impact="significant"
)

log_change(
    project_id="proj-456",
    file_path="backend/main.py",
    change_type="create",
    description="Created FastAPI application with todo routes",
    architecture_impact="significant"
)
```

**Result:** Complete change history

---

#### Step 9: Cleanup

Files are unlocked and context is ended.

**Behind the Scenes:**
```
unlock_files(
    agent_id="agent-123",
    project_id="proj-456",
    files=["frontend/src/App.jsx", "backend/main.py"]
)

end_context(agent_id="agent-123")
```

**Result:** Clean state for next session

---

## Summary

| What You Did | What CoordMCP Did |
|--------------|-------------------|
| Said "Create a todo app" | Discovered/created project |
| Nothing | Registered agent |
| Nothing | Started tracking context |
| Nothing | Got architecture recommendation |
| Nothing | Locked files automatically |
| Nothing | Recorded tech stack |
| Nothing | Saved decisions |
| Nothing | Logged all changes |
| Nothing | Cleaned up automatically |

## Next Session

When you return and say:

> "Continue working on the todo app"

CoordMCP:
1. Reconnects with same agent ID (uses same agent name)
2. Loads previous context and decisions
3. Knows you're using React and FastAPI
4. Can continue where you left off

## See Also

- [Multi-Agent Coordination](multi-agent.md)
- [Architecture Recommendation](architecture-recommendation.md)
