# Security Policy

## Supported Versions

We actively support and provide security updates for the following versions:

| Version | Supported | Status |
| ------- | --------- | ------ |
| 0.1.x   | ✅ Yes | Current stable release |
| < 0.1.0 | ❌ No | Development/beta versions |

Security updates will be released for supported versions as patch releases (e.g., 0.1.1, 0.1.2).

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue in CoordMCP, please follow responsible disclosure practices.

### Responsible Disclosure Process

#### 1. Do Not Open a Public Issue

**Please DO NOT** create a public GitHub issue for security vulnerabilities. Public disclosure could expose the vulnerability to malicious actors before a fix is available.

#### 2. Report Privately

Send an email to **security@coordmcp.dev** with the following information:

**Subject Line:**
```
[SECURITY] Brief description of the vulnerability
```

**Email Body:**
```
Vulnerability Summary:
[One-line summary of the issue]

Description:
[Detailed explanation of the vulnerability]

Steps to Reproduce:
1. Step one
2. Step two
3. Step three

Impact:
[What could happen if this is exploited]

Suggested Fix:
[Your ideas for fixing it, if any - optional]

Your Contact Information:
[How to reach you for follow-up questions]
```

#### 3. Response Timeline

We commit to the following response times:

| Timeframe | Action |
|-----------|--------|
| **24 hours** | Acknowledgment of receipt |
| **72 hours** | Initial assessment and next steps |
| **7 days** | Progress update or fix timeline |
| **30 days** | Target for fix release (critical vulnerabilities) |

#### 4. After Fix

Once the vulnerability is fixed:

1. You will be credited in the security advisory (unless you prefer anonymity)
2. We will publish a security advisory on GitHub Security tab
3. The fix will be included in the next release
4. We will notify you before public disclosure

## Security Measures

### Current Protections

CoordMCP implements multiple layers of security:

#### Input Validation

- **UUID format validation** - All IDs are validated as proper UUIDs
- **Path traversal prevention** - File operations sanitize paths
- **Length limits** - String inputs have maximum length constraints
- **Enum validation** - Constrained values are validated against allowed options
- **Type checking** - Pydantic models enforce type safety

```python
# Example: Path traversal prevention
def validate_workspace_path(path: str) -> Tuple[bool, str]:
    """Validate workspace path doesn't allow traversal."""
    normalized = os.path.normpath(path)
    if ".." in normalized or not os.path.isabs(normalized):
        return False, "Path must be absolute and not contain traversal"
    return True, ""
```

#### File System Security

- **Atomic file writes** - Prevents corruption during concurrent writes
- **Path sanitization** - All file paths are normalized and validated
- **File locking** - Prevents concurrent modification conflicts
- **Restricted write locations** - Only writes to configured data directory
- **Permission checks** - Respects OS file permissions

#### Data Protection

- **JSON storage with validation** - All data is validated against schemas
- **Data integrity checks** - Checksums verify data hasn't been corrupted
- **No sensitive data in logs** - Personal/sensitive data is excluded from logs
- **Configurable log levels** - Adjust logging verbosity as needed

### Best Practices for Users

When using CoordMCP:

1. **Keep software updated**
   ```bash
   pip install --upgrade coordmcp
   ```

2. **Secure data directory**
   ```bash
   # Set restrictive permissions
   chmod 700 ~/.coordmcp/data/
   
   # On Windows, restrict folder permissions through Properties > Security
   ```

3. **Use environment variables** for configuration
   ```bash
   # Good
   export COORDMCP_DATA_DIR=/secure/path
   
   # Avoid hardcoding in scripts
   ```

4. **Review permissions** on data files regularly

5. **Monitor logs** for unusual activity
   ```bash
   tail -f ~/.coordmcp/logs/coordmcp.log
   ```

## Security Considerations

### Data Storage

**Important Notes:**

- CoordMCP stores data in **JSON files on the local filesystem**
- **No encryption at rest by default** - relies on OS-level security
- Store data on encrypted volumes for additional security
- Regular backups recommended

**Securing Your Data:**

```bash
# Set secure permissions
chmod 700 ~/.coordmcp/
chmod 600 ~/.coordmcp/data/*.json

# On macOS/Linux with FileVault or LUKS encryption
# Data will be encrypted at the volume level

# For additional security, store on encrypted volume
export COORDMCP_DATA_DIR=/Volumes/EncryptedDrive/coordmcp-data
```

### Network Security

- **No network ports opened** - CoordMCP uses stdio transport only
- **Local process communication** - All communication is between local processes
- **No external network connections** - Does not connect to external servers

**Transport Methods:**

| Transport | Network | Use Case |
|-----------|---------|----------|
| stdio (default) | No | Local agents |
| HTTP/SSE | Optional | Remote agents (not implemented) |

### Agent Permissions

**Current Limitations:**

- Agents have **access to all tools** by default
- **No role-based access control** implemented
- All agents in a project can see each other's activity

**Mitigation Strategies:**

1. **Use project isolation**
   ```python
   # Create separate projects for sensitive work
   await create_project(
       project_name="sensitive-api",
       workspace_path="/secure/path"
   )
   ```

2. **Monitor agent activity**
   ```python
   # Regularly check active agents
   agents = await get_active_agents(project_id)
   ```

3. **Review tool usage** in logs

## Known Limitations

We believe in transparency. Here are known security limitations:

1. **No Authentication**
   - CoordMCP assumes a trusted local environment
   - Anyone with access to the data directory can read all project data
   - **Mitigation:** Use OS-level permissions and encryption

2. **No Encryption at Rest**
   - Data stored as plain JSON
   - **Mitigation:** Use encrypted volumes (FileVault, BitLocker, LUKS)

3. **Single User Design**
   - Not designed for multi-user environments
   - All agents share the same data access level
   - **Mitigation:** Run separate CoordMCP instances per user

4. **No Audit Trail for Data Access**
   - Logs track tool usage but not data reads
   - **Mitigation:** Monitor file system access logs

5. **Memory-Based Session State**
   - Some state held in memory (file locks, contexts)
   - Server restart clears volatile state
   - **Mitigation:** Persistent data remains in JSON files

## Security Checklist

Before deploying CoordMCP:

- [ ] Data directory has restrictive permissions (700)
- [ ] Running on encrypted volume (recommended)
- [ ] Regular backups configured
- [ ] Log monitoring enabled
- [ ] Environment variables used for sensitive config
- [ ] Latest version installed
- [ ] Only trusted agents have access
- [ ] Project data reviewed for sensitive information

## Reporting Non-Security Issues

For regular bugs (not security vulnerabilities), please use:

- [GitHub Issues](https://github.com/yourusername/coordmcp/issues)
- Email: support@coordmcp.dev

## Contact

| Type | Contact |
|------|---------|
| **Security Team** | security@coordmcp.dev |
| **General Support** | support@coordmcp.dev |
| **Discord** | [Join our community](https://discord.gg/coordmcp) |

## Security Updates

Subscribe to security announcements:

- Watch the repository on GitHub
- Join our Discord #security channel
- Follow @coordmcp on Twitter

---

Thank you for helping keep CoordMCP secure! 🔒
