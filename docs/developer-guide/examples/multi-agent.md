# Multi-Agent Coordination Example

How multiple AI agents coordinate using CoordMCP.

## Scenario: Two Agents on One Project

### Setup

- **Agent A (FrontendDev):** Working on React components
- **Agent B (BackendDev):** Working on API endpoints
- **Project:** E-commerce platform

---

## What Happens

### Agent A Starts

**You say to Agent A:**
> "Build the product listing page"

**Behind the Scenes:**
```
discover_project(path=os.getcwd())           # Find project
register_agent("FrontendDev", "opencode")    # Register
start_context(agent_id, project_id, 
    objective="Build product listing page")  # Start tracking
lock_files(agent_id, project_id,
    files=["src/components/ProductList.jsx",
           "src/styles/products.css"],
    reason="Building product listing UI")    # Lock files
```

**Result:** Agent A is now working, files are locked.

---

### Agent B Checks In

**You say to Agent B:**
> "What's Agent A working on?"

**Behind the Scenes:**
```
get_active_agents(project_id="proj-123")
get_locked_files(project_id="proj-123")
```

**Agent B sees:**
```
Active Agent: FrontendDev
  Objective: Build product listing page
  Locked Files:
    - src/components/ProductList.jsx
    - src/styles/products.css
```

**Agent B knows:** Can't edit those files, should work elsewhere.

---

### Agent B Starts Different Work

**You say to Agent B:**
> "Build the product API endpoints instead"

**Behind the Scenes:**
```
register_agent("BackendDev", "opencode")
start_context(agent_id, project_id,
    objective="Build product API endpoints")
lock_files(agent_id, project_id,
    files=["src/api/products.py",
           "src/models/product.py"],
    reason="Building product API")           # Different files!
```

**Result:** Both agents working on different files, no conflicts.

---

### Conflict Prevention

**If Agent B tried to lock ProductList.jsx:**

```
lock_files(
    files=["src/components/ProductList.jsx", ...]
)

# Returns:
{
    "success": false,
    "error": "Files already locked",
    "locked_by": "FrontendDev",
    "locked_at": "2024-01-20T14:00:00"
}
```

**Agent B would be warned and could:**
- Wait for Agent A to finish
- Work on different files
- Coordinate with Agent A

---

### Agent A Finishes

**You say to Agent A:**
> "I'm done with the product listing"

**Behind the Scenes:**
```
save_decision(project_id,
    title="Use grid layout for products",
    description="CSS Grid for responsive product cards",
    rationale="Better mobile support, simpler code")

log_change(project_id,
    file_path="src/components/ProductList.jsx",
    change_type="create",
    description="Created product listing component")

unlock_files(agent_id, project_id,
    files=["src/components/ProductList.jsx",
           "src/styles/products.css"])

end_context(agent_id)
```

**Result:** Files unlocked, Agent B can now access them if needed.

---

### Agent B Can Continue

Now Agent B can access the product listing files if needed:

```
lock_files(agent_id, project_id,
    files=["src/components/ProductList.jsx"],
    reason="Connecting API to frontend")

# Success! Files are now available.
```

---

## Coordination Flow Summary

```
Time    Agent A                  Agent B
────────────────────────────────────────────
T1      Lock ProductList.jsx     
T2      Working on UI...         
T3                               Check locked files
T4                               See ProductList locked
T5                               Lock products.py instead
T6      Working on UI...         Working on API...
T7      Unlock ProductList.jsx   
T8      Done                     Can now access ProductList
```

## Key Coordination Features

### Visibility

Each agent can see:
- Who else is working
- What they're working on
- Which files are locked

### Prevention

- Can't lock already-locked files
- Clear error messages with lock info
- Automatic timeout (default: 24 hours)

### Communication

Decisions are shared:
- Agent A's decisions visible to Agent B
- Tech stack updates shared
- Change history available to all

## Best Practices

1. **Check before starting:** Look at active agents and locked files
2. **Lock before editing:** Always lock files you're modifying
3. **Unlock promptly:** Release locks when done
4. **Document decisions:** Save decisions so others understand your choices
5. **Log changes:** Keep history for coordination

## See Also

- [Basic Workflow](basic-workflow.md)
- [Architecture Recommendation](architecture-recommendation.md)
- [API Reference](../api-reference.md)
