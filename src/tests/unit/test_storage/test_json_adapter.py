"""
Unit tests for JSONStorageBackend functionality.

Tests cover:
- Basic CRUD operations (save, load, delete, exists)
- Listing operations
- Security validation (path traversal prevention)
- Edge cases and error handling
"""

import pytest
import json
from pathlib import Path

from coordmcp.storage.json_adapter import JSONStorageBackend


@pytest.mark.unit
@pytest.mark.storage
class TestJSONStorageBasicOperations:
    """Test basic CRUD operations."""
    
    def test_save_creates_file(self, fresh_temp_dir):
        """Test that save creates a JSON file."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        result = storage.save("test_key", {"data": "value"})
        
        assert result is True
        assert (fresh_temp_dir / "test_key.json").exists()
    
    def test_save_returns_true_on_success(self, fresh_temp_dir):
        """Test that save returns True on success."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        result = storage.save("test_key", {"data": "value"})
        
        assert result is True
    
    def test_save_creates_nested_directories(self, fresh_temp_dir):
        """Test that save creates nested directories for keys with slashes."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        result = storage.save("nested/deep/key", {"data": "value"})
        
        assert result is True
        assert (fresh_temp_dir / "nested" / "deep" / "key.json").exists()
    
    def test_load_returns_saved_data(self, fresh_temp_dir):
        """Test that load returns the saved data."""
        storage = JSONStorageBackend(fresh_temp_dir)
        data = {"name": "test", "value": 123, "nested": {"key": "value"}}
        
        storage.save("test_key", data)
        loaded = storage.load("test_key")
        
        assert loaded == data
    
    def test_load_missing_key_returns_none(self, fresh_temp_dir):
        """Test that load returns None for missing keys."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        result = storage.load("nonexistent")
        
        assert result is None
    
    def test_delete_removes_file(self, fresh_temp_dir):
        """Test that delete removes the file."""
        storage = JSONStorageBackend(fresh_temp_dir)
        storage.save("test_key", {"data": "value"})
        
        result = storage.delete("test_key")
        
        assert result is True
        assert not (fresh_temp_dir / "test_key.json").exists()
    
    def test_delete_nonexistent_returns_true(self, fresh_temp_dir):
        """Test that delete returns True even for nonexistent keys."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        result = storage.delete("nonexistent")
        
        assert result is True
    
    def test_exists_returns_true_for_saved(self, fresh_temp_dir):
        """Test that exists returns True for saved data."""
        storage = JSONStorageBackend(fresh_temp_dir)
        storage.save("test_key", {"data": "value"})
        
        result = storage.exists("test_key")
        
        assert result is True
    
    def test_exists_returns_false_for_missing(self, fresh_temp_dir):
        """Test that exists returns False for missing keys."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        result = storage.exists("nonexistent")
        
        assert result is False


@pytest.mark.unit
@pytest.mark.storage
class TestJSONStorageListOperations:
    """Test listing operations."""
    
    def test_list_keys_returns_all_keys(self, fresh_temp_dir):
        """Test that list_keys returns all saved keys."""
        storage = JSONStorageBackend(fresh_temp_dir)
        storage.save("key1", {"data": 1})
        storage.save("key2", {"data": 2})
        storage.save("key3", {"data": 3})
        
        keys = storage.list_keys()
        
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys
        assert "key3" in keys
    
    def test_list_keys_with_prefix_filter(self, fresh_temp_dir):
        """Test that list_keys filters by prefix."""
        storage = JSONStorageBackend(fresh_temp_dir)
        storage.save("project/key1", {"data": 1})
        storage.save("project/key2", {"data": 2})
        storage.save("other/key3", {"data": 3})
        
        keys = storage.list_keys("project")
        
        assert len(keys) == 2
        assert all(k.startswith("project") for k in keys)
    
    def test_list_keys_returns_sorted_keys(self, fresh_temp_dir):
        """Test that list_keys returns sorted keys."""
        storage = JSONStorageBackend(fresh_temp_dir)
        storage.save("z_key", {"data": 1})
        storage.save("a_key", {"data": 2})
        storage.save("m_key", {"data": 3})
        
        keys = storage.list_keys()
        
        assert keys == ["a_key", "m_key", "z_key"]
    
    def test_list_keys_empty_storage(self, fresh_temp_dir):
        """Test list_keys on empty storage."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        keys = storage.list_keys()
        
        assert keys == []
    
    def test_batch_save_multiple_items(self, fresh_temp_dir):
        """Test batch_save saves multiple items."""
        storage = JSONStorageBackend(fresh_temp_dir)
        items = {
            "key1": {"data": 1},
            "key2": {"data": 2},
            "key3": {"data": 3}
        }
        
        result = storage.batch_save(items)
        
        assert result is True
        assert storage.exists("key1")
        assert storage.exists("key2")
        assert storage.exists("key3")


@pytest.mark.unit
@pytest.mark.storage
class TestJSONStorageSecurity:
    """Test security validation."""
    
    def test_path_traversal_dotdot_rejected(self, fresh_temp_dir):
        """Test that path traversal with .. is rejected."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        with pytest.raises(ValueError, match="path traversal"):
            storage.save("../outside", {"data": "value"})
    
    def test_path_traversal_absolute_rejected(self, fresh_temp_dir):
        """Test that absolute paths are rejected."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        with pytest.raises(ValueError, match="path traversal"):
            storage.save("/etc/passwd", {"data": "value"})
    
    def test_path_traversal_backslash_rejected(self, fresh_temp_dir):
        """Test that backslash absolute paths are rejected."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        with pytest.raises(ValueError, match="path traversal"):
            storage.save("\\\\server\\share", {"data": "value"})
    
    def test_invalid_key_special_chars_rejected(self, fresh_temp_dir):
        """Test that invalid characters in keys are rejected."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        with pytest.raises(ValueError, match="Invalid key"):
            storage.save("key with spaces", {"data": "value"})
    
    def test_invalid_key_dots_rejected(self, fresh_temp_dir):
        """Test that . and .. in key paths are rejected."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        with pytest.raises(ValueError):
            storage.save("path/./key", {"data": "value"})


@pytest.mark.unit
@pytest.mark.storage
class TestJSONStorageValidation:
    """Test input validation."""
    
    def test_save_empty_key_rejected(self, fresh_temp_dir):
        """Test that empty key is rejected."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        result = storage.save("", {"data": "value"})
        
        assert result is False
    
    def test_save_none_key_rejected(self, fresh_temp_dir):
        """Test that None key is rejected."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        result = storage.save(None, {"data": "value"})
        
        assert result is False
    
    def test_save_non_dict_rejected(self, fresh_temp_dir):
        """Test that non-dict data is rejected."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        result = storage.save("test_key", "not a dict")
        
        assert result is False
    
    def test_delete_empty_key_rejected(self, fresh_temp_dir):
        """Test that delete with empty key is handled."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        result = storage.delete("")
        
        assert result is False


@pytest.mark.unit
@pytest.mark.storage
class TestJSONStorageEdgeCases:
    """Test edge cases."""
    
    def test_overwrite_existing_key(self, fresh_temp_dir):
        """Test that save overwrites existing data."""
        storage = JSONStorageBackend(fresh_temp_dir)
        storage.save("test_key", {"data": "original"})
        
        storage.save("test_key", {"data": "updated"})
        loaded = storage.load("test_key")
        
        assert loaded == {"data": "updated"}
    
    def test_save_complex_nested_data(self, fresh_temp_dir):
        """Test saving complex nested data structures."""
        storage = JSONStorageBackend(fresh_temp_dir)
        complex_data = {
            "level1": {
                "level2": {
                    "level3": ["a", "b", "c"],
                    "number": 123,
                    "boolean": True,
                    "null": None
                }
            },
            "list": [1, 2, 3],
            "datetime": "2024-01-01T00:00:00"
        }
        
        storage.save("complex", complex_data)
        loaded = storage.load("complex")
        
        assert loaded == complex_data
    
    def test_load_corrupted_json_returns_none(self, fresh_temp_dir):
        """Test that corrupted JSON returns None."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        # Write invalid JSON directly
        corrupted_file = fresh_temp_dir / "corrupted.json"
        corrupted_file.write_text("{ invalid json }")
        
        result = storage.load("corrupted")
        
        assert result is None
    
    def test_base_dir_created_if_not_exists(self, fresh_temp_dir):
        """Test that base_dir is created if it doesn't exist."""
        new_dir = fresh_temp_dir / "new_storage"
        
        storage = JSONStorageBackend(new_dir)
        
        assert new_dir.exists()
    
    def test_atomic_write_uses_temp_file(self, fresh_temp_dir):
        """Test that writes use temp file then rename."""
        storage = JSONStorageBackend(fresh_temp_dir)
        
        storage.save("test_key", {"data": "value"})
        
        # Temp file should not exist after save
        assert not (fresh_temp_dir / "test_key.tmp").exists()
        # Final file should exist
        assert (fresh_temp_dir / "test_key.json").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
