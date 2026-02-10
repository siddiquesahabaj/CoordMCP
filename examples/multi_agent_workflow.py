"""
Example: Multi-Agent Workflow

This example demonstrates how multiple agents can coordinate work on a project
using file locking and context management.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.context.manager import ContextManager
from coordmcp.context.file_tracker import FileTracker, FileLockError
from coordmcp.storage.json_adapter import JSONStorageBackend
from coordmcp.memory.models import Change
from coordmcp.config import get_config


async def multi_agent_workflow():
    """
    Demonstrates multi-agent coordination:
    1. Create project
    2. Register multiple agents
    3. Start contexts for each agent
    4. Lock files for each agent
    5. Detect conflicts
    6. Log changes
    7. Unlock files when done
    """
    print("=" * 70)
    print("Example: Multi-Agent Workflow")
    print("=" * 70)
    print()
    
    # Initialize components
    config = get_config()
    storage = JSONStorageBackend(config.data_dir)
    memory_store = ProjectMemoryStore(storage)
    file_tracker = FileTracker(storage)
    context_manager = ContextManager(storage, file_tracker)
    
    # Step 1: Create a project
    print("Step 1: Creating project...")
    project_id = memory_store.create_project(
        project_name="E-Commerce Platform",
        description="Multi-agent collaboration on e-commerce platform"
    )
    print(f"  ✓ Project created: {project_id}")
    print()
    
    # Step 2: Register multiple agents
    print("Step 2: Registering agents...")
    
    frontend_agent_id = context_manager.register_agent(
        agent_name="FrontendAgent",
        agent_type="opencode",
        capabilities=["react", "typescript", "css", "ui-design"]
    )
    print(f"  ✓ Frontend Agent: {frontend_agent_id}")
    
    backend_agent_id = context_manager.register_agent(
        agent_name="BackendAgent",
        agent_type="cursor",
        capabilities=["python", "fastapi", "postgresql", "api-design"]
    )
    print(f"  ✓ Backend Agent: {backend_agent_id}")
    
    database_agent_id = context_manager.register_agent(
        agent_name="DatabaseAgent",
        agent_type="claude_code",
        capabilities=["sql", "postgresql", "database-design", "migrations"]
    )
    print(f"  ✓ Database Agent: {database_agent_id}")
    print()
    
    # Step 3: Start contexts for each agent
    print("Step 3: Starting agent contexts...")
    
    context1 = context_manager.start_context(
        agent_id=frontend_agent_id,
        project_id=project_id,
        objective="Implement user authentication UI",
        task_description="Create login, register, and password reset pages",
        priority="high",
        current_file="src/components/Auth/Login.tsx"
    )
    print(f"  ✓ Frontend context: {context1.current_context.current_objective}")
    
    context2 = context_manager.start_context(
        agent_id=backend_agent_id,
        project_id=project_id,
        objective="Implement authentication API",
        task_description="Create login, register, and JWT token endpoints",
        priority="high",
        current_file="src/api/auth.py"
    )
    print(f"  ✓ Backend context: {context2.current_context.current_objective}")
    
    context3 = context_manager.start_context(
        agent_id=database_agent_id,
        project_id=project_id,
        objective="Design user schema",
        task_description="Create users table and authentication tables",
        priority="high",
        current_file="migrations/001_users.sql"
    )
    print(f"  ✓ Database context: {context3.current_context.current_objective}")
    print()
    
    # Step 4: Lock files for each agent
    print("Step 4: Locking files for each agent...")
    
    result1 = file_tracker.lock_files(
        agent_id=frontend_agent_id,
        project_id=project_id,
        files=[
            "src/components/Auth/Login.tsx",
            "src/components/Auth/Register.tsx",
            "src/components/Auth/PasswordReset.tsx",
            "src/styles/auth.css"
        ],
        reason="Working on authentication UI components"
    )
    print(f"  ✓ Frontend locked {len(result1['locked_files'])} files")
    
    result2 = file_tracker.lock_files(
        agent_id=backend_agent_id,
        project_id=project_id,
        files=[
            "src/api/auth.py",
            "src/services/auth_service.py",
            "src/models/user.py"
        ],
        reason="Implementing authentication API"
    )
    print(f"  ✓ Backend locked {len(result2['locked_files'])} files")
    
    result3 = file_tracker.lock_files(
        agent_id=database_agent_id,
        project_id=project_id,
        files=[
            "migrations/001_users.sql",
            "migrations/002_auth_tables.sql",
            "schema/users.er"
        ],
        reason="Designing user database schema"
    )
    print(f"  ✓ Database locked {len(result3['locked_files'])} files")
    print()
    
    # Step 5: Detect conflicts (simulate another agent trying to access locked file)
    print("Step 5: Testing conflict detection...")
    try:
        # Backend agent tries to lock a frontend file
        file_tracker.lock_files(
            agent_id=backend_agent_id,
            project_id=project_id,
            files=["src/components/Auth/Login.tsx"],
            reason="Need to check the UI structure"
        )
        print("  ✗ ERROR: Should have raised FileLockError!")
    except FileLockError as e:
        print(f"  ✓ Conflict detected correctly!")
        print(f"    File 'src/components/Auth/Login.tsx' is locked by FrontendAgent")
    print()
    
    # Step 6: Log changes
    print("Step 6: Logging changes...")
    
    change1 = Change(
        file_path="src/components/Auth/Login.tsx",
        change_type="create",
        description="Created login component with email/password fields",
        agent_id=frontend_agent_id,
        architecture_impact="minor"
    )
    memory_store.log_change(project_id, change1)
    print(f"  ✓ Logged: {change1.description}")
    
    change2 = Change(
        file_path="src/api/auth.py",
        change_type="create",
        description="Created authentication endpoints",
        agent_id=backend_agent_id,
        architecture_impact="significant"
    )
    memory_store.log_change(project_id, change2)
    print(f"  ✓ Logged: {change2.description}")
    
    change3 = Change(
        file_path="migrations/001_users.sql",
        change_type="create",
        description="Created users table with indexes",
        agent_id=database_agent_id,
        architecture_impact="significant"
    )
    memory_store.log_change(project_id, change3)
    print(f"  ✓ Logged: {change3.description}")
    print()
    
    # Step 7: Show active agents in project
    print("Step 7: Checking active agents in project...")
    active_agents = context_manager.get_agents_in_project(project_id)
    print(f"  Active agents: {len(active_agents)}")
    for agent_info in active_agents:
        print(f"    - {agent_info['agent_name']}: {agent_info['current_objective']}")
    print()
    
    # Step 8: Show all locked files
    print("Step 8: Checking all locked files...")
    locked = file_tracker.get_locked_files(project_id)
    print(f"  Total locked files: {locked['total_locked']}")
    for agent_id, files in locked['by_agent'].items():
        agent = context_manager.get_agent(agent_id)
        agent_name = agent.agent_name if agent else agent_id[:8]
        print(f"    {agent_name}: {len(files)} files")
    print()
    
    # Step 9: Unlock files when done
    print("Step 9: Unlocking files when work is complete...")
    
    file_tracker.unlock_files(
        agent_id=frontend_agent_id,
        project_id=project_id,
        files=[
            "src/components/Auth/Login.tsx",
            "src/components/Auth/Register.tsx",
            "src/components/Auth/PasswordReset.tsx",
            "src/styles/auth.css"
        ]
    )
    print(f"  ✓ Frontend files unlocked")
    
    file_tracker.unlock_files(
        agent_id=backend_agent_id,
        project_id=project_id,
        files=[
            "src/api/auth.py",
            "src/services/auth_service.py",
            "src/models/user.py"
        ]
    )
    print(f"  ✓ Backend files unlocked")
    
    file_tracker.unlock_files(
        agent_id=database_agent_id,
        project_id=project_id,
        files=[
            "migrations/001_users.sql",
            "migrations/002_auth_tables.sql",
            "schema/users.er"
        ]
    )
    print(f"  ✓ Database files unlocked")
    print()
    
    # Step 10: End contexts
    print("Step 10: Ending agent contexts...")
    context_manager.end_context(frontend_agent_id)
    context_manager.end_context(backend_agent_id)
    context_manager.end_context(database_agent_id)
    print(f"  ✓ All contexts ended")
    print()
    
    # Final summary
    print("=" * 70)
    print("Multi-Agent Workflow Complete!")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  - 3 agents registered and coordinated")
    print(f"  - {locked['total_locked']} files were locked and unlocked")
    print(f"  - 3 changes logged")
    print(f"  - Conflicts were properly detected and prevented")
    print()
    print("Key Benefits:")
    print("  ✓ Prevents file conflicts between agents")
    print("  ✓ Tracks which agent is working on what")
    print("  ✓ Maintains audit trail of changes")
    print("  ✓ Coordinates work across multiple agents")
    print()


if __name__ == "__main__":
    asyncio.run(multi_agent_workflow())
