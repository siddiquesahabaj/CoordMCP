# CoordMCP - Multi-Agent Code Coordination Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-powered-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://github.com/yourusername/coordmcp/releases)

**CoordMCP** is a powerful [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that enables intelligent coordination between multiple AI coding agents. It provides shared long-term memory, context management, file locking, and architectural guidance - all without requiring additional LLM API calls.

## 🌟 What is CoordMCP?

CoordMCP solves the multi-agent coordination problem by acting as a central hub where AI agents can:

- **Share project memory** across sessions and agents
- **Prevent file conflicts** through intelligent locking
- **Track technical decisions** with rationale and context
- **Maintain project context** across multiple work sessions
- **Get architecture recommendations** using rule-based analysis
- **Coordinate work** between multiple agents simultaneously

### Why CoordMCP?

When multiple AI agents (OpenCode, Cursor, Claude Code, etc.) work on the same project, they often:
- ❌ Overwrite each other's changes
- ❌ Forget decisions made in previous sessions
- ❌ Lack visibility into what other agents are doing
- ❌ Make inconsistent architectural choices

**CoordMCP solves all of these problems** with a unified coordination layer that persists project state and enables seamless multi-agent collaboration.

## ✨ Key Features

### 🧠 Long-Term Memory
- Store and retrieve **architectural decisions** with full context
- Track **technology stack** across the entire project
- Maintain **change history** with impact assessment
- Query **project metadata** and dependencies

### 🤖 Multi-Agent Coordination
- **Agent registration** with capabilities and session tracking
- **Context switching** between projects and tasks
- **File locking** to prevent edit conflicts
- **Activity monitoring** to see what other agents are doing

### 🏗️ Architecture Guidance
- **Pattern library** with 9+ design patterns
- **Rule-based recommendations** (no LLM costs)
- **Code structure validation**
- **Dependency analysis**

### 📝 Comprehensive Logging
- **Change tracking** with architecture impact
- **Decision history** with rationale
- **Session logs** for debugging
- **File operation history**

### ⚡ Zero LLM Costs
All architectural recommendations and analysis use **rule-based logic** - no expensive LLM API calls required!

## 🚀 Quick Start Guide

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

#### Option 1: Install from PyPI (Recommended)

```bash
# Install the latest stable version
pip install coordmcp

# Verify installation
coordmcp --version
```

#### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## 🔧 MCP Configuration

CoordMCP is an MCP (Model Context Protocol) server that integrates with AI coding agents. Here's how to configure it for different agents:

### OpenCode Configuration

Create an `opencode.jsonc` file in your project root:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "name": "CoordMCP Configuration",
  "description": "Configuration for using CoordMCP with OpenCode",
  
  "mcp": {
    "coordmcp": {
      "type": "local",
      "command": ["python", "-m", "coordmcp"],
      "enabled": true,
      "environment": {
        "COORDMCP_DATA_DIR": "${workspaceFolder}/.coordmcp/data",
        "COORDMCP_LOG_LEVEL": "INFO"
      }
    }
  },
  
  "tools": {
    "coordmcp_*": true
  },
  
  "agent": {
    "default": {
      "system": [
        "You are an intelligent coding assistant integrated with CoordMCP.",
        "",
        "=== CRITICAL WORKFLOW ===",
        "For EVERY project, you MUST follow this sequence:",
        "",
        "1. Discover or Create Project:",
        "   - Try: await coordmcp_discover_project(path=os.getcwd())",
        "   - If not found: await coordmcp_create_project(name, workspace_path=os.getcwd(), description)",
        "",
        "2. Register as Agent:",
        "   - await coordmcp_register_agent(name='YourName', type='opencode', capabilities=['python', 'react'])",
        "",
        "3. Start Context:",
        "   - await coordmcp_start_context(agent_id, project_id, objective='Your objective')",
        "",
        "4. Work with Coordination:",
        "   - Check active agents: await coordmcp_get_active_agents(project_id)",
        "   - Check locked files: await coordmcp_get_locked_files(project_id)",
        "   - Lock files before editing: await coordmcp_lock_files(agent_id, project_id, files=['src/file.py'])",
        "   - Record decisions: await coordmcp_save_decision(project_id, title, description, rationale)",
        "   - Update tech stack: await coordmcp_update_tech_stack(project_id, category, technology)",
        "   - Log changes: await coordmcp_log_change(project_id, file_path, change_type, description)",
        "   - Unlock files when done: await coordmcp_unlock_files(agent_id, project_id, files)",
        "",
        "5. End Session:",
        "   - await coordmcp_end_context(agent_id, summary='What you completed')",
        "",
        "Always use workspace_path=os.getcwd() for the current project directory."
      ]
    }
  }
}
```

### Claude Code Configuration

For Claude Code, add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "python",
      "args": ["-m", "coordmcp"],
      "env": {
        "COORDMCP_DATA_DIR": "~/.coordmcp/data",
        "COORDMCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Config file locations:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%AppData%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

### Cursor Configuration

Add to your `.cursorrules` or Cursor settings:

```
[CoordMCP Integration]

You are integrated with CoordMCP for multi-agent coordination.

WORKFLOW:
1. Discover project: await coordmcp_discover_project(path=os.getcwd())
2. Register agent: await coordmcp_register_agent(name='Cursor', type='cursor', capabilities=[])
3. Start context: await coordmcp_start_context(agent_id, project_id, objective)
4. Lock files before editing: await coordmcp_lock_files(agent_id, project_id, files)
5. Record decisions and log changes
6. Unlock files when done: await coordmcp_unlock_files(agent_id, project_id, files)
7. End context: await coordmcp_end_context(agent_id, summary)
```

## 🏃 Getting Started

### Step 1: Start the CoordMCP Server

```bash
# Start the server
python -m coordmcp

# Or using the command
coordmcp

# Check version
coordmcp --version
```

The server will start and listen for MCP connections.

### Step 2: Configure Your Agent

Follow the MCP configuration instructions above for your specific agent (OpenCode, Claude Code, Cursor, etc.).

### Step 3: Start Working

Once configured, your agent will automatically use CoordMCP for:

- **Project discovery** in the current directory
- **Agent registration** with persistent identity
- **File locking** before modifications
- **Decision recording** for technical choices
- **Change logging** for audit trails

### Example Workflow

Here's what happens when you say **"Create a todo app"**:

```
You: Create a todo app

Agent automatically:
→ Discovers/creates project in current directory
→ Registers as agent with capabilities
→ Starts context: "Create todo app"
→ Checks for locked files
→ Locks files: index.html, app.js, styles.css
→ Gets architecture recommendation (if needed)
→ Implements the app
→ Records decision: "Use vanilla JS"
→ Logs changes: Created index.html, app.js, styles.css
→ Updates tech stack: HTML, CSS, JavaScript
→ Unlocks files
→ Ends context
```

All of this happens automatically - you just code naturally!

## 📚 Available Tools

CoordMCP provides **35+ tools** organized into categories:

### 🔍 Discovery Tools
- `discover_project` - Find project by directory
- `get_project` - Get project by ID/name/path
- `list_projects` - Browse all projects
- `get_active_agents` - See who's working

### 🏗️ Project Management
- `create_project` - Create new project with workspace
- `get_project_info` - Get project details
- `get_project_decisions` - View decision history
- `search_decisions` - Search through decisions

### 👤 Agent Management
- `register_agent` - Register as agent
- `get_agents_in_project` - View project agents
- `get_agent_context` - View agent activity

### 📝 Context & Coordination
- `start_context` - Start working on task
- `end_context` - Finish task
- `lock_files` - Lock files before editing
- `unlock_files` - Unlock files when done
- `get_locked_files` - Check file locks

### 💾 Memory & Documentation
- `save_decision` - Record technical decisions
- `update_tech_stack` - Track technologies
- `get_tech_stack` - View tech stack
- `log_change` - Log code changes
- `get_recent_changes` - View recent activity

### 🏛️ Architecture
- `get_architecture_recommendation` - Get guidance
- `analyze_architecture` - Analyze structure
- `validate_code_structure` - Check compliance

## 🔍 How It Works

### Workspace-Based Project Discovery

Projects are linked to directories via `workspace_path`:

```python
import os

# Discover project in current directory
discovery = await coordmcp_discover_project(path=os.getcwd())

if discovery["found"]:
    project_id = discovery["project"]["project_id"]
else:
    # Create new project
    result = await coordmcp_create_project(
        project_name="My App",
        workspace_path=os.getcwd(),  # Links to current directory
        description="A web application"
    )
    project_id = result["project_id"]
```

### Flexible Project Lookup

All tools support flexible project identification:

```python
# By project ID
await coordmcp_get_project_info(project_id="proj-abc-123")

# By project name
await coordmcp_get_project_info(project_name="My App")

# By workspace path
await coordmcp_get_project_info(workspace_path=os.getcwd())
```

**Priority:** project_id > workspace_path > project_name

### Session Persistence

Your agent identity persists across sessions:

```python
# First session
gent = await coordmcp_register_agent(name="Dev1", type="opencode")
# Returns: agent_id = "agent-xyz-789"

# Next session (same name = same ID)
agent = await coordmcp_register_agent(name="Dev1", type="opencode")
# Returns: agent_id = "agent-xyz-789" (same!)
```

## 🛠️ Development

### Project Structure

```
coordmcp/
├── src/coordmcp/
│   ├── core/              # Server and tool management
│   ├── memory/            # Long-term memory system
│   ├── context/           # Context and file locking
│   ├── architecture/      # Architecture tools
│   ├── tools/             # MCP tool implementations
│   ├── resources/         # MCP resource implementations
│   └── storage/           # Storage backends
├── src/tests/             # Test suite
├── docs/                  # Documentation
└── examples/              # Example scripts
```

### Running Tests

```bash
# Run all tests
python -m pytest src/tests/ -v

# Run specific test category
python -m pytest src/tests/unit/ -v
```

## 🐛 Troubleshooting

### "Project not found" error

```python
# Use discover_project first
discovery = await coordmcp_discover_project(path=os.getcwd())
```

### "Files already locked" error

```python
# Check which agent has the lock
locked = await coordmcp_get_locked_files(project_id=project_id)
for lock in locked["locked_files"]:
    print(f"Locked by {lock['agent_name']}: {lock['files']}")
```

### Server won't start

```bash
# Check if port is in use
# CoordMCP uses stdio transport (no network ports)
# Just run: python -m coordmcp

# Check for errors
coordmcp --version
```

### Agent not registering

- Ensure `agent_type` is valid: "opencode", "cursor", "claude_code", or "custom"
- Check that `capabilities` is a list of strings
- Verify the server is running

## 📖 Documentation

- **[Getting Started Guide](docs/GETTING_STARTED.md)** - Detailed walkthrough
- **[API Reference](docs/API_REFERENCE.md)** - Complete tool documentation
- **[System Prompt](SYSTEM_PROMPT.md)** - Full agent configuration
- **[Quick Reference](QUICK_REFERENCE.md)** - Condensed guide
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Security Policy](SECURITY.md)** - Security information

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) by Jetify
- Inspired by the need for better multi-agent coordination
- Design patterns based on industry best practices

## 📞 Support

- 📧 Email: support@coordmcp.dev
- 💬 Discord: [Join our community](https://discord.gg/coordmcp)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

---

Made with ❤️ for better multi-agent coding experiences
