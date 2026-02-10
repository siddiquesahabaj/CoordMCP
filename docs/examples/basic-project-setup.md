# Basic Project Setup

Learn how to create your first project and record architectural decisions with CoordMCP.

**Difficulty:** ⭐ Easy  
**Time:** 5-10 minutes

## Introduction

This example demonstrates the fundamental workflow for setting up a project and recording key architectural decisions. By the end, you'll understand how to:

- Create a new project
- Record architectural decisions with context
- Update your technology stack
- Query project information

## Scenario

You're starting a new REST API project and want to track your decisions from day one.

## Prerequisites

- CoordMCP installed and running
- Your agent connected to CoordMCP

## Step-by-Step Guide

### Step 1: Create a Project

Every piece of work in CoordMCP belongs to a project. Let's create one:

```python
# Create your first project
result = await create_project(
    project_name="My Awesome API",
    description="A RESTful API service built with FastAPI"
)

project_id = result["project_id"]
print(f"✓ Project created with ID: {project_id}")
```

**What this does:**
- Creates a new project with a unique ID
- Sets up storage for decisions, tech stack, and changes
- Makes the project available for all agents

### Step 2: Record Your First Decision

Now let's document why you're choosing FastAPI:

```python
await save_decision(
    project_id=project_id,
    title="Use FastAPI for API framework",
    description="We will use FastAPI as our primary web framework",
    rationale="FastAPI offers excellent performance, automatic validation, and automatic OpenAPI documentation generation",
    impact="All API endpoints will be built with FastAPI",
    author_agent="your-agent-id"  # Get this from register_agent
)

print("✓ Decision 1 recorded: Framework choice")
```

**Key Concepts:**
- **Title**: Short, descriptive name
- **Description**: What was decided
- **Rationale**: Why this decision was made
- **Impact**: What this affects

### Step 3: Record Another Decision

Let's document the database choice:

```python
await save_decision(
    project_id=project_id,
    title="Use PostgreSQL for primary database",
    description="PostgreSQL will be our main data store",
    rationale="ACID compliance, excellent Python support via SQLAlchemy, battle-tested for production",
    impact="All data persistence will use PostgreSQL",
    author_agent="your-agent-id"
)

print("✓ Decision 2 recorded: Database choice")
```

### Step 4: Update Technology Stack

Track what technologies you're using:

```python
await update_tech_stack(
    project_id=project_id,
    category="backend",
    technology="FastAPI",
    version="0.104.0",
    rationale="High-performance async Python web framework"
)

await update_tech_stack(
    project_id=project_id,
    category="database",
    technology="PostgreSQL",
    version="15",
    rationale="Reliable relational database with ACID compliance"
)

print("✓ Technology stack updated")
```

### Step 5: Query Project Information

Now let's see what we've recorded:

```python
# Get all decisions
decisions = await get_project_decisions(project_id=project_id)
print(f"Total decisions: {decisions['count']}")

for decision in decisions['decisions']:
    print(f"  - {decision['title']} ({decision['status']})")
```

**Expected Output:**
```
Total decisions: 2
  - Use FastAPI for API framework (active)
  - Use PostgreSQL for primary database (active)
```

### Step 6: Search Decisions

Find decisions related to specific topics:

```python
results = await search_decisions(
    project_id=project_id,
    query="FastAPI"
)

print(f"Search for 'FastAPI': {results['count']} results")
for r in results['decisions']:
    print(f"  - {r['title']}")
```

**Expected Output:**
```
Search for 'FastAPI': 1 results
  - Use FastAPI for API framework
```

## Complete Example Code

Here's everything together:

```python
# 1. Create project
project = await create_project(
    project_name="My Awesome API",
    description="A RESTful API service built with FastAPI"
)
project_id = project["project_id"]

# 2. Save decisions
await save_decision(
    project_id=project_id,
    title="Use FastAPI",
    description="FastAPI for high performance",
    rationale="Async support, automatic docs"
)

await save_decision(
    project_id=project_id,
    title="Use PostgreSQL",
    description="PostgreSQL for data storage",
    rationale="ACID compliance, reliability"
)

# 3. Update tech stack
await update_tech_stack(
    project_id=project_id,
    category="backend",
    technology="FastAPI",
    version="0.104.0"
)

await update_tech_stack(
    project_id=project_id,
    category="database",
    technology="PostgreSQL",
    version="15"
)

# 4. Verify
print("Project setup complete!")
print(f"Project ID: {project_id}")
```

## Expected Output

When you run this example, you should see:

```
✓ Project created with ID: proj-abc-123
✓ Decision 1 recorded: Framework choice
✓ Decision 2 recorded: Database choice
✓ Technology stack updated
Total decisions: 2
  - Use FastAPI for API framework (active)
  - Use PostgreSQL for primary database (active)
Technology stack:
  - backend: FastAPI
  - database: PostgreSQL
Search for 'FastAPI': 1 results
  - Use FastAPI for API framework
```

## Key Concepts Learned

1. **Projects** - The foundation of CoordMCP organization
2. **Decisions** - Documented architectural choices with context
3. **Tech Stack** - Tracked technology choices
4. **Search** - Finding decisions by keywords

## Next Steps

Now that you have a project:

1. **Log changes** as you implement features:
   ```python
   await log_change(
       project_id=project_id,
       file_path="src/main.py",
       change_type="create",
       description="Created main application file"
   )
   ```

2. **Get architecture recommendations** for new features:
   ```python
   await get_architecture_recommendation(
       project_id=project_id,
       feature_description="Add user authentication"
   )
   ```

3. **Try the next example**: [Architecture Recommendations](./architecture-recommendation.md)

## Troubleshooting

### "Project not found"
- Make sure you're using the correct `project_id`
- Check with `get_project_info(project_id=...)`

### "Agent not authorized"
- Register yourself first: `register_agent(...)`
- Use the returned `agent_id` in calls

## Tips

- **Be specific** in decision titles and descriptions
- **Always explain the rationale** - future you will thank you
- **Update the tech stack** when adding new technologies
- **Tag decisions** for easier searching (if supported)

---

**Congratulations!** You've created your first CoordMCP project. 🎉

Next: Learn how to get [Architecture Recommendations](./architecture-recommendation.md)
