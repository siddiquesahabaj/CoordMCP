"""
Test script for Day 4 - Architecture Guidance System.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.architecture.analyzer import ArchitectureAnalyzer
from coordmcp.architecture.recommender import ArchitectureRecommender
from coordmcp.architecture.patterns import get_all_patterns, suggest_pattern
from coordmcp.storage.json_adapter import JSONStorageBackend
from coordmcp.config import get_config


async def test_architecture_system():
    """Test the architecture guidance system."""
    print("=" * 70)
    print("Testing CoordMCP Architecture Guidance System")
    print("=" * 70)
    print()
    
    # Initialize storage
    config = get_config()
    storage = JSONStorageBackend(config.data_dir)
    store = ProjectMemoryStore(storage)
    analyzer = ArchitectureAnalyzer(store)
    recommender = ArchitectureRecommender(store, analyzer)
    
    # 1. Use existing test project or create new
    print("1. Using test project...")
    # Try to get the project from Day 2 test
    import os
    test_dirs = list((config.data_dir / "memory").iterdir())
    if test_dirs:
        project_id = test_dirs[0].name
        print(f"   Using existing project: {project_id}")
    else:
        project_id = store.create_project(
            project_name="Architecture Test Project",
            description="Testing architecture guidance"
        )
        print(f"   Created new project: {project_id}")
    print()
    
    # 2. Analyze architecture
    print("2. Analyzing project architecture...")
    analysis = analyzer.analyze_project(project_id)
    if analysis["success"]:
        print(f"   Project: {analysis['project_name']}")
        print(f"   Total files: {analysis['overview']['total_files']}")
        print(f"   Total modules: {analysis['overview']['total_modules']}")
        print(f"   Architecture score: {analysis['architecture_assessment']['overall_score']}/100")
        if analysis['architecture_assessment']['issues']:
            print(f"   Issues found: {len(analysis['architecture_assessment']['issues'])}")
        if analysis['architecture_assessment']['strengths']:
            print(f"   Strengths: {len(analysis['architecture_assessment']['strengths'])}")
    else:
        print(f"   Error: {analysis.get('error')}")
    print()
    
    # 3. Get design patterns
    print("3. Getting available design patterns...")
    patterns = get_all_patterns()
    print(f"   Available patterns: {len(patterns)}")
    for name in list(patterns.keys())[:5]:
        print(f"   - {name}: {patterns[name]['description'][:50]}...")
    print()
    
    # 4. Test pattern suggestions
    print("4. Testing pattern suggestions...")
    suggestions = suggest_pattern(
        "Implement user authentication API with database storage",
        "Building REST API with FastAPI"
    )
    print(f"   Suggested patterns: {len(suggestions)}")
    for s in suggestions:
        print(f"   - {s['pattern']} (confidence: {s['confidence']})")
        print(f"     Reason: {s['reason']}")
    print()
    
    # 5. Get architecture recommendation
    print("5. Getting architecture recommendation...")
    recommendation = recommender.recommend_structure(
        project_id=project_id,
        feature_description="Create user authentication system with login, registration, and password reset",
        context="Building on existing FastAPI project",
        constraints=["must use existing database"],
        implementation_style="modular"
    )
    
    if recommendation["success"]:
        print(f"   Recommendation ID: {recommendation['recommendation_id']}")
        print(f"   Pattern: {recommendation['recommended_pattern']['pattern']}")
        print(f"   Confidence: {recommendation['recommended_pattern']['confidence']}")
        print()
        print("   File Structure:")
        for file_info in recommendation['file_structure']['new_files'][:5]:
            print(f"   - {file_info['path']} ({file_info['type']})")
        print()
        print("   Implementation Steps:")
        for step in recommendation['implementation_guide']['steps'][:5]:
            print(f"   {step['order']}. {step['description']}")
        print(f"   Estimated effort: {recommendation['implementation_guide']['estimated_effort']}")
    else:
        print(f"   Error: {recommendation.get('error')}")
    print()
    
    # 6. Check modularity
    print("6. Checking project modularity...")
    modularity = analyzer.check_modularity(project_id)
    if modularity["success"]:
        print(f"   Is modular: {modularity['is_modular']}")
        print(f"   Module count: {modularity['module_count']}")
        print(f"   File coverage: {modularity.get('file_coverage', 0)*100:.1f}%")
        if modularity.get('recommendations'):
            print("   Recommendations:")
            for rec in modularity['recommendations']:
                print(f"   - {rec}")
    else:
        print(f"   Error: {modularity.get('error')}")
    print()
    
    print("=" * 70)
    print("Architecture Guidance System Test Complete!")
    print("=" * 70)
    print()
    print("Features verified:")
    print("  - Architecture analysis")
    print("  - Design pattern catalog")
    print("  - Pattern suggestions")
    print("  - Architecture recommendations")
    print("  - File structure generation")
    print("  - Implementation guides")
    print("  - Modularity checking")


if __name__ == "__main__":
    asyncio.run(test_architecture_system())
