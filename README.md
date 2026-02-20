# CoordMCP - Multi-Agent Code Coordination Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-powered-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CoordMCP is a coordination server that helps multiple AI coding agents work together on the same project without conflicts.

## Why CoordMCP?

When you use AI coding assistants (OpenCode, Cursor, Claude Code, Windsurf) on a project:

- **Lost decisions** - The AI forgets what was decided in previous sessions
- **Inconsistent choices** - Different sessions make different architectural decisions  
- **No coordination** - Multiple AI agents don't know what each other is doing
- **No history** - There's no record of why certain decisions were made

**CoordMCP solves this** by giving your AI agents a shared brain that persists across sessions.

## How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│     YOU     │────▶│  AI AGENT   │────▶│  CoordMCP   │
│             │     │             │     │   Server    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                    ┌─────────────────┐
                                    │  Shared Memory  │
                                    │  • Decisions    │
                                    │  • Tech Stack   │
                                    │  • File Locks   │
                                    └─────────────────┘
```

**You just talk to your AI agent normally.** CoordMCP works automatically in the background:

- Remembers decisions across sessions
- Prevents file conflicts between agents
- Provides architecture recommendations
- Tracks all changes

## Example

**You say:**
> "Create a todo app with React and FastAPI"

**CoordMCP automatically:**
1. Discovers or creates the project
2. Registers your AI agent
3. Locks files before editing
4. Records "Use React" and "Use FastAPI" decisions
5. Tracks all created/modified files
6. Unlocks files when done

**Next session:** Your AI remembers you're using React and FastAPI.

## Quick Start

### Install

```bash
pip install coordmcp
coordmcp --version
```

### Configure Your Agent

**Option 1: Using coordmcp CLI (recommended)**

For most agents, add to your config file:

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "coordmcp",
      "args": [],
      "env": {
        "COORDMCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Option 2: Using Python module**

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp"],
      "env": {
        "COORDMCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

See [integrations](docs/user-guide/integrations/) for specific setup instructions for each agent.

### Test It

Restart your AI agent and say:

> "What CoordMCP tools are available?"

## Documentation

| Audience | Start Here |
|----------|------------|
| **End Users** | [User Guide](docs/user-guide/what-is-coordmcp.md) |
| **Developers** | [API Reference](docs/developer-guide/api-reference.md) |
| **Contributors** | [Contributor Guide](docs/contributor-guide/architecture.md) |

### User Guide

- [What is CoordMCP?](docs/user-guide/what-is-coordmcp.md) - Overview and features
- [Installation](docs/user-guide/installation.md) - Install and configure
- [How It Works](docs/user-guide/how-it-works.md) - Behind the scenes

### Integrations

- [OpenCode](docs/user-guide/integrations/opencode.md)
- [Cursor](docs/user-guide/integrations/cursor.md)
- [Claude Code](docs/user-guide/integrations/claude-code.md)
- [Windsurf](docs/user-guide/integrations/windsurf.md)
- [Antigravity](docs/user-guide/integrations/antigravity.md)

### Developer Guide

- [API Reference](docs/developer-guide/api-reference.md) - All 49 tools
- [Data Models](docs/developer-guide/data-models.md) - Data structures
- [Examples](docs/developer-guide/examples/) - Usage examples

### Contributor Guide

- [Architecture](docs/contributor-guide/architecture.md) - System design
- [Development Setup](docs/contributor-guide/development-setup.md) - Dev environment
- [Testing](docs/contributor-guide/testing.md) - Run and write tests
- [Extending](docs/contributor-guide/extending.md) - Add new features

### Reference

- [Troubleshooting](docs/reference/troubleshooting.md) - Common issues
- [Configuration](docs/reference/configuration.md) - All options

## Features

### Long-Term Memory

Your AI agent remembers decisions across sessions. If you chose React last week, it knows this week.

### Multi-Agent Coordination

Multiple AI agents can work on the same project without conflicts through file locking.

### Architecture Guidance

Design pattern recommendations without expensive LLM calls. 9 patterns available: MVC, Repository, Service, Factory, Observer, Adapter, Strategy, Decorator, CRUD.

### Task Management

Create, assign, and track tasks across agents. Support for task dependencies, priorities, and completion tracking.

### Agent Messaging

Enable communication between agents with direct messages and broadcast capabilities.

### Health Dashboard

Monitor project health with comprehensive dashboards showing task progress, agent activity, and actionable recommendations.

### Zero LLM Costs

All architectural analysis is rule-based - no external API calls needed.

## Development

```bash
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp
pip install -e ".[dev]"
python -m pytest src/tests/ -v
```

## License

MIT License - see [LICENSE](LICENSE).

## Support

- Email: support@coordmcp.dev
- Discord: [Join our community](https://discord.gg/coordmcp)
- Issues: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)
