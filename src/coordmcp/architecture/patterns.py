"""
Design patterns reference for CoordMCP architecture guidance.
"""

from typing import Dict, List, Any, Optional


# Design patterns catalog with structure recommendations
DESIGN_PATTERNS = {
    "CRUD": {
        "name": "CRUD",
        "description": "Basic Create, Read, Update, Delete operations",
        "best_for": ["simple data models", "admin interfaces", "basic APIs"],
        "structure": {
            "files": [
                {"path": "models/{name}.py", "purpose": "Data model definition"},
                {"path": "repositories/{name}_repository.py", "purpose": "Data access layer"},
                {"path": "services/{name}_service.py", "purpose": "Business logic"},
                {"path": "api/{name}_routes.py", "purpose": "API endpoints"},
                {"path": "schemas/{name}_schema.py", "purpose": "Request/response schemas"}
            ]
        },
        "design_principles": [
            "Separation of concerns between layers",
            "Repository pattern for data access",
            "Service layer for business logic"
        ],
        "code_structure": {
            "classes": [
                {
                    "name": "{Name}Repository",
                    "methods": ["create", "get_by_id", "update", "delete", "list"],
                    "purpose": "Database operations"
                },
                {
                    "name": "{Name}Service",
                    "methods": ["create", "get", "update", "delete", "list"],
                    "purpose": "Business logic"
                }
            ]
        }
    },
    
    "Repository": {
        "name": "Repository",
        "description": "Data access abstraction layer",
        "best_for": ["database operations", "data access abstraction", "testing"],
        "structure": {
            "files": [
                {"path": "repositories/base.py", "purpose": "Abstract repository interface"},
                {"path": "repositories/{name}_repository.py", "purpose": "Concrete implementation"},
                {"path": "repositories/factory.py", "purpose": "Repository creation"}
            ]
        },
        "design_principles": [
            "Abstract data access from business logic",
            "Easy to swap implementations",
            "Simplifies unit testing with mocks"
        ],
        "code_structure": {
            "classes": [
                {
                    "name": "I{Name}Repository",
                    "type": "abstract",
                    "methods": ["add", "get", "update", "remove"],
                    "purpose": "Interface definition"
                },
                {
                    "name": "{Name}Repository",
                    "methods": ["add", "get", "update", "remove"],
                    "purpose": "Database implementation"
                }
            ]
        }
    },
    
    "Service": {
        "name": "Service",
        "description": "Business logic layer",
        "best_for": ["complex business rules", "transaction management", "coordination"],
        "structure": {
            "files": [
                {"path": "services/{name}_service.py", "purpose": "Business logic implementation"},
                {"path": "services/interfaces.py", "purpose": "Service interfaces"},
                {"path": "services/exceptions.py", "purpose": "Service-specific exceptions"}
            ]
        },
        "design_principles": [
            "Encapsulate business rules",
            "Coordinate multiple repositories",
            "Handle transactions"
        ],
        "code_structure": {
            "classes": [
                {
                    "name": "{Name}Service",
                    "methods": ["execute", "validate", "process"],
                    "purpose": "Business logic"
                }
            ]
        }
    },
    
    "Factory": {
        "name": "Factory",
        "description": "Object creation pattern",
        "best_for": ["complex object creation", "multiple implementations", "runtime selection"],
        "structure": {
            "files": [
                {"path": "factories/{name}_factory.py", "purpose": "Object creation logic"},
                {"path": "factories/registry.py", "purpose": "Factory registration"}
            ]
        },
        "design_principles": [
            "Encapsulate object creation",
            "Decouple object creation from usage",
            "Support multiple implementations"
        ],
        "code_structure": {
            "classes": [
                {
                    "name": "{Name}Factory",
                    "methods": ["create", "register"],
                    "purpose": "Object creation"
                }
            ]
        }
    },
    
    "Strategy": {
        "name": "Strategy",
        "description": "Algorithm selection pattern",
        "best_for": ["multiple algorithms", "runtime strategy selection", "behavioral variations"],
        "structure": {
            "files": [
                {"path": "strategies/base.py", "purpose": "Strategy interface"},
                {"path": "strategies/{name}_strategy.py", "purpose": "Concrete strategy"},
                {"path": "strategies/context.py", "purpose": "Strategy context"}
            ]
        },
        "design_principles": [
            "Define family of algorithms",
            "Make them interchangeable",
            "Strategy independent of clients"
        ],
        "code_structure": {
            "classes": [
                {
                    "name": "I{Name}Strategy",
                    "type": "abstract",
                    "methods": ["execute"],
                    "purpose": "Strategy interface"
                },
                {
                    "name": "Concrete{Name}Strategy",
                    "methods": ["execute"],
                    "purpose": "Strategy implementation"
                }
            ]
        }
    },
    
    "Observer": {
        "name": "Observer",
        "description": "Event-driven subscription pattern",
        "best_for": ["event handling", "notification systems", "loose coupling"],
        "structure": {
            "files": [
                {"path": "observers/base.py", "purpose": "Observer interface"},
                {"path": "observers/{name}_observer.py", "purpose": "Concrete observer"},
                {"path": "events/{name}_event.py", "purpose": "Event definitions"}
            ]
        },
        "design_principles": [
            "Define one-to-many dependency",
            "Notify observers automatically",
            "Loose coupling between subjects and observers"
        ],
        "code_structure": {
            "classes": [
                {
                    "name": "Subject",
                    "methods": ["attach", "detach", "notify"],
                    "purpose": "Observable object"
                },
                {
                    "name": "IObserver",
                    "type": "abstract",
                    "methods": ["update"],
                    "purpose": "Observer interface"
                }
            ]
        }
    },
    
    "Adapter": {
        "name": "Adapter",
        "description": "Interface adaptation pattern",
        "best_for": ["integration with external systems", "interface compatibility", "legacy code"],
        "structure": {
            "files": [
                {"path": "adapters/{name}_adapter.py", "purpose": "Adapter implementation"},
                {"path": "adapters/interfaces.py", "purpose": "Target interface"}
            ]
        },
        "design_principles": [
            "Convert interface to another",
            "Enable incompatible interfaces to work together",
            "Wrap existing classes"
        ],
        "code_structure": {
            "classes": [
                {
                    "name": "ITarget",
                    "type": "abstract",
                    "methods": ["request"],
                    "purpose": "Target interface"
                },
                {
                    "name": "{Name}Adapter",
                    "methods": ["request"],
                    "purpose": "Adapter implementation"
                }
            ]
        }
    },
    
    "MVC": {
        "name": "MVC",
        "description": "Model-View-Controller pattern",
        "best_for": ["web applications", "UI frameworks", "separation of concerns"],
        "structure": {
            "files": [
                {"path": "models/{name}.py", "purpose": "Data and business logic"},
                {"path": "views/{name}_view.py", "purpose": "Presentation layer"},
                {"path": "controllers/{name}_controller.py", "purpose": "Request handling"}
            ]
        },
        "design_principles": [
            "Separation of Model, View, Controller",
            "Model independent of UI",
            "Controller handles user input"
        ],
        "code_structure": {
            "classes": [
                {
                    "name": "{Name}Model",
                    "methods": ["get_data", "update_data"],
                    "purpose": "Data model"
                },
                {
                    "name": "{Name}View",
                    "methods": ["render", "update"],
                    "purpose": "View logic"
                },
                {
                    "name": "{Name}Controller",
                    "methods": ["handle_request", "update_model", "update_view"],
                    "purpose": "Controller logic"
                }
            ]
        }
    },
    
    "Layered": {
        "name": "Layered",
        "description": "N-tier architecture",
        "best_for": ["enterprise applications", "clear separation", "maintainability"],
        "structure": {
            "files": [
                {"path": "presentation/{name}_controller.py", "purpose": "UI/API layer"},
                {"path": "business/{name}_service.py", "purpose": "Business logic"},
                {"path": "data/{name}_repository.py", "purpose": "Data access"}
            ],
            "layers": ["presentation", "business", "data"]
        },
        "design_principles": [
            "Organize by functional layers",
            "Lower layers independent of higher",
            "Each layer has specific responsibility"
        ],
        "code_structure": {
            "layers": {
                "presentation": ["controllers", "views", "dto"],
                "business": ["services", "domain", "logic"],
                "data": ["repositories", "models", "access"]
            }
        }
    }
}


def get_pattern(pattern_name: str) -> Optional[Dict[str, Any]]:
    """
    Get a design pattern by name.
    
    Args:
        pattern_name: Name of the pattern
        
    Returns:
        Pattern definition or None if not found
    """
    return DESIGN_PATTERNS.get(pattern_name)


def get_patterns_for_feature(feature_type: str) -> List[str]:
    """
    Get recommended patterns for a feature type.
    
    Args:
        feature_type: Type of feature (e.g., 'api', 'database', 'ui')
        
    Returns:
        List of recommended pattern names
    """
    feature_patterns = {
        "api": ["CRUD", "Service", "Layered"],
        "database": ["Repository", "CRUD", "Factory"],
        "ui": ["MVC", "Observer", "Strategy"],
        "integration": ["Adapter", "Factory", "Strategy"],
        "processing": ["Strategy", "Observer", "Service"],
        "workflow": ["Service", "Observer", "Strategy"],
        "configuration": ["Factory", "Strategy"]
    }
    
    return feature_patterns.get(feature_type.lower(), ["CRUD", "Service"])


def get_all_patterns() -> Dict[str, Dict[str, Any]]:
    """
    Get all available design patterns.
    
    Returns:
        Dictionary of all patterns
    """
    return DESIGN_PATTERNS.copy()


def suggest_pattern(feature_description: str, context: str = "") -> List[Dict[str, Any]]:
    """
    Suggest design patterns based on feature description.
    
    Args:
        feature_description: Description of the feature
        context: Additional context
        
    Returns:
        List of recommended patterns with reasons
    """
    description_lower = feature_description.lower()
    context_lower = context.lower()
    combined = description_lower + " " + context_lower
    
    suggestions = []
    
    # Rule-based pattern matching
    keywords_to_patterns = {
        "database": ("Repository", "For data access abstraction and testability"),
        "api": ("CRUD", "For standard REST API operations"),
        "rest": ("CRUD", "For RESTful API structure"),
        "endpoint": ("CRUD", "For API endpoint organization"),
        "web": ("MVC", "For web application structure"),
        "ui": ("MVC", "For user interface organization"),
        "interface": ("MVC", "For presentation layer separation"),
        "integration": ("Adapter", "For integrating external systems"),
        "external": ("Adapter", "For external system compatibility"),
        "third-party": ("Adapter", "For third-party integrations"),
        "algorithm": ("Strategy", "For interchangeable algorithms"),
        "strategy": ("Strategy", "For runtime algorithm selection"),
        "behavior": ("Strategy", "For behavioral variations"),
        "event": ("Observer", "For event-driven architecture"),
        "notification": ("Observer", "For notification systems"),
        "subscribe": ("Observer", "For subscription patterns"),
        "create": ("Factory", "For object creation logic"),
        "instantiate": ("Factory", "For object instantiation"),
        "business": ("Service", "For business logic encapsulation"),
        "logic": ("Service", "For business rules"),
        "rule": ("Service", "For business rules"),
        "layer": ("Layered", "For n-tier architecture"),
        "tier": ("Layered", "For tiered architecture"),
        "enterprise": ("Layered", "For enterprise application structure")
    }
    
    suggested_names = set()
    
    for keyword, (pattern_name, reason) in keywords_to_patterns.items():
        if keyword in combined and pattern_name not in suggested_names:
            pattern = get_pattern(pattern_name)
            if pattern:
                suggestions.append({
                    "pattern": pattern_name,
                    "confidence": "high" if keyword in description_lower else "medium",
                    "reason": reason,
                    "description": pattern["description"],
                    "best_for": pattern["best_for"]
                })
                suggested_names.add(pattern_name)
    
    # Always suggest CRUD and Service as defaults
    if "CRUD" not in suggested_names:
        pattern = get_pattern("CRUD")
        if pattern:
            suggestions.append({
                "pattern": "CRUD",
                "confidence": "low",
                "reason": "Standard pattern for data operations",
                "description": pattern["description"],
                "best_for": pattern["best_for"]
            })
    
    return suggestions
