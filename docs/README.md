# CoordMCP Documentation

Welcome to the CoordMCP documentation! This is your comprehensive guide to using and extending CoordMCP.

## 📚 Documentation Overview

### 🚀 Getting Started
New to CoordMCP? Start here!

| Document | Description | Time |
|----------|-------------|------|
| **[Getting Started](GETTING_STARTED.md)** | 5-minute quick start guide | 5 min |
| **[Installation](INSTALLATION.md)** | Detailed installation instructions | 15 min |
| **[Configuration](CONFIGURATION.md)** | Environment variables and settings | 10 min |

### 🔧 User Guides
Learn how to use CoordMCP effectively.

| Document | Description |
|----------|-------------|
| **[API Reference](API_REFERENCE.md)** | Complete reference for all 33 tools and 14+ resources |
| **[Data Models](DATA_MODELS.md)** | Understanding data structures and storage |
| **[Troubleshooting](TROUBLESHOOTING.md)** | Common issues and solutions |
| **[Extending](EXTENDING.md)** | How to extend CoordMCP with custom tools |

### 🤖 Agent Integrations
Setup guides for different coding agents.

| Agent | Description |
|-------|-------------|
| **[OpenCode](INTEGRATIONS/opencode.md)** | Integration with OpenCode |
| **[Cursor](INTEGRATIONS/cursor.md)** | Integration with Cursor IDE |
| **[Claude Code](INTEGRATIONS/claude-code.md)** | Integration with Claude Code |
| **[Windsurf](INTEGRATIONS/windsurf.md)** | Integration with Windsurf |

### 📝 Examples
Step-by-step walkthroughs with code.

| Example | Description | Complexity |
|---------|-------------|------------|
| **[Basic Project Setup](examples/basic-project-setup.md)** | Create your first project | ⭐ Easy |
| **[Architecture Recommendation](examples/architecture-recommendation.md)** | Get architectural guidance | ⭐⭐ Medium |
| **[Context Switching](examples/context-switching.md)** | Work on multiple tasks | ⭐⭐ Medium |
| **[Multi-Agent Workflow](examples/multi-agent-workflow.md)** | Coordinate multiple agents | ⭐⭐⭐ Advanced |

### 🛠️ Developer Documentation
For developers contributing to or extending CoordMCP.

| Document | Description |
|----------|-------------|
| **[Developer Guide](DEVELOPMENT.md)** | Complete developer guide including architecture, data models, tools, resources, and contribution guidelines |

### 📋 Project Information

- **[Changelog](../CHANGELOG.md)** - Version history and release notes
- **[Contributing](../CONTRIBUTING.md)** - How to contribute to the project
- **[Security](../SECURITY.md)** - Security policy and reporting

## 🎯 Quick Navigation

### By Use Case

**I want to...** | **Go to...**
---|---
Get started quickly | [Getting Started](GETTING_STARTED.md)
Set up with my agent | [Integrations](#-agent-integrations)
Learn the API | [API Reference](API_REFERENCE.md)
Understand the data | [Data Models](DATA_MODELS.md)
Fix a problem | [Troubleshooting](TROUBLESHOOTING.md)
Add custom functionality | [Extending](EXTENDING.md)
Understand the architecture | [Developer Guide](DEVELOPMENT.md)
Contribute code | [Contributing](../CONTRIBUTING.md) → [Developer Guide](DEVELOPMENT.md)

### By Role

**I'm a...** | **Start with...**
---|---
New user | [Getting Started](GETTING_STARTED.md)
Developer using CoordMCP | [API Reference](API_REFERENCE.md)
Agent configuration | [Integrations](#-agent-integrations)
Contributor | [Contributing](../CONTRIBUTING.md) → [Developer Guide](DEVELOPMENT.md)
System architect | [Developer Guide](DEVELOPMENT.md) → [Data Models](DATA_MODELS.md)

## 📊 Documentation Stats

- **33 Tools** documented (4 discovery, 11 memory, 13 context, 5 architecture)
- **14+ Resources** documented
- **9 Design Patterns** catalogued
- **4 Integration Guides** available
- **4 Example Walkthroughs** with code
- **Flexible Project Lookup** by ID, name, or workspace path

## 🔍 Search Tips

- Use the **API Reference** for tool syntax and parameters
- Check **Troubleshooting** for error messages
- Browse **Examples** for usage patterns
- Review **Data Models** for understanding storage
- Read **Developer Guide** for architecture and extending

## 💡 Getting Help

- 📧 **Email**: support@coordmcp.dev
- 💬 **Discord**: [Join our community](https://discord.gg/coordmcp)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

## 🚀 Quick Start

Don't want to read? Try these quick commands in your agent:

```python
# Create a project
await coordmcp_create_project(
    project_name="My Project",
    workspace_path=os.getcwd(),
    description="My first project"
)

# Register yourself
await coordmcp_register_agent(
    agent_name="MyAgent",
    agent_type="opencode",
    capabilities=["python"]
)

# Save a decision
await coordmcp_save_decision(
    project_id="proj-xxx",
    title="Use FastAPI",
    description="Async framework",
    rationale="Performance"
)
```

---

**Ready to dive in?** Start with [Getting Started](GETTING_STARTED.md) or jump to [Installation](INSTALLATION.md)!
