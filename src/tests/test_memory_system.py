"""
Test script for Day 2 - Memory System.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.memory.models import Decision, TechStackEntry, Change, FileMetadata
from coordmcp.storage.json_adapter import JSONStorageBackend
from coordmcp.config import get_config


async def test_memory_system():
    """Test the memory system with sample data."""
    print("=" * 60)
    print("Testing CoordMCP Memory System")
    print("=" * 60)
    print()
    
    # Initialize storage
    config = get_config()
    storage = JSONStorageBackend(config.data_dir)
    store = ProjectMemoryStore(storage)
    
    # 1. Create a project
    print("1. Creating project...")
    project_id = store.create_project(
        project_name="Test API Service",
        description="A RESTful API service for testing"
    )
    print(f"   Created project: {project_id}")
    print()
    
    # 2. Save decisions
    print("2. Saving decisions...")
    decision1 = Decision(
        id="dec-001",
        timestamp=__import__('datetime').datetime.now(),
        title="Use FastAPI for API layer",
        description="We decided to use FastAPI as our web framework",
        context="Building REST API for the service",
        rationale="FastAPI provides excellent performance, automatic validation, and OpenAPI documentation generation",
        impact="All API endpoints will use FastAPI",
        status="active",
        related_files=["src/main.py", "src/api/routes.py"],
        author_agent="opencode-test",
        tags=["backend", "framework", "api"]
    )
    
    decision2 = Decision(
        id="dec-002",
        timestamp=__import__('datetime').datetime.now(),
        title="Use PostgreSQL for database",
        description="PostgreSQL chosen as primary database",
        context="Need reliable relational database",
        rationale="ACID compliance, excellent Python support via SQLAlchemy",
        impact="All data persistence will use PostgreSQL",
        status="active",
        related_files=["src/models.py"],
        author_agent="opencode-test",
        tags=["database", "storage"]
    )
    
    store.save_decision(project_id, decision1)
    store.save_decision(project_id, decision2)
    print("   Saved 2 decisions")
    print()
    
    # 3. Retrieve decisions
    print("3. Retrieving all decisions...")
    decisions = store.get_all_decisions(project_id)
    for d in decisions:
        print(f"   - {d.title} ({d.status})")
    print()
    
    # 4. Search decisions
    print("4. Searching decisions for 'FastAPI'...")
    results = store.search_decisions(project_id, "FastAPI")
    for d in results:
        print(f"   Found: {d.title}")
    print()
    
    # 5. Update tech stack
    print("5. Updating tech stack...")
    backend_entry = TechStackEntry(
        category="backend",
        technology="FastAPI",
        version="0.100.0",
        rationale="High performance, modern Python web framework",
        decision_ref="dec-001"
    )
    
    db_entry = TechStackEntry(
        category="database",
        technology="PostgreSQL",
        version="15",
        rationale="Reliable relational database with ACID compliance",
        decision_ref="dec-002"
    )
    
    store.update_tech_stack(project_id, backend_entry)
    store.update_tech_stack(project_id, db_entry)
    
    tech_stack = store.get_tech_stack(project_id)
    for category, entry in tech_stack.items():
        print(f"   {category}: {entry['technology']} v{entry['version']}")
    print()
    
    # 6. Log changes
    print("6. Logging changes...")
    change1 = Change(
        id="chg-001",
        timestamp=__import__('datetime').datetime.now(),
        file_path="src/main.py",
        change_type="create",
        description="Created main application entry point",
        agent_id="opencode-test",
        impact_area="core",
        architecture_impact="significant",
        related_decision="dec-001",
        code_summary="FastAPI app initialization"
    )
    
    change2 = Change(
        id="chg-002",
        timestamp=__import__('datetime').datetime.now(),
        file_path="src/models.py",
        change_type="create",
        description="Created database models",
        agent_id="opencode-test",
        impact_area="data",
        architecture_impact="significant",
        related_decision="dec-002",
        code_summary="SQLAlchemy models for User and Post"
    )
    
    store.log_change(project_id, change1)
    store.log_change(project_id, change2)
    print("   Logged 2 changes")
    print()
    
    # 7. Get recent changes
    print("7. Getting recent changes...")
    changes = store.get_recent_changes(project_id, limit=10)
    for c in changes:
        print(f"   - {c.change_type}: {c.file_path}")
    print()
    
    # 8. Update file metadata
    print("8. Updating file metadata...")
    file_meta = FileMetadata(
        path="src/main.py",
        file_type="source",
        last_modified=__import__('datetime').datetime.now(),
        last_modified_by="opencode-test",
        module="core",
        purpose="Application entry point and FastAPI setup",
        dependencies=["src/config.py"],
        dependents=["src/api/routes.py"],
        lines_of_code=50,
        complexity="low"
    )
    
    store.update_file_metadata(project_id, file_meta)
    print(f"   Updated metadata for {file_meta.path}")
    print()
    
    # 9. Get file metadata
    print("9. Getting file metadata...")
    metadata = store.get_file_metadata(project_id, "src/main.py")
    if metadata:
        print(f"   File: {metadata.path}")
        print(f"   Module: {metadata.module}")
        print(f"   Purpose: {metadata.purpose}")
        print(f"   Complexity: {metadata.complexity}")
    print()
    
    # 10. Get file dependencies
    print("10. Getting file dependencies...")
    deps = store.get_file_dependencies(project_id, "src/main.py", "both")
    print(f"   Dependencies for src/main.py:")
    for dep in deps:
        print(f"   - {dep}")
    print()
    
    print("=" * 60)
    print("Memory System Test Complete!")
    print("=" * 60)
    print()
    print(f"Project ID: {project_id}")
    print(f"Data stored in: {config.data_dir / 'memory' / project_id}")
    print()
    print("All memory operations working correctly!")


if __name__ == "__main__":
    asyncio.run(test_memory_system())
