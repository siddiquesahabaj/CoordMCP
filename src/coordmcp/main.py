"""
CoordMCP - Main entry point for the FastMCP server.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from coordmcp.core.server import create_server
from coordmcp.core.tool_manager import register_all_tools
from coordmcp.logger import get_logger

logger = get_logger("main")


def main():
    """Main entry point for the CoordMCP server."""
    logger.info("Starting CoordMCP server...")
    
    # Create the server
    server = create_server()
    
    # Register all tools
    server = register_all_tools(server)
    
    logger.info("CoordMCP server initialized and ready")
    
    # Run the server (FastMCP handles the transport)
    server.run()


if __name__ == "__main__":
    main()
