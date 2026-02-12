# CoordMCP - Multi-Agent Code Coordination Server

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-powered-green.svg)](https://github.com/jlowin/fastmcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CoordMCP is a FastMCP-based Model Context Protocol server designed to enable intelligent coordination between multiple coding agents. It provides shared long-term memory, context switching capabilities, and architectural guidance without requiring additional LLM API calls.

## 🌟 Features

- **📚 Long-term Memory**: Store and retrieve project decisions, tech stack, and file metadata
- **🔄 Multi-Agent Context**: Switch between projects and track what each agent is working on
- **🔒 File Locking**: Prevent conflicts between agents working on the same files
- **🏗️ Architecture Guidance**: Get recommendations for new features based on design patterns
- **📝 Change Tracking**: Log all changes with architecture impact assessment
- **🔍 Search & Query**: Search through decisions and query project information
- **⚡ No LLM Required**: All recommendations use rule-based logic (no API costs)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp

# Install dependencies
pip install -e .
```

### Running the Server

```bash
# Start the CoordMCP server
python -m coordmcp.main
```

The server will start and listen for MCP connections.

## 🖥️ Getting Started with OpenCode

OpenCode integrates seamlessly with CoordMCP, enabling automatic multi-agent coordination while you code naturally.

### Quick Setup (2 minutes)

1. **Copy the configuration** to your OpenCode config:

```bash
# Copy the pre-configured template
cp opencode-config.jsonc ~/.config/opencode/opencode.jsonc

# Or for project-specific config
cp opencode-config.jsonc ./opencode.jsonc
```

2. **Start CoordMCP** in one terminal:
```bash
python -m coordmcp.main
```

3. **Start OpenCode** in another terminal:
```bash
opencode
```

That's it! OpenCode will now automatically use CoordMCP tools in the background.

### How It Works

When you say something like: **"Create a todo app"**

OpenCode will automatically:

1. ✅ **Create a project** in CoordMCP (`create_project`)
2. ✅ **Register itself** as an agent (`register_agent`)
3. ✅ **Start a work context** (`start_context`)
4. ✅ **Get architecture recommendations** (`get_architecture_recommendation`)
5. ✅ **Lock files** before editing (`lock_files`)
6. ✅ **Save decisions** for technical choices (`save_decision`)
7. ✅ **Log changes** after modifications (`log_change`)
8. ✅ **Track tech stack** entries (`update_tech_stack`)

All this happens automatically - you just code naturally!

### Example Workflow

```
You: Create a todo app with React and Node.js

OpenCode automatically:
→ Creates project "Todo App" in CoordMCP
→ Registers as agent "OpenCodeDev"
→ Starts context: "Build todo app with React and Node.js"
→ Gets architecture recommendations for MERN stack
→ Locks files: src/App.jsx, server/index.js
→ Saves decision: "Use React for frontend"
→ Saves decision: "Use Express.js for backend"
→ Updates tech stack: React, Node.js, Express
→ Implements the app...
→ Logs changes: Created App.jsx, Created server.js
→ Unlocks files when done
```

### What Makes This Powerful

**No Manual Tool Calls**: The enhanced tool descriptions and system prompts guide OpenCode to automatically use the right tools at the right time.

**Automatic Coordination**: If multiple agents work on the same project, file locking prevents conflicts automatically.

**Built-in Memory**: Every decision, change, and tech choice is recorded - no more forgetting why you chose React over Vue!

**Architecture Guidance**: OpenCode automatically asks for architectural recommendations before implementing major features.

### Configuration Details

The `opencode-config.jsonc` file includes:

- **MCP Server Configuration**: Points to your CoordMCP server
- **System Prompt**: Guides OpenCode on when and how to use tools
- **Mandatory Workflow**: Ensures proper initialization sequence
- **Tool Descriptions**: Clear guidance on tool usage

### Manual Configuration (Alternative)

If you prefer manual setup, add this to your `~/.config/opencode/opencode.jsonc`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "coordmcp": {
      "type": "local",
      "command": ["python", "-m", "coordmcp.main"],
      "enabled": true
    }
  },
  "tools": {
    "coordmcp_*": true
  }
}
```

Then copy the system prompt from `SYSTEM_PROMPT.md` into your OpenCode agent configuration.

### Verification

To verify everything is working:

1. Start CoordMCP: `python -m coordmcp.main`
2. Start OpenCode: `opencode`
3. Type: "Create a test project"
4. Watch the logs - you should see:
   - Project created
   - Agent registered
   - Context started
   - Tools being called automatically

### Troubleshooting

**OpenCode doesn't use CoordMCP tools:**
- Ensure CoordMCP server is running
- Check that `opencode-config.jsonc` is in the right location
- Try restarting both services
- Use explicit prompt: "Use coordmcp to create a project"

**"Agent not found" errors:**
- This is normal on first use - OpenCode will auto-register
- If it persists, check the system prompt is loaded

**File lock conflicts:**
- Check `get_locked_files()` to see what's locked
- Wait for other agents to unlock files
- Or coordinate with other agents

### Next Steps

- Read the [System Prompt Guidelines](SYSTEM_PROMPT.md) for detailed configuration
- Explore the [OpenCode Integration Guide](docs/INTEGRATIONS/opencode.md)
- Check out [Example Workflows](docs/examples/)

## 📖 Documentation

### User Documentation
- **[Getting Started](docs/GETTING_STARTED.md)** - 5-minute quick start
- **[Installation](docs/INSTALLATION.md)** - Detailed setup guide
- **[Configuration](docs/CONFIGURATION.md)** - Environment variables and settings
- **[API Reference](docs/API_REFERENCE.md)** - Complete tool and resource reference
- **[Data Models](docs/DATA_MODELS.md)** - Data structures and storage
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Agent Integrations
- **[OpenCode](docs/INTEGRATIONS/opencode.md)** - Setup with OpenCode
- **[Cursor](docs/INTEGRATIONS/cursor.md)** - Setup with Cursor IDE
- **[Claude Code](docs/INTEGRATIONS/claude-code.md)** - Setup with Claude Code
- **[Windsurf](docs/INTEGRATIONS/windsurf.md)** - Setup with Windsurf

### Developer Documentation
- **[Architecture](docs/DEVELOPMENT/ARCHITECTURE.md)** - System design and patterns
- **[Implementation Guide](docs/DEVELOPMENT/IMPLEMENTATION_GUIDE.md)** - Development details
- **[Code Examples](docs/DEVELOPMENT/CODE_EXAMPLES.md)** - Patterns and templates
- **[Testing](docs/DEVELOPMENT/TESTING.md)** - Testing strategy and guides
- **[Contributing](CONTRIBUTING.md)** - How to contribute

### Examples
- **[Basic Project Setup](docs/examples/basic-project-setup.md)** - Your first project
- **[Architecture Recommendation](docs/examples/architecture-recommendation.md)** - Get guidance
- **[Context Switching](docs/examples/context-switching.md)** - Work on multiple tasks
- **[Multi-Agent Workflow](docs/examples/multi-agent-workflow.md)** - Coordinate agents

## 🛠️ Available Tools

### Memory Management
- `create_project` - Create a new project
- `save_decision` - Record architectural decisions
- `get_project_decisions` - Retrieve project decisions
- `search_decisions` - Search through decisions
- `update_tech_stack` - Update technology choices
- `get_tech_stack` - View tech stack
- `log_change` - Log file changes
- `get_recent_changes` - View recent changes
- `update_file_metadata` - Track file information
- `get_file_dependencies` - View file dependencies
- `get_module_info` - Get module details

### Context Management
- `register_agent` - Register a new agent
- `get_agents_list` - List all agents
- `get_agent_profile` - View agent information
- `start_context` - Start working on a task
- `get_agent_context` - View current context
- `switch_context` - Switch between projects/tasks
- `end_context` - Finish current task
- `lock_files` - Lock files to prevent conflicts
- `unlock_files` - Unlock files when done
- `get_locked_files` - View locked files
- `get_context_history` - View context history
- `get_session_log` - View session activity
- `get_agents_in_project` - View active agents

### Architecture Tools
- `analyze_architecture` - Analyze project structure
- `get_architecture_recommendation` - Get feature recommendations
- `validate_code_structure` - Validate code organization
- `get_design_patterns` - View available patterns
- `update_architecture` - Update after implementation

## 💡 Quick Example

```python
# Create a project
result = await create_project(
    project_name="My API",
    description="RESTful API service"
)

# Record a decision
await save_decision(
    project_id=result["project_id"],
    title="Use FastAPI",
    description="FastAPI for high performance",
    rationale="Async support, automatic docs"
)

# Register yourself as an agent
agent = await register_agent(
    agent_name="BackendDev",
    agent_type="opencode",
    capabilities=["python", "fastapi"]
)

# Start working
await start_context(
    agent_id=agent["agent_id"],
    project_id=result["project_id"],
    objective="Implement authentication"
)
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
make test-all

# Or with pytest directly
python -m pytest src/tests/ -v
```

## 📁 Project Structure

```
coordmcp/
├── src/coordmcp/              # Main source code
│   ├── core/                  # Server and tool management
│   ├── memory/                # Long-term memory system
│   ├── context/               # Context and file locking
│   ├── architecture/          # Architecture tools
│   ├── tools/                 # MCP tool implementations
│   ├── resources/             # MCP resource implementations
│   └── storage/               # Storage backends
├── docs/                      # Documentation
│   ├── INTEGRATIONS/          # Agent integration guides
│   ├── DEVELOPMENT/           # Developer documentation
│   └── examples/              # Example walkthroughs
├── src/tests/                 # Test suite
└── examples/                  # Runnable example scripts
```

## 🎯 Use Cases

- **Multi-Agent Projects**: Coordinate work between Opencode, Cursor, and Claude Code agents
- **Long-Term Memory**: Remember decisions across sessions
- **Architecture Guidance**: Get recommendations for new features
- **Change Tracking**: Maintain audit trail of modifications
- **File Coordination**: Prevent conflicts in multi-agent scenarios

## 📊 Stats

- **29 Tools** for memory, context, and architecture
- **14 Resources** for querying project and agent data
- **9 Design Patterns** built-in
- **0 LLM Calls** required (rule-based recommendations)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

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
