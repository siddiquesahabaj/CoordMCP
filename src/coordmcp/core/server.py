"""
FastMCP server setup and configuration.
"""

from fastmcp import FastMCP

from coordmcp.config import get_config
from coordmcp.logger import get_logger
from coordmcp.storage.json_adapter import JSONStorageBackend

logger = get_logger("core.server")

# Global storage instance (singleton pattern)
_storage_instance = None


def get_storage() -> JSONStorageBackend:
    """Get the global storage instance."""
    global _storage_instance
    if _storage_instance is None:
        config = get_config()
        _storage_instance = JSONStorageBackend(config.data_dir)
        logger.info("Storage backend initialized")
    return _storage_instance


def create_server() -> FastMCP:
    """
    Create and configure the FastMCP server.
    
    Returns:
        Configured FastMCP instance
    """
    config = get_config()
    
    # Create FastMCP server
    server = FastMCP(
        name="CoordMCP",
        instructions="""
        CoordMCP - Multi-Agent Code Coordination Server
        
        This MCP server provides:
        - Long-term memory for projects (decisions, tech stack, changes)
        - Multi-agent context switching and file locking
        - Architectural guidance and recommendations
        
        Use the available tools to coordinate between multiple coding agents
        and maintain project context across sessions.
        """
    )
    
    # Initialize storage backend
    storage = get_storage()
    
    logger.info(f"CoordMCP server v{config.version} created")
    return server
