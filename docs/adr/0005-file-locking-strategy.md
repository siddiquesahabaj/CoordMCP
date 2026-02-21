# ADR-0005: File Locking Strategy

## Status

Accepted

## Context

When multiple AI agents work on the same project simultaneously, conflicts can occur:
1. Two agents edit the same file at the same time
2. Changes are overwritten unknowingly
3. No visibility into what others are working on
4. Difficult to coordinate handoffs

Requirements:
1. Prevent concurrent edits to the same file
2. Make locks visible to all agents
3. Handle agent crashes gracefully (orphaned locks)
4. Support optional lock expiration
5. Minimal overhead and complexity

## Alternatives Considered

### 1. No Locking (Conflict Detection Only)

**Pros:**
- Simplest implementation
- No coordination overhead

**Cons:**
- Conflicts only detected after they occur
- Requires merge conflict resolution
- Poor user experience

### 2. Centralized Lock Server

**Pros:**
- True distributed locking
- Can handle multiple machines
- Strong consistency

**Cons:**
- Requires running a server
- Adds infrastructure complexity
- Single point of failure
- Overkill for local-only use case

### 3. File-Based Locks with Indefinite Duration

**Pros:**
- Simple implementation
- No expiration logic needed

**Cons:**
- Orphaned locks if agent crashes
- Manual intervention required
- Poor developer experience

### 4. File-Based Locks with Timeout

**Pros:**
- Automatic cleanup of stale locks
- Self-healing after crashes
- Simple implementation
- Works locally without infrastructure
- Visible and debuggable (JSON files)

**Cons:**
- Locks may expire during long operations
- Requires timeout configuration

## Decision

We chose **file-based locks with automatic timeout** for the following reasons:

1. **Self-Healing**: Orphaned locks automatically expire
2. **Visibility**: All agents can see lock status
3. **Simplicity**: No server infrastructure required
4. **Debuggability**: Lock files are human-readable JSON
5. **Flexibility**: Timeout is configurable

## Implementation

### Lock Data Structure

```python
class LockedFile(BaseModel):
    file_path: str
    locked_by: str           # Agent ID
    locked_at: datetime
    reason: str              # Why the file is locked
    expected_duration_minutes: int
    expected_unlock_time: datetime
```

### Lock File Storage

```
~/.coordmcp/data/agents/{agent_id}/locked_files.json

{
    "locks": {
        "src/auth.py": {
            "file_path": "src/auth.py",
            "locked_by": "agent-abc-123",
            "locked_at": "2024-01-20T10:30:00",
            "reason": "Implementing JWT authentication",
            "expected_duration_minutes": 60,
            "expected_unlock_time": "2024-01-20T11:30:00"
        }
    }
}
```

### Lock Acquisition

```python
async def lock_files(
    agent_id: str,
    project_id: str,
    files: List[str],
    reason: str,
    expected_duration_minutes: int = 60
) -> Dict[str, Any]:
    # 1. Check for existing locks
    conflicts = []
    for file_path in files:
        existing_lock = get_lock(project_id, file_path)
        if existing_lock and not is_expired(existing_lock):
            conflicts.append({
                "file": file_path,
                "locked_by": existing_lock.locked_by,
                "reason": existing_lock.reason
            })
    
    # 2. If conflicts, return error
    if conflicts:
        return {
            "success": False,
            "error": "Files locked by other agents",
            "error_type": "FileLockConflict",
            "conflicts": conflicts
        }
    
    # 3. Create locks
    for file_path in files:
        create_lock(agent_id, project_id, file_path, reason, expected_duration_minutes)
    
    return {
        "success": True,
        "locked_files": files,
        "message": f"Locked {len(files)} file(s)"
    }
```

### Lock Expiration Check

```python
def is_expired(lock: LockedFile) -> bool:
    timeout_hours = get_config().lock_timeout_hours
    expiration = lock.locked_at + timedelta(hours=timeout_hours)
    return datetime.now() > expiration
```

### Stale Lock Cleanup

```python
def cleanup_stale_locks(project_id: str) -> int:
    """Remove expired locks. Called on server start and periodically."""
    locks = get_all_locks(project_id)
    cleaned = 0
    for lock in locks:
        if is_expired(lock):
            remove_lock(lock)
            cleaned += 1
    return cleaned
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `COORDMCP_LOCK_TIMEOUT_HOURS` | 24 | Hours before locks expire |
| `COORDMCP_MAX_FILE_LOCKS_PER_AGENT` | 100 | Max files one agent can lock |
| `COORDMCP_AUTO_CLEANUP_STALE_LOCKS` | true | Auto-remove expired locks |

## Workflow

```
1. Agent A calls lock_files(["src/auth.py"], reason="Implementing JWT")
2. CoordMCP checks: Is src/auth.py locked?
   - No → Create lock, return success
   - Yes → Return conflict with lock owner info
3. Agent A edits the file
4. Agent A calls unlock_files(["src/auth.py"])
5. Lock is removed, file available to others
```

### Conflict Scenario

```
1. Agent A locks src/auth.py
2. Agent B tries to lock src/auth.py
3. CoordMCP returns:
   {
     "success": false,
     "error": "File locked by Agent A",
     "conflicts": [{
       "file": "src/auth.py",
       "locked_by": "agent-A-id",
       "reason": "Implementing JWT",
       "expected_unlock": "2024-01-20T11:30:00"
     }]
   }
4. Agent B can:
   - Wait for Agent A to finish
   - Message Agent A via send_message()
   - Work on different files
```

## Consequences

### Positive

- **Conflict Prevention**: Files cannot be edited by multiple agents simultaneously
- **Visibility**: All agents can see what's locked and by whom
- **Self-Healing**: Expired locks are automatically cleaned up
- **Graceful Degradation**: If locks fail, system still works
- **Low Overhead**: Simple file operations, no server needed
- **Debuggable**: Lock files are JSON, easy to inspect

### Negative

- **Not Distributed**: Only works for agents on the same machine
- **Time-Based**: Relies on system clock for expiration
- **Optimistic**: Assumes agents will unlock when done
- **Long Operations**: May need timeout extension for long tasks

### Neutral

- 24-hour default timeout works well for most workflows
- Can be configured shorter for faster cleanup or longer for complex tasks
- Not suitable for distributed teams, but that's not the target use case

## Best Practices

1. **Always Lock Before Edit**: Agents should lock files before any modification
2. **Unlock Promptly**: Release locks as soon as work is complete
3. **Use Meaningful Reasons**: Help others understand why file is locked
4. **Estimate Duration**: Set realistic expected duration
5. **Check Locks First**: Always check `get_locked_files()` before planning work

## References

- [File Locking Implementation](../../src/coordmcp/context/file_tracker.py)
- [Context Manager](../../src/coordmcp/context/manager.py)
- [Configuration Reference](../reference/configuration.md)
