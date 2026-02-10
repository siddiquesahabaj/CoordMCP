# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability within CoordMCP, please follow these steps:

### 1. Do Not Open a Public Issue

Please **DO NOT** create a public GitHub issue for security vulnerabilities. This could expose the vulnerability to malicious actors before a fix is available.

### 2. Report Privately

Send an email to **security@coordmcp.dev** with:

- **Subject**: `[SECURITY] Brief description of the issue`
- **Description**: Detailed explanation of the vulnerability
- **Steps to reproduce**: Clear instructions to demonstrate the issue
- **Impact**: What could happen if exploited
- **Suggested fix**: If you have ideas for fixing it (optional)
- **Your contact**: How to reach you for follow-up

### 3. Response Timeline

We will respond to security reports within:

- **24 hours**: Acknowledgment of receipt
- **72 hours**: Initial assessment and next steps
- **7 days**: Progress update or fix timeline
- **30 days**: Target for fix release (critical vulnerabilities)

### 4. After Fix

Once the vulnerability is fixed:

- You will be credited in the security advisory (unless you prefer anonymity)
- We will publish a security advisory on GitHub
- The fix will be included in the next release

## Security Measures

### Current Protections

CoordMCP implements several security measures:

#### Input Validation
- All tool inputs are validated using custom decorators
- UUID format validation for IDs
- Path traversal prevention in file operations
- Length limits on string inputs
- Enum validation for constrained values

#### File System Security
- Atomic file writes prevent corruption
- Path sanitization prevents directory traversal
- File locking prevents concurrent modification conflicts
- Restricted write locations (data directory only)

#### Data Protection
- JSON storage with schema validation
- Data integrity checks on read/write
- No sensitive data in logs (by default)
- Configurable log levels

### Best Practices

When using CoordMCP:

1. **Keep software updated** - Always use the latest version
2. **Secure data directory** - Restrict access to `~/.coordmcp/data/`
3. **Review permissions** - Ensure proper file permissions on data files
4. **Monitor logs** - Regularly check for unusual activity
5. **Use environment variables** - Don't hardcode sensitive configuration
6. **Validate inputs** - Even with validation decorators, be cautious with user input

## Security Considerations

### Data Storage

- CoordMCP stores data in JSON files on the local filesystem
- No encryption at rest by default (rely on OS-level security)
- Backup your data directory regularly
- Use strong OS-level permissions

### Network Security

- CoordMCP uses stdio transport (no network ports)
- Communication is between local processes only
- No external network connections

### Agent Permissions

- Agents using CoordMCP have access to all tools
- Implement agent-level permissions in your agent configuration
- Review tool usage in logs regularly

## Known Limitations

1. **No authentication** - CoordMCP assumes trusted local environment
2. **No encryption** - Data is stored as plain JSON
3. **Single user** - Not designed for multi-user environments without additional controls

## Reporting Non-Security Bugs

For regular bugs (not security vulnerabilities), please use [GitHub Issues](https://github.com/yourusername/coordmcp/issues).

## Contact

- **Security Team**: security@coordmcp.dev
- **General Support**: support@coordmcp.dev
- **Discord**: [Join our community](https://discord.gg/coordmcp)

---

Thank you for helping keep CoordMCP secure! 🔒
