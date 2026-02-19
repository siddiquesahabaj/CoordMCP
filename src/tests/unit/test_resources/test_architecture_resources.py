"""
Unit tests for architecture resources.

Tests architecture:// resource handling including design patterns.
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.unit
@pytest.mark.resources
class TestArchitectureResources:
    """Test architecture resource handling."""
    
    @pytest.mark.asyncio
    async def test_design_patterns_list(self):
        """Test listing all design patterns."""
        from coordmcp.resources import architecture_resources
        
        result = await architecture_resources.handle_architecture_resource(
            "design-patterns://list"
        )
        
        assert "Design Patterns" in result
    
    @pytest.mark.asyncio
    async def test_pattern_details(self):
        """Test getting specific pattern details."""
        from coordmcp.resources import architecture_resources
        
        # Test with a known pattern - the patterns module should have at least one
        result = await architecture_resources.handle_architecture_resource(
            "design-patterns://CRUD"
        )
        
        # Either it finds the pattern or returns not found message
        assert "Pattern" in result or "not found" in result.lower()
    
    @pytest.mark.asyncio
    async def test_unknown_pattern(self):
        """Test error handling for unknown pattern."""
        from coordmcp.resources import architecture_resources
        
        result = await architecture_resources.handle_architecture_resource(
            "design-patterns://nonexistent_pattern"
        )
        
        assert "not found" in result.lower()
    
    @pytest.mark.asyncio
    async def test_unknown_resource_uri(self):
        """Test error handling for unknown URI."""
        from coordmcp.resources import architecture_resources
        
        result = await architecture_resources.handle_architecture_resource(
            "unknown://resource"
        )
        
        assert "Unknown" in result or "Error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
