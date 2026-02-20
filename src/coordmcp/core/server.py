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
        
        ⚠️ MANDATORY: All agents MUST follow the CoordMCP workflow:
        
        1. discover_project() or create_project() - FIRST step
        2. register_agent() - Register your agent identity
        3. start_context() - Begin a work context
        4. lock_files() - Lock files before editing
        5. log_change() - Document changes after editing
        6. unlock_files() - Unlock files when done
        7. end_context() - End your work session
        
        Get started with: await get_workflow_guidance_tool()
        Check your state with: await validate_workflow_state_tool(agent_id)
        
        This server provides:
        - Long-term memory for projects (decisions, tech stack, changes)
        - Multi-agent context switching and file locking
        - Architectural guidance and recommendations
        - Task management and agent messaging
        
        Use the available tools to coordinate between multiple coding agents
        and maintain project context across sessions.
        
        IMPORTANT: Read the system prompt at startup using get_system_prompt() tool
        or see SYSTEM_PROMPT.md in the CoordMCP directory.
        """
    )
    
    # Initialize storage backend
    storage = get_storage()
    
    logger.info(f"CoordMCP server v{config.version} created")
    return server
