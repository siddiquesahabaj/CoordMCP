"""
CoordMCP - Main entry point for the FastMCP server.

This module initializes the CoordMCP server, registers all tools and resources,
and starts the FastMCP server to handle client connections.

Usage:
    coordmcp [options]
    python -m coordmcp [options]
    
Options:
    --version   Show version number and exit
    --help      Show help message and exit
    
Environment Variables:
    COORDMCP_DATA_DIR: Data storage directory (default: ~/.coordmcp/data)
    COORDMCP_LOG_LEVEL: Log level (default: INFO)
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Handle --version early before importing heavy modules
if "--version" in sys.argv:
    from coordmcp import __version__
    print(f"coordmcp {__version__}")
    sys.exit(0)

from coordmcp import __version__
from coordmcp.core.server import create_server
from coordmcp.core.tool_manager import register_all_tools
from coordmcp.core.resource_manager import register_all_resources
from coordmcp.logger import get_logger

logger = get_logger("main")


def main():
    """
    Main entry point for the CoordMCP server.
    
    This function:
    1. Parses command line arguments
    2. Creates the FastMCP server
    3. Registers all tools (35+ tools)
    4. Registers all resources (14+ resources)
    5. Starts the server
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="CoordMCP - A FastMCP-based Model Context Protocol server for intelligent multi-agent code coordination",
        prog="coordmcp"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    # Parse args (will exit if --version or --help is passed)
    args = parser.parse_args()
    
    # Start the server
    logger.info(f"Starting CoordMCP server v{__version__}...")
    
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
