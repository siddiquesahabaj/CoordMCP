"""
Example: Context Switching

This example demonstrates how agents can switch between projects and tasks
while maintaining context history.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.context.manager import ContextManager
from coordmcp.context.file_tracker import FileTracker
from coordmcp.storage.json_adapter import JSONStorageBackend
from coordmcp.config import get_config


async def context_switching():
    """
    Demonstrates context switching workflow:
    1. Create multiple projects
    2. Register agent
    3. Start context on Project A
    4. Lock files on Project A
    5. Switch context to Project B
    6. View context history
    7. Switch back to Project A
    8. View session log
    """
    print("=" * 70)
    print("Example: Context Switching")
    print("=" * 70)
    print()
    
    # Initialize components
    config = get_config()
    storage = JSONStorageBackend(config.data_dir)
    memory_store = ProjectMemoryStore(storage)
    file_tracker = FileTracker(storage)
    context_manager = ContextManager(storage, file_tracker)
    
    # Step 1: Create multiple projects
    print("Step 1: Creating multiple projects...")
    
    project_a_id = memory_store.create_project(
        project_name="Website Redesign",
        description="Redesign company website with modern UI"
    )
    print(f"  ✓ Project A: Website Redesign ({project_a_id})")
    
    project_b_id = memory_store.create_project(
        project_name="API Migration",
        description="Migrate legacy API to FastAPI"
    )
    print(f"  ✓ Project B: API Migration ({project_b_id})")
    
    project_c_id = memory_store.create_project(
        project_name="Database Optimization",
        description="Optimize database queries and indexes"
    )
    print(f"  ✓ Project C: Database Optimization ({project_c_id})")
    print()
    
    # Step 2: Register agent
    print("Step 2: Registering agent...")
    agent_id = context_manager.register_agent(
        agent_name="MultiTasker",
        agent_type="opencode",
        capabilities=["frontend", "backend", "database", "devops"]
    )
    print(f"  ✓ Agent registered: MultiTasker ({agent_id})")
    print()
    
    # Step 3: Start context on Project A
    print("Step 3: Starting context on Project A...")
    context_a = context_manager.start_context(
        agent_id=agent_id,
        project_id=project_a_id,
        objective="Implement new homepage design",
        task_description="Create responsive homepage with hero section, features grid, and footer",
        priority="high",
        current_file="src/pages/Home.tsx"
    )
    print(f"  ✓ Context started: {context_a.current_context.current_objective}")
    print(f"    Project: Website Redesign")
    print(f"    Current file: {context_a.current_context.current_file}")
    print()
    
    # Step 4: Lock files on Project A
    print("Step 4: Locking files on Project A...")
    result = file_tracker.lock_files(
        agent_id=agent_id,
        project_id=project_a_id,
        files=[
            "src/pages/Home.tsx",
            "src/components/Hero.tsx",
            "src/components/Features.tsx",
            "src/styles/home.css"
        ],
        reason="Implementing homepage redesign"
    )
    print(f"  ✓ Locked {len(result['locked_files'])} files for homepage work")
    print()
    
    # Step 5: Switch context to Project B
    print("Step 5: Switching context to Project B...")
    print("  (Files from Project A will be automatically unlocked)")
    context_b = context_manager.switch_context(
        agent_id=agent_id,
        to_project_id=project_b_id,
        to_objective="Migrate authentication endpoints",
        task_description="Convert legacy auth endpoints to FastAPI",
        priority="critical"
    )
    print(f"  ✓ Context switched: {context_b.current_context.current_objective}")
    print(f"    Project: API Migration")
    print()
    
    # Step 6: Lock files on Project B
    print("Step 6: Locking files on Project B...")
    result = file_tracker.lock_files(
        agent_id=agent_id,
        project_id=project_b_id,
        files=[
            "src/api/auth.py",
            "src/services/auth_service.py",
            "tests/test_auth.py"
        ],
        reason="Migrating authentication system"
    )
    print(f"  ✓ Locked {len(result['locked_files'])} files for API migration")
    print()
    
    # Step 7: View context history
    print("Step 7: Viewing context history...")
    history = context_manager.get_context_history(agent_id, limit=10)
    print(f"  Context history ({len(history)} entries):")
    for i, entry in enumerate(history, 1):
        print(f"    {i}. {entry.timestamp}")
        print(f"       {entry.operation}: {entry.file}")
        if entry.summary:
            print(f"       Summary: {entry.summary}")
    print()
    
    # Step 8: Switch to Project C
    print("Step 8: Switching context to Project C...")
    context_c = context_manager.switch_context(
        agent_id=agent_id,
        to_project_id=project_c_id,
        to_objective="Add database indexes",
        task_description="Create indexes for frequently queried columns",
        priority="medium"
    )
    print(f"  ✓ Context switched: {context_c.current_context.current_objective}")
    print(f"    Project: Database Optimization")
    print()
    
    # Step 9: Lock files on Project C
    print("Step 9: Locking files on Project C...")
    result = file_tracker.lock_files(
        agent_id=agent_id,
        project_id=project_c_id,
        files=[
            "migrations/003_add_indexes.sql",
            "schema/optimization_plan.md"
        ],
        reason="Adding performance indexes"
    )
    print(f"  ✓ Locked {len(result['locked_files'])} files for optimization")
    print()
    
    # Step 10: View session log
    print("Step 10: Viewing session log...")
    session_log = context_manager.get_session_log(agent_id, limit=20)
    print(f"  Session log ({len(session_log)} entries):")
    for i, entry in enumerate(session_log, 1):
        emoji = {
            "context_started": "🚀",
            "context_ended": "🏁",
            "context_switched": "🔄",
            "files_locked": "🔒",
            "files_unlocked": "🔓"
        }.get(entry.event, "📌")
        print(f"    {emoji} {entry.event} at {entry.timestamp}")
        if entry.details:
            for key, value in entry.details.items():
                print(f"       {key}: {value}")
    print()
    
    # Step 11: Check which project agent is currently working on
    print("Step 11: Checking current agent status...")
    current_context = context_manager.get_agent_context_full(agent_id)
    if current_context:
        current_project_id = current_context.current_context.project_id
        # Find project name
        if current_project_id == project_a_id:
            project_name = "Website Redesign"
        elif current_project_id == project_b_id:
            project_name = "API Migration"
        elif current_project_id == project_c_id:
            project_name = "Database Optimization"
        else:
            project_name = "Unknown"
        
        print(f"  Current project: {project_name}")
        print(f"  Current objective: {current_context.current_context.current_objective}")
        print(f"  Locked files: {len(current_context.locked_files)}")
    print()
    
    # Step 12: Switch back to Project A
    print("Step 12: Switching back to Project A...")
    context_a2 = context_manager.switch_context(
        agent_id=agent_id,
        to_project_id=project_a_id,
        to_objective="Complete homepage footer",
        task_description="Finish implementing footer component",
        priority="high"
    )
    print(f"  ✓ Context switched back to Project A")
    print(f"    New objective: {context_a2.current_context.current_objective}")
    print()
    
    # Step 13: End context
    print("Step 13: Ending context...")
    context_manager.end_context(agent_id)
    print(f"  ✓ Context ended")
    print()
    
    # Summary
    print("=" * 70)
    print("Context Switching Example Complete!")
    print("=" * 70)
    print()
    print("Key Features Demonstrated:")
    print("  ✓ Switch between multiple projects")
    print("  ✓ Automatic file unlock on context switch")
    print("  ✓ Context history tracking")
    print("  ✓ Session logging")
    print("  ✓ Multi-project agent coordination")
    print()
    print("Benefits:")
    print("  - Work on multiple projects without losing context")
    print("  - Automatic file management between switches")
    print("  - Full audit trail of context changes")
    print("  - Easy to resume work on previous projects")
    print()


if __name__ == "__main__":
    asyncio.run(context_switching())
