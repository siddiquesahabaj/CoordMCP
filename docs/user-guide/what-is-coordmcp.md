# What is CoordMCP?

CoordMCP is a coordination server that helps multiple AI coding agents work together on the same project without conflicts.

## The Problem

When you use AI coding assistants like OpenCode, Cursor, or Claude Code on a project, you might run into these issues:

- **Lost decisions** - The AI forgets what was decided in previous sessions
- **Inconsistent choices** - Different sessions make different architectural decisions
- **No coordination** - If you use multiple AI agents, they don't know what each other is doing
- **No history** - There's no record of why certain decisions were made

## The Solution

CoordMCP gives your AI agents a shared brain. When you ask your AI to do something, CoordMCP automatically:

- **Remembers** - Stores all decisions, tech choices, and rationale
- **Coordinates** - Prevents multiple agents from editing the same files
- **Tracks** - Logs all changes and their impact on the architecture
- **Guides** - Provides architectural recommendations based on your project

## How You Use It

You don't. Your AI agent does.

Just talk to your AI agent normally. CoordMCP works automatically in the background.

### Example

**You say:**
> "Create a todo app with React and FastAPI"

**CoordMCP automatically:**
1. Discovers or creates your project
2. Registers the AI agent
3. Locks files before editing
4. Records "Use React" and "Use FastAPI" decisions
5. Tracks all created/modified files
6. Unlocks files when done

**Result:** Your todo app is built, and CoordMCP remembers everything for future sessions.

## Key Features

### Long-Term Memory

Your AI agent remembers decisions across sessions. If you asked for React last week, it remembers this week.

**Example scenario:**
```
Session 1: "Use PostgreSQL for the database"
Session 2 (new session): AI knows you chose PostgreSQL
Session 3: AI suggests PostgreSQL-compatible patterns
```

### Multi-Agent Coordination

Multiple AI agents can work on the same project without conflicts.

**Example scenario:**
```
Agent A: Working on src/auth.py (file locked)
Agent B: Tries to edit src/auth.py → Gets warning
Agent B: Works on src/api.py instead
Result: No conflicts, clean coordination
```

### Architecture Guidance

CoordMCP provides design pattern recommendations without expensive LLM calls.

**Example scenario:**
```
You: "Add user authentication"
CoordMCP: Recommends Repository pattern
         Suggests file structure
         Provides implementation steps
```

### Change Tracking

Every code change is logged with context and impact assessment.

**Example scenario:**
```
Change: src/auth.py created
Impact: Significant (new authentication layer)
Reason: Implementing JWT authentication
Related to: Decision "Use JWT for auth"
```

## What You Need To Do

1. **Install CoordMCP** - One-time setup
2. **Configure your AI agent** - Add CoordMCP to your agent's config
3. **Just code normally** - CoordMCP handles the rest

See [Installation](installation.md) to get started.

## Behind the Scenes

Curious about what's happening? See [How It Works](how-it-works.md).

## Next Steps

- [Install CoordMCP](installation.md)
- [Configure your AI agent](integrations/)
- [Understand how it works](how-it-works.md)
