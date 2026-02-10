"""
Tool registration for CoordMCP FastMCP server.
"""

from fastmcp import FastMCP

from coordmcp.tools import memory_tools
from coordmcp.tools import context_tools
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
    
    # ==================== Agent Registration Tools ====================
    
    @server.tool()
    async def register_agent(
        agent_name: str,
        agent_type: str,
        capabilities: list = [],
        version: str = "1.0.0"
    ):
        """Register a new agent in the global registry."""
        return await context_tools.register_agent(
            agent_name, agent_type, capabilities, version
        )
    
    @server.tool()
    async def get_agents_list(status: str = "all"):
        """Get list of all registered agents."""
        return await context_tools.get_agents_list(status)
    
    @server.tool()
    async def get_agent_profile(agent_id: str):
        """Get an agent's profile information."""
        return await context_tools.get_agent_profile(agent_id)
    
    # ==================== Context Management Tools ====================
    
    @server.tool()
    async def start_context(
        agent_id: str,
        project_id: str,
        objective: str,
        task_description: str = "",
        priority: str = "medium",
        current_file: str = ""
    ):
        """Start a new work context for an agent."""
        return await context_tools.start_context(
            agent_id, project_id, objective, task_description,
            priority, current_file
        )
    
    @server.tool()
    async def get_agent_context(agent_id: str):
        """Get current context for an agent."""
        return await context_tools.get_agent_context(agent_id)
    
    @server.tool()
    async def switch_context(
        agent_id: str,
        to_project_id: str,
        to_objective: str,
        task_description: str = "",
        priority: str = "medium"
    ):
        """Switch agent context between projects or objectives."""
        return await context_tools.switch_context(
            agent_id, to_project_id, to_objective,
            task_description, priority
        )
    
    @server.tool()
    async def end_context(agent_id: str):
        """End an agent's current context."""
        return await context_tools.end_context(agent_id)
    
    # ==================== File Locking Tools ====================
    
    @server.tool()
    async def lock_files(
        agent_id: str,
        project_id: str,
        files: list,
        reason: str,
        expected_duration_minutes: int = 60
    ):
        """Lock files to prevent conflicts between agents."""
        return await context_tools.lock_files(
            agent_id, project_id, files, reason, expected_duration_minutes
        )
    
    @server.tool()
    async def unlock_files(
        agent_id: str,
        project_id: str,
        files: list
    ):
        """Unlock files after work is complete."""
        return await context_tools.unlock_files(agent_id, project_id, files)
    
    @server.tool()
    async def get_locked_files(project_id: str):
        """Get list of currently locked files in a project."""
        return await context_tools.get_locked_files(project_id)
    
    # ==================== Session & History Tools ====================
    
    @server.tool()
    async def get_context_history(agent_id: str, limit: int = 10):
        """Get recent context history for an agent."""
        return await context_tools.get_context_history(agent_id, limit)
    
    @server.tool()
    async def get_session_log(agent_id: str, limit: int = 50):
        """Get session log for an agent."""
        return await context_tools.get_session_log(agent_id, limit)
    
    @server.tool()
    async def get_agents_in_project(project_id: str):
        """Get all agents currently working in a project."""
        return await context_tools.get_agents_in_project(project_id)
    
    logger.info("All tools registered successfully")
    return server
