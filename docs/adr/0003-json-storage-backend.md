# ADR-0003: JSON Storage Backend

## Status

Accepted

## Context

CoordMCP needs to persist data including:
- Project information and metadata
- Architectural decisions
- Technology stack information
- Code change history
- File metadata
- Agent contexts and profiles
- File locks
- Tasks and messages

Requirements:
1. Zero external dependencies for data storage
2. Human-readable format for debugging
3. Easy backup and portability
4. Fast read/write operations
5. Support for indexing and search

## Alternatives Considered

### 1. SQLite Database

**Pros:**
- Single file, easy to transport
- Built into Python standard library
- ACID transactions
- Supports complex queries
- Excellent performance

**Cons:**
- Binary format (not human-readable)
- Requires SQL knowledge to debug
- Schema migrations can be complex
- Not as easy to version control

### 2. PostgreSQL / MySQL

**Pros:**
- Production-grade database
- Excellent performance at scale
- Advanced querying capabilities

**Cons:**
- Requires external server installation
- Adds operational complexity
- Overkill for local-only use case
- Not portable without server

### 3. MongoDB / Document Database

**Pros:**
- Flexible schema
- JSON-like documents
- Good for hierarchical data

**Cons:**
- Requires external server
- Additional dependency
- Overkill for single-user scenario

### 4. JSON Files

**Pros:**
- Zero external dependencies (Python standard library)
- Human-readable and debuggable
- Easy to backup (just copy files)
- Works with version control
- Portable across systems
- Simple to understand and maintain

**Cons:**
- No built-in querying (must load entire file)
- No transaction support
- Potential for corruption during writes
- Performance degrades with very large files

## Decision

We chose **JSON files** for storage with the following design:

1. **Directory Structure**: Organized by entity type
   ```
   ~/.coordmcp/data/
   ├── memory/{project_id}/    # Project-specific data
   ├── agents/{agent_id}/      # Agent-specific data
   └── global/                 # Cross-project data
   ```

2. **Atomic Writes**: Use temporary files + rename to prevent corruption
   ```python
   def atomic_write(path: str, data: dict):
       temp_path = f"{path}.tmp"
       with open(temp_path, 'w') as f:
           json.dump(data, f, indent=2)
       os.replace(temp_path, path)
   ```

3. **In-Memory Indexes**: Build indexes on load for fast lookups
   ```python
   class DecisionIndex(BaseModel):
       by_tag: Dict[str, List[str]]
       by_author: Dict[str, List[str]]
       by_word: Dict[str, List[str]]
   ```

4. **Storage Abstraction**: Interface allows future backend changes
   ```python
   class StorageBackend(ABC):
       @abstractmethod
       def load(self, key: str) -> Optional[Dict]:
           pass
       
       @abstractmethod
       def save(self, key: str, data: Dict) -> None:
           pass
   ```

## Consequences

### Positive

- **Zero Dependencies**: Works with Python standard library only
- **Easy Debugging**: Open any file in a text editor
- **Portable**: Copy `~/.coordmcp/data/` to backup or migrate
- **Version Control Friendly**: Can commit data to git if desired
- **Simple Architecture**: Easy to understand and maintain
- **Fast for Small Data**: JSON parsing is fast for typical usage

### Negative

- **Scalability**: Not suitable for very large datasets (millions of records)
- **No Transactions**: No rollback if operation fails mid-write
- **Memory Usage**: Large files must be fully loaded into memory
- **Query Limitations**: Complex queries require custom code

### Neutral

- With atomic writes, data corruption risk is minimal
- For CoordMCP's use case (project memory), file sizes remain manageable
- Storage abstraction layer allows future migration to SQLite if needed

## Future Considerations

If scalability becomes an issue, we could:
1. Migrate to SQLite while maintaining the same interface
2. Implement file-based sharding for large projects
3. Add optional database backend for enterprise use

## References

- [JSON Storage Pattern](https://www.json.org/)
- [Atomic File Operations](https://stackoverflow.com/questions/2333872/atomic-writing-to-file-with-python)
- [Storage Backend Interface](../../src/coordmcp/storage/base.py)
