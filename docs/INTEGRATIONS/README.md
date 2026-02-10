# CoordMCP Integration Guides

Setup guides for integrating CoordMCP with various coding agents.

## Available Integrations

| Agent | Description | Difficulty |
|-------|-------------|------------|
| **[OpenCode](opencode.md)** | OpenCode AI editor | ⭐ Easy |
| **[Cursor](cursor.md)** | Cursor IDE | ⭐ Easy |
| **[Claude Code](claude-code.md)** | Claude Code CLI | ⭐⭐ Medium |
| **[Windsurf](windsurf.md)** | Windsurf IDE | ⭐⭐ Medium |

## Quick Comparison

| Feature | OpenCode | Cursor | Claude Code | Windsurf |
|---------|----------|--------|-------------|----------|
| Config File | `opencode.jsonc` | `settings.json` | `claude.json` | `windsurf-tools.json` |
| Auto-start | ✅ | ✅ | ⚠️ Manual | ✅ |
| Tool Visibility | Sidebar | Command palette | Commands | Sidebar |
| Restart Required | Yes | Yes | Yes | Yes |

## General Setup Steps

All integrations follow these general steps:

1. **Install CoordMCP**:
   ```bash
   pip install -e .
   ```

2. **Start CoordMCP Server**:
   ```bash
   python -m coordmcp.main
   ```

3. **Configure Agent**: Add MCP server config to agent settings

4. **Restart Agent**: Full restart of the IDE/editor

5. **Test**: Try basic commands like `create_project`

## Which Agent Should I Use?

### Choose OpenCode if:
- You want a terminal-based workflow
- You prefer lightweight tools
- You're comfortable with TUI interfaces

### Choose Cursor if:
- You want a VS Code-like experience
- You need IDE features (debugger, extensions)
- You prefer graphical interfaces

### Choose Claude Code if:
- You want a CLI-first workflow
- You need powerful code understanding
- You prefer conversational interfaces

### Choose Windsurf if:
- You want AI-native IDE features
- You need real-time collaboration
- You want integrated AI assistance

## Common Issues

### "Tools not appearing"
- Ensure CoordMCP server is running
- Check configuration syntax
- Restart the agent completely

### "Connection errors"
- Verify Python is in PATH
- Check server logs: `~/.coordmcp/logs/coordmcp.log`
- Try using full Python path

### "Tools appear but don't work"
- Check agent console for errors
- Verify data directory permissions
- Try a simple test command

## Getting Help

- 📧 **Email**: support@coordmcp.dev
- 💬 **Discord**: [Join our community](https://discord.gg/coordmcp)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/coordmcp/issues)

---

Select your agent above for detailed setup instructions!
