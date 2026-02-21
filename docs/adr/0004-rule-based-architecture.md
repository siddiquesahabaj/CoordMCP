# ADR-0004: Rule-Based Architecture Analysis

## Status

Accepted

## Context

CoordMCP provides architectural guidance to help AI agents make good design decisions. This includes:
- Recommending design patterns (MVC, Repository, Factory, etc.)
- Analyzing project structure
- Suggesting file organization
- Validating code structure

Key requirements:
1. **Zero Latency**: Recommendations must be instant
2. **Zero Cost**: No API calls to external services
3. **Privacy**: All analysis happens locally
4. **Reliability**: No dependency on external services
5. **Predictability**: Same input always produces same output

## Alternatives Considered

### 1. LLM-Based Analysis

**Pros:**
- Can understand nuanced context
- Handles natural language descriptions
- Adapts to new patterns automatically
- Can explain reasoning

**Cons:**
- **Cost**: API calls cost money per request
- **Latency**: Network requests add delay (1-5 seconds)
- **Privacy**: Code context sent to external service
- **Reliability**: Depends on API availability
- **Unpredictability**: Results vary between calls
- **Rate Limits**: Usage limits on API calls

### 2. Hybrid Approach (Rules + LLM)

**Pros:**
- Best of both worlds
- Can fall back to LLM for complex cases

**Cons:**
- Added complexity
- Still has LLM downsides for some requests
- Harder to test and debug

### 3. Rule-Based Analysis

**Pros:**
- **Zero Cost**: No API calls, runs entirely locally
- **Instant**: Sub-millisecond response times
- **Private**: No data leaves the machine
- **Reliable**: No external dependencies
- **Predictable**: Deterministic results
- **Testable**: Easy to write unit tests
- **Transparent**: Logic is visible in code

**Cons:**
- **Limited Context**: Can't understand nuanced situations
- **Maintenance**: Rules must be updated manually
- **Rigidity**: May not handle edge cases well

## Decision

We chose **pure rule-based analysis** for the following reasons:

1. **Cost-Free**: Users never pay for recommendations
2. **Privacy-First**: No code leaves their machine
3. **Instant Response**: No network latency
4. **Reliability**: Works offline, no API dependencies
5. **Transparency**: Users can inspect recommendation logic

## Implementation

### Pattern Definition

```python
PATTERNS = {
    "Repository": {
        "description": "Data access abstraction layer",
        "best_for": ["data access", "persistence", "database operations"],
        "keywords": ["repository", "dao", "data access", "persistence"],
        "file_structure": {
            "repositories/": {
                "base_repository.py": "Abstract base class",
                "user_repository.py": "User data operations",
                "item_repository.py": "Item data operations"
            }
        }
    },
    "Strategy": {
        "description": "Interchangeable algorithms",
        "best_for": ["algorithms", "variations", "interchangeable behavior"],
        "keywords": ["strategy", "algorithm", "payment", "sorting"],
        # ...
    }
}
```

### Recommendation Algorithm

```python
def recommend_pattern(feature_description: str, project_context: dict) -> dict:
    tokens = tokenize(feature_description.lower())
    scores = {}
    
    for pattern_name, pattern_info in PATTERNS.items():
        score = 0
        for keyword in pattern_info["keywords"]:
            if keyword in tokens:
                score += 2
        for use_case in pattern_info["best_for"]:
            if use_case in tokens:
                score += 3
        scores[pattern_name] = score
    
    best_pattern = max(scores, key=scores.get)
    return {
        "pattern": best_pattern,
        "confidence": scores[best_pattern] / max_possible_score,
        "implementation_guide": PATTERNS[best_pattern]["file_structure"]
    }
```

### Pattern Matching

```python
def analyze_project_structure(project_id: str) -> dict:
    files = get_project_files(project_id)
    
    detected_patterns = []
    for pattern_name, pattern_info in PATTERNS.items():
        expected_files = pattern_info.get("expected_files", [])
        matches = sum(1 for f in expected_files if f in files)
        if matches / len(expected_files) > 0.5:
            detected_patterns.append(pattern_name)
    
    return {"patterns": detected_patterns}
```

## Available Patterns

| Pattern | Best For | Keywords |
|---------|----------|----------|
| CRUD | Simple data operations | crud, create, read, update, delete |
| MVC | Web applications | model, view, controller, web |
| Repository | Data access abstraction | repository, dao, persistence |
| Service | Business logic | service, business, logic, domain |
| Factory | Complex object creation | factory, create, builder |
| Observer | Event-driven systems | observer, event, notify, subscribe |
| Adapter | Interface compatibility | adapter, wrapper, interface |
| Strategy | Interchangeable algorithms | strategy, algorithm, payment |
| Decorator | Extending functionality | decorator, wrapper, extend |

## Consequences

### Positive

- **Zero Cost**: Unlimited recommendations at no charge
- **Instant**: Sub-millisecond response time
- **Privacy**: No data leaves the user's machine
- **Reliability**: Works 100% of the time, no API downtime
- **Predictability**: Same feature description = same recommendation
- **Testability**: 100% test coverage achievable
- **Offline**: Works without internet connection

### Negative

- **Limited Nuance**: Can't understand complex context like an LLM
- **Manual Updates**: New patterns require code changes
- **Keyword Dependence**: Relies on matching specific terms

### Neutral

- For CoordMCP's use case (common patterns), rules cover 95% of needs
- Advanced users can still consult external resources for complex decisions
- The transparency of rules is actually beneficial for learning

## Future Considerations

1. **Pattern Library**: Could allow users to define custom patterns
2. **Learning**: Could track which recommendations are accepted/rejected
3. **Community Patterns**: Could share pattern definitions between users

## References

- [Design Patterns - Gang of Four](https://en.wikipedia.org/wiki/Design_Patterns)
- [Pattern Definitions](../../src/coordmcp/architecture/patterns.py)
- [Recommender Implementation](../../src/coordmcp/architecture/recommender.py)
