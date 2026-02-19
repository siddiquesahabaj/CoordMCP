"""
Integration test for CoordMCP - Complete workflow test.
Tests all major functionality end-to-end.
"""

import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.context.manager import ContextManager
from coordmcp.context.file_tracker import FileTracker
from coordmcp.architecture.analyzer import ArchitectureAnalyzer
from coordmcp.architecture.recommender import ArchitectureRecommender
from coordmcp.storage.json_adapter import JSONStorageBackend
from coordmcp.memory.models import Decision, Change, TechStackEntry, ChangeType, ArchitectureImpact
from coordmcp.config import get_config, Config


async def run_integration_test():
    """Run complete integration test."""
    print("=" * 70)
    print("CoordMCP Integration Test - Complete Workflow")
    print("=" * 70)
    print()
    
    # Use temp directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override config to use temp directory
        config = Config(data_dir=Path(tmpdir) / "data")
        
        # Initialize components
        storage = JSONStorageBackend(config.data_dir)
        memory_store = ProjectMemoryStore(storage)
        file_tracker = FileTracker(storage)
        context_manager = ContextManager(storage, file_tracker)
        analyzer = ArchitectureAnalyzer(memory_store)
        recommender = ArchitectureRecommender(memory_store, analyzer)
        
        test_results = []
        
        # ========== TEST 1: Project Creation ==========
        print("Test 1: Project Creation")
        try:
            workspace_path = Path(tmpdir) / "project_workspace"
            workspace_path.mkdir()
            project_id = memory_store.create_project(
                project_name="Integration Test Project",
                description="Testing complete CoordMCP workflow",
                workspace_path=str(workspace_path)
            )
            print(f"  [PASS] Project created: {project_id}")
            test_results.append(("Project Creation", True, None))
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            test_results.append(("Project Creation", False, str(e)))
            return
        
        # ========== TEST 2: Agent Registration ==========
        print("\nTest 2: Agent Registration")
        try:
            agent1_id = context_manager.register_agent(
                agent_name="FrontendDev",
                agent_type="opencode",
                capabilities=["react", "typescript", "ui"]
            )
            agent2_id = context_manager.register_agent(
                agent_name="BackendDev",
                agent_type="cursor",
                capabilities=["python", "fastapi", "database"]
            )
            print(f"  [PASS] Agent 1 registered: {agent1_id}")
            print(f"  [PASS] Agent 2 registered: {agent2_id}")
            test_results.append(("Agent Registration", True, None))
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            test_results.append(("Agent Registration", False, str(e)))
            return
        
        # ========== TEST 3: Context Management ==========
        print("\nTest 3: Context Management")
        try:
            context1 = context_manager.start_context(
                agent_id=agent1_id,
                project_id=project_id,
                objective="Build user interface",
                task_description="Create React components",
                priority="high"
            )
            context2 = context_manager.start_context(
                agent_id=agent2_id,
                project_id=project_id,
                objective="Build API endpoints",
                task_description="Create FastAPI routes",
                priority="high"
            )
            print(f"  [PASS] Context 1 started: {context1.current_context.current_objective if context1.current_context else 'N/A'}")
            print(f"  [PASS] Context 2 started: {context2.current_context.current_objective if context2.current_context else 'N/A'}")
            test_results.append(("Context Management", True, None))
        except Exception as e:
            print(f"  [FAIL] Error: {e}")
            test_results.append(("Context Management", False, str(e)))
        
        # ========== TEST 4: File Locking ==========
        print("\nTest 4: File Locking")
        try:
            result1 = file_tracker.lock_files(
                agent_id=agent1_id,
                project_id=project_id,
                files=["src/components/App.tsx", "src/components/Header.tsx"],
                reason="Working on UI"
            )
            result2 = file_tracker.lock_files(
                agent_id=agent2_id,
                project_id=project_id,
                files=["src/api/main.py", "src/api/routes.py"],
                reason="Working on API"
            )
            print(f"  [PASS] Agent 1 locked files: {len(result1['locked_files'])}")
            print(f"  [PASS] Agent 2 locked files: {len(result2['locked_files'])}")
            test_results.append(("File Locking", True, None))
        except Exception as e:
            print(f"  [FAIL] Failed: {e}")
            test_results.append(("File Locking", False, str(e)))
        
        # ========== TEST 5: Conflict Detection ==========
        print("\nTest 5: Conflict Detection")
        try:
            try:
                file_tracker.lock_files(
                    agent_id=agent2_id,
                    project_id=project_id,
                    files=["src/components/App.tsx"],
                    reason="Trying to access locked file"
                )
                print(f"  [FAIL] Should have raised FileLockError")
                test_results.append(("Conflict Detection", False, "No error raised"))
            except Exception:
                print(f"  [PASS] Correctly detected conflict")
                test_results.append(("Conflict Detection", True, None))
        except Exception as e:
            print(f"  [FAIL] Failed: {e}")
            test_results.append(("Conflict Detection", False, str(e)))
        
        # ========== TEST 6: Decision Management ==========
        print("\nTest 6: Decision Management")
        try:
            from uuid import uuid4
            decision1 = Decision(
                id=str(uuid4()),
                title="Use FastAPI for backend",
                description="FastAPI provides great performance",
                rationale="Async support, automatic docs",
                impact="All API endpoints",
                tags=["backend", "framework"]
            )
            decision2 = Decision(
                id=str(uuid4()),
                title="Use React for frontend",
                description="React for UI components",
                rationale="Component-based, large ecosystem",
                impact="All UI components",
                tags=["frontend", "framework"]
            )
            
            memory_store.save_decision(project_id, decision1)
            memory_store.save_decision(project_id, decision2)
            
            decisions = memory_store.get_all_decisions(project_id)
            print(f"  [PASS] Saved {len(decisions)} decisions")
            test_results.append(("Decision Management", True, None))
        except Exception as e:
            print(f"  [FAIL] Failed: {e}")
            test_results.append(("Decision Management", False, str(e)))
        
        # ========== TEST 7: Tech Stack ==========
        print("\nTest 7: Tech Stack")
        try:
            entry1 = TechStackEntry(
                category="backend",
                technology="FastAPI",
                version="0.100.0",
                rationale="High performance"
            )
            entry2 = TechStackEntry(
                category="frontend",
                technology="React",
                version="18.0.0",
                rationale="Component-based UI"
            )
            
            memory_store.update_tech_stack(project_id, entry1)
            memory_store.update_tech_stack(project_id, entry2)
            
            tech_stack = memory_store.get_tech_stack(project_id)
            print(f"  [PASS] Tech stack updated: {len(tech_stack)} categories")
            test_results.append(("Tech Stack", True, None))
        except Exception as e:
            print(f"  [FAIL] Failed: {e}")
            test_results.append(("Tech Stack", False, str(e)))
        
        # ========== TEST 8: Change Logging ==========
        print("\nTest 8: Change Logging")
        try:
            from uuid import uuid4
            change1 = Change(
                id=str(uuid4()),
                file_path="src/api/main.py",
                change_type=ChangeType.CREATE,
                description="Created main API file",
                agent_id=agent2_id,
                architecture_impact=ArchitectureImpact.SIGNIFICANT
            )
            change2 = Change(
                id=str(uuid4()),
                file_path="src/components/App.tsx",
                change_type=ChangeType.CREATE,
                description="Created main App component",
                agent_id=agent1_id,
                architecture_impact=ArchitectureImpact.SIGNIFICANT
            )
            
            memory_store.log_change(project_id, change1)
            memory_store.log_change(project_id, change2)
            
            changes = memory_store.get_recent_changes(project_id)
            print(f"  [PASS] Logged {len(changes)} changes")
            test_results.append(("Change Logging", True, None))
        except Exception as e:
            print(f"  [FAIL] Failed: {e}")
            test_results.append(("Change Logging", False, str(e)))
        
        # ========== TEST 9: Architecture Analysis ==========
        print("\nTest 9: Architecture Analysis")
        try:
            analysis = analyzer.analyze_project(project_id)
            if analysis["success"]:
                print(f"  [PASS] Architecture analyzed: {analysis['overview']['total_files']} files")
                test_results.append(("Architecture Analysis", True, None))
            else:
                print(f"  [FAIL] Analysis failed: {analysis.get('error')}")
                test_results.append(("Architecture Analysis", False, analysis.get('error')))
        except Exception as e:
            print(f"  [FAIL] Failed: {e}")
            test_results.append(("Architecture Analysis", False, str(e)))
        
        # ========== TEST 10: Architecture Recommendation ==========
        print("\nTest 10: Architecture Recommendation")
        try:
            recommendation = recommender.recommend_structure(
                project_id=project_id,
                feature_description="Add user authentication system",
                context="Building on existing FastAPI project",
                implementation_style="modular"
            )
            if recommendation["success"]:
                print(f"  [PASS] Recommendation generated: {recommendation['recommended_pattern']['pattern']}")
                test_results.append(("Architecture Recommendation", True, None))
            else:
                print(f"  [FAIL] Recommendation failed: {recommendation.get('error')}")
                test_results.append(("Architecture Recommendation", False, recommendation.get('error')))
        except Exception as e:
            print(f"  [FAIL] Failed: {e}")
            test_results.append(("Architecture Recommendation", False, str(e)))
        
        # ========== TEST 11: Context Switching ==========
        print("\nTest 11: Context Switching")
        try:
            new_context = context_manager.switch_context(
                agent_id=agent1_id,
                new_project_id=project_id,
                new_objective="Fix UI bugs",
                task_description="Fix styling issues"
            )
            print(f"  [PASS] Context switched: {new_context.current_context.current_objective if new_context.current_context else 'N/A'}")
            test_results.append(("Context Switching", True, None))
        except Exception as e:
            print(f"  [FAIL] Failed: {e}")
            test_results.append(("Context Switching", False, str(e)))
        
        # ========== TEST 12: Agent Registry ==========
        print("\nTest 12: Agent Registry")
        try:
            all_agents = context_manager.get_all_agents()
            print(f"  [PASS] Registry query: {len(all_agents)} agents")
            test_results.append(("Agent Registry", True, None))
        except Exception as e:
            print(f"  [FAIL] Failed: {e}")
            test_results.append(("Agent Registry", False, str(e)))
        
        # ========== TEST 13: Session Cleanup ==========
        print("\nTest 13: Session Cleanup")
        try:
            context_manager.end_context(agent1_id)
            context_manager.end_context(agent2_id)
            print(f"  [PASS] Contexts ended for both agents")
            test_results.append(("Session Cleanup", True, None))
        except Exception as e:
            print(f"  [FAIL] Failed: {e}")
            test_results.append(("Session Cleanup", False, str(e)))
        
        # ========== TEST 14: File Unlocking ==========
        print("\nTest 14: File Unlocking")
        try:
            file_tracker.unlock_files(agent1_id, project_id, ["src/components/App.tsx", "src/components/Header.tsx"])
            file_tracker.unlock_files(agent2_id, project_id, ["src/api/main.py", "src/api/routes.py"])
            
            locked = file_tracker.get_locked_files(project_id)
            if locked['total_locked'] == 0:
                print(f"  [PASS] All files unlocked")
                test_results.append(("File Unlocking", True, None))
            else:
                print(f"  [FAIL] Some files still locked: {locked['total_locked']}")
                test_results.append(("File Unlocking", False, "Files still locked"))
        except Exception as e:
            print(f"  [FAIL] Failed: {e}")
            test_results.append(("File Unlocking", False, str(e)))
        
        # ========== SUMMARY ==========
        print("\n" + "=" * 70)
        print("Integration Test Summary")
        print("=" * 70)
        
        passed = sum(1 for _, success, _ in test_results if success)
        failed = sum(1 for _, success, _ in test_results if not success)
        
        print(f"\nTotal: {len(test_results)} tests")
        print(f"Passed: {passed} [PASS]")
        print(f"Failed: {failed} [FAIL]")
        print()
        
        if failed > 0:
            print("Failed tests:")
            for name, success, error in test_results:
                if not success:
                    print(f"  - {name}: {error}")
        
        print()
        if passed == len(test_results):
            print("[SUCCESS] All integration tests passed!")
            return True
        else:
            print(f"[WARNING]  {failed} test(s) failed")
            return False


if __name__ == "__main__":
    success = asyncio.run(run_integration_test())
    sys.exit(0 if success else 1)
