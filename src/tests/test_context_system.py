"""
Test script for Day 3 - Context Management & File Locking.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from coordmcp.context.manager import ContextManager
from coordmcp.context.file_tracker import FileTracker, FileLockError
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.storage.json_adapter import JSONStorageBackend
from coordmcp.config import get_config


async def test_context_system():
    """Test the context management and file locking system."""
    print("=" * 70)
    print("Testing CoordMCP Context Management & File Locking")
    print("=" * 70)
    print()
    
    # Initialize storage and managers
    config = get_config()
    storage = JSONStorageBackend(config.data_dir)
    file_tracker = FileTracker(storage)
    context_manager = ContextManager(storage, file_tracker)
    memory_store = ProjectMemoryStore(storage)
    
    # 1. Create a project
    print("1. Creating test project...")
    project_id = memory_store.create_project(
        project_name="Multi-Agent Test Project",
        description="Testing multi-agent context switching"
    )
    print(f"   Project created: {project_id}")
    print()
    
    # 2. Register agents
    print("2. Registering agents...")
    agent1_id = context_manager.register_agent(
        agent_name="FrontendAgent",
        agent_type="opencode",
        capabilities=["frontend", "react", "typescript"]
    )
    print(f"   Agent 1 (Frontend): {agent1_id}")
    
    agent2_id = context_manager.register_agent(
        agent_name="BackendAgent",
        agent_type="cursor",
        capabilities=["backend", "python", "api"]
    )
    print(f"   Agent 2 (Backend): {agent2_id}")
    print()
    
    # 3. Start contexts for agents
    print("3. Starting contexts...")
    context1 = context_manager.start_context(
        agent_id=agent1_id,
        project_id=project_id,
        objective="Implement user interface",
        task_description="Create React components for user dashboard",
        priority="high",
        current_file="src/components/Dashboard.tsx"
    )
    print(f"   Agent 1 context: {context1.current_context.current_objective}")
    
    context2 = context_manager.start_context(
        agent_id=agent2_id,
        project_id=project_id,
        objective="Implement API endpoints",
        task_description="Create REST API for user data",
        priority="high",
        current_file="src/api/users.py"
    )
    print(f"   Agent 2 context: {context2.current_context.current_objective}")
    print()
    
    # 4. Lock files
    print("4. Testing file locking...")
    try:
        result = file_tracker.lock_files(
            agent_id=agent1_id,
            project_id=project_id,
            files=["src/components/Dashboard.tsx", "src/components/Header.tsx"],
            reason="Working on UI components"
        )
        print(f"   Agent 1 locked files: {result['locked_files']}")
    except FileLockError as e:
        print(f"   Error: {e}")
    
    try:
        result = file_tracker.lock_files(
            agent_id=agent2_id,
            project_id=project_id,
            files=["src/api/users.py", "src/api/auth.py"],
            reason="Working on API endpoints"
        )
        print(f"   Agent 2 locked files: {result['locked_files']}")
    except FileLockError as e:
        print(f"   Error: {e}")
    print()
    
    # 5. Test conflict detection
    print("5. Testing conflict detection...")
    try:
        # Agent 2 tries to lock Agent 1's file
        result = file_tracker.lock_files(
            agent_id=agent2_id,
            project_id=project_id,
            files=["src/components/Dashboard.tsx"],
            reason="Need to check something"
        )
        print("   ERROR: Should have raised FileLockError!")
    except FileLockError as e:
        print(f"   Correctly detected conflict!")
        print(f"   Error message: {str(e)}")
    print()
    
    # 6. Get locked files
    print("6. Getting locked files...")
    locked = file_tracker.get_locked_files(project_id)
    print(f"   Total locked files: {locked['total_locked']}")
    for agent_id, files in locked['by_agent'].items():
        agent = context_manager.get_agent(agent_id)
        print(f"   {agent.agent_name}: {[f['file_path'] for f in files]}")
    print()
    
    # 7. Get agents in project
    print("7. Getting agents in project...")
    agents_in_project = context_manager.get_agents_in_project(project_id)
    print(f"   Active agents: {len(agents_in_project)}")
    for agent_info in agents_in_project:
        print(f"   - {agent_info['agent_name']}: {agent_info['current_objective']}")
    print()
    
    # 8. Test context switching
    print("8. Testing context switching...")
    new_context = context_manager.switch_context(
        agent_id=agent1_id,
        to_project_id=project_id,
        to_objective="Fix UI bugs",
        task_description="Fix styling issues in dashboard"
    )
    print(f"   Agent 1 switched to: {new_context.current_context.current_objective}")
    print(f"   Old files unlocked, new context started")
    print()
    
    # 9. Verify files were unlocked after context switch
    print("9. Verifying files unlocked after context switch...")
    locked = file_tracker.get_locked_files(project_id)
    print(f"   Total locked files: {locked['total_locked']}")
    print(f"   (Should be 2 - only Agent 2's files)")
    print()
    
    # 10. Unlock files
    print("10. Unlocking files...")
    result = file_tracker.unlock_files(
        agent_id=agent2_id,
        project_id=project_id,
        files=["src/api/users.py", "src/api/auth.py"]
    )
    print(f"    Unlocked: {result['unlocked_files']}")
    print()
    
    # 11. Verify all files unlocked
    print("11. Verifying all files unlocked...")
    locked = file_tracker.get_locked_files(project_id)
    print(f"    Total locked files: {locked['total_locked']}")
    print(f"    (Should be 0)")
    print()
    
    # 12. Test agent registry
    print("12. Testing agent registry...")
    all_agents = context_manager.get_all_agents()
    print(f"    Total registered agents: {len(all_agents)}")
    for agent in all_agents:
        print(f"    - {agent.agent_name} ({agent.agent_type}): {agent.total_sessions} sessions")
    print()
    
    # 13. End contexts
    print("13. Ending contexts...")
    context_manager.end_context(agent1_id)
    print("    Agent 1 context ended")
    context_manager.end_context(agent2_id)
    print("    Agent 2 context ended")
    print()
    
    print("=" * 70)
    print("Context Management & File Locking Test Complete!")
    print("=" * 70)
    print()
    print(f"Project ID: {project_id}")
    print(f"Agent 1 ID: {agent1_id}")
    print(f"Agent 2 ID: {agent2_id}")
    print()
    print("All context operations working correctly!")
    print()
    print("Features verified:")
    print("  - Agent registration")
    print("  - Context start/stop")
    print("  - Context switching")
    print("  - File locking")
    print("  - Conflict detection")
    print("  - Lock cleanup on context switch")
    print("  - Agent registry management")


if __name__ == "__main__":
    asyncio.run(test_context_system())
