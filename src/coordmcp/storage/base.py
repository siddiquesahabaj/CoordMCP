"""
Abstract storage backend interface for CoordMCP.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def save(self, key: str, data: Dict[str, Any]) -> bool:
        """
        Save data to storage.
        
        Args:
            key: Unique identifier for the data
            data: Dictionary to store
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Load data from storage.
        
        Args:
            key: Unique identifier for the data
            
        Returns:
            Dictionary if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete data from storage.
        
        Args:
            key: Unique identifier for the data
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if data exists.
        
        Args:
            key: Unique identifier for the data
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def list_keys(self, prefix: str = "") -> List[str]:
        """
        List all keys with optional prefix filter.
        
        Args:
            prefix: Optional prefix to filter keys
            
        Returns:
            List of keys
        """
        pass
    
    @abstractmethod
    def batch_save(self, items: Dict[str, Dict[str, Any]]) -> bool:
        """
        Save multiple items atomically.
        
        Args:
            items: Dictionary of key -> data mappings
            
        Returns:
            True if all successful, False otherwise
        """
        pass
