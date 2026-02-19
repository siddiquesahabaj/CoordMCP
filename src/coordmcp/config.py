"""
Configuration management for CoordMCP.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

from coordmcp import __version__

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """CoordMCP configuration settings."""
    
    # Data storage
    data_dir: Path = field(default_factory=lambda: Path.home() / ".coordmcp" / "data")
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    
    # File locking
    max_file_locks_per_agent: int = 100
    lock_timeout_hours: int = 24
    auto_cleanup_stale_locks: bool = True
    
    # Features
    enable_compression: bool = False
    
    # Version
    version: str = __version__
    
    def __post_init__(self):
        """Initialize derived paths."""
        if self.log_file is None:
            self.log_file = self.data_dir / "logs" / "coordmcp.log"


def expand_path_variables(path: str) -> str:
    """
    Expand variables in path strings.
    
    Supports:
    - ${WorkspaceFolder} or ${workspaceFolder} - Current working directory
    - ${HOME} or ~ - User home directory
    - ${USER} - Current username
    - Environment variables
    """
    import getpass
    
    # Expand environment variables
    path = os.path.expandvars(path)
    
    # Expand user home (~)
    path = os.path.expanduser(path)
    
    # Handle WorkspaceFolder variables (OpenCode/VSCode convention)
    if "${WorkspaceFolder}" in path or "${workspaceFolder}" in path:
        # Try to get from environment first
        workspace = os.getenv("WORKSPACE_FOLDER") or os.getenv("workspaceFolder")
        if not workspace:
            # Fall back to current working directory
            workspace = os.getcwd()
        path = path.replace("${WorkspaceFolder}", workspace)
        path = path.replace("${workspaceFolder}", workspace)
    
    # Handle USER variable if not already expanded
    if "${USER}" in path:
        path = path.replace("${USER}", getpass.getuser())
    
    return path


def load_config() -> Config:
    """Load configuration from environment variables."""
    config = Config()
    
    # Always use global storage in ~/.coordmcp/data
    # Local/workspace storage removed to ensure all agents share the same data
    config.data_dir = Path.home() / ".coordmcp" / "data"
    
    if log_level := os.getenv("COORDMCP_LOG_LEVEL"):
        config.log_level = log_level
    
    if max_locks := os.getenv("COORDMCP_MAX_FILE_LOCKS_PER_AGENT"):
        config.max_file_locks_per_agent = int(max_locks)
    
    if timeout := os.getenv("COORDMCP_LOCK_TIMEOUT_HOURS"):
        config.lock_timeout_hours = int(timeout)
    
    if enable_compression := os.getenv("COORDMCP_ENABLE_COMPRESSION"):
        config.enable_compression = enable_compression.lower() == "true"
    
    # Ensure directories exist
    config.data_dir.mkdir(parents=True, exist_ok=True)
    (config.data_dir / "logs").mkdir(parents=True, exist_ok=True)
    (config.data_dir / "memory").mkdir(parents=True, exist_ok=True)
    (config.data_dir / "agents").mkdir(parents=True, exist_ok=True)
    (config.data_dir / "global").mkdir(parents=True, exist_ok=True)
    
    return config


# Global config instance (cached)
_config: Optional[Config] = None


def get_config() -> Config:
    """Get cached configuration instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config
