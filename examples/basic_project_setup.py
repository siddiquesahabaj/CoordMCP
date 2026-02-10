"""
Example: Basic Project Setup

This example demonstrates the basic workflow for setting up a project
and recording architectural decisions.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.memory.models import Decision, TechStackEntry
from coordmcp.storage.json_adapter import JSONStorageBackend
from coordmcp.config import get_config


async def basic_project_setup():
    """
    Demonstrates basic project setup workflow:
    1. Create a project
    2. Record architectural decisions
    3. Update tech stack
    4. Query project information
    """
    print("=" * 70)
    print("Example: Basic Project Setup")
    print("=" * 70)
    print()
    
    # Initialize storage
    config = get_config()
    storage = JSONStorageBackend(config.data_dir)
    store = ProjectMemoryStore(storage)
    
    # Step 1: Create a project
    print("Step 1: Creating project...")
    project_id = store.create_project(
        project_name="My Awesome API",
        description="A RESTful API service built with FastAPI"
    )
    print(f"  ✓ Project created with ID: {project_id}")
    print()
    
    # Step 2: Record architectural decisions
    print("Step 2: Recording architectural decisions...")
    
    # Decision 1: Framework choice
    decision1 = Decision(
        title="Use FastAPI for API framework",
        description="We will use FastAPI as our primary web framework",
        context="Building a new RESTful API service",
        rationale="FastAPI offers excellent performance, automatic validation, and automatic OpenAPI documentation generation",
        impact="All API endpoints will be built with FastAPI",
        status="active",
        related_files=["src/main.py", "requirements.txt"],
        author_agent="opencode",
        tags=["backend", "framework", "api"]
    )
    store.save_decision(project_id, decision1)
    print(f"  ✓ Decision 1 recorded: {decision1.title}")
    
    # Decision 2: Database choice
    decision2 = Decision(
        title="Use PostgreSQL for primary database",
        description="PostgreSQL will be our main data store",
        context="Need reliable relational database for user data",
        rationale="ACID compliance, excellent Python support via SQLAlchemy, battle-tested",
        impact="All data persistence will use PostgreSQL",
        status="active",
        related_files=["src/models.py", "docker-compose.yml"],
        author_agent="opencode",
        tags=["database", "storage", "infrastructure"]
    )
    store.save_decision(project_id, decision2)
    print(f"  ✓ Decision 2 recorded: {decision2.title}")
    print()
    
    # Step 3: Update tech stack
    print("Step 3: Updating technology stack...")
    
    backend_entry = TechStackEntry(
        category="backend",
        technology="FastAPI",
        version="0.104.0",
        rationale="High-performance async Python web framework",
        decision_ref=decision1.id
    )
    store.update_tech_stack(project_id, backend_entry)
    print(f"  ✓ Backend: {backend_entry.technology} v{backend_entry.version}")
    
    database_entry = TechStackEntry(
        category="database",
        technology="PostgreSQL",
        version="15",
        rationale="Reliable relational database with ACID compliance",
        decision_ref=decision2.id
    )
    store.update_tech_stack(project_id, database_entry)
    print(f"  ✓ Database: {database_entry.technology} v{database_entry.version}")
    print()
    
    # Step 4: Query project information
    print("Step 4: Querying project information...")
    
    # Get all decisions
    decisions = store.get_all_decisions(project_id)
    print(f"  Total decisions: {len(decisions)}")
    for d in decisions:
        print(f"    - {d.title} ({d.status})")
    
    # Get tech stack
    tech_stack = store.get_tech_stack(project_id)
    print(f"\n  Technology stack:")
    for category, entry in tech_stack.items():
        print(f"    - {category}: {entry['technology']}")
    
    # Search decisions
    results = store.search_decisions(project_id, "FastAPI")
    print(f"\n  Search for 'FastAPI': {len(results)} results")
    for r in results:
        print(f"    - {r.title}")
    
    print()
    print("=" * 70)
    print("Example complete!")
    print("=" * 70)
    print()
    print(f"Project ID: {project_id}")
    print(f"Data location: {config.data_dir / 'memory' / project_id}")
    print()
    print("Next steps:")
    print("  1. Log changes as you implement features")
    print("  2. Update file metadata for tracking")
    print("  3. Get architecture recommendations for new features")
    print()


if __name__ == "__main__":
    asyncio.run(basic_project_setup())
