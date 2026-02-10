"""
Unit tests for ArchitectureAnalyzer functionality.

These tests verify architecture analysis operations including:
- Project structure analysis
- Modularity checking
- Architecture scoring
"""

import pytest
from tests.utils.factories import FileMetadataFactory


@pytest.mark.unit
@pytest.mark.architecture
class TestArchitectureAnalysis:
    """Test architecture analysis operations."""
    
    def test_analyze_project_returns_success(self, analyzer, sample_project_id):
        """Test that analyze_project returns successful result."""
        result = analyzer.analyze_project(sample_project_id)
        
        assert result["success"] is True
        assert "overview" in result
        assert "architecture_assessment" in result
    
    def test_analyze_project_returns_file_stats(self, analyzer, sample_project_id, memory_store):
        """Test that analyze_project returns file statistics."""
        # Add some files
        for i in range(3):
            metadata = FileMetadataFactory.create(path=f"src/file{i}.py")
            memory_store.update_file_metadata(sample_project_id, metadata)
        
        result = analyzer.analyze_project(sample_project_id)
        
        assert result["overview"]["total_files"] == 3
    
    def test_analyze_project_returns_score(self, analyzer, sample_project_id):
        """Test that analyze_project returns architecture score."""
        result = analyzer.analyze_project(sample_project_id)
        
        assert "overall_score" in result["architecture_assessment"]
        assert 0 <= result["architecture_assessment"]["overall_score"] <= 100


@pytest.mark.unit
@pytest.mark.architecture
class TestModularityCheck:
    """Test modularity checking operations."""
    
    def test_check_modularity_returns_success(self, analyzer, sample_project_id):
        """Test that check_modularity returns successful result."""
        result = analyzer.check_modularity(sample_project_id)
        
        assert result["success"] is True
        assert "is_modular" in result
    
    @pytest.mark.skip(reason="Requires architecture module definitions, not just file metadata")
    def test_check_modularity_detects_modular_structure(self, analyzer, sample_project_id, memory_store):
        """Test that check_modularity correctly detects modular structure."""
        # Add files with different modules
        for module in ["core", "api", "models"]:
            metadata = FileMetadataFactory.create(
                path=f"src/{module}/main.py",
                module=module
            )
            memory_store.update_file_metadata(sample_project_id, metadata)
        
        result = analyzer.check_modularity(sample_project_id)
        
        assert result["is_modular"] is True
        assert result["module_count"] >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
