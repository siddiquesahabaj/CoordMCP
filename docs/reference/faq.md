# Frequently Asked Questions

## General

### What is CoordMCP?

CoordMCP is a coordination server that helps multiple AI coding agents work together on the same project without conflicts. It provides:
- Long-term memory across sessions
- File locking to prevent conflicts
- Architecture recommendations
- Task tracking and agent messaging

### Why do I need CoordMCP?

When using AI coding assistants, you might experience:
- Lost decisions - The AI forgets what was decided in previous sessions
- Inconsistent choices - Different sessions make different architectural decisions
- No coordination - Multiple AI agents don't know what each other is doing
- No history - There's no record of why certain decisions were made

CoordMCP solves all of these problems.

### How does CoordMCP work?

CoordMCP acts as a central coordination hub:
1. Your AI agent connects to CoordMCP via MCP (Model Context Protocol)
2. CoordMCP maintains a shared memory of all decisions, tech stacks, and file states
3. When agents make changes, CoordMCP tracks them and locks files to prevent conflicts
4. Future sessions can query this memory to stay consistent

### Is CoordMCP free?

Yes, CoordMCP is open source under the MIT license. You're free to use it for personal and commercial projects.

---

## Installation

### What are the installation requirements?

- Python 3.10 or higher
- pip (Python package manager)
- An AI coding agent (OpenCode, Cursor, Claude Code, Windsurf, or Antigravity)

### How do I install CoordMCP?

```bash
pip install coordmcp
coordmcp --version
```

### I'm getting "command not found" after installation

**On macOS/Linux:**
```bash
# Find where coordmcp is installed
which coordmcp

# Add to PATH if needed
export PATH="$PATH:/full/path/to/coordmcp"
```

**On Windows:**
```bash
# Find where coordmcp is installed
where coordmcp
```

**Alternative:** Use Python module instead:
```json
{
  "command": "python",
  "args": ["-m", "coordmcp"]
}
```

---

## Configuration

### Where should I put the config file?

| Agent | Config Location |
|-------|-----------------|
| OpenCode | `opencode.jsonc` in project root |
| Cursor | `~/.cursor/mcp.json` or project `.cursor/mcp.json` |
| Claude Code | `claude.json` in project root |
| Windsurf | `~/.windsurf/mcp.json` |
| Antigravity | `~/.antigravity/mcp_config.json` |

### What config options are available?

See the [Configuration Reference](../reference/configuration.md) for all options.

### How do I customize the data directory?

```json
{
  "mcpServers": {
    "coordmcp": {
      "command": "coordmcp",
      "args": [],
      "env": {
        "COORDMCP_DATA_DIR": "/path/to/custom/data"
      }
    }
  }
}
```

---

## Usage

### How do I know CoordMCP is working?

After configuring your agent, ask:

> "What CoordMCP tools are available?"

If the agent responds with tool information, CoordMCP is connected.

### Does CoordMCP work with multiple agents?

Yes! You can run multiple agents with CoordMCP on the same project. They'll automatically:
- See each other's activity
- Know which files are locked
- Share architectural decisions

### What happens when an agent crashes with locks held?

CoordMCP has automatic lock expiration (default: 24 hours). Locks will automatically release after the timeout. You can also manually release locks or adjust the timeout.

### Can I use CoordMCP without an AI agent?

Technically yes, you can use the MCP tools directly, but CoordMCP is designed to work with AI coding agents to provide the best experience.

---

## Troubleshooting

### Tools are not appearing in the agent

1. Verify installation: `coordmcp --version`
2. Check JSON syntax in your config file
3. Restart the agent completely
4. Check agent's MCP settings

### Getting "Connection refused" errors

CoordMCP uses stdio transport by default. This is normal - the agent will connect when needed.

### Data directory permission errors

```bash
# Fix permissions on macOS/Linux
chmod -R 755 ~/.coordmcp/data
```

### Logs show errors but everything seems to work

Check the log level. You might have DEBUG logging enabled which shows extra information. Set `COORDMCP_LOG_LEVEL=INFO` in your config.

---

## Security

### Is my data secure?

CoordMCP stores data locally on your machine. Key security points:
- No network connections (local stdio only)
- Data stored as JSON files
- No built-in encryption (use OS-level encryption like FileVault/BitLocker)

### Can others access my CoordMCP data?

Only users with access to your computer can access the data directory. Use OS-level permissions and encryption for additional security.

---

## Contributing

### How can I contribute?

See our [Contributing Guide](../../CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing procedures
- Pull request process

### Where can I report bugs?

[GitHub Issues](https://github.com/yourusername/coordmcp/issues)

### How do I request new features?

Open a GitHub issue with the `feature-request` label or email support@coordmcp.dev

---

## Support

### How do I get help?

- **Email:** support@coordmcp.dev
- **Discord:** [Join our community](https://discord.gg/coordmcp)
- **GitHub:** [Issues](https://github.com/yourusername/coordmcp/issues)

### What's the response time?

We aim to respond to support requests within 48 hours.

---

## Related Documentation

- [Installation Guide](../user-guide/installation.md)
- [Integrations](../user-guide/integrations.md)
- [How It Works](../user-guide/how-it-works.md)
- [API Reference](../developer-guide/api-reference.md)
- [Configuration Reference](../reference/configuration.md)
- [Troubleshooting](../reference/troubleshooting.md)
