# MCP Resources

CoordMCP provides 14 read-only resources via the Model Context Protocol.

## Overview

Resources provide direct access to CoordMCP data without requiring tool calls. They're useful for reading information quickly.

| Category | Count | Purpose |
|----------|-------|---------|
| Project | 7 | Project information and data |
| Agent | 5 | Agent profiles and activity |
| Architecture | 2 | Design patterns |

## Project Resources (7)

### project://{project_id}

Get full project overview.

**Returns:** Project name, description, stats, and links to other resources.

**Natural Language Example:**
> "Get the project overview"

**Behind the Scenes:**
```
resource: project://proj-abc-123
```

---

### project://{project_id}/decisions

Get all decisions for a project.

**Returns:** All decisions in markdown format.

**Natural Language Example:**
> "Show me all decisions made in this project"

---

### project://{project_id}/tech-stack

Get technology stack.

**Returns:** All technologies by category.

**Natural Language Example:**
> "What technologies are we using?"

---

### project://{project_id}/architecture

Get architecture overview.

**Returns:** Modules, patterns, and file organization.

**Natural Language Example:**
> "Show me the project architecture"

---

### project://{project_id}/recent-changes

Get recent changes.

**Returns:** Recent changes with impact assessment.

**Natural Language Example:**
> "What changed recently?"

---

### project://{project_id}/modules

Get list of all modules.

**Returns:** Module names and descriptions.

---

### project://{project_id}/modules/{module_name}

Get detailed module information.

**Returns:** Files, dependencies, and responsibilities.

---

## Agent Resources (5)

### agent://{agent_id}

Get agent profile.

**Returns:** Agent name, type, capabilities, and stats.

**Natural Language Example:**
> "Tell me about this agent"

---

### agent://{agent_id}/context

Get current agent context.

**Returns:** Current project, objective, and locked files.

**Natural Language Example:**
> "What is this agent working on?"

---

### agent://{agent_id}/locked-files

Get files locked by agent.

**Returns:** List of locked files with lock details.

---

### agent://{agent_id}/session-log

Get agent session log.

**Returns:** Activity history.

---

### agent://registry

Get all registered agents.

**Returns:** List of all agents with status.

**Natural Language Example:**
> "Show me all agents"

---

## Architecture Resources (2)

### design-patterns://list

Get all available design patterns.

**Returns:** Pattern names, descriptions, and best use cases.

**Natural Language Example:**
> "What design patterns are available?"

---

### design-patterns://{pattern_name}

Get detailed pattern information.

**Returns:** Description, structure, example, and best practices.

**Available patterns:**
- `crud`
- `mvc`
- `repository`
- `service`
- `factory`
- `observer`
- `adapter`
- `strategy`
- `decorator`

---

## Resource vs Tool

| Aspect | Resource | Tool |
|--------|----------|------|
| Purpose | Read data | Perform actions |
| Example | `project://id/decisions` | `save_decision()` |
| Modifies data | No | Yes |
| Use case | Quick lookup | Make changes |

## See Also

- [API Reference](api-reference.md) - All tools
- [Data Models](data-models.md) - Data structures
