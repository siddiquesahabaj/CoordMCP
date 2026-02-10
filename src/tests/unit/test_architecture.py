"""
Unit tests for Architecture components
"""

import pytest
import tempfile
from pathlib import Path
from coordmcp.storage.json_adapter import JSONStorageBackend
from coordmcp.memory.json_store import ProjectMemoryStore
from coordmcp.architecture.analyzer import ArchitectureAnalyzer
from coordmcp.architecture.recommender import ArchitectureRecommender
from coordmcp.architecture.validators import CodeStructureValidator


class TestArchitectureAnalyzer:
    """Test suite for ArchitectureAnalyzer"""
    
    @pytest.fixture
    def temp_storage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            backend = JSONStorageBackend(Path(tmpdir))
            yield backend
    
    @pytest.fixture
    def analyzer(self, temp_storage):
        store = ProjectMemoryStore(temp_storage)
        return ArchitectureAnalyzer(store)
    
    def test_analyze_project(self, analyzer, temp_storage):
        """Test project analysis"""
        store = ProjectMemoryStore(temp_storage)
        project_id = store.create_project("Test Project")
        
        result = analyzer.analyze_project(project_id)
        
        assert result["success"] is True
        assert "overview" in result
        assert "architecture_assessment" in result
    
    def test_check_modularity(self, analyzer, temp_storage):
        """Test modularity check"""
        store = ProjectMemoryStore(temp_storage)
        project_id = store.create_project("Test Project")
        
        result = analyzer.check_modularity(project_id)
        
        assert result["success"] is True
        assert "is_modular" in result


class TestCodeStructureValidator:
    """Test suite for CodeStructureValidator"""
    
    def test_validate_structure(self):
        """Test code structure validation"""
        validator = CodeStructureValidator()
        
        code_structure = {
            "classes": ["MyClass"],
            "functions": ["my_function"]
        }
        
        result = validator.validate(
            project_id="proj-1",
            file_path="src/test.py",
            code_structure=code_structure
        )
        
        assert result["success"] is True
        assert "score" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
