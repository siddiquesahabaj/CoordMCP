# CoordMCP Developer Documentation

Technical documentation for developers contributing to or extending CoordMCP.

## Overview

This section contains detailed technical documentation for understanding and working with CoordMCP's internals.

## Available Documentation

### Architecture & Design
- **[Architecture](ARCHITECTURE.md)** - System architecture, design patterns, and data flows
  - System overview and component diagram
  - Data flow diagrams
  - Architecture Decision Records (ADRs)
  - Design patterns used
  - Extension points

### Implementation
- **[Implementation Guide](IMPLEMENTATION_GUIDE.md)** - Detailed implementation specifications
  - Core modules and interfaces
  - Data models
  - Tool and resource patterns
  - Error handling strategy
  - Implementation order

### Code Patterns
- **[Code Examples](CODE_EXAMPLES.md)** - Common patterns and templates
  - Configuration patterns
  - Storage abstraction
  - Data models (Pydantic)
  - Manager patterns
  - Tool implementation
  - Testing patterns

### Quick Reference
- **[Quick Reference](QUICK_REFERENCE.md)** - Quick lookup for developers
  - All tools at-a-glance
  - All resources at-a-glance
  - File layout
  - Command cheat sheet

### Testing
- **[Testing](TESTING.md)** - Testing strategy and guidelines
  - Test structure and organization
  - Running tests
  - Writing tests
  - Coverage goals

## Getting Started as a Developer

### 1. Set Up Development Environment

```bash
# Clone and setup
git clone https://github.com/yourusername/coordmcp.git
cd coordmcp
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### 2. Understand the Architecture

Start with [Architecture](ARCHITECTURE.md) to understand:
- How components interact
- Data flows
- Design decisions

### 3. Read the Implementation Guide

[Implementation Guide](IMPLEMENTATION_GUIDE.md) covers:
- Module interfaces
- Data models
- Patterns to follow

### 4. Explore Code Examples

[Code Examples](CODE_EXAMPLES.md) provides:
- Copy-paste templates
- Common patterns
- Best practices

### 5. Run Tests

```bash
# Run all tests
python -m pytest src/tests/ -v

# Run specific test
python -m pytest src/tests/unit/test_memory/ -v
```

## Contributing

See [Contributing Guide](../CONTRIBUTING.md) for:
- Development workflow
- Code style guidelines
- Pull request process

## Architecture at a Glance

```
┌──────────────────────────────────────────────┐
│         EXTERNAL AGENTS                       │
│  (Opencode, Cursor, Claude Code)             │
└──────────┬───────────────────────────────────┘
           │ FastMCP Protocol
┌──────────▼───────────────────────────────────┐
│   FastMCP SERVER (main.py)                    │
│   ├── Tool Manager (29 tools)                 │
│   └── Resource Manager (14 resources)         │
└──────────┬───────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────┐
│   BUSINESS LOGIC                              │
│   ├── Memory System                           │
│   ├── Context System                          │
│   └── Architecture System                     │
└──────────┬───────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────┐
│   STORAGE ABSTRACTION                         │
│   └── JSONStorageBackend (pluggable)          │
└──────────┬───────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────┐
│   DATA STORAGE (~/.coordmcp/data)             │
│   ├── memory/{project_id}/                    │
│   ├── agents/{agent_id}/                      │
│   └── global/                                 │
└──────────────────────────────────────────────┘
```

## Key Technologies

- **Python 3.8+** - Core language
- **FastMCP** - MCP protocol implementation
- **Pydantic** - Data validation and models
- **pytest** - Testing framework
- **JSON** - Storage format (pluggable)

## Extension Points

CoordMCP is designed for extensibility:

1. **Custom Tools** - Add new capabilities
2. **Custom Resources** - Add new data sources
3. **Storage Backends** - Use PostgreSQL, MongoDB, etc.
4. **Plugins** - Dynamic tool loading
5. **Events** - Hook into tool execution

See [Extending](../EXTENDING.md) for details.

## Questions?

- 📧 **Email**: support@coordmcp.dev
- 💬 **Discord**: [Join our community](https://discord.gg/coordmcp)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

---

**Ready to dive deep?** Start with [Architecture](ARCHITECTURE.md)!
