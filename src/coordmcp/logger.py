"""
Logging setup for CoordMCP.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from coordmcp.config import get_config


class CoordLogger:
    """CoordMCP logger configuration."""
    
    _initialized = False
    
    @classmethod
    def setup_logging(
        cls,
        log_level: Optional[str] = None,
        log_file: Optional[Path] = None
    ) -> None:
        """Setup logging configuration."""
        if cls._initialized:
            return
        
        config = get_config()
        
        # Use provided values or defaults from config
        level = (log_level or config.log_level).upper()
        file_path = log_file or config.log_file
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup root logger
        root_logger = logging.getLogger("coordmcp")
        root_logger.setLevel(getattr(logging, level))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler with rotation (10MB per file, keep 5 files)
        if file_path:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.handlers.RotatingFileHandler(
                file_path,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(getattr(logging, level))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        cls._initialized = True
        root_logger.info(f"Logging initialized at level {level}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    if not CoordLogger._initialized:
        CoordLogger.setup_logging()
    return logging.getLogger(f"coordmcp.{name}")
