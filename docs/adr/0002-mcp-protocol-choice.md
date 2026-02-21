# ADR-0002: MCP Protocol Choice

## Status

Accepted

## Context

CoordMCP needs to communicate with multiple AI coding agents (OpenCode, Cursor, Claude Code, Windsurf, Antigravity) to provide coordination and memory services. We need a standardized protocol that:

1. Works across different AI agent implementations
2. Supports bi-directional communication (tools and resources)
3. Is well-documented and actively maintained
4. Has good Python support
5. Runs locally without requiring cloud services

## Alternatives Considered

### 1. Custom REST API

**Pros:**
- Full control over API design
- Familiar to most developers
- Easy to debug with standard tools

**Cons:**
- Requires hosting infrastructure
- Authentication complexity
- Not standardized across AI agents
- Each agent would need custom integration

### 2. gRPC

**Pros:**
- Strong typing with protobufs
- Excellent performance
- Bi-directional streaming

**Cons:**
- No standard adoption in AI agent space
- More complex setup
- Requires code generation
- Not natively supported by AI agents

### 3. Language Server Protocol (LSP)

**Pros:**
- Well-established standard
- Good tooling support
- Designed for IDE integration

**Cons:**
- Focused on language features, not coordination
- Not designed for AI agent communication
- Would require significant adaptation

### 4. Model Context Protocol (MCP)

**Pros:**
- Designed specifically for AI agent communication
- Supported by major AI tools (Claude, Cursor, etc.)
- Runs over stdio (no network required)
- Built-in support for tools and resources
- Active development and community
- FastMCP provides excellent Python support

**Cons:**
- Relatively new protocol
- Limited to AI agent use cases
- Requires agents to support MCP

## Decision

We chose **Model Context Protocol (MCP)** with the **FastMCP** Python framework for the following reasons:

1. **Native AI Agent Support**: MCP is designed for exactly our use case - AI agents interacting with external tools
2. **Local-First**: Runs over stdio, no network or hosting required
3. **Rich Feature Set**: Built-in support for tools, resources, and prompts
4. **FastMCP**: Excellent Python library with decorators and async support
5. **Growing Ecosystem**: Major AI tools (Claude Desktop, Cursor, etc.) already support MCP

## Implementation

```python
from fastmcp import FastMCP

server = FastMCP(
    name="CoordMCP",
    instructions="Multi-agent coordination server"
)

@server.tool()
async def save_decision(title: str, description: str, rationale: str):
    """Save an architectural decision."""
    # Implementation
    pass

server.run()
```

## Consequences

### Positive

- **Universal Compatibility**: Works with all MCP-compliant AI agents
- **No Infrastructure**: Runs entirely locally, no servers to maintain
- **Rich Introspection**: AI agents can discover available tools automatically
- **Type Safety**: Tool parameters are validated automatically
- **Simple Deployment**: Just `pip install coordmcp` and configure agent

### Negative

- **Agent Dependency**: Requires agents to support MCP (though adoption is growing)
- **stdio Limitation**: Communication is limited to local machine
- **Learning Curve**: Teams unfamiliar with MCP need to learn the concepts

### Neutral

- MCP is evolving rapidly, may require updates as protocol changes
- FastMCP library is relatively new but well-maintained

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
