"""
Example: Architecture Recommendations

This example demonstrates how to get architectural recommendations
for new features and validate code structure.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.architecture.analyzer import ArchitectureAnalyzer
from coordmcp.architecture.recommender import ArchitectureRecommender
from coordmcp.architecture.validators import CodeStructureValidator
from coordmcp.architecture.patterns import get_all_patterns, suggest_pattern
from coordmcp.storage.json_adapter import JSONStorageBackend
from coordmcp.memory.models import Decision, FileMetadata
from coordmcp.config import get_config


async def architecture_recommendations():
    """
    Demonstrates architecture guidance workflow:
    1. Create project with existing decisions
    2. Analyze current architecture
    3. Get recommendations for new feature
    4. View design patterns
    5. Validate proposed code structure
    """
    print("=" * 70)
    print("Example: Architecture Recommendations")
    print("=" * 70)
    print()
    
    # Initialize components
    config = get_config()
    storage = JSONStorageBackend(config.data_dir)
    memory_store = ProjectMemoryStore(storage)
    analyzer = ArchitectureAnalyzer(memory_store)
    recommender = ArchitectureRecommender(memory_store, analyzer)
    validator = CodeStructureValidator()
    
    # Step 1: Create project and record existing decisions
    print("Step 1: Setting up project with existing decisions...")
    project_id = memory_store.create_project(
        project_name="SaaS Platform",
        description="Multi-tenant SaaS platform with existing foundation"
    )
    print(f"  ✓ Project created: {project_id}")
    
    # Record existing architectural decisions
    decision1 = Decision(
        title="Use Clean Architecture",
        description="Implement Clean Architecture pattern with clear layer separation",
        rationale="Better testability, maintainability, and separation of concerns",
        impact="All new features must follow Clean Architecture principles",
        tags=["architecture", "clean-code"]
    )
    memory_store.save_decision(project_id, decision1)
    
    # Add some existing files
    files = [
        FileMetadata(path="src/domain/models.py", file_type="source", module="domain", purpose="Domain entities"),
        FileMetadata(path="src/application/services.py", file_type="source", module="application", purpose="Use cases"),
        FileMetadata(path="src/infrastructure/database.py", file_type="source", module="infrastructure", purpose="Database layer"),
        FileMetadata(path="src/api/routes.py", file_type="source", module="api", purpose="API endpoints"),
    ]
    for f in files:
        memory_store.update_file_metadata(project_id, f)
    print(f"  ✓ Added {len(files)} existing files")
    print()
    
    # Step 2: Analyze current architecture
    print("Step 2: Analyzing current architecture...")
    analysis = analyzer.analyze_project(project_id)
    if analysis["success"]:
        print(f"  ✓ Architecture analyzed")
        print(f"    Total files: {analysis['overview']['total_files']}")
        print(f"    Total modules: {analysis['overview']['total_modules']}")
        print(f"    Architecture score: {analysis['architecture_assessment']['overall_score']}/100")
        
        if analysis['architecture_assessment']['issues']:
            print(f"\n    Issues found:")
            for issue in analysis['architecture_assessment']['issues']:
                print(f"      - {issue}")
        
        if analysis['architecture_assessment']['strengths']:
            print(f"\n    Strengths:")
            for strength in analysis['architecture_assessment']['strengths']:
                print(f"      - {strength}")
    print()
    
    # Step 3: Get architecture recommendation for new feature
    print("Step 3: Getting recommendation for new feature...")
    print("  Feature: User subscription and billing system")
    print()
    
    recommendation = recommender.recommend_structure(
        project_id=project_id,
        feature_description="Implement user subscription management with Stripe integration, billing history, and subscription tiers",
        context="Building on existing Clean Architecture project with domain, application, infrastructure, and API layers",
        constraints=["must use existing database", "must follow Clean Architecture"],
        implementation_style="modular"
    )
    
    if recommendation["success"]:
        print(f"  ✓ Recommendation generated")
        print(f"\n    Recommended Pattern: {recommendation['recommended_pattern']['pattern']}")
        print(f"    Confidence: {recommendation['recommended_pattern']['confidence']}%")
        print(f"    Reason: {recommendation['recommended_pattern']['reason']}")
        
        print(f"\n    File Structure:")
        for file_info in recommendation['file_structure']['new_files'][:8]:
            print(f"      - {file_info['path']} ({file_info['type']})")
        
        print(f"\n    Implementation Steps:")
        for step in recommendation['implementation_guide']['steps'][:6]:
            print(f"      {step['order']}. {step['description']}")
        
        print(f"\n    Estimated Effort: {recommendation['implementation_guide']['estimated_effort']}")
    print()
    
    # Step 4: View available design patterns
    print("Step 4: Exploring design patterns...")
    patterns = get_all_patterns()
    print(f"  ✓ Available patterns: {len(patterns)}")
    print(f"\n  Pattern categories:")
    for name, info in list(patterns.items())[:5]:
        print(f"    - {name}: {info['description'][:60]}...")
    print()
    
    # Step 5: Get pattern suggestions for specific feature
    print("Step 5: Getting pattern suggestions...")
    suggestions = suggest_pattern(
        feature_description="Implement caching layer for API responses",
        context="High-traffic API needs response caching"
    )
    print(f"  ✓ Suggestions for caching feature:")
    for suggestion in suggestions[:3]:
        print(f"    - {suggestion['pattern']} (confidence: {suggestion['confidence']})")
        print(f"      Reason: {suggestion['reason']}")
    print()
    
    # Step 6: Validate proposed code structure
    print("Step 6: Validating proposed code structure...")
    proposed_structure = {
        "files": [
            {
                "path": "src/domain/subscription.py",
                "classes": ["Subscription", "SubscriptionTier"],
                "purpose": "Domain entities for subscriptions"
            },
            {
                "path": "src/application/subscription_service.py",
                "classes": ["SubscriptionService"],
                "purpose": "Business logic for subscriptions"
            },
            {
                "path": "src/infrastructure/stripe_adapter.py",
                "classes": ["StripePaymentAdapter"],
                "purpose": "Stripe integration"
            },
            {
                "path": "src/api/subscription_routes.py",
                "classes": [],
                "purpose": "API endpoints for subscriptions"
            }
        ]
    }
    
    validation = validator.validate(
        project_id=project_id,
        file_path="src/domain/subscription.py",
        code_structure=proposed_structure,
        strict=False
    )
    
    if validation["success"]:
        print(f"  ✓ Code structure validated")
        print(f"\n    Validation score: {validation['score']}/100")
        print(f"    Is valid: {validation['is_valid']}")
        
        if validation['issues']:
            print(f"\n    Issues:")
            for issue in validation['issues']:
                print(f"      - [{issue['severity'].upper()}] {issue['message']}")
        
        if validation['suggestions']:
            print(f"\n    Suggestions:")
            for suggestion in validation['suggestions']:
                print(f"      - {suggestion}")
    print()
    
    # Step 7: Check modularity
    print("Step 7: Checking project modularity...")
    modularity = analyzer.check_modularity(project_id)
    if modularity["success"]:
        print(f"  ✓ Modularity check complete")
        print(f"    Is modular: {modularity['is_modular']}")
        print(f"    Module count: {modularity['module_count']}")
        print(f"    File coverage: {modularity.get('file_coverage', 0)*100:.1f}%")
        
        if modularity.get('recommendations'):
            print(f"\n    Recommendations:")
            for rec in modularity['recommendations']:
                print(f"      - {rec}")
    print()
    
    # Summary
    print("=" * 70)
    print("Architecture Recommendations Example Complete!")
    print("=" * 70)
    print()
    print("Key Features Demonstrated:")
    print("  ✓ Analyze existing project architecture")
    print("  ✓ Get recommendations for new features")
    print("  ✓ View design pattern catalog")
    print("  ✓ Get pattern suggestions based on feature")
    print("  ✓ Validate proposed code structure")
    print("  ✓ Check project modularity")
    print()
    print("Benefits:")
    print("  - Consistent architecture across features")
    print("  - Guidance without external LLM calls")
    print("  - Validation before implementation")
    print("  - Pattern-based recommendations")
    print()


if __name__ == "__main__":
    asyncio.run(architecture_recommendations())
