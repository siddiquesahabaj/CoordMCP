"""
Architecture analyzer for CoordMCP.
Analyzes project structure and provides insights.
"""

from typing import Dict, List, Any, Optional
from collections import defaultdict

from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.memory.models import FileMetadata, ArchitectureModule
from coordmcp.logger import get_logger

logger = get_logger("architecture.analyzer")


class ArchitectureAnalyzer:
    """Analyzes project architecture and provides insights."""
    
    def __init__(self, memory_store: ProjectMemoryStore):
        """
        Initialize the architecture analyzer.
        
        Args:
            memory_store: Project memory store
        """
        self.memory_store = memory_store
    
    def analyze_project(self, project_id: str) -> Dict[str, Any]:
        """
        Analyze current project architecture.
        
        Args:
            project_id: Project ID
            
        Returns:
            Analysis results
        """
        if not self.memory_store.project_exists(project_id):
            return {
                "success": False,
                "error": f"Project {project_id} not found"
            }
        
        # Gather data
        project_info = self.memory_store.get_project_info(project_id)
        files = self.memory_store.get_all_file_metadata(project_id)
        modules = self.memory_store.get_all_modules(project_id)
        architecture = self.memory_store.get_architecture(project_id)
        
        # Analyze structure
        analysis = {
            "success": True,
            "project_id": project_id,
            "project_name": project_info.project_name if project_info else "Unknown",
            "overview": {
                "total_files": len(files),
                "total_modules": len(modules),
                "has_architecture_definition": bool(architecture)
            },
            "file_analysis": self._analyze_files(files),
            "module_analysis": self._analyze_modules(modules),
            "dependency_analysis": self._analyze_dependencies(files),
            "architecture_assessment": self._assess_architecture(files, modules, architecture)
        }
        
        logger.info(f"Analyzed architecture for project {project_id}")
        
        return analysis
    
    def _analyze_files(self, files: List[FileMetadata]) -> Dict[str, Any]:
        """Analyze file structure."""
        if not files:
            return {
                "total_files": 0,
                "by_type": {},
                "by_module": {},
                "complexity_distribution": {}
            }
        
        # Count by type
        by_type = defaultdict(int)
        by_module = defaultdict(int)
        complexity_dist = defaultdict(int)
        total_loc = 0
        
        for file in files:
            by_type[file.file_type] += 1
            by_module[file.module] += 1
            complexity_dist[file.complexity] += 1
            total_loc += file.lines_of_code
        
        return {
            "total_files": len(files),
            "by_type": dict(by_type),
            "by_module": dict(by_module),
            "complexity_distribution": dict(complexity_dist),
            "total_lines_of_code": total_loc,
            "average_loc_per_file": total_loc // len(files) if files else 0
        }
    
    def _analyze_modules(self, modules: List[ArchitectureModule]) -> Dict[str, Any]:
        """Analyze module structure."""
        if not modules:
            return {
                "total_modules": 0,
                "modules": [],
                "dependencies": {}
            }
        
        # Map dependencies
        dependency_map = {}
        for module in modules:
            dependency_map[module.name] = module.dependencies
        
        # Check for circular dependencies
        circular_deps = self._detect_circular_dependencies(dependency_map)
        
        return {
            "total_modules": len(modules),
            "modules": [
                {
                    "name": m.name,
                    "purpose": m.purpose,
                    "file_count": len(m.files),
                    "dependencies": m.dependencies
                }
                for m in modules
            ],
            "dependencies": dependency_map,
            "circular_dependencies": circular_deps
        }
    
    def _detect_circular_dependencies(self, dependency_map: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies in modules."""
        circular = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependency_map.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, path + [neighbor])
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    if cycle not in circular:
                        circular.append(cycle)
            
            rec_stack.remove(node)
        
        for node in dependency_map:
            if node not in visited:
                dfs(node, [node])
        
        return circular
    
    def _analyze_dependencies(self, files: List[FileMetadata]) -> Dict[str, Any]:
        """Analyze file dependencies."""
        if not files:
            return {
                "total_dependencies": 0,
                "orphaned_files": [],
                "highly_coupled": []
            }
        
        # Count dependencies per file
        dep_counts = {}
        orphaned = []
        highly_coupled = []
        
        for file in files:
            dep_count = len(file.dependencies) + len(file.dependents)
            dep_counts[file.path] = dep_count
            
            if dep_count == 0 and file.file_type == "source":
                orphaned.append(file.path)
            
            if dep_count > 10:  # Arbitrary threshold
                highly_coupled.append({
                    "file": file.path,
                    "dependency_count": dep_count
                })
        
        total_deps = sum(len(f.dependencies) for f in files)
        
        return {
            "total_dependencies": total_deps,
            "orphaned_files": orphaned,
            "highly_coupled_files": sorted(highly_coupled, key=lambda x: x["dependency_count"], reverse=True),
            "average_dependencies_per_file": total_deps // len(files) if files else 0
        }
    
    def _assess_architecture(
        self,
        files: List[FileMetadata],
        modules: List[ArchitectureModule],
        architecture: Dict
    ) -> Dict[str, Any]:
        """Assess overall architecture quality."""
        issues = []
        strengths = []
        
        # Check for files without modules
        files_in_modules = set()
        for module in modules:
            files_in_modules.update(module.files)
        
        unassigned_files = [f.path for f in files if f.path not in files_in_modules]
        if unassigned_files:
            issues.append({
                "type": "unassigned_files",
                "message": f"{len(unassigned_files)} files not assigned to any module",
                "files": unassigned_files[:10]  # Show first 10
            })
        
        # Check complexity distribution
        high_complexity = [f.path for f in files if f.complexity == "high"]
        if len(high_complexity) > len(files) * 0.2:  # More than 20% high complexity
            issues.append({
                "type": "high_complexity",
                "message": f"{len(high_complexity)} files have high complexity ({len(high_complexity)/len(files)*100:.1f}%)",
                "files": high_complexity[:10]
            })
        
        # Check for architecture definition
        if not architecture:
            issues.append({
                "type": "missing_architecture",
                "message": "No architecture definition found for project"
            })
        else:
            strengths.append({
                "type": "architecture_defined",
                "message": "Project has architecture definition"
            })
        
        # Check module cohesion
        if modules:
            strengths.append({
                "type": "modular_structure",
                "message": f"Project has {len(modules)} defined modules"
            })
        
        # Check for orphaned files
        orphaned = [f.path for f in files if not f.dependencies and not f.dependents and f.file_type == "source"]
        if len(orphaned) > len(files) * 0.1:  # More than 10% orphaned
            issues.append({
                "type": "orphaned_files",
                "message": f"{len(orphaned)} files have no dependencies (potential orphans)",
                "files": orphaned[:10]
            })
        
        return {
            "issues": issues,
            "strengths": strengths,
            "overall_score": self._calculate_score(issues, strengths, len(files), len(modules))
        }
    
    def _calculate_score(
        self,
        issues: List[Dict],
        strengths: List[Dict],
        total_files: int,
        total_modules: int
    ) -> int:
        """Calculate overall architecture score (0-100)."""
        score = 70  # Start with base score
        
        # Adjust for issues
        for issue in issues:
            if issue["type"] == "high_complexity":
                score -= 15
            elif issue["type"] == "missing_architecture":
                score -= 20
            elif issue["type"] == "unassigned_files":
                score -= 10
            elif issue["type"] == "orphaned_files":
                score -= 5
        
        # Adjust for strengths
        for strength in strengths:
            if strength["type"] == "architecture_defined":
                score += 10
            elif strength["type"] == "modular_structure":
                score += 5 * min(total_modules, 5)  # Cap at 25 points
        
        # Ensure score is within bounds
        return max(0, min(100, score))
    
    def check_modularity(self, project_id: str) -> Dict[str, Any]:
        """
        Check project modularity.
        
        Args:
            project_id: Project ID
            
        Returns:
            Modularity assessment
        """
        modules = self.memory_store.get_all_modules(project_id)
        files = self.memory_store.get_all_file_metadata(project_id)
        
        if not modules:
            return {
                "success": True,
                "is_modular": False,
                "message": "No modules defined",
                "recommendation": "Consider defining modules to improve organization"
            }
        
        # Calculate modularity metrics
        files_in_modules = sum(len(m.files) for m in modules)
        coverage = files_in_modules / len(files) if files else 0
        
        # Check for inter-module dependencies
        cross_module_deps = 0
        for module in modules:
            for dep_module in module.dependencies:
                if dep_module in [m.name for m in modules]:
                    cross_module_deps += 1
        
        is_modular = coverage > 0.8 and len(modules) >= 2
        
        return {
            "success": True,
            "is_modular": is_modular,
            "module_count": len(modules),
            "file_coverage": coverage,
            "cross_module_dependencies": cross_module_deps,
            "message": f"Project has {len(modules)} modules covering {coverage*100:.1f}% of files",
            "recommendations": self._get_modularity_recommendations(coverage, modules, files)
        }
    
    def _get_modularity_recommendations(
        self,
        coverage: float,
        modules: List[ArchitectureModule],
        files: List[FileMetadata]
    ) -> List[str]:
        """Generate modularity recommendations."""
        recommendations = []
        
        if coverage < 0.5:
            recommendations.append("Assign remaining files to appropriate modules")
        
        if len(modules) < 2:
            recommendations.append("Consider splitting into multiple modules for better organization")
        
        if len(modules) > 10:
            recommendations.append("Consider consolidating modules - may be too granular")
        
        return recommendations
