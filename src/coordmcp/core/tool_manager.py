"""
Tool registration for CoordMCP FastMCP server.
"""

from fastmcp import FastMCP

from coordmcp.tools import memory_tools
from coordmcp.logger import get_logger

logger = get_logger("tools")


def register_all_tools(server: FastMCP) -> FastMCP:
    """
    Register all tools with the FastMCP server.
    
    Args:
        server: FastMCP server instance
        
    Returns:
        Server with registered tools
    """
    logger.info("Registering tools...")
    
    # ==================== Project Tools ====================
    
    @server.tool()
    async def create_project(project_name: str, description: str = ""):
        """Create a new project in the memory system."""
        return await memory_tools.create_project(project_name, description)
    
    @server.tool()
    async def get_project_info(project_id: str):
        """Get information about a project."""
        return await memory_tools.get_project_info(project_id)
    
    # ==================== Decision Tools ====================
    
    @server.tool()
    async def save_decision(
        project_id: str,
        title: str,
        description: str,
        rationale: str,
        context: str = "",
        impact: str = "",
        tags: list = [],
        related_files: list = [],
        author_agent: str = ""
    ):
        """Save a major architectural or technical decision to project memory."""
        return await memory_tools.save_decision(
            project_id, title, description, rationale,
            context, impact, tags, related_files, author_agent
        )
    
    @server.tool()
    async def get_project_decisions(
        project_id: str,
        status: str = "all",
        tags: list = []
    ):
        """Retrieve all major decisions for a project."""
        return await memory_tools.get_project_decisions(
            project_id, status, tags
        )
    
    @server.tool()
    async def search_decisions(
        project_id: str,
        query: str,
        tags: list = []
    ):
        """Search through decisions by keywords or metadata."""
        return await memory_tools.search_decisions(
            project_id, query, tags
        )
    
    # ==================== Tech Stack Tools ====================
    
    @server.tool()
    async def update_tech_stack(
        project_id: str,
        category: str,
        technology: str,
        version: str = "",
        rationale: str = "",
        decision_ref: str = ""
    ):
        """Update technology stack information for a project."""
        return await memory_tools.update_tech_stack(
            project_id, category, technology, version, rationale, decision_ref
        )
    
    @server.tool()
    async def get_tech_stack(project_id: str, category: str = ""):
        """Get current technology stack for a project."""
        return await memory_tools.get_tech_stack(project_id, category or None)
    
    # ==================== Change Log Tools ====================
    
    @server.tool()
    async def log_change(
        project_id: str,
        file_path: str,
        change_type: str,
        description: str,
        agent_id: str = "",
        code_summary: str = "",
        architecture_impact: str = "none",
        related_decision: str = ""
    ):
        """Log a recent change to project structure or architecture."""
        return await memory_tools.log_change(
            project_id, file_path, change_type, description,
            agent_id, code_summary, architecture_impact, related_decision
        )
    
    @server.tool()
    async def get_recent_changes(
        project_id: str,
        limit: int = 20,
        architecture_impact_filter: str = "all"
    ):
        """Get recent changes to a project."""
        return await memory_tools.get_recent_changes(
            project_id, limit, architecture_impact_filter
        )
    
    # ==================== File Metadata Tools ====================
    
    @server.tool()
    async def update_file_metadata(
        project_id: str,
        file_path: str,
        file_type: str = "source",
        module: str = "",
        purpose: str = "",
        dependencies: list = [],
        dependents: list = [],
        lines_of_code: int = 0,
        complexity: str = "low",
        last_modified_by: str = ""
    ):
        """Update metadata for a file in the project."""
        return await memory_tools.update_file_metadata(
            project_id, file_path, file_type, module, purpose,
            dependencies, dependents, lines_of_code,
            complexity, last_modified_by
        )
    
    @server.tool()
    async def get_file_dependencies(
        project_id: str,
        file_path: str,
        direction: str = "dependencies"
    ):
        """Get dependency graph for a file."""
        return await memory_tools.get_file_dependencies(
            project_id, file_path, direction
        )
    
    @server.tool()
    async def get_module_info(project_id: str, module_name: str):
        """Get detailed information about a project module."""
        return await memory_tools.get_module_info(project_id, module_name)
    
    logger.info("All tools registered successfully")
    return server
