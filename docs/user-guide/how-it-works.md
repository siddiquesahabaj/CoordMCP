# How It Works

Understand what happens when you use CoordMCP with your AI agent.

## The Big Picture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│     YOU     │────▶│  AI AGENT   │────▶│  CoordMCP   │
│             │     │             │     │   Server    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │    DATA     │
                                        │  ~/.coordmcp│
                                        └─────────────┘
```

1. **You** talk to your AI agent normally
2. **AI Agent** calls CoordMCP tools automatically
3. **CoordMCP** stores and retrieves data
4. **Data** persists across sessions

## What Happens When You Ask for Something

### Example: "Create a todo app"

When you say this to your AI agent, here's what happens:

#### Step 1: Project Discovery

**Your AI agent checks:** Is there already a CoordMCP project in this directory?

> Behind the scenes: `discover_project` tool is called

- If found: Uses existing project
- If not found: Creates a new project

#### Step 2: Agent Registration

**Your AI agent identifies itself:** "I'm working on this project"

> Behind the scenes: `register_agent` tool is called

- Gets a unique agent ID
- Can reconnect to same ID in future sessions

#### Step 3: Context Setup

**Your AI agent starts tracking:** "I'm building a todo app"

> Behind the scenes: `start_context` tool is called

- Records current objective
- Sets priority level
- Tracks start time

#### Step 4: File Coordination

**Before editing any file:** "I need to lock these files"

> Behind the scenes: `lock_files` tool is called

- Prevents other agents from editing same files
- Records reason for the lock
- Other agents can see who's working on what

#### Step 5: Decision Recording

**When making choices:** "I'll use React for the frontend"

> Behind the scenes: `save_decision` tool is called

- Stores the decision with rationale
- Links to related files
- Tags for easy searching

#### Step 6: Tech Stack Update

**When adding technologies:** "Adding React 18.2.0"

> Behind the scenes: `update_tech_stack` tool is called

- Records frontend: React 18.2.0
- Links to the decision
- Future sessions know what's being used

#### Step 7: Change Logging

**After creating files:** "Created App.jsx"

> Behind the scenes: `log_change` tool is called

- Records what was created/modified
- Assesses architecture impact
- Links to related decision

#### Step 8: Cleanup

**When done:** "Unlock files and finish"

> Behind the scenes: `unlock_files` and `end_context` tools are called

- Releases file locks
- Records completion summary
- Updates session history

## The Data That's Stored

### Project Memory

```
~/.coordmcp/data/memory/{project-id}/
├── project_info.json    # Project name, description, path
├── decisions.json       # All architectural decisions
├── tech_stack.json      # Technologies used
├── changes.json         # All code changes
└── file_metadata.json   # File information
```

### Agent Context

```
~/.coordmcp/data/agents/{agent-id}/
├── context.json         # Current work context
├── locked_files.json    # Files this agent has locked
└── session_log.json     # Activity history
```

### Global Registry

```
~/.coordmcp/data/global/
├── agent_registry.json  # All known agents
└── project_registry.json # All projects
```

## MCP Protocol Basics

CoordMCP uses the Model Context Protocol (MCP) to communicate with AI agents.

### What is MCP?

MCP is a standard protocol that lets AI agents interact with external tools and resources. Think of it as a standardized way for AI agents to:

- Call tools (functions)
- Read resources (data)
- Get prompts (instructions)

### Why MCP?

- **Standard** - Works with multiple AI agents (OpenCode, Cursor, Claude Code, etc.)
- **Secure** - Tools run locally, no external API calls
- **Extensible** - Easy to add new tools

### Tools vs Resources

| Type | Purpose | Example |
|------|---------|---------|
| **Tools** | Actions the AI can take | `save_decision`, `lock_files` |
| **Resources** | Data the AI can read | `project://proj-123/decisions` |

## Session Persistence

One of CoordMCP's key features is session persistence.

### How It Works

When your AI agent registers with the same name:

```
Session 1:
  Agent registers as "DevAgent"
  Gets agent_id: agent-abc-123
  
Session 2 (new session):
  Agent registers as "DevAgent"
  Gets SAME agent_id: agent-abc-123
  Previous context restored
```

### What Persists

- Agent identity and ID
- Context history
- Session logs
- Locked files (until timeout)

### What Doesn't Persist

- Active context (ended when session ends)
- File locks (expire after timeout, default 24 hours)

## Multi-Agent Coordination

When multiple AI agents work on the same project:

### File Locking

```
Agent A: lock_files(["src/auth.py"])
  ✓ Success: Files locked

Agent B: lock_files(["src/auth.py"])
  ✗ Error: Files locked by Agent A
  → Must wait or coordinate
```

### Visibility

Each agent can see:
- Who else is working on the project
- What files are locked
- What objectives others are working on

### Coordination Flow

```
1. Agent A starts working, locks src/auth.py
2. Agent B checks locked files, sees src/auth.py is locked
3. Agent B works on src/api.py instead
4. Agent A finishes, unlocks src/auth.py
5. Agent B can now work on src/auth.py if needed
```

## Architecture Guidance

CoordMCP provides design recommendations using rule-based analysis (no LLM calls needed).

### Available Patterns

| Pattern | Best For |
|---------|----------|
| CRUD | Simple create/read/update/delete operations |
| MVC | Web applications with clear separation |
| Repository | Data access abstraction |
| Service | Business logic layer |
| Factory | Complex object creation |
| Observer | Event-driven systems |
| Adapter | Interface compatibility |
| Strategy | Interchangeable algorithms |
| Decorator | Extending functionality |

### How Recommendations Work

1. You describe the feature
2. CoordMCP analyzes your project structure
3. Recommends appropriate patterns
4. Suggests file structure
5. Provides implementation steps

## Next Steps

- [Configure your AI agent](integrations/)
- [API Reference](../developer-guide/api-reference.md) - See all available tools
- [Troubleshooting](../reference/troubleshooting.md) - Common issues
