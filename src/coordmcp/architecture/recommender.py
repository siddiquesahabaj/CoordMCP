"""
Architecture recommendation engine for CoordMCP.
Provides recommendations without LLM calls using rule-based logic.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import uuid4

from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.architecture.analyzer import ArchitectureAnalyzer
from coordmcp.architecture.patterns import (
    get_pattern, suggest_pattern, get_patterns_for_feature
)
from coordmcp.memory.models import ArchitectureModule
from coordmcp.logger import get_logger

logger = get_logger("architecture.recommender")


class ArchitectureRecommender:
    """
    Provides architectural recommendations using rule-based logic.
    NO LLM calls - all recommendations are deterministic.
    """
    
    def __init__(self, memory_store: ProjectMemoryStore, analyzer: ArchitectureAnalyzer):
        """
        Initialize the recommendation engine.
        
        Args:
            memory_store: Project memory store
            analyzer: Architecture analyzer
        """
        self.memory_store = memory_store
        self.analyzer = analyzer
    
    def recommend_structure(
        self,
        project_id: str,
        feature_description: str,
        context: str = "",
        constraints: List[str] = [],
        implementation_style: str = "modular"
    ) -> Dict[str, Any]:
        """
        Get architectural recommendation for a new feature or change.
        
        Args:
            project_id: Project ID
            feature_description: Description of the feature
            context: Additional context
            constraints: List of constraints
            implementation_style: Style preference (modular, monolithic, auto)
            
        Returns:
            Recommendation with file structure, code structure, and implementation guide
        """
        if not self.memory_store.project_exists(project_id):
            return {
                "success": False,
                "error": f"Project {project_id} not found"
            }
        
        constraints = constraints or []
        
        # Step 1: Analyze current architecture
        current_arch = self.analyzer.analyze_project(project_id)
        
        # Step 2: Suggest design patterns
        pattern_suggestions = suggest_pattern(feature_description, context)
        
        # Step 3: Select best pattern based on current architecture
        selected_pattern = self._select_best_pattern(
            pattern_suggestions,
            current_arch,
            implementation_style
        )
        
        # Step 4: Generate file structure
        file_structure = self._generate_file_structure(
            feature_description,
            selected_pattern,
            current_arch,
            constraints
        )
        
        # Step 5: Generate code structure
        code_structure = self._generate_code_structure(
            feature_description,
            selected_pattern,
            file_structure
        )
        
        # Step 6: Analyze architecture impact
        arch_impact = self._analyze_architecture_impact(
            file_structure,
            code_structure,
            current_arch
        )
        
        # Step 7: Generate implementation steps
        implementation_guide = self._generate_implementation_guide(
            file_structure,
            code_structure,
            arch_impact
        )
        
        # Step 8: Generate design principles
        design_principles = self._generate_design_principles(selected_pattern)
        
        recommendation = {
            "success": True,
            "recommendation_id": str(uuid4()),
            "timestamp": datetime.now().isoformat(),
            "project_id": project_id,
            "request": {
                "feature_description": feature_description,
                "context": context,
                "constraints": constraints
            },
            "current_architecture_summary": {
                "total_files": current_arch.get("overview", {}).get("total_files", 0),
                "total_modules": current_arch.get("overview", {}).get("total_modules", 0),
                "architecture_score": current_arch.get("architecture_assessment", {}).get("overall_score", 0)
            },
            "recommended_pattern": selected_pattern,
            "alternative_patterns": [
                p for p in pattern_suggestions
                if p["pattern"] != selected_pattern["pattern"]
            ],
            "file_structure": file_structure,
            "code_structure": code_structure,
            "architecture_impact": arch_impact,
            "design_principles": design_principles,
            "implementation_guide": implementation_guide,
            "status": "pending"
        }
        
        logger.info(f"Generated recommendation for project {project_id}")
        
        return recommendation
    
    def _select_best_pattern(
        self,
        pattern_suggestions: List[Dict],
        current_arch: Dict,
        implementation_style: str
    ) -> Dict:
        """Select the best pattern based on context."""
        if not pattern_suggestions:
            # Default to CRUD
            return {
                "pattern": "CRUD",
                "confidence": "high",
                "reason": "Default pattern for data operations",
                "description": "Basic Create, Read, Update, Delete operations",
                "best_for": ["simple data models"]
            }
        
        # For modular style, prefer patterns that support modularity
        if implementation_style == "modular":
            # Prefer Repository or Service patterns
            for p in pattern_suggestions:
                if p["pattern"] in ["Repository", "Service", "Layered"]:
                    return p
        
        # For monolithic style, prefer simpler patterns
        if implementation_style == "monolithic":
            for p in pattern_suggestions:
                if p["pattern"] in ["CRUD", "MVC"]:
                    return p
        
        # Return highest confidence suggestion
        return pattern_suggestions[0]
    
    def _generate_file_structure(
        self,
        feature_description: str,
        pattern: Dict,
        current_arch: Dict,
        constraints: List[str]
    ) -> Dict[str, Any]:
        """Generate file structure recommendations."""
        pattern_name = pattern["pattern"]
        pattern_def = get_pattern(pattern_name)
        
        if not pattern_def:
            pattern_def = get_pattern("CRUD")
        
        # Extract feature name from description
        feature_name = self._extract_feature_name(feature_description)
        
        new_files = []
        
        # Generate files based on pattern template
        if pattern_def and "structure" in pattern_def and "files" in pattern_def["structure"]:
            for file_template in pattern_def["structure"]["files"]:
                file_path = file_template["path"].format(name=feature_name.lower())
                
                # Check constraints
                if any(c in file_path for c in constraints):
                    continue
                
                new_files.append({
                    "path": file_path,
                    "purpose": file_template["purpose"],
                    "type": self._determine_file_type(file_path),
                    "suggested_content_outline": self._generate_content_outline(
                        file_path, pattern_name, feature_name
                    )
                })
        
        # Identify files that might need modification
        modified_files = self._identify_modified_files(
            feature_description, current_arch
        )
        
        return {
            "new_files": new_files,
            "modified_files": modified_files,
            "deleted_files": [],
            "total_new_files": len(new_files),
            "total_modified_files": len(modified_files)
        }
    
    def _extract_feature_name(self, description: str) -> str:
        """Extract feature name from description."""
        # Simple heuristic: take first few words
        words = description.split()[:3]
        return "".join(w.capitalize() for w in words if w.isalpha())
    
    def _determine_file_type(self, file_path: str) -> str:
        """Determine file type from path."""
        if "test" in file_path.lower():
            return "test"
        elif any(x in file_path for x in ["model", "schema", "entity"]):
            return "model"
        elif any(x in file_path for x in ["service", "business"]):
            return "service"
        elif any(x in file_path for x in ["repository", "data"]):
            return "repository"
        elif any(x in file_path for x in ["controller", "route", "api"]):
            return "controller"
        else:
            return "module"
    
    def _generate_content_outline(
        self,
        file_path: str,
        pattern_name: str,
        feature_name: str
    ) -> str:
        """Generate content outline for a file."""
        outlines = {
            "model": f"""
Class {feature_name}:
    - Define data attributes
    - Validation methods
    - Serialization methods
""",
            "repository": f"""
Class {feature_name}Repository:
    - create(data) -> {feature_name}
    - get_by_id(id) -> {feature_name}
    - update(id, data) -> {feature_name}
    - delete(id) -> bool
    - list(filters) -> List[{feature_name}]
""",
            "service": f"""
Class {feature_name}Service:
    - create_{feature_name.lower()}(data)
    - get_{feature_name.lower()}(id)
    - update_{feature_name.lower()}(id, data)
    - delete_{feature_name.lower()}(id)
    - list_{feature_name.lower()}s(filters)
    - validate_{feature_name.lower()}(data)
""",
            "controller": f"""
{feature_name} Routes/Controller:
    - POST /{feature_name.lower()}s (create)
    - GET /{feature_name.lower()}s/:id (get)
    - PUT /{feature_name.lower()}s/:id (update)
    - DELETE /{feature_name.lower()}s/:id (delete)
    - GET /{feature_name.lower()}s (list)
""",
            "default": f"""
{feature_name} implementation:
    - Main functionality
    - Helper methods
    - Error handling
"""
        }
        
        file_type = self._determine_file_type(file_path)
        return outlines.get(file_type, outlines["default"])
    
    def _identify_modified_files(
        self,
        feature_description: str,
        current_arch: Dict
    ) -> List[Dict]:
        """Identify files that might need modification."""
        modified = []
        
        # Check if there are existing modules
        modules = current_arch.get("module_analysis", {}).get("modules", [])
        
        # If there's a module that seems related, suggest modifying it
        desc_lower = feature_description.lower()
        for module in modules:
            module_name = module["name"].lower()
            if any(word in desc_lower for word in module_name.split("_")):
                modified.append({
                    "path": f"modules/{module['name']}/__init__.py",
                    "modifications": f"Register new components with {module['name']} module"
                })
        
        # Suggest updating main app file
        modified.append({
            "path": "src/main.py",
            "modifications": "Register new routes/services"
        })
        
        return modified
    
    def _generate_code_structure(
        self,
        feature_description: str,
        pattern: Dict,
        file_structure: Dict
    ) -> Dict[str, Any]:
        """Generate code structure recommendations."""
        pattern_name = pattern["pattern"]
        pattern_def = get_pattern(pattern_name)
        feature_name = self._extract_feature_name(feature_description)
        
        new_classes = []
        new_functions = []
        
        if pattern_def and "code_structure" in pattern_def:
            code_def = pattern_def["code_structure"]
            
            # Generate classes based on pattern
            if "classes" in code_def:
                for class_template in code_def["classes"]:
                    class_name = class_template["name"].format(Name=feature_name)
                    methods = [
                        m.format(name=feature_name.lower())
                        for m in class_template.get("methods", [])
                    ]
                    
                    new_classes.append({
                        "name": class_name,
                        "purpose": class_template.get("purpose", ""),
                        "methods": methods,
                        "module": f"{feature_name.lower()}_{self._determine_file_type(class_name.lower())}",
                        "design_pattern": pattern_name
                    })
        
        # Generate additional functions if needed
        new_functions.append({
            "name": f"initialize_{feature_name.lower()}",
            "signature": f"def initialize_{feature_name.lower()}() -> None",
            "purpose": f"Initialize {feature_name} components",
            "module": f"{feature_name.lower()}_setup"
        })
        
        # Suggest refactoring if needed
        refactoring_suggestions = []
        if pattern_name == "Layered" and len(file_structure["new_files"]) > 5:
            refactoring_suggestions.append(
                "Consider breaking into smaller features if this becomes too large"
            )
        
        return {
            "new_classes": new_classes,
            "new_functions": new_functions,
            "refactoring_suggestions": refactoring_suggestions,
            "total_new_classes": len(new_classes),
            "total_new_functions": len(new_functions)
        }
    
    def _analyze_architecture_impact(
        self,
        file_structure: Dict,
        code_structure: Dict,
        current_arch: Dict
    ) -> Dict[str, Any]:
        """Analyze the impact on overall architecture."""
        new_files = file_structure["new_files"]
        new_classes = code_structure["new_classes"]
        
        # Determine if new modules are needed
        new_modules = []
        
        # Check if this introduces a new domain
        if len(new_files) >= 3:
            # Suggest a module
            module_name = self._extract_feature_name(
                " ".join(f["path"] for f in new_files[:2])
            )
            new_modules.append({
                "name": module_name,
                "purpose": f"Module for {module_name} functionality",
                "dependencies": [],
                "rationale": "Groups related functionality together"
            })
        
        # Assess layer changes
        layer_changes = []
        layers_affected = set()
        
        for file_info in new_files:
            file_type = file_info["type"]
            if file_type == "model":
                layers_affected.add("data")
            elif file_type == "service":
                layers_affected.add("business")
            elif file_type == "controller":
                layers_affected.add("presentation")
        
        if layers_affected:
            layer_changes.append(
                f"Affects layers: {', '.join(sorted(layers_affected))}"
            )
        
        return {
            "new_modules": new_modules,
            "layer_changes": "\n".join(layer_changes) if layer_changes else "None",
            "scalability_notes": self._generate_scalability_notes(new_files, new_classes),
            "future_expandability": self._generate_expandability_notes(new_modules)
        }
    
    def _generate_scalability_notes(self, new_files: List[Dict], new_classes: List[Dict]) -> str:
        """Generate scalability notes."""
        notes = []
        
        if len(new_files) > 10:
            notes.append("Consider breaking into smaller features to maintain scalability")
        
        if len(new_classes) > 5:
            notes.append("Large number of classes - ensure proper abstraction")
        
        # Check for potential bottlenecks
        has_repository = any(f["type"] == "repository" for f in new_files)
        if has_repository:
            notes.append("Database access via repository pattern - consider caching for high traffic")
        
        return "\n".join(notes) if notes else "No major scalability concerns"
    
    def _generate_expandability_notes(self, new_modules: List[Dict]) -> str:
        """Generate future expandability notes."""
        if new_modules:
            return f"New module '{new_modules[0]['name']}' provides clear extension point for related features"
        return "Feature can be extended by adding methods to existing classes"
    
    def _generate_design_principles(self, pattern: Dict) -> List[Dict]:
        """Generate design principles for the recommendation."""
        principles = []
        
        # Get pattern principles
        pattern_name = pattern["pattern"]
        pattern_def = get_pattern(pattern_name)
        
        if pattern_def and "design_principles" in pattern_def:
            for principle_text in pattern_def["design_principles"]:
                principles.append({
                    "principle": principle_text,
                    "application": f"Applied in {pattern_name} pattern implementation",
                    "rationale": "Ensures maintainability and testability"
                })
        
        # Add general SOLID principles
        principles.extend([
            {
                "principle": "Single Responsibility",
                "application": "Each class has one reason to change",
                "rationale": "Improves maintainability"
            },
            {
                "principle": "Dependency Inversion",
                "application": "Depend on abstractions, not concrete implementations",
                "rationale": "Enables testing and flexibility"
            }
        ])
        
        return principles
    
    def _generate_implementation_guide(
        self,
        file_structure: Dict,
        code_structure: Dict,
        arch_impact: Dict
    ) -> Dict[str, Any]:
        """Generate step-by-step implementation guide."""
        steps = []
        step_num = 1
        
        # Step 1: Create models
        model_files = [f for f in file_structure["new_files"] if f["type"] == "model"]
        if model_files:
            steps.append({
                "order": step_num,
                "description": "Create data models",
                "files_affected": [f["path"] for f in model_files]
            })
            step_num += 1
        
        # Step 2: Create repositories
        repo_files = [f for f in file_structure["new_files"] if f["type"] == "repository"]
        if repo_files:
            steps.append({
                "order": step_num,
                "description": "Implement data access layer (repositories)",
                "files_affected": [f["path"] for f in repo_files]
            })
            step_num += 1
        
        # Step 3: Create services
        service_files = [f for f in file_structure["new_files"] if f["type"] == "service"]
        if service_files:
            steps.append({
                "order": step_num,
                "description": "Implement business logic (services)",
                "files_affected": [f["path"] for f in service_files]
            })
            step_num += 1
        
        # Step 4: Create controllers/routes
        controller_files = [f for f in file_structure["new_files"] if f["type"] == "controller"]
        if controller_files:
            steps.append({
                "order": step_num,
                "description": "Create API endpoints (controllers/routes)",
                "files_affected": [f["path"] for f in controller_files]
            })
            step_num += 1
        
        # Step 5: Create remaining files
        other_files = [f for f in file_structure["new_files"] 
                      if f["type"] not in ["model", "repository", "service", "controller"]]
        if other_files:
            steps.append({
                "order": step_num,
                "description": "Create remaining supporting files",
                "files_affected": [f["path"] for f in other_files]
            })
            step_num += 1
        
        # Step 6: Update existing files
        if file_structure["modified_files"]:
            steps.append({
                "order": step_num,
                "description": "Update existing files to integrate new components",
                "files_affected": [f["path"] for f in file_structure["modified_files"]]
            })
            step_num += 1
        
        # Step 7: Testing
        steps.append({
            "order": step_num,
            "description": "Write tests for new functionality",
            "files_affected": ["tests/"]
        })
        
        # Estimate effort
        effort = self._estimate_effort(file_structure, code_structure)
        
        return {
            "steps": steps,
            "estimated_effort": effort,
            "testing_strategy": "Write unit tests for services and repositories, integration tests for API endpoints"
        }
    
    def _estimate_effort(self, file_structure: Dict, code_structure: Dict) -> str:
        """Estimate implementation effort."""
        new_file_count = len(file_structure["new_files"])
        new_class_count = len(code_structure["new_classes"])
        
        if new_file_count <= 2:
            return "Small (2-4 hours)"
        elif new_file_count <= 5:
            return "Medium (1-2 days)"
        elif new_file_count <= 10:
            return "Large (3-5 days)"
        else:
            return "Very Large (1-2 weeks)"
