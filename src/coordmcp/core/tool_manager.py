"""
Tool registration for CoordMCP FastMCP server.

This module handles the registration of all MCP tools.
Resources are handled separately by resource_manager.py.

Usage:
    from coordmcp.core.tool_manager import register_all_tools
    server = create_server()
    server = register_all_tools(server)
"""

from fastmcp import FastMCP

from coordmcp.tools import memory_tools
from coordmcp.tools import context_tools
from coordmcp.tools import architecture_tools
from coordmcp.logger import get_logger

logger = get_logger("tools")


def register_all_tools(server: FastMCP) -> FastMCP:
    """
    Register all MCP tools with the FastMCP server.
    
    This function registers all tool categories:
    - Memory tools (project, decision, tech stack, changes)
    - Context tools (agents, contexts, file locking)
    - Architecture tools (analysis, recommendations, validation)
    
    Args:
        server: FastMCP server instance
        
    Returns:
        Server with registered tools
        
    Example:
        >>> server = create_server()
        >>> server = register_all_tools(server)
        >>> # Server now has all tools registered
    """
    logger.info("Registering tools...")
    
    # Register tools by category
    _register_memory_tools(server)
    _register_context_tools(server)
    _register_architecture_tools(server)
    
    logger.info("All tools registered successfully")
    return server


def _register_memory_tools(server: FastMCP) -> None:
    """
    Register memory management tools.
    
    These tools handle:
    - Project creation and management
    - Architectural decisions
    - Technology stack tracking
    - Change logging
    - File metadata
    """
    logger.debug("Registering memory tools...")
    
    # ==================== Project Tools ====================
    
    @server.tool()
    async def create_project(project_name: str, description: str = ""):
        """
        Create a new project in the memory system.
        
        Args:
            project_name: Name of the project (required)
            description: Project description (optional)
            
        Returns:
            Dictionary with project_id and success status
            
        Example:
            >>> result = await create_project("My API", "RESTful API service")
            >>> print(result["project_id"])
        """
        return await memory_tools.create_project(project_name, description)
    
    @server.tool()
    async def get_project_info(project_id: str):
        """
        Get information about a project.
        
        Args:
            project_id: Project ID (required)
            
        Returns:
            Dictionary with project information
        """
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
        """
        Save a major architectural or technical decision to project memory.
        
        Args:
            project_id: Project ID
            title: Decision title
            description: Detailed description
            rationale: Why this decision was made
            context: Context around the decision
            impact: Expected impact
            tags: List of tags for categorization
            related_files: List of related file paths
            author_agent: ID of the agent making the decision
            
        Returns:
            Dictionary with decision_id and success status
        """
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
        """
        Retrieve all major decisions for a project.
        
        Args:
            project_id: Project ID
            status: Filter by status (active, archived, superseded, all)
            tags: Filter by tags
            
        Returns:
            Dictionary with list of decisions
        """
        return await memory_tools.get_project_decisions(
            project_id, status, tags
        )
    
    @server.tool()
    async def search_decisions(
        project_id: str,
        query: str,
        tags: list = []
    ):
        """
        Search through decisions by keywords or metadata.
        
        Args:
            project_id: Project ID
            query: Search query string
            tags: Optional tags to filter by
            
        Returns:
            Dictionary with matching decisions
        """
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
        """
        Update technology stack information for a project.
        
        Args:
            project_id: Project ID
            category: Category (backend, frontend, database, infrastructure)
            technology: Technology name
            version: Version string
            rationale: Why this technology was chosen
            decision_ref: Reference to a decision ID
            
        Returns:
            Dictionary with success status
        """
        return await memory_tools.update_tech_stack(
            project_id, category, technology, version, rationale, decision_ref
        )
    
    @server.tool()
    async def get_tech_stack(project_id: str, category: str = ""):
        """
        Get current technology stack for a project.
        
        Args:
            project_id: Project ID
            category: Optional specific category to retrieve
            
        Returns:
            Dictionary with tech stack information
        """
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
        """
        Log a recent change to project structure or architecture.
        
        Args:
            project_id: Project ID
            file_path: Path of the file changed
            change_type: Type of change (create, modify, delete, refactor)
            description: Description of the change
            agent_id: ID of the agent making the change
            code_summary: Brief code summary
            architecture_impact: Impact level (none, minor, significant)
            related_decision: Related decision ID
            
        Returns:
            Dictionary with change_id and success status
        """
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
        """
        Get recent changes to a project.
        
        Args:
            project_id: Project ID
            limit: Maximum number of changes to return
            architecture_impact_filter: Filter by impact (all, none, minor, significant)
            
        Returns:
            Dictionary with list of changes
        """
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
        """
        Update metadata for a file in the project.
        
        Args:
            project_id: Project ID
            file_path: File path
            file_type: Type (source, test, config, doc)
            module: Module name
            purpose: Purpose description
            dependencies: Files this file depends on
            dependents: Files that depend on this file
            lines_of_code: Lines of code
            complexity: Complexity level (low, medium, high)
            last_modified_by: Agent who last modified
            
        Returns:
            Dictionary with success status
        """
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
        """
        Get dependency graph for a file.
        
        Args:
            project_id: Project ID
            file_path: File path
            direction: dependencies, dependents, or both
            
        Returns:
            Dictionary with file dependencies
        """
        return await memory_tools.get_file_dependencies(
            project_id, file_path, direction
        )
    
    @server.tool()
    async def get_module_info(project_id: str, module_name: str):
        """
        Get detailed information about a project module.
        
        Args:
            project_id: Project ID
            module_name: Name of the module
            
        Returns:
            Dictionary with module information
        """
        return await memory_tools.get_module_info(project_id, module_name)
    
    logger.debug("Memory tools registered")


def _register_context_tools(server: FastMCP) -> None:
    """
    Register context management tools.
    
    These tools handle:
    - Agent registration and profiles
    - Context lifecycle (start, switch, end)
    - File locking and conflict prevention
    - Session logging and history
    """
    logger.debug("Registering context tools...")
    
    # ==================== Agent Registration Tools ====================
    
    @server.tool()
    async def register_agent(
        agent_name: str,
        agent_type: str,
        capabilities: list = [],
        version: str = "1.0.0"
    ):
        """
        Register a new agent in the global registry.
        
        Args:
            agent_name: Name of the agent
            agent_type: Type (opencode, cursor, claude_code, custom)
            capabilities: List of agent capabilities
            version: Agent version
            
        Returns:
            Dictionary with agent_id and success status
        """
        return await context_tools.register_agent(
            agent_name, agent_type, capabilities, version
        )
    
    @server.tool()
    async def get_agents_list(status: str = "all"):
        """
        Get list of all registered agents.
        
        Args:
            status: Filter by status (active, inactive, deprecated, all)
            
        Returns:
            Dictionary with list of agents
        """
        return await context_tools.get_agents_list(status)
    
    @server.tool()
    async def get_agent_profile(agent_id: str):
        """
        Get an agent's profile information.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Dictionary with agent profile
        """
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
        """
        Start a new work context for an agent.
        
        Args:
            agent_id: Agent ID
            project_id: Project ID
            objective: Current objective
            task_description: Detailed task description
            priority: Priority level (critical, high, medium, low)
            current_file: Current file being worked on
            
        Returns:
            Dictionary with context information
        """
        return await context_tools.start_context(
            agent_id, project_id, objective, task_description,
            priority, current_file
        )
    
    @server.tool()
    async def get_agent_context(agent_id: str):
        """
        Get current context for an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Dictionary with agent context
        """
        return await context_tools.get_agent_context(agent_id)
    
    @server.tool()
    async def switch_context(
        agent_id: str,
        to_project_id: str,
        to_objective: str,
        task_description: str = "",
        priority: str = "medium"
    ):
        """
        Switch agent context between projects or objectives.
        
        Args:
            agent_id: Agent ID
            to_project_id: Target project ID
            to_objective: New objective
            task_description: New task description
            priority: Priority level
            
        Returns:
            Dictionary with new context information
        """
        return await context_tools.switch_context(
            agent_id, to_project_id, to_objective,
            task_description, priority
        )
    
    @server.tool()
    async def end_context(agent_id: str):
        """
        End an agent's current context.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Dictionary with success status
        """
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
        """
        Lock files to prevent conflicts between agents.
        
        Args:
            agent_id: Agent ID
            project_id: Project ID
            files: List of file paths to lock
            reason: Reason for locking
            expected_duration_minutes: Expected duration in minutes
            
        Returns:
            Dictionary with locked files or conflicts
        """
        return await context_tools.lock_files(
            agent_id, project_id, files, reason, expected_duration_minutes
        )
    
    @server.tool()
    async def unlock_files(
        agent_id: str,
        project_id: str,
        files: list
    ):
        """
        Unlock files after work is complete.
        
        Args:
            agent_id: Agent ID
            project_id: Project ID
            files: List of file paths to unlock
            
        Returns:
            Dictionary with unlocked files
        """
        return await context_tools.unlock_files(agent_id, project_id, files)
    
    @server.tool()
    async def get_locked_files(project_id: str):
        """
        Get list of currently locked files in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary with locked files by agent
        """
        return await context_tools.get_locked_files(project_id)
    
    # ==================== Session & History Tools ====================
    
    @server.tool()
    async def get_context_history(agent_id: str, limit: int = 10):
        """
        Get recent context history for an agent.
        
        Args:
            agent_id: Agent ID
            limit: Maximum number of entries
            
        Returns:
            Dictionary with context history
        """
        return await context_tools.get_context_history(agent_id, limit)
    
    @server.tool()
    async def get_session_log(agent_id: str, limit: int = 50):
        """
        Get session log for an agent.
        
        Args:
            agent_id: Agent ID
            limit: Maximum number of entries
            
        Returns:
            Dictionary with session log
        """
        return await context_tools.get_session_log(agent_id, limit)
    
    @server.tool()
    async def get_agents_in_project(project_id: str):
        """
        Get all agents currently working in a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary with list of active agents
        """
        return await context_tools.get_agents_in_project(project_id)
    
    logger.debug("Context tools registered")


def _register_architecture_tools(server: FastMCP) -> None:
    """
    Register architecture guidance tools.
    
    These tools handle:
    - Project architecture analysis
    - Design recommendations
    - Code structure validation
    - Design pattern catalog
    """
    logger.debug("Registering architecture tools...")
    
    @server.tool()
    async def analyze_architecture(project_id: str):
        """
        Analyze current project architecture.
        
        Args:
            project_id: Project ID
            
        Returns:
            Dictionary with architecture analysis
        """
        return await architecture_tools.analyze_architecture(project_id)
    
    @server.tool()
    async def get_architecture_recommendation(
        project_id: str,
        feature_description: str,
        context: str = "",
        constraints: list = [],
        implementation_style: str = "modular"
    ):
        """
        Get architectural recommendation for a new feature or change.
        
        Args:
            project_id: Project ID
            feature_description: Description of the feature
            context: Additional context
            constraints: Implementation constraints
            implementation_style: Style (modular, monolithic, auto)
            
        Returns:
            Dictionary with recommendation
        """
        return await architecture_tools.get_architecture_recommendation(
            project_id, feature_description, context, constraints, implementation_style
        )
    
    @server.tool()
    async def validate_code_structure(
        project_id: str,
        file_path: str,
        code_structure: dict,
        strict_mode: bool = False
    ):
        """
        Validate if proposed code structure follows architectural guidelines.
        
        Args:
            project_id: Project ID
            file_path: File path
            code_structure: Proposed code structure
            strict_mode: Strict validation
            
        Returns:
            Dictionary with validation results
        """
        return await architecture_tools.validate_code_structure(
            project_id, file_path, code_structure, strict_mode
        )
    
    @server.tool()
    async def get_design_patterns():
        """
        Get all available design patterns.
        
        Returns:
            Dictionary with design patterns
        """
        return await architecture_tools.get_design_patterns()
    
    @server.tool()
    async def update_architecture(
        project_id: str,
        recommendation_id: str,
        implementation_summary: str,
        actual_files_created: list = [],
        actual_files_modified: list = []
    ):
        """
        Update project architecture after implementation.
        
        Args:
            project_id: Project ID
            recommendation_id: Recommendation ID
            implementation_summary: Summary of changes
            actual_files_created: Files created
            actual_files_modified: Files modified
            
        Returns:
            Dictionary with success status
        """
        return await architecture_tools.update_architecture(
            project_id, recommendation_id, implementation_summary,
            actual_files_created, actual_files_modified
        )
    
    logger.debug("Architecture tools registered")
