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
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Running the Server

```bash
# Start the CoordMCP server
python -m coordmcp.main
```

The server will start and listen for MCP connections.

### Using with Opencode

Add CoordMCP to your Opencode configuration (`~/.opencode/config.toml`):

```toml
[[mcp_servers]]
name = "coordmcp"
command = "python"
args = ["-m", "coordmcp.main"]
```

## 📖 Documentation

- **[SETUP.md](docs/SETUP.md)** - Detailed installation and configuration
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - Complete tool and resource reference
- **[USAGE_EXAMPLES.md](docs/USAGE_EXAMPLES.md)** - Common usage patterns
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design

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

## 📚 Resources

### Project Resources
- `project://{project_id}` - Project overview
- `project://{project_id}/decisions` - All decisions
- `project://{project_id}/tech-stack` - Tech stack
- `project://{project_id}/architecture` - Architecture overview
- `project://{project_id}/recent-changes` - Recent changes
- `project://{project_id}/modules` - Module list

### Agent Resources
- `agent://{agent_id}` - Agent profile
- `agent://{agent_id}/context` - Current context
- `agent://{agent_id}/locked-files` - Locked files
- `agent://{agent_id}/session-log` - Session log
- `agent://registry` - All registered agents

### Architecture Resources
- `design-patterns://list` - All design patterns
- `design-patterns://{pattern_name}` - Pattern details

## 💡 Usage Examples

### Basic Project Setup

```python
# Create a project
await create_project(
    project_name="My API",
    description="RESTful API service"
)

# Record a decision
await save_decision(
    project_id="proj-123",
    title="Use FastAPI",
    description="FastAPI for high performance",
    rationale="Async support, automatic docs"
)

# Update tech stack
await update_tech_stack(
    project_id="proj-123",
    category="backend",
    technology="FastAPI",
    version="0.104.0"
)
```

### Multi-Agent Coordination

```python
# Register agents
agent1 = await register_agent(
    agent_name="FrontendDev",
    agent_type="opencode",
    capabilities=["react", "typescript"]
)

agent2 = await register_agent(
    agent_name="BackendDev",
    agent_type="cursor",
    capabilities=["python", "fastapi"]
)

# Start contexts
await start_context(
    agent_id=agent1["agent_id"],
    project_id="proj-123",
    objective="Build UI components"
)

# Lock files
await lock_files(
    agent_id=agent1["agent_id"],
    project_id="proj-123",
    files=["src/components/App.tsx"],
    reason="Working on app component"
)
```

### Architecture Recommendations

```python
# Analyze current architecture
analysis = await analyze_architecture(project_id="proj-123")

# Get recommendation
recommendation = await get_architecture_recommendation(
    project_id="proj-123",
    feature_description="Add user authentication",
    constraints=["use existing database"]
)

# Validate code structure
validation = await validate_code_structure(
    project_id="proj-123",
    file_path="src/auth/service.py",
    code_structure={"classes": ["AuthService"]}
)
```

## 📁 Project Structure

```
coordmcp/
├── src/
│   └── coordmcp/
│       ├── main.py              # Server entry point
│       ├── config.py            # Configuration
│       ├── logger.py            # Logging setup
│       ├── core/
│       │   ├── server.py        # FastMCP server
│       │   └── tool_manager.py  # Tool registration
│       ├── memory/
│       │   ├── models.py        # Data models
│       │   └── json_store.py    # Memory storage
│       ├── context/
│       │   ├── manager.py       # Context management
│       │   ├── file_tracker.py  # File locking
│       │   └── state.py         # Context state
│       ├── architecture/
│       │   ├── analyzer.py      # Architecture analysis
│       │   ├── recommender.py   # Recommendations
│       │   ├── validators.py    # Code validation
│       │   └── patterns.py      # Design patterns
│       ├── tools/
│       │   ├── memory_tools.py  # Memory tools
│       │   ├── context_tools.py # Context tools
│       │   └── architecture_tools.py
│       └── resources/
│           ├── project_resources.py
│           ├── agent_resources.py
│           └── architecture_resources.py
├── examples/                    # Usage examples
├── tests/                       # Test suite
├── dev_docs/                    # Development docs
└── docs/                        # User documentation
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python src/tests/test_memory_system.py
python src/tests/test_context_system.py
python src/tests/test_architecture_system.py

# Run integration test
python src/tests/integration/test_full_integration.py
```

## 🔧 Configuration

CoordMCP can be configured via environment variables or a `.env` file:

```bash
# Data directory (default: ~/.coordmcp/data)
COORDMCP_DATA_DIR=/path/to/data

# Log level (default: INFO)
COORDMCP_LOG_LEVEL=DEBUG

# Lock timeout in hours (default: 24)
COORDMCP_LOCK_TIMEOUT_HOURS=24
```

## 🎯 Use Cases

- **Multi-Agent Projects**: Coordinate work between Opencode, Cursor, and Claude Code agents
- **Long-Term Memory**: Remember decisions across sessions
- **Architecture Guidance**: Get recommendations for new features
- **Change Tracking**: Maintain audit trail of modifications
- **File Coordination**: Prevent conflicts in multi-agent scenarios

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](docs/CONTRIBUTING.md) for details.

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
