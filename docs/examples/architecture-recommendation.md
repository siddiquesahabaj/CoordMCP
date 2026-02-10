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

## Step-by-Step Guide

### Step 1: Set Up Project with Existing Decisions

First, create a project with some existing foundation:

```python
# Create project
project = await create_project(
    project_name="SaaS Platform",
    description="Multi-tenant SaaS platform with existing foundation"
)
project_id = project["project_id"]

# Record existing architectural decision
await save_decision(
    project_id=project_id,
    title="Use Clean Architecture",
    description="Implement Clean Architecture pattern with clear layer separation",
    rationale="Better testability, maintainability, and separation of concerns",
    impact="All new features must follow Clean Architecture principles"
)

print(f"✓ Project set up: {project_id}")
```

### Step 2: Analyze Current Architecture

Let's see what CoordMCP thinks of your current architecture:

```python
analysis = await analyze_architecture(project_id=project_id)

if analysis["success"]:
    print(f"✓ Architecture analyzed")
    print(f"  Total files: {analysis['overview']['total_files']}")
    print(f"  Total modules: {analysis['overview']['total_modules']}")
    print(f"  Architecture score: {analysis['architecture_assessment']['overall_score']}/100")
    
    if analysis['architecture_assessment']['strengths']:
        print(f"\n  Strengths:")
        for strength in analysis['architecture_assessment']['strengths']:
            print(f"    - {strength}")
```

**What this does:**
- Scans your project's structure
- Evaluates modularity
- Scores overall architecture
- Identifies strengths and issues

### Step 3: Get Recommendation for New Feature

Now the exciting part—getting recommendations for your subscription system:

```python
recommendation = await get_architecture_recommendation(
    project_id=project_id,
    feature_description="Implement user subscription management with Stripe integration, billing history, and subscription tiers",
    context="Building on existing Clean Architecture project with domain, application, infrastructure, and API layers",
    constraints=["must use existing database", "must follow Clean Architecture"],
    implementation_style="modular"
)

if recommendation["success"]:
    print(f"✓ Recommendation generated")
    print(f"\n  Recommended Pattern: {recommendation['recommended_pattern']['pattern']}")
    print(f"  Confidence: {recommendation['recommended_pattern']['confidence']}%")
    print(f"  Reason: {recommendation['recommended_pattern']['reason']}")
```

**Expected Output:**
```
✓ Recommendation generated

  Recommended Pattern: Service Layer
  Confidence: 95%
  Reason: Complex business logic requiring clear separation from domain and infrastructure
```

### Step 4: View Recommended File Structure

See exactly what files to create:

```python
print(f"\n  File Structure:")
for file_info in recommendation['file_structure']['new_files'][:6]:
    print(f"    - {file_info['path']} ({file_info['type']})")

print(f"\n  Implementation Steps:")
for step in recommendation['implementation_guide']['steps'][:5]:
    print(f"    {step['order']}. {step['description']}")
```

**Example Output:**
```
  File Structure:
    - src/domain/subscription.py (domain model)
    - src/application/subscription_service.py (service)
    - src/infrastructure/stripe_adapter.py (adapter)
    - src/api/subscription_routes.py (api)

  Implementation Steps:
    1. Create domain models for Subscription and SubscriptionTier
    2. Implement SubscriptionService with business logic
    3. Create StripePaymentAdapter for payment processing
    4. Add API endpoints for subscription management
    5. Write tests for all components
```

### Step 5: Explore Design Patterns

Learn about available patterns:

```python
patterns = await get_design_patterns()

print(f"✓ Available patterns: {len(patterns['patterns'])}")
print(f"\n  Pattern categories:")
for name, info in list(patterns['patterns'].items())[:5]:
    print(f"    - {name}: {info['description'][:50]}...")
```

**Available Patterns Include:**
- **Repository** - Data access abstraction
- **Service Layer** - Business logic encapsulation
- **Factory** - Object creation patterns
- **Observer** - Event-driven architecture
- **Adapter** - Interface adaptation

### Step 6: Get Pattern Suggestions

Get pattern suggestions based on your specific feature:

```python
suggestions = await get_design_patterns(feature_description="Implement caching layer for API responses")

print(f"✓ Suggestions for caching feature:")
for suggestion in suggestions['suggestions'][:3]:
    print(f"    - {suggestion['pattern']} (confidence: {suggestion['confidence']})")
    print(f"      Reason: {suggestion['reason']}")
```

### Step 7: Validate Proposed Code Structure

Before implementing, validate your plan:

```python
validation = await validate_code_structure(
    project_id=project_id,
    file_path="src/domain/subscription.py",
    code_structure={
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
            }
        ]
    },
    strict=False
)

if validation["success"]:
    print(f"✓ Code structure validated")
    print(f"  Validation score: {validation['score']}/100")
    print(f"  Is valid: {validation['is_valid']}")
    
    if validation['suggestions']:
        print(f"\n  Suggestions:")
        for suggestion in validation['suggestions']:
            print(f"    - {suggestion}")
```

## Complete Example Code

```python
# Setup project with existing architecture
project = await create_project(
    project_name="SaaS Platform",
    description="Multi-tenant SaaS with Clean Architecture"
)

# Record existing decision
await save_decision(
    project_id=project["project_id"],
    title="Use Clean Architecture",
    description="Clean Architecture pattern",
    rationale="Better testability and maintainability"
)

# Analyze current architecture
analysis = await analyze_architecture(project_id=project["project_id"])
print(f"Architecture score: {analysis['architecture_assessment']['overall_score']}/100")

# Get recommendation for subscription feature
rec = await get_architecture_recommendation(
    project_id=project["project_id"],
    feature_description="Implement user subscription management with Stripe",
    implementation_style="modular"
)

print(f"\nRecommended pattern: {rec['recommended_pattern']['pattern']}")
print(f"Confidence: {rec['recommended_pattern']['confidence']}%")

# Show file structure
print("\nCreate these files:")
for f in rec['file_structure']['new_files'][:4]:
    print(f"  - {f['path']}")

# Validate proposed structure
validation = await validate_code_structure(
    project_id=project["project_id"],
    file_path="src/domain/subscription.py",
    code_structure={"files": [{"path": "src/domain/subscription.py", "classes": ["Subscription"]}]}
)

print(f"\nValidation score: {validation['score']}/100")
```

## Expected Output

```
✓ Project set up: proj-xyz-789
✓ Architecture analyzed
  Total files: 4
  Total modules: 2
  Architecture score: 85/100

  Strengths:
    - Clear layer separation
    - Well-organized module structure

✓ Recommendation generated

  Recommended Pattern: Service Layer
  Confidence: 95%
  Reason: Complex business logic requiring clear separation

  File Structure:
    - src/domain/subscription.py (domain model)
    - src/application/subscription_service.py (service)
    - src/infrastructure/stripe_adapter.py (adapter)
    - src/api/subscription_routes.py (api)

  Implementation Steps:
    1. Create domain models
    2. Implement service layer
    3. Create payment adapter
    4. Add API endpoints

✓ Code structure validated
  Validation score: 92/100
  Is valid: True

  Suggestions:
    - Consider adding repository pattern for data access
```

## Key Concepts Learned

1. **Architecture Analysis** - Automated project structure evaluation
2. **Pattern Matching** - Rule-based pattern recommendations
3. **Structure Validation** - Verify code organization before implementation
4. **No LLM Required** - Fast, free recommendations

## Common Patterns

### When to Use Each Pattern

| Pattern | Best For | Example Use Case |
|---------|----------|------------------|
| **Repository** | Data access abstraction | Database operations |
| **Service** | Business logic | Payment processing |
| **Factory** | Object creation | Report generators |
| **Observer** | Event handling | Notifications |
| **Adapter** | Interface compatibility | External API integration |

## Tips

- **Provide context** - The more context, the better recommendations
- **List constraints** - Helps narrow down suitable patterns
- **Validate early** - Check structure before writing code
- **Follow recommendations** - They're based on proven patterns

## Troubleshooting

### "Low confidence recommendation"
- Add more context about your project
- Specify constraints
- Check existing decisions for consistency

### "Validation failed"
- Check file paths follow project conventions
- Ensure classes are properly named
- Review suggested improvements

## Next Steps

1. **Implement the recommendation** - Follow the suggested file structure
2. **Log changes** - Track your implementation
3. **Try context switching** - [Context Switching Example](./context-switching.md)

---

**Great!** You now know how to get architecture guidance from CoordMCP. 🎉

Next: Learn about [Context Switching](./context-switching.md)
