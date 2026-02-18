# Architecture Recommendation Example

How to use CoordMCP for architectural guidance.

## Scenario: Adding User Authentication

### You Say

> "I need to add user authentication with JWT tokens"

### What Happens

#### Step 1: Request Recommendation

**Behind the Scenes:**
```
get_architecture_recommendation(
    project_id="proj-123",
    feature_description="User authentication with JWT tokens",
    context="Existing FastAPI backend, need secure login/logout",
    implementation_style="modular"
)
```

#### Step 2: CoordMCP Analyzes

CoordMCP uses rule-based analysis (no LLM calls):

1. Checks existing tech stack
2. Analyzes current architecture
3. Matches feature to patterns
4. Generates recommendation

#### Step 3: Returns Recommendation

```json
{
  "success": true,
  "recommendation_id": "rec-abc-123",
  "recommended_pattern": {
    "pattern": "Repository",
    "confidence": 92,
    "reason": "Clean separation of auth logic from API routes"
  },
  "file_structure": {
    "new_files": [
      "src/auth/repository.py",
      "src/auth/service.py",
      "src/auth/routes.py",
      "src/models/user.py"
    ],
    "modified_files": [
      "src/main.py",
      "src/config.py"
    ]
  },
  "implementation_guide": {
    "steps": [
      "1. Create User model with password hashing",
      "2. Implement AuthRepository for database operations",
      "3. Create AuthService for JWT token generation",
      "4. Add login/logout routes",
      "5. Add authentication middleware"
    ],
    "estimated_effort": "4-6 hours",
    "dependencies": ["python-jose", "passlib", "python-multipart"]
  },
  "alternatives": [
    {
      "pattern": "Service",
      "confidence": 75,
      "reason": "Simpler but less testable"
    }
  ]
}
```

---

## Using the Recommendation

### Apply the Pattern

**You say:**
> "Implement the authentication following the recommendation"

**Behind the Scenes:**
```
lock_files(
    files=[
        "src/auth/repository.py",
        "src/auth/service.py",
        "src/auth/routes.py",
        "src/models/user.py",
        "src/main.py"
    ],
    reason="Implementing JWT authentication"
)
```

### Record Decision

**Behind the Scenes:**
```
save_decision(
    title="Use Repository pattern for authentication",
    description="Separate auth logic into repository and service layers",
    rationale="Better testability, clean separation of concerns",
    related_files=[
        "src/auth/repository.py",
        "src/auth/service.py"
    ],
    tags=["authentication", "architecture", "security"]
)
```

### Update Tech Stack

**Behind the Scenes:**
```
update_tech_stack(
    category="infrastructure",
    technology="JWT",
    rationale="Stateless authentication for REST API"
)

update_tech_stack(
    category="backend",
    technology="python-jose",
    rationale="JWT token generation and validation"
)
```

### Update Architecture

**Behind the Scenes:**
```
update_architecture(
    recommendation_id="rec-abc-123",
    implementation_summary="Implemented JWT authentication with Repository pattern",
    actual_files_created=[
        "src/auth/repository.py",
        "src/auth/service.py",
        "src/auth/routes.py",
        "src/models/user.py"
    ],
    actual_files_modified=[
        "src/main.py",
        "src/config.py"
    ]
)
```

---

## Available Patterns

| Pattern | Best For | Example Use Case |
|---------|----------|------------------|
| **CRUD** | Simple data operations | Admin panel for managing records |
| **MVC** | Web applications | Full-stack web app |
| **Repository** | Data access | Database operations, auth systems |
| **Service** | Business logic | Complex business rules |
| **Factory** | Object creation | Multi-database support |
| **Observer** | Events | Real-time notifications |
| **Adapter** | Compatibility | Third-party API integration |
| **Strategy** | Algorithms | Payment processors, exporters |
| **Decorator** | Extending | Adding features dynamically |

---

## Customization

### With Constraints

**You say:**
> "Add authentication, but we must use our existing user database and can't add new dependencies"

**Behind the Scenes:**
```
get_architecture_recommendation(
    feature_description="User authentication",
    constraints=[
        "Use existing user database",
        "No new dependencies"
    ]
)
```

### With Style Preference

**You say:**
> "Add authentication with a monolithic approach"

**Behind the Scenes:**
```
get_architecture_recommendation(
    feature_description="User authentication",
    implementation_style="monolithic"  # vs "modular"
)
```

---

## Benefits

| Feature | Benefit |
|---------|---------|
| **No LLM costs** | Rule-based, no API calls |
| **Instant results** | Milliseconds, not seconds |
| **Consistent** | Same input = same output |
| **Project-aware** | Considers your tech stack |
| **Actionable** | File structure + steps |

## See Also

- [Basic Workflow](basic-workflow.md)
- [API Reference](../api-reference.md) - `get_architecture_recommendation`
