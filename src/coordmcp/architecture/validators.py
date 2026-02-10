"""
Code structure validators for CoordMCP architecture guidance.
"""

import re
from typing import Dict, List, Any, Optional


class ValidationIssue:
    """Represents a validation issue."""
    def __init__(self, severity: str, message: str, suggestion: str = ""):
        self.severity = severity  # error, warning, info
        self.message = message
        self.suggestion = suggestion
    
    def to_dict(self) -> Dict:
        return {
            "severity": self.severity,
            "message": self.message,
            "suggestion": self.suggestion
        }


class CodeStructureValidator:
    """Validates code structure against architectural guidelines."""
    
    # Naming conventions by file type
    NAMING_CONVENTIONS = {
        "python": {
            "class": r"^[A-Z][a-zA-Z0-9]*$",  # PascalCase
            "function": r"^[a-z_][a-z0-9_]*$",  # snake_case
            "constant": r"^[A-Z][A-Z0-9_]*$",  # UPPER_SNAKE_CASE
            "module": r"^[a-z_][a-z0-9_]*$"  # snake_case
        }
    }
    
    def __init__(self):
        """Initialize validator."""
        self.issues: List[ValidationIssue] = []
    
    def validate(
        self,
        project_id: str,
        file_path: str,
        code_structure: Dict,
        strict: bool = False
    ) -> Dict[str, Any]:
        """
        Validate proposed code structure.
        
        Args:
            project_id: Project ID
            file_path: File path
            code_structure: Code structure to validate
            strict: Enable strict mode
            
        Returns:
            Validation report
        """
        self.issues = []
        
        # Validate naming conventions
        self._check_naming_conventions(file_path, code_structure)
        
        # Validate layer separation
        self._check_layer_separation(file_path, code_structure)
        
        # Validate modularity
        self._check_modularity(code_structure)
        
        # Calculate score
        score = self._calculate_validation_score()
        
        return {
            "success": True,
            "is_valid": len([i for i in self.issues if i.severity == "error"]) == 0,
            "score": score,
            "issues": [i.to_dict() for i in self.issues],
            "error_count": len([i for i in self.issues if i.severity == "error"]),
            "warning_count": len([i for i in self.issues if i.severity == "warning"]),
            "info_count": len([i for i in self.issues if i.severity == "info"])
        }
    
    def _check_naming_conventions(self, file_path: str, code_structure: Dict):
        """Check naming conventions."""
        # Determine language from file extension
        language = self._detect_language(file_path)
        
        if language not in self.NAMING_CONVENTIONS:
            return
        
        conventions = self.NAMING_CONVENTIONS[language]
        
        # Check class names
        for class_def in code_structure.get("classes", []):
            class_name = class_def.get("name", "")
            if not re.match(conventions["class"], class_name):
                self.issues.append(ValidationIssue(
                    severity="warning",
                    message=f"Class name '{class_name}' doesn't follow {language} naming conventions",
                    suggestion=f"Use PascalCase for class names (e.g., 'MyClass')"
                ))
        
        # Check function names
        for func_def in code_structure.get("functions", []):
            func_name = func_def.get("name", "")
            if not re.match(conventions["function"], func_name):
                self.issues.append(ValidationIssue(
                    severity="warning",
                    message=f"Function name '{func_name}' doesn't follow {language} naming conventions",
                    suggestion=f"Use snake_case for function names (e.g., 'my_function')"
                ))
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file path."""
        if file_path.endswith(".py"):
            return "python"
        elif file_path.endswith(".js") or file_path.endswith(".ts"):
            return "javascript"
        elif file_path.endswith(".java"):
            return "java"
        return "unknown"
    
    def _check_layer_separation(self, file_path: str, code_structure: Dict):
        """Check layer separation violations."""
        # Check if file mixes concerns
        file_type = self._determine_file_type(file_path)
        
        # Controllers shouldn't have direct DB calls
        if file_type == "controller":
            for class_def in code_structure.get("classes", []):
                methods = class_def.get("methods", [])
                for method in methods:
                    if any(db_word in method.lower() for db_word in ["query", "insert", "update", "delete", "sql"]):
                        self.issues.append(ValidationIssue(
                            severity="error",
                            message=f"Controller has direct database operation: '{method}'",
                            suggestion="Move database operations to a repository layer"
                        ))
        
        # Models shouldn't have business logic
        if file_type == "model":
            for class_def in code_structure.get("classes", []):
                methods = class_def.get("methods", [])
                business_methods = [m for m in methods if any(word in m.lower() 
                    for word in ["process", "calculate", "validate", "compute", "execute"])]
                if len(business_methods) > 3:
                    self.issues.append(ValidationIssue(
                        severity="warning",
                        message=f"Model has {len(business_methods)} business logic methods",
                        suggestion="Consider moving business logic to a service layer"
                    ))
    
    def _determine_file_type(self, file_path: str) -> str:
        """Determine file type from path."""
        path_lower = file_path.lower()
        if any(x in path_lower for x in ["controller", "route", "api", "view"]):
            return "controller"
        elif any(x in path_lower for x in ["service", "business", "logic"]):
            return "service"
        elif any(x in path_lower for x in ["repository", "dao", "data"]):
            return "repository"
        elif any(x in path_lower for x in ["model", "entity", "schema"]):
            return "model"
        return "other"
    
    def _check_modularity(self, code_structure: Dict):
        """Check modularity principles."""
        classes = code_structure.get("classes", [])
        
        # Check for god classes (too many methods)
        for class_def in classes:
            method_count = len(class_def.get("methods", []))
            if method_count > 20:
                self.issues.append(ValidationIssue(
                    severity="warning",
                    message=f"Class '{class_def.get('name')}' has {method_count} methods (god class)",
                    suggestion="Consider splitting into smaller, more focused classes"
                ))
        
        # Check for empty classes
        for class_def in classes:
            if not class_def.get("methods") and not class_def.get("attributes"):
                self.issues.append(ValidationIssue(
                    severity="warning",
                    message=f"Class '{class_def.get('name')}' appears to be empty",
                    suggestion="Add methods or remove if not needed"
                ))
    
    def _calculate_validation_score(self) -> int:
        """Calculate validation score (0-100)."""
        if not self.issues:
            return 100
        
        errors = len([i for i in self.issues if i.severity == "error"])
        warnings = len([i for i in self.issues if i.severity == "warning"])
        
        score = 100
        score -= errors * 20  # Each error costs 20 points
        score -= warnings * 5  # Each warning costs 5 points
        
        return max(0, score)
    
    def validate_naming_convention(self, name: str, convention_type: str, language: str = "python") -> bool:
        """
        Validate a single name against naming conventions.
        
        Args:
            name: Name to validate
            convention_type: Type (class, function, constant, module)
            language: Programming language
            
        Returns:
            True if valid
        """
        if language not in self.NAMING_CONVENTIONS:
            return True
        
        pattern = self.NAMING_CONVENTIONS[language].get(convention_type)
        if not pattern:
            return True
        
        return bool(re.match(pattern, name))
