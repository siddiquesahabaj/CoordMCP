# Architecture Recommendations

Learn how to get AI-powered architecture guidance without LLM calls.

**Difficulty:** ⭐⭐ Medium  
**Time:** 10-15 minutes

## Introduction

CoordMCP provides intelligent architecture recommendations using rule-based logic—no external LLM API calls required. This example shows you how to:

- Analyze your project's current architecture
- Get recommendations for new features
- Explore design patterns
- Validate proposed code structure

## Scenario

You have an existing SaaS platform built with Clean Architecture and need to add a subscription management system.

## Prerequisites

- Completed [Basic Project Setup](./basic-project-setup.md)
- Existing project with some architectural decisions
- Understanding of basic CoordMCP workflow

## Step-by-Step Guide

### Step 1: Set Up Project with Existing Decisions

First, discover or create a project with some architectural foundation:

```python
import os

# Discover existing project or create new one
discovery = await coordmcp_discover_project(path=os.getcwd())

if discovery["found"]:
    project_id = discovery["project"]["project_id"]
    print(f"✓ Found existing project: {discovery['project']['project_name']}")
else:
    # Create new project
    result = await coordmcp_create_project(
        project_name="SaaS Platform",
        workspace_path=os.getcwd(),
        description="Multi-tenant SaaS platform with Clean Architecture"
    )
    project_id = result["project_id"]
    print(f"✓ Created project: {result['project_name']}")

# Register as agent
agent = await coordmcp_register_agent(
    agent_name="ArchitectDev",
    agent_type="opencode",
    capabilities=["python", "architecture", "design_patterns"]
)
agent_id = agent["agent_id"]

# Record existing architectural decision
await coordmcp_save_decision(
    project_id=project_id,
    title="Use Clean Architecture",
    description="Implement Clean Architecture pattern with clear layer separation (Domain, Application, Infrastructure, API)",
    rationale="Better testability, maintainability, and separation of concerns. Allows swapping infrastructure without affecting business logic.",
    impact="All new features must follow Clean Architecture principles with proper layer boundaries",
    tags=["architecture", "clean-architecture", "design-pattern"],
    author_agent=agent_id
)

# Record existing tech stack
await coordmcp_update_tech_stack(
    project_id=project_id,
    category="backend",
    technology="FastAPI",
    version="0.104.0",
    rationale="High-performance async Python web framework"
)

await coordmcp_update_tech_stack(
    project_id=project_id,
    category="database",
    technology="PostgreSQL",
    version="15",
    rationale="Reliable relational database"
)

print(f"✓ Project set up: {project_id}")
```

### Step 2: Analyze Current Architecture

Let's see what CoordMCP thinks of your current architecture:

```python
# Analyze the project architecture
analysis = await coordmcp_analyze_architecture(project_id=project_id)

if analysis["success"]:
    print(f"✓ Architecture analyzed")
    print(f"\n📊 Overview:")
    print(f"   Total files: {analysis['overview']['total_files']}")
    print(f"   Total modules: {analysis['overview']['total_modules']}")
    print(f"   Architecture score: {analysis['architecture_assessment']['overall_score']}/100")
    
    if analysis['architecture_assessment']['strengths']:
        print(f"\n✅ Strengths:")
        for strength in analysis['architecture_assessment']['strengths']:
            print(f"   • {strength}")
    
    if analysis['architecture_assessment']['issues']:
        print(f"\n⚠️  Issues:")
        for issue in analysis['architecture_assessment']['issues']:
            print(f"   • {issue}")
else:
    print(f"❌ Analysis failed: {analysis.get('error', 'Unknown error')}")
```

**What this does:**
- Scans your project's recorded structure
- Evaluates modularity and separation of concerns
- Scores overall architecture quality
- Identifies strengths and potential issues
- Provides improvement suggestions

**Example Output:**
```
✓ Architecture analyzed

📊 Overview:
   Total files: 24
   Total modules: 4
   Architecture score: 85/100

✅ Strengths:
   • Clear layer separation following Clean Architecture
   • Well-organized module structure
   • Proper dependency direction

⚠️  Issues:
   • Some modules have high coupling
   • Missing repository abstraction in 2 modules
```

### Step 3: Get Recommendation for New Feature

Now the exciting part—getting recommendations for your subscription system:

```python
# Get architecture recommendation for subscription feature
recommendation = await coordmcp_get_architecture_recommendation(
    project_id=project_id,
    feature_description="Implement user subscription management with Stripe integration, billing history, subscription tiers (Basic, Pro, Enterprise), and automated renewals",
    context="Building on existing Clean Architecture project with Domain, Application, Infrastructure, and API layers. Currently has User and Organization modules.",
    constraints=[
        "must use existing PostgreSQL database",
        "must follow Clean Architecture principles",
        "must integrate with Stripe API",
        "must support multiple subscription tiers"
    ],
    implementation_style="modular"
)

if recommendation["success"]:
    print(f"✓ Recommendation generated")
    print(f"\n🎯 Recommended Pattern: {recommendation['recommended_pattern']['pattern']}")
    print(f"📈 Confidence: {recommendation['recommended_pattern']['confidence']}%")
    print(f"📝 Reason: {recommendation['recommended_pattern']['reason']}")
    
    if 'alternatives' in recommendation and recommendation['alternatives']:
        print(f"\n💡 Alternative Patterns:")
        for alt in recommendation['alternatives'][:2]:
            print(f"   • {alt['pattern']} (confidence: {alt['confidence']}%)")
else:
    print(f"❌ Recommendation failed: {recommendation.get('error', 'Unknown error')}")
```

**Expected Output:**
```
✓ Recommendation generated

🎯 Recommended Pattern: Repository + Service Layer
📈 Confidence: 95%
📝 Reason: Complex business logic requiring clear separation from domain and infrastructure. Payment processing needs isolated service.

💡 Alternative Patterns:
   • Factory Pattern (confidence: 70%)
   • Strategy Pattern (confidence: 65%)
```

### Step 4: View Recommended File Structure

See exactly what files to create:

```python
print(f"\n📁 Recommended File Structure:")
print(f"\n   New Files to Create:")
for file_info in recommendation['file_structure']['new_files'][:8]:
    print(f"   • {file_info['path']}")
    print(f"     Type: {file_info['type']}, Purpose: {file_info['purpose']}")

if recommendation['file_structure'].get('modified_files'):
    print(f"\n   Files to Modify:")
    for mod_file in recommendation['file_structure']['modified_files'][:3]:
        print(f"   • {mod_file['path']}")
        print(f"     Changes: {mod_file.get('modifications', 'N/A')}")

print(f"\n📋 Implementation Guide:")
print(f"   Estimated Effort: {recommendation['implementation_guide']['estimated_effort']}")
print(f"   Testing Strategy: {recommendation['implementation_guide']['testing_strategy']}")

print(f"\n   Implementation Steps:")
for step in recommendation['implementation_guide']['steps'][:6]:
    print(f"   {step['order']}. {step['description']}")
    if step.get('files_affected'):
        print(f"      Files: {', '.join(step['files_affected'])}")
```

**Example Output:**
```
📁 Recommended File Structure:

   New Files to Create:
   • src/domain/subscription.py
     Type: domain_model, Purpose: Domain entities for Subscription and SubscriptionTier
   • src/application/subscription_service.py
     Type: service, Purpose: Business logic for subscription management
   • src/infrastructure/stripe_adapter.py
     Type: adapter, Purpose: Stripe payment gateway integration
   • src/infrastructure/subscription_repository.py
     Type: repository, Purpose: Data access for subscription entities
   • src/api/subscription_routes.py
     Type: api, Purpose: REST endpoints for subscription management
   • src/api/billing_routes.py
     Type: api, Purpose: Billing and invoice endpoints

   Files to Modify:
   • src/domain/user.py
     Changes: Add subscription relationship

📋 Implementation Guide:
   Estimated Effort: 3-4 days
   Testing Strategy: Unit tests for services, integration tests for Stripe adapter

   Implementation Steps:
   1. Create domain models for Subscription and SubscriptionTier
      Files: src/domain/subscription.py
   2. Implement SubscriptionRepository for data access
      Files: src/infrastructure/subscription_repository.py
   3. Create SubscriptionService with business logic
      Files: src/application/subscription_service.py
   4. Implement StripePaymentAdapter for payment processing
      Files: src/infrastructure/stripe_adapter.py
   5. Add API endpoints for subscription management
      Files: src/api/subscription_routes.py
   6. Write comprehensive tests
      Files: tests/unit/test_subscription_service.py, tests/integration/test_stripe_adapter.py
```

### Step 5: Explore Design Patterns

Learn about available patterns:

```python
# Get all available design patterns
patterns = await coordmcp_get_design_patterns()

print(f"✓ Available patterns: {patterns['count']}")
print(f"\n🎨 Pattern Catalog:")
for pattern in patterns['patterns']:
    print(f"\n   {pattern['name']}:")
    print(f"   Description: {pattern['description']}")
    print(f"   Best For: {', '.join(pattern['best_for'])}")
```

**Available Patterns:**
- **Repository** - Data access abstraction layer
- **Service Layer** - Business logic encapsulation
- **Factory** - Object creation patterns
- **Observer** - Event-driven architecture
- **Adapter** - Interface adaptation
- **Strategy** - Algorithm selection
- **Decorator** - Extend functionality dynamically
- **MVC** - Model-View-Controller separation
- **CRUD** - Basic data operations structure

### Step 6: Validate Proposed Code Structure

Before implementing, validate your plan:

```python
# Validate proposed code structure
validation = await coordmcp_validate_code_structure(
    project_id=project_id,
    file_path="src/domain/subscription.py",
    code_structure={
        "files": [
            {
                "path": "src/domain/subscription.py",
                "type": "domain_model",
                "classes": ["Subscription", "SubscriptionTier"],
                "purpose": "Domain entities for subscription management"
            },
            {
                "path": "src/application/subscription_service.py",
                "type": "service",
                "classes": ["SubscriptionService"],
                "purpose": "Business logic for subscription operations"
            },
            {
                "path": "src/infrastructure/stripe_adapter.py",
                "type": "adapter",
                "classes": ["StripePaymentAdapter"],
                "purpose": "Stripe payment gateway integration"
            }
        ],
        "dependencies": [
            {"from": "subscription_service.py", "to": "subscription.py"},
            {"from": "stripe_adapter.py", "to": "subscription_service.py"}
        ]
    },
    strict_mode=False  # Set True for stricter validation
)

if validation["success"]:
    print(f"✓ Code structure validated")
    print(f"   Validation score: {validation['score']}/100")
    print(f"   Is valid: {validation['is_valid']}")
    
    if validation.get('suggestions'):
        print(f"\n💡 Suggestions:")
        for suggestion in validation['suggestions']:
            print(f"   • {suggestion}")
    
    if validation.get('issues'):
        print(f"\n⚠️  Issues:")
        for issue in validation['issues']:
            print(f"   • {issue}")
else:
    print(f"❌ Validation failed: {validation.get('error', 'Unknown error')}")
```

**Expected Output:**
```
✓ Code structure validated
   Validation score: 92/100
   Is valid: True

💡 Suggestions:
   • Consider adding SubscriptionRepository for data access
   • Add validation layer for Stripe webhook handling
   • Document API endpoints in OpenAPI format
```

### Step 7: Save the Recommendation Decision

Document the architectural choice:

```python
# Save the decision to implement the recommendation
await coordmcp_save_decision(
    project_id=project_id,
    title="Implement Subscription System using Repository + Service Pattern",
    description="""Build subscription management using Repository pattern for data access 
and Service Layer for business logic. Integrate with Stripe for payments. 
Structure follows Clean Architecture with clear separation of concerns.""",
    rationale="""This approach maintains Clean Architecture principles while handling 
complex business logic. Repository pattern allows swapping database implementations, 
and Service Layer encapsulates business rules separate from infrastructure concerns. 
Stripe integration is isolated in adapter layer.""",
    impact="Adds subscription domain to the platform. Affects User model, adds new tables, requires Stripe configuration.",
    tags=["architecture", "subscription", "stripe", "clean-architecture", "repository-pattern"],
    related_files=[
        "src/domain/subscription.py",
        "src/application/subscription_service.py",
        "src/infrastructure/stripe_adapter.py",
        "src/api/subscription_routes.py"
    ],
    author_agent=agent_id
)
print("✓ Architecture decision recorded")

# Log the architecture change
await coordmcp_log_change(
    project_id=project_id,
    file_path="architecture/subscription-system",
    change_type="create",
    description="Designed subscription system architecture with Repository and Service patterns",
    agent_id=agent_id,
    architecture_impact="significant",
    code_summary="Added subscription domain, Stripe integration, billing system"
)
print("✓ Architecture change logged")
```

## Complete Example Code

Here's the complete example:

```python
import os

# 1. Setup project with existing architecture
discovery = await coordmcp_discover_project(path=os.getcwd())

if discovery["found"]:
    project_id = discovery["project"]["project_id"]
else:
    result = await coordmcp_create_project(
        project_name="SaaS Platform",
        workspace_path=os.getcwd(),
        description="Multi-tenant SaaS with Clean Architecture"
    )
    project_id = result["project_id"]

# 2. Register as agent
agent = await coordmcp_register_agent(
    agent_name="ArchitectDev",
    agent_type="opencode",
    capabilities=["python", "architecture"]
)
agent_id = agent["agent_id"]

# 3. Record existing decision
await coordmcp_save_decision(
    project_id=project_id,
    title="Use Clean Architecture",
    description="Clean Architecture pattern",
    rationale="Better testability and maintainability",
    tags=["architecture"],
    author_agent=agent_id
)

# 4. Analyze current architecture
analysis = await coordmcp_analyze_architecture(project_id=project_id)
print(f"Architecture score: {analysis['architecture_assessment']['overall_score']}/100")

# 5. Get recommendation for subscription feature
rec = await coordmcp_get_architecture_recommendation(
    project_id=project_id,
    feature_description="Implement user subscription management with Stripe",
    context="Clean Architecture project with existing User module",
    constraints=["must use PostgreSQL", "must follow Clean Architecture"],
    implementation_style="modular"
)

print(f"\nRecommended pattern: {rec['recommended_pattern']['pattern']}")
print(f"Confidence: {rec['recommended_pattern']['confidence']}%")

# 6. Show file structure
print("\nCreate these files:")
for f in rec['file_structure']['new_files'][:4]:
    print(f"  - {f['path']}")

# 7. Validate proposed structure
validation = await coordmcp_validate_code_structure(
    project_id=project_id,
    file_path="src/domain/subscription.py",
    code_structure={
        "files": [
            {"path": "src/domain/subscription.py", "classes": ["Subscription"]},
            {"path": "src/application/subscription_service.py", "classes": ["SubscriptionService"]}
        ]
    },
    strict_mode=False
)

print(f"\nValidation score: {validation['score']}/100")

# 8. Save decision
await coordmcp_save_decision(
    project_id=project_id,
    title=f"Implement using {rec['recommended_pattern']['pattern']}",
    description="Architecture for subscription system",
    rationale=rec['recommended_pattern']['reason'],
    tags=["architecture", "subscription"],
    author_agent=agent_id
)

print("\n✅ Architecture recommendation process complete!")
```

## Key Concepts Learned

1. **Architecture Analysis** - Automated project structure evaluation with scoring
2. **Pattern Matching** - Rule-based pattern recommendations without LLM calls
3. **Structure Validation** - Verify code organization before implementation
4. **Implementation Guide** - Step-by-step implementation instructions
5. **Decision Recording** - Document architectural choices with full context

## Common Patterns Reference

### When to Use Each Pattern

| Pattern | Best For | Example Use Case |
|---------|----------|------------------|
| **Repository** | Data access abstraction | Database operations, data persistence |
| **Service** | Business logic | Payment processing, billing calculations |
| **Factory** | Object creation | Report generators, notification senders |
| **Observer** | Event handling | Real-time notifications, audit logging |
| **Adapter** | Interface compatibility | External API integration, legacy system wrappers |
| **Strategy** | Algorithm selection | Payment methods (Stripe, PayPal), sorting strategies |
| **Decorator** | Extend functionality | Caching layer, logging, metrics collection |

## Tips for Best Results

1. **Provide Context** - The more context you give, the better the recommendations
2. **List Constraints** - Helps narrow down suitable patterns
3. **Validate Early** - Check structure before writing code
4. **Follow Recommendations** - They're based on proven patterns
5. **Document Decisions** - Record WHY you chose a particular approach
6. **Review Alternatives** - Sometimes second-best pattern fits better

## Troubleshooting

### "Low confidence recommendation"
```python
# Add more context and constraints
rec = await coordmcp_get_architecture_recommendation(
    project_id=project_id,
    feature_description="Detailed description of what you're building",
    context="More details about your existing architecture",
    constraints=["specific technical constraints"]
)
```

### "Validation failed"
```python
# Check file paths follow project conventions
# Review suggestions and fix issues
# Try with strict_mode=False first
validation = await coordmcp_validate_code_structure(
    project_id=project_id,
    file_path="src/domain/model.py",
    code_structure={...},
    strict_mode=False  # Less strict validation
)
```

### "No recommendations returned"
- Ensure project exists and has some decisions recorded
- Check that feature_description is clear and specific
- Try with fewer constraints first

## Next Steps

1. **Implement the recommendation** - Follow the suggested file structure
2. **Log your implementation** - Track changes as you build
3. **Validate as you go** - Check code structure incrementally
4. **Try context switching** - Work on multiple features

Learn more:
- [Context Switching](./context-switching.md) - Manage multiple tasks
- [Multi-Agent Workflow](./multi-agent-workflow.md) - Coordinate with team

---

**Great!** You now know how to get architecture guidance from CoordMCP without expensive LLM calls. 🎉

Next: Learn about [Context Switching](./context-switching.md)
