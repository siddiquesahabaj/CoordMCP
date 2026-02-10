"""
CoordMCP - Main entry point for the FastMCP server.

This module initializes the CoordMCP server, registers all tools and resources,
and starts the FastMCP server to handle client connections.

Usage:
    python -m coordmcp.main
    
Environment Variables:
    COORDMCP_DATA_DIR: Data storage directory (default: ~/.coordmcp/data)
    COORDMCP_LOG_LEVEL: Log level (default: INFO)
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from coordmcp.core.server import create_server
from coordmcp.core.tool_manager import register_all_tools
from coordmcp.core.resource_manager import register_all_resources
from coordmcp.logger import get_logger

logger = get_logger("main")


def main():
    """
    Main entry point for the CoordMCP server.
    
    This function:
    1. Creates the FastMCP server
    2. Registers all tools (29 tools)
    3. Registers all resources (14 resources)
    4. Starts the server
    """
    logger.info("Starting CoordMCP server...")
    
    # Create the server
    server = create_server()
    logger.info("Server created")
    
    # Register all tools
    server = register_all_tools(server)
    logger.info("Tools registered")
    
    # Register all resources
    server = register_all_resources(server)
    logger.info("Resources registered")
    
    logger.info("CoordMCP server initialized and ready")
    logger.info("Server is listening for MCP connections...")
    
    # Run the server (FastMCP handles the transport)
    server.run()


if __name__ == "__main__":
    main()
