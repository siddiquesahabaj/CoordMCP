"""
Resource registration for CoordMCP FastMCP server.

This module handles the registration of all MCP resources, separate from tools.
Resources provide read-only access to project data via MCP resource URIs.
"""

from fastmcp import FastMCP

from coordmcp.resources.project_resources import handle_project_resource
from coordmcp.resources.agent_resources import handle_agent_resource
from coordmcp.resources.architecture_resources import handle_architecture_resource
from coordmcp.logger import get_logger

logger = get_logger("resources")


def register_all_resources(server: FastMCP) -> FastMCP:
    """
    Register all MCP resources with the FastMCP server.
    
    Resources provide read-only access to project data and are accessed via
    MCP resource URIs like 'project://{project_id}' or 'agent://{agent_id}'.
    
    Args:
        server: FastMCP server instance
        
    Returns:
        Server with registered resources
    """
    logger.info("Registering resources...")
    
    # Register all resource types
    _register_project_resources(server)
    _register_agent_resources(server)
    _register_architecture_resources(server)
    
    logger.info("All resources registered successfully")
    return server


def _register_project_resources(server: FastMCP) -> None:
    """
    Register all project-related resources.
    
    Project resources provide access to:
    - Project overview and metadata
    - Architectural decisions
    - Technology stack
    - Architecture definition
    - Recent changes
    - Module information
    """
    logger.debug("Registering project resources...")
    
    @server.resource("project://{project_id}")
    async def project_resource(project_id: str):
        """
        Access project information.
        
        Returns a markdown overview of the project including:
        - Project name and description
        - Creation date and last update
        - Quick stats
        - Links to other project resources
        """
        return await handle_project_resource(f"project://{project_id}")
    
    @server.resource("project://{project_id}/decisions")
    async def project_decisions_resource(project_id: str):
        """
        Access project decisions.
        
        Returns all architectural decisions for the project in markdown format,
        including status, rationale, impact, and related files.
        """
        return await handle_project_resource(f"project://{project_id}/decisions")
    
    @server.resource("project://{project_id}/tech-stack")
    async def project_tech_stack_resource(project_id: str):
        """
        Access project tech stack.
        
        Returns the technology stack with versions, rationale, and
        links to related decisions.
        """
        return await handle_project_resource(f"project://{project_id}/tech-stack")
    
    @server.resource("project://{project_id}/architecture")
    async def project_architecture_resource(project_id: str):
        """
        Access project architecture.
        
        Returns architecture overview with modules, design patterns,
        and structural information.
        """
        return await handle_project_resource(f"project://{project_id}/architecture")
    
    @server.resource("project://{project_id}/recent-changes")
    async def project_changes_resource(project_id: str):
        """
        Access project recent changes.
        
        Returns recent changes with impact assessment and agent information.
        """
        return await handle_project_resource(f"project://{project_id}/recent-changes")
    
    @server.resource("project://{project_id}/modules")
    async def project_modules_resource(project_id: str):
        """
        Access project modules.
        
        Returns list of all modules in the project with summaries.
        """
        return await handle_project_resource(f"project://{project_id}/modules")
    
    @server.resource("project://{project_id}/modules/{module_name}")
    async def project_module_detail_resource(project_id: str, module_name: str):
        """
        Access specific module details.
        
        Returns detailed information about a module including:
        - Purpose and responsibilities
        - Files in the module
        - Dependencies
        """
        return await handle_project_resource(f"project://{project_id}/modules/{module_name}")
    
    logger.debug("Project resources registered")


def _register_agent_resources(server: FastMCP) -> None:
    """
    Register all agent-related resources.
    
    Agent resources provide access to:
    - Agent profiles and capabilities
    - Current working context
    - Locked files
    - Session logs
    - Global agent registry
    """
    logger.debug("Registering agent resources...")
    
    @server.resource("agent://{agent_id}")
    async def agent_resource(agent_id: str):
        """
        Access agent profile.
        
        Returns agent information including name, type, capabilities,
        activity statistics, and project involvement.
        """
        return await handle_agent_resource(f"agent://{agent_id}")
    
    @server.resource("agent://{agent_id}/context")
    async def agent_context_resource(agent_id: str):
        """
        Access agent context.
        
        Returns current working context including objective,
        project, locked files, and recent activity.
        """
        return await handle_agent_resource(f"agent://{agent_id}/context")
    
    @server.resource("agent://{agent_id}/locked-files")
    async def agent_locked_files_resource(agent_id: str):
        """
        Access agent locked files.
        
        Returns all files currently locked by the agent with
        lock timestamps and reasons.
        """
        return await handle_agent_resource(f"agent://{agent_id}/locked-files")
    
    @server.resource("agent://{agent_id}/session-log")
    async def agent_session_log_resource(agent_id: str):
        """
        Access agent session log.
        
        Returns session activity log with events like context switches,
        file locks, and decisions made.
        """
        return await handle_agent_resource(f"agent://{agent_id}/session-log")
    
    @server.resource("agent://registry")
    async def agent_registry_resource():
        """
        Access agent registry.
        
        Returns all registered agents grouped by status (active, inactive, deprecated).
        """
        return await handle_agent_resource("agent://registry")
    
    logger.debug("Agent resources registered")


def _register_architecture_resources(server: FastMCP) -> None:
    """
    Register all architecture-related resources.
    
    Architecture resources provide access to:
    - Design pattern catalog
    - Pattern details and examples
    """
    logger.debug("Registering architecture resources...")
    
    @server.resource("design-patterns://list")
    async def design_patterns_list_resource():
        """
        List all design patterns.
        
        Returns complete catalog of available design patterns with
        descriptions and best use cases.
        """
        return await handle_architecture_resource("design-patterns://list")
    
    @server.resource("design-patterns://{pattern_name}")
    async def design_pattern_resource(pattern_name: str):
        """
        Access specific design pattern.
        
        Returns detailed information about a pattern including:
        - Description and best use cases
        - Structure (files, classes)
        - Example code
        - Best practices
        - Common pitfalls
        """
        return await handle_architecture_resource(f"design-patterns://{pattern_name}")
    
    logger.debug("Architecture resources registered")
