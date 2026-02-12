"""
JSON file-based storage adapter for CoordMCP.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any

from coordmcp.storage.base import StorageBackend
from coordmcp.logger import get_logger

logger = get_logger("storage.json")


class JSONStorageBackend(StorageBackend):
    """JSON file-based storage implementation."""
    
    def __init__(self, base_dir: Path):
        """
        Initialize JSON storage backend.
        
        Args:
            base_dir: Base directory for all JSON files
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"JSON storage initialized at {self.base_dir}")
    
    def _get_file_path(self, key: str) -> Path:
        """Convert key to file path with security validation."""
        import re
        
        # Security: Prevent path traversal attacks
        if ".." in key or key.startswith("/") or key.startswith("\\"):
            raise ValueError(f"Invalid key contains path traversal attempt: {key}")
        
        # Security: Sanitize key to prevent directory traversal
        # Only allow alphanumeric characters, hyphens, underscores, and forward slashes
        if not re.match(r'^[\w\-/]+$', key):
            raise ValueError(f"Invalid key format. Key must contain only alphanumeric characters, hyphens, underscores, and forward slashes: {key}")
        
        # Replace path separators with underscores for flat storage
        # Or use nested directories if key contains slashes
        if "/" in key:
            parts = key.split("/")
            # Validate each part
            for part in parts[:-1]:
                if not part or part in ('.', '..'):
                    raise ValueError(f"Invalid directory component in key: {key}")
            
            dir_path = self.base_dir / "/".join(parts[:-1])
            dir_path.mkdir(parents=True, exist_ok=True)
            return dir_path / f"{parts[-1]}.json"
        return self.base_dir / f"{key}.json"
    
    def save(self, key: str, data: Dict[str, Any]) -> bool:
        """Save data to JSON file with atomic write."""
        try:
            # Validate inputs
            if not isinstance(key, str) or not key.strip():
                logger.error("Invalid key: key must be a non-empty string")
                return False
            
            if not isinstance(data, dict):
                logger.error("Invalid data: data must be a dictionary")
                return False
            
            file_path = self._get_file_path(key)
            temp_path = file_path.with_suffix('.tmp')
            
            # Write to temp file first (atomic operation)
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            # Rename temp file to actual file (atomic on most systems)
            os.replace(temp_path, file_path)
            
            logger.debug(f"Saved data for key '{key}'")
            return True
            
        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error saving data for key '{key}': {type(e).__name__}")
            return False
    
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """Load data from JSON file."""
        try:
            file_path = self._get_file_path(key)
            
            if not file_path.exists():
                logger.debug(f"No data found for key '{key}'")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.debug(f"Loaded data for key '{key}'")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted JSON data for key '{key}': {e}")
            return None
        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error loading data for key '{key}': {type(e).__name__}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete JSON file."""
        try:
            # Validate input
            if not isinstance(key, str) or not key.strip():
                logger.error("Invalid key: key must be a non-empty string")
                return False
            
            file_path = self._get_file_path(key)
            
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted data for key '{key}'")
            
            return True
            
        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Error deleting data for key '{key}': {type(e).__name__}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if JSON file exists."""
        file_path = self._get_file_path(key)
        return file_path.exists()
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with optional prefix filter."""
        keys = []
        
        if prefix:
            search_dir = self.base_dir / prefix
        else:
            search_dir = self.base_dir
        
        if not search_dir.exists():
            return keys
        
        for json_file in search_dir.rglob("*.json"):
            # Convert file path back to key
            relative_path = json_file.relative_to(self.base_dir)
            key = str(relative_path.with_suffix('')).replace(os.sep, '/')
            keys.append(key)
        
        return sorted(keys)
    
    def batch_save(self, items: Dict[str, Dict[str, Any]]) -> bool:
        """Save multiple items."""
        try:
            for key, data in items.items():
                if not self.save(key, data):
                    return False
            return True
        except Exception as e:
            logger.error(f"Error in batch save: {e}")
            return False
