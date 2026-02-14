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
from coordmcp.tools import discovery_tools
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
    _register_discovery_tools(server)
    
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
    async def create_project(project_name: str, workspace_path: str, description: str = ""):
        """
        MANDATORY STEP 1: Create a new project in the memory system before starting any work.
        
        CRITICAL: You MUST call this tool FIRST before writing any code or creating files.
        This establishes the project in CoordMCP for tracking decisions, changes, and context.
        
        WHEN TO USE:
        - Starting ANY new project or application
        - User says "Create a todo app", "Build an API", "Make a website", etc.
        - Beginning work in a new repository or codebase
        - Starting a new feature that deserves its own project tracking
        
        WORKFLOW: 
        1. Call create_project() FIRST
        2. Then register_agent() 
        3. Then start_context()
        4. Then begin coding
        
        Args:
            project_name: Name of the project (required) - e.g., "Todo App", "User API", "Dashboard"
            workspace_path: Absolute path to the project workspace directory (required)
                           Example: "/home/user/projects/myapp" or "C:\\Users\\name\\projects\\myapp"
            description: Project description (optional but recommended) - What is this project for?
            
        Returns:
            Dictionary with project_id (SAVE THIS - you'll need it for ALL other operations) and success status
            
        Example:
            >>> result = await create_project("Todo App", "/home/user/projects/todo-app", "A task management application")
            >>> project_id = result["project_id"]  # SAVE THIS ID!
        """
        return await memory_tools.create_project(project_name, workspace_path, description)
    
    @server.tool()
    async def get_project_info(
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None
    ):
        """
        Get comprehensive information about a project from CoordMCP memory.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - Before starting work to understand project context and history
        - To check existing tech stack and architectural decisions
        - To see recent changes made by other agents
        - When resuming work on an existing project
        - To understand the project structure before making changes
        
        This retrieves: project metadata, tech stack, recent decisions, file dependencies, and change history.
        
        Args:
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            
        Returns:
            Dictionary with complete project information including decisions, changes, and architecture
            
        Examples:
            # Get by ID
            await get_project_info(project_id="proj-abc-123")
            
            # Get by name
            await get_project_info(project_name="My App")
            
            # Get by workspace path
            await get_project_info(workspace_path="/home/user/projects/myapp")
        """
        return await memory_tools.get_project_info(project_id, project_name, workspace_path)
    
    # ==================== Decision Tools ====================
    
    @server.tool()
    async def save_decision(
        title: str,
        description: str,
        rationale: str,
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None,
        context: str = "",
        impact: str = "",
        tags: list = None,
        related_files: list = None,
        author_agent: str = ""
    ):
        """
        CRITICAL: Record important architectural and technical decisions for future reference.
        
        MANDATORY: Call this whenever you make significant technical choices. This builds the project's
        decision history and helps maintain consistency across the codebase.
        
        WHEN TO USE (Always save decisions for):
        - Choosing a framework or library (React vs Vue, Flask vs FastAPI, etc.)
        - Database selection (PostgreSQL vs MongoDB, Redis vs Memcached)
        - Architecture patterns (Microservices vs Monolith, MVC vs Clean Architecture)
        - API design choices (REST vs GraphQL, authentication methods)
        - Infrastructure decisions (Cloud provider, containerization, CI/CD approach)
        - Security implementations (auth strategy, encryption methods)
        - Performance optimizations (caching strategy, database indexing)
        - Any decision that affects the project's direction or maintainability
        
        WHY THIS MATTERS:
        - Other agents (or you later) will understand WHY choices were made
        - Prevents inconsistent approaches across the codebase
        - Documents the evolution of the architecture
        - Helps onboard new team members
        
        Args:
            title: Short, clear decision title - e.g., "Use JWT for Authentication"
            description: Detailed description of what was decided and how it will be implemented
            rationale: WHY this decision was made - the reasoning, trade-offs, alternatives considered
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            context: Background information that led to this decision (optional)
            impact: Expected impact on the project (performance, complexity, maintenance) (optional)
            tags: Categorization tags - e.g., ["architecture", "security", "database"] (optional)
            related_files: File paths affected by this decision (optional)
            author_agent: Your agent_id from register_agent() (optional)
            
        Returns:
            Dictionary with decision_id and success status
            
        Examples:
            # Save by project ID
            await save_decision(
                project_id="proj-abc-123",
                title="Use FastAPI",
                description="FastAPI chosen for API framework",
                rationale="Type hints, automatic docs, async support"
            )
            
            # Save by workspace path
            await save_decision(
                workspace_path="/home/user/projects/myapp",
                title="Use PostgreSQL",
                description="Primary database selection",
                rationale="ACID compliance, complex queries, JSON support"
            )
        """
        return await memory_tools.save_decision(
            title=title,
            description=description,
            rationale=rationale,
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path,
            context=context,
            impact=impact,
            tags=tags,
            related_files=related_files,
            author_agent=author_agent
        )
    
    @server.tool()
    async def get_project_decisions(
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None,
        status: str = "all",
        tags: list = None
    ):
        """
        Retrieve all recorded architectural and technical decisions for a project.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - Before making new technical decisions to see what was already decided
        - When you're unsure about the project's architectural direction
        - To understand why certain patterns or technologies are used
        - Before contradicting an existing approach - check if there's already a decision
        - When joining an existing project to understand its evolution
        
        RECOMMENDED: Call this at the start of work to understand the project's decision history.
        This prevents you from unknowingly contradicting previous architectural choices.
        
        Args:
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            status: Filter by status - "active" (current), "archived" (old), "superseded" (replaced), or "all" (default)
            tags: Filter by specific tags - e.g., ["database", "security"] (optional)
            
        Returns:
            Dictionary with list of decisions including titles, rationale, and impact
            
        Examples:
            # Get all decisions by project ID
            await get_project_decisions(project_id="proj-abc-123")
            
            # Get only active decisions by workspace path
            await get_project_decisions(
                workspace_path="/home/user/projects/myapp",
                status="active"
            )
            
            # Get database-related decisions by project name
            await get_project_decisions(
                project_name="My App",
                tags=["database"]
            )
        """
        return await memory_tools.get_project_decisions(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path,
            status=status,
            tags=tags
        )
    
    @server.tool()
    async def search_decisions(
        query: str,
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None,
        tags: list = None
    ):
        """
        Search through recorded decisions by keywords or metadata.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - Looking for decisions about specific topics (e.g., "authentication", "database")
        - Checking if a particular technology or pattern was already decided upon
        - Finding decisions made by specific approaches or requirements
        - Researching the history of a specific feature or component
        
        USEFUL FOR: Quickly finding relevant decisions without reading through all of them.
        
        Args:
            query: Search keywords - e.g., "authentication", "performance", "database" (required)
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            tags: Optional tags to filter by - e.g., ["security", "architecture"]
            
        Returns:
            Dictionary with matching decisions ranked by relevance
            
        Examples:
            # Search for database-related decisions by project ID
            await search_decisions(
                project_id="proj-abc-123",
                query="PostgreSQL"
            )
            
            # Search by workspace and filter by tags
            await search_decisions(
                workspace_path="/home/user/projects/myapp",
                query="authentication",
                tags=["security", "backend"]
            )
        """
        return await memory_tools.search_decisions(
            query=query,
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path,
            tags=tags
        )
    
    # ==================== Tech Stack Tools ====================
    
    @server.tool()
    async def update_tech_stack(
        category: str,
        technology: str,
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None,
        version: str = "",
        rationale: str = "",
        decision_ref: str = ""
    ):
        """
        CRITICAL: Record the technology stack used in this project.
        
        MANDATORY: Call this whenever you add or change a major technology in the project.
        This creates a central registry of all technologies used.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - Setting up a new project - record ALL technologies you plan to use
        - Adding a new dependency or framework
        - Changing versions of existing technologies
        - Adding infrastructure tools (Docker, Kubernetes, etc.)
        - Setting up databases, message queues, or external services
        - Adding testing frameworks, build tools, or CI/CD pipelines
        
        CATEGORIES TO TRACK:
        - "backend": Python/Node/Java frameworks, runtime environments
        - "frontend": React/Vue/Angular, CSS frameworks, build tools
        - "database": PostgreSQL, MongoDB, Redis, Elasticsearch
        - "infrastructure": Docker, Kubernetes, AWS services, monitoring
        - "testing": Jest, Pytest, Cypress, etc.
        - "devops": CI/CD tools, deployment platforms
        
        BEST PRACTICE: Always link to a decision via decision_ref when the tech choice
        was based on a documented decision.
        
        Args:
            category: Technology category (required) - "backend", "frontend", "database", "infrastructure", "testing", "devops"
            technology: Technology name (required) - e.g., "React", "PostgreSQL", "Docker"
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            version: Version string (optional but recommended) - e.g., "18.2.0", "14.5"
            rationale: Brief explanation of why this technology was chosen (optional)
            decision_ref: Decision ID if this choice was documented via save_decision() (optional)
            
        Returns:
            Dictionary with success status
            
        Examples:
            # Update by project ID
            await update_tech_stack(
                project_id="proj-abc-123",
                category="backend",
                technology="FastAPI",
                version="0.104.0",
                rationale="High performance, async support, type hints"
            )
            
            # Update by workspace path
            await update_tech_stack(
                workspace_path="/home/user/projects/myapp",
                category="database",
                technology="PostgreSQL",
                version="15",
                decision_ref="dec-xyz-789"
            )
        """
        return await memory_tools.update_tech_stack(
            category=category,
            technology=technology,
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path,
            version=version,
            rationale=rationale,
            decision_ref=decision_ref
        )
    
    @server.tool()
    async def get_tech_stack(
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None,
        category: str = None
    ):
        """
        Retrieve the complete technology stack for a project.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - At the start of work to understand what technologies are already in use
        - Before adding new dependencies to avoid conflicts or duplicates
        - To check version compatibility when upgrading
        - When onboarding or explaining the project to others
        - To ensure consistency with existing technology choices
        
        RECOMMENDED: Call this early in your workflow to understand the technical landscape.
        
        Args:
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            category: Filter by specific category (optional) - "backend", "frontend", "database", "infrastructure", etc.
            
        Returns:
            Dictionary with complete tech stack organized by category
            
        Examples:
            # Get full tech stack by project ID
            await get_tech_stack(project_id="proj-abc-123")
            
            # Get only database technologies by workspace
            await get_tech_stack(
                workspace_path="/home/user/projects/myapp",
                category="database"
            )
            
            # Get backend stack by project name
            await get_tech_stack(
                project_name="My App",
                category="backend"
            )
        """
        return await memory_tools.get_tech_stack(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path,
            category=category
        )
    
    # ==================== Change Log Tools ====================
    
    @server.tool()
    async def log_change(
        file_path: str,
        change_type: str,
        description: str,
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None,
        agent_id: str = "",
        code_summary: str = "",
        architecture_impact: str = "none",
        related_decision: str = ""
    ):
        """
        CRITICAL: Log every significant code change for project tracking and history.
        
        MANDATORY: Call this AFTER completing any substantial file modification, creation, or deletion.
        This maintains a complete audit trail of all changes made to the project.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE (Always log changes for):
        - Creating new files or components
        - Modifying existing functionality
        - Refactoring code
        - Deleting files or features
        - Any change that affects the project's behavior or structure
        
        CHANGE TYPES:
        - "create": New files, new components, new features
        - "modify": Updates to existing code, bug fixes, enhancements
        - "delete": Removing files, features, or code
        - "refactor": Restructuring code without changing behavior
        
        ARCHITECTURE IMPACT:
        - "none": Simple changes, bug fixes, formatting (default)
        - "minor": Small API changes, new utility functions, config updates
        - "significant": New architectural patterns, major refactoring, breaking changes
        
        BEST PRACTICES:
        - Always log after the change is complete and tested
        - Link to related decisions when changes implement architectural decisions
        - Be descriptive in the description field
        - Use code_summary to briefly explain what the code does
        
        Args:
            file_path: Path of the file that was changed (required) - e.g., "src/auth.py", "components/Button.tsx"
            change_type: Type of change (required) - "create", "modify", "delete", or "refactor"
            description: Clear description of WHAT was changed and WHY (required)
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            agent_id: Your agent_id from register_agent() (optional)
            code_summary: Brief summary of the code/functionality (optional but recommended)
            architecture_impact: Impact on overall architecture - "none", "minor", or "significant" (default: "none")
            related_decision: Decision ID if this change implements a documented decision (optional)
            
        Returns:
            Dictionary with change_id and success status
            
        Examples:
            # Log a file creation by project ID
            await log_change(
                project_id="proj-abc-123",
                file_path="src/models/user.py",
                change_type="create",
                description="Added User model with authentication fields",
                agent_id="agent-1",
                architecture_impact="significant"
            )
            
            # Log a modification by workspace path
            await log_change(
                workspace_path="/home/user/projects/myapp",
                file_path="config/database.py",
                change_type="modify",
                description="Updated connection pooling settings",
                architecture_impact="minor"
            )
        """
        return await memory_tools.log_change(
            file_path=file_path,
            change_type=change_type,
            description=description,
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path,
            agent_id=agent_id,
            code_summary=code_summary,
            architecture_impact=architecture_impact,
            related_decision=related_decision
        )
    
    @server.tool()
    async def get_recent_changes(
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None,
        limit: int = 20,
        architecture_impact_filter: str = "all"
    ):
        """
        Retrieve recent changes made to a project for context and continuity.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - At the start of a session to see what was recently worked on
        - Before making changes to understand the current state
        - To check if another agent has been working on the same files
        - To review the evolution of the codebase
        - After being away from the project for a while
        - To identify patterns in recent development
        
        RECOMMENDED: Call this when resuming work or joining an active project to understand
        recent activity and avoid conflicts.
        
        Args:
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            limit: Maximum number of recent changes to retrieve (default: 20)
            architecture_impact_filter: Filter by impact level (optional) - "all", "none", "minor", or "significant"
            
        Returns:
            Dictionary with chronological list of recent changes
            
        Examples:
            # Get last 20 changes by project ID
            await get_recent_changes(project_id="proj-abc-123")
            
            # Get only significant changes by workspace
            await get_recent_changes(
                workspace_path="/home/user/projects/myapp",
                limit=10,
                architecture_impact_filter="significant"
            )
            
            # Get recent changes by project name
            await get_recent_changes(
                project_name="My App",
                limit=50
            )
        """
        return await memory_tools.get_recent_changes(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path,
            limit=limit,
            architecture_impact_filter=architecture_impact_filter
        )
    
    # ==================== File Metadata Tools ====================
    
    @server.tool()
    async def update_file_metadata(
        file_path: str,
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None,
        file_type: str = "source",
        module: str = "",
        purpose: str = "",
        dependencies: list = None,
        dependents: list = None,
        lines_of_code: int = 0,
        complexity: str = "low",
        last_modified_by: str = ""
    ):
        """
        Track important file metadata for project understanding and dependency management.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - After creating new files to document their purpose and relationships
        - When you understand a file's dependencies on other files
        - To update complexity assessments as files grow
        - To organize files into logical modules
        - When refactoring changes file dependencies
        
        RECOMMENDED FOR: Key architectural files, complex modules, files with many dependencies.
        This helps build a dependency graph and understand the codebase structure.
        
        FILE TYPES:
        - "source": Production code files (default)
        - "test": Test files and test suites
        - "config": Configuration files (package.json, .env, etc.)
        - "doc": Documentation files (README, docs, etc.)
        
        COMPLEXITY LEVELS:
        - "low": Simple files, straightforward logic, minimal dependencies
        - "medium": Moderate complexity, some business logic, several dependencies
        - "high": Complex files, intricate logic, many dependencies, high cognitive load
        
        Args:
            file_path: Path of the file (required) - e.g., "src/components/Button.tsx"
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            file_type: Type of file - "source", "test", "config", or "doc" (default: "source")
            module: Logical module/component this file belongs to (optional) - e.g., "auth", "ui", "api"
            purpose: Brief description of what this file does (optional)
            dependencies: List of files this file imports/depends on (optional) - e.g., ["src/utils.ts", "src/types.ts"]
            dependents: List of files that import/depend on this file (optional)
            lines_of_code: Approximate line count (optional, for tracking growth)
            complexity: Complexity level - "low", "medium", or "high" (default: "low")
            last_modified_by: Your agent_id from register_agent() (optional)
            
        Returns:
            Dictionary with success status
            
        Examples:
            # Update metadata by project ID
            await update_file_metadata(
                project_id="proj-abc-123",
                file_path="src/models/user.py",
                file_type="source",
                module="models",
                purpose="User model with authentication and validation",
                dependencies=["src/database.py", "src/utils/crypto.py"],
                complexity="medium",
                lines_of_code=150
            )
            
            # Update by workspace path
            await update_file_metadata(
                workspace_path="/home/user/projects/myapp",
                file_path="tests/test_api.py",
                file_type="test",
                module="api_tests",
                purpose="API endpoint tests",
                dependents=["src/api/routes.py"]
            )
        """
        return await memory_tools.update_file_metadata(
            file_path=file_path,
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path,
            file_type=file_type,
            module=module,
            purpose=purpose,
            dependencies=dependencies,
            dependents=dependents,
            lines_of_code=lines_of_code,
            complexity=complexity,
            last_modified_by=last_modified_by
        )
    
    @server.tool()
    async def get_file_dependencies(
        file_path: str,
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None,
        direction: str = "dependencies"
    ):
        """
        Analyze file dependencies to understand the impact of changes.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - Before modifying a file to see what else might break
        - When refactoring to understand the ripple effects
        - To find all files affected by a bug fix
        - To understand the codebase architecture and relationships
        - When deleting files to ensure nothing depends on them
        - To identify circular dependencies
        
        IMPORTANT: This helps prevent breaking changes and understand refactoring impact.
        Always check dependencies before making significant modifications.
        
        DIRECTIONS:
        - "dependencies": What this file imports/uses (downstream)
        - "dependents": What imports/uses this file (upstream) - USE THIS BEFORE DELETING
        - "both": Complete dependency graph in both directions
        
        Args:
            file_path: Path of the file to analyze (required) - e.g., "src/auth.ts"
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            direction: Direction to analyze - "dependencies", "dependents", or "both" (default: "dependencies")
            
        Returns:
            Dictionary with dependency information and related files
            
        Examples:
            # Get what a file depends on by project ID
            await get_file_dependencies(
                project_id="proj-abc-123",
                file_path="src/models/user.py",
                direction="dependencies"
            )
            
            # Get what depends on a file by workspace
            await get_file_dependencies(
                workspace_path="/home/user/projects/myapp",
                file_path="src/config.py",
                direction="dependents"
            )
            
            # Get both directions by project name
            await get_file_dependencies(
                project_name="My App",
                file_path="src/api/routes.py",
                direction="both"
            )
        """
        return await memory_tools.get_file_dependencies(
            file_path=file_path,
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path,
            direction=direction
        )
    
    @server.tool()
    async def get_module_info(
        module_name: str,
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None
    ):
        """
        Retrieve comprehensive information about a logical module in the project.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - To understand the structure and purpose of a specific module
        - Before working on a module to see its responsibilities and files
        - To check module dependencies and avoid circular dependencies
        - When planning module refactoring or restructuring
        - To understand the relationship between modules
        
        USEFUL FOR: Getting a high-level view of a specific component or subsystem.
        
        Args:
            module_name: Name of the module (required) - e.g., "auth", "database", "ui"
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            
        Returns:
            Dictionary with module details, files, dependencies, and responsibilities
            
        Examples:
            # Get module info by project ID
            await get_module_info(
                project_id="proj-abc-123",
                module_name="authentication"
            )
            
            # Get module info by workspace path
            await get_module_info(
                workspace_path="/home/user/projects/myapp",
                module_name="database"
            )
            
            # Get module info by project name
            await get_module_info(
                project_name="My App",
                module_name="api"
            )
        """
        return await memory_tools.get_module_info(
            module_name=module_name,
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
    
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
        MANDATORY STEP 2: Register yourself as an agent in the CoordMCP system.
        
        CRITICAL: You MUST call this tool AFTER create_project() but BEFORE starting any work.
        This establishes your identity for multi-agent coordination and enables:
        - Context tracking across sessions
        - File locking to prevent conflicts
        - Change attribution
        - Session history and logging
        
        WHEN TO USE:
        - At the start of EVERY new session or conversation
        - When beginning work on a new project
        - When you haven't yet registered in the current session
        - After restarting or reconnecting to CoordMCP
        
        WORKFLOW:
        1. create_project() - Create project
        2. register_agent() - Register yourself (THIS STEP)
        3. start_context() - Start working context
        4. Begin coding
        
        SAVE THE AGENT_ID: You'll need it for ALL subsequent operations.
        
        Args:
            agent_name: Your agent name (required) - e.g., "OpenCodeDev", "ClaudeCoder", "CursorAI"
            agent_type: Type of agent (required) - "opencode", "cursor", "claude_code", or "custom"
            capabilities: List of your skills/capabilities (optional but recommended) - e.g., ["python", "react", "database"]
            version: Version identifier (optional) - e.g., "1.0.0"
            
        Returns:
            Dictionary with agent_id (SAVE THIS - needed for all operations) and success status
            
        Example:
            >>> result = await register_agent("OpenCodeDev", "opencode", ["python", "fastapi"])
            >>> agent_id = result["agent_id"]  # SAVE THIS ID!
        """
        return await context_tools.register_agent(
            agent_name, agent_type, capabilities, version
        )
    
    @server.tool()
    async def get_agents_list(status: str = "all"):
        """
        Retrieve a list of all registered agents and their current status.
        
        WHEN TO USE:
        - At the start of work to see who else is working on this project
        - To check if other agents are currently active
        - To understand the capabilities of other agents in the system
        - When coordinating multi-agent work
        - To see the history of agents that have worked on this project
        
        USEFUL FOR: Multi-agent coordination and understanding the project's agent ecosystem.
        
        Args:
            status: Filter by agent status (optional) - "active", "inactive", "deprecated", or "all" (default)
            
        Returns:
            Dictionary with list of registered agents and their details
        """
        return await context_tools.get_agents_list(status)
    
    @server.tool()
    async def get_agent_profile(agent_id: str):
        """
        Retrieve detailed profile information about a specific agent.
        
        WHEN TO USE:
        - To check your own registration details and capabilities
        - To understand what another agent is working on
        - To verify an agent's identity and permissions
        - When coordinating work between multiple agents
        
        Args:
            agent_id: Agent ID from register_agent() (required)
            
        Returns:
            Dictionary with agent profile including name, type, capabilities, and status
        """
        return await context_tools.get_agent_profile(agent_id)
    
    # ==================== Context Management Tools ====================
    
    @server.tool()
    async def start_context(
        agent_id: str,
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None,
        objective: str = "",
        task_description: str = "",
        priority: str = "medium",
        current_file: str = ""
    ):
        """
        MANDATORY STEP 3: Start a new work context before beginning any coding task.

        CRITICAL: You MUST call this tool AFTER create_project() and register_agent().
        This establishes your current objective and enables:
        - Context tracking for the current task
        - File locking coordination
        - Session logging and history
        - Conflict prevention with other agents
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name

        WHEN TO USE:
        - At the beginning of every coding session or task
        - When switching to a new objective or feature
        - When the user's request changes significantly
        - After completing one task and starting another
        - When you need to establish clear boundaries for your current work

        WORKFLOW:
        1. create_project() - Create project (if new)
        2. register_agent() - Register yourself
        3. start_context() - Start work context (THIS STEP)
        4. lock_files() - Lock files you plan to modify (recommended)
        5. Begin coding

        PRIORITY LEVELS:
        - "critical": Production outage, security vulnerability, critical bug fix
        - "high": Important features, significant refactoring, blocking issues
        - "medium": Standard development work (default)
        - "low": Documentation, minor optimizations, nice-to-have features

        Args:
            agent_id: Your agent_id from register_agent() (required)
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            objective: Clear, concise statement of what you're working on (required) - e.g., "Implement user authentication", "Fix API pagination bug"
            task_description: Detailed description of the work (optional) - Include specific requirements, acceptance criteria
            priority: Priority level - "critical", "high", "medium", or "low" (default: "medium")
            current_file: File you're starting with (optional) - e.g., "src/auth/login.ts"

        Returns:
            Dictionary with context information and session details
            
        Examples:
            # By project ID
            result = await start_context("agent-123", project_id="proj-456", objective="Fix bug")
            
            # By project name
            result = await start_context("agent-123", project_name="My Project", objective="Fix bug")
            
            # By workspace path
            result = await start_context("agent-123", workspace_path="/path/to/project", objective="Fix bug")
        """
        return await context_tools.start_context(
            agent_id=agent_id,
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path,
            objective=objective,
            task_description=task_description,
            priority=priority,
            current_file=current_file
        )
    
    @server.tool()
    async def get_agent_context(agent_id: str):
        """
        Retrieve your current work context and session information.
        
        WHEN TO USE:
        - At the start of a conversation to check if you have an active context
        - To verify your current objective and project
        - To see what files you have locked
        - To understand what you were working on in a previous session
        - When resuming work after an interruption
        
        RECOMMENDED: Call this at the beginning of each conversation to establish
        context and understand your current state in the system.
        
        Args:
            agent_id: Your agent_id from register_agent() (required)
            
        Returns:
            Dictionary with current context including objective, project, locked files, and history
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
        Switch your work context to a different project or objective.
        
        WHEN TO USE:
        - When the user asks you to work on something different
        - When switching from one task to another in the same conversation
        - When moving between multiple projects
        - After completing one objective and starting a new one
        
        IMPORTANT: This will end your current context and start a new one.
        Make sure to complete or document any pending work in the current context first.
        
        WORKFLOW:
        1. Complete current work and log changes
        2. unlock_files() - Release any locked files
        3. switch_context() - Switch to new objective (THIS STEP)
        4. lock_files() - Lock files for new work (if needed)
        5. Begin new work
        
        Args:
            agent_id: Your agent_id from register_agent() (required)
            to_project_id: Target project ID (required) - Can be same or different project
            to_objective: New objective statement (required) - e.g., "Add pagination to API"
            task_description: Detailed description of new work (optional)
            priority: Priority level - "critical", "high", "medium", or "low" (default: "medium")
            
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
        End your current work context and session.
        
        WHEN TO USE:
        - At the end of a conversation or coding session
        - When you've completed the current objective
        - Before switching to a completely different task
        - When you want to release all file locks and close the session
        
        IMPORTANT: This will:
        - Release all file locks you hold
        - Log the end of your session
        - Clear your current context
        
        BEST PRACTICE: Always call this before ending a conversation to ensure
        clean state for the next session.
        
        WORKFLOW:
        1. Complete all work and log changes with log_change()
        2. unlock_files() - Release all locked files
        3. end_context() - End session (THIS STEP)
        
        Args:
            agent_id: Your agent_id from register_agent() (required)
            
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
        CRITICAL: Lock files before modifying them to prevent conflicts with other agents.
        
        MANDATORY: Always lock files BEFORE making changes. This prevents:
        - Multiple agents editing the same file simultaneously
        - Lost changes and merge conflicts
        - Race conditions in multi-agent environments
        
        WHEN TO USE:
        - Before editing any existing file
        - Before creating files in shared directories
        - Before refactoring code that spans multiple files
        - When you plan to modify files over an extended period
        
        WORKFLOW:
        1. lock_files() - Lock the files you plan to modify (THIS STEP)
        2. Make your changes
        3. log_change() - Log the changes made
        4. unlock_files() - Release the locks when done
        
        CONFLICT HANDLING:
        If files are already locked by another agent, you'll receive conflict information
        including which agent has the lock and when it expires. You should either:
        - Wait for the lock to be released
        - Coordinate with the other agent
        - Work on different files first
        
        Args:
            agent_id: Your agent_id from register_agent() (required)
            project_id: Project ID from create_project() (required)
            files: List of file paths to lock (required) - e.g., ["src/auth.ts", "src/utils.ts"]
            reason: Clear reason for locking (required) - e.g., "Implementing JWT authentication"
            expected_duration_minutes: How long you expect to hold the locks (default: 60)
            
        Returns:
            Dictionary with locked files or conflict information if files are already locked
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
        Release file locks after you've completed your changes.
        
        WHEN TO USE:
        - Immediately after completing changes to files
        - When you're done working on a specific file or set of files
        - Before switching to work on different files
        - At the end of a task or session
        
        IMPORTANT: Always unlock files as soon as you're done with them.
        This allows other agents to work on those files and prevents unnecessary blocking.
        
        WORKFLOW:
        1. Complete your changes and test them
        2. log_change() - Log what you changed
        3. unlock_files() - Release the locks (THIS STEP)
        
        Args:
            agent_id: Your agent_id from register_agent() (required)
            project_id: Project ID from create_project() (required)
            files: List of file paths to unlock (required) - e.g., ["src/auth.ts", "src/utils.ts"]
            
        Returns:
            Dictionary with unlocked files and success status
        """
        return await context_tools.unlock_files(agent_id, project_id, files)
    
    @server.tool()
    async def get_locked_files(
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None
    ):
        """
        Check which files are currently locked and by whom.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - Before planning your work to see what files are unavailable
        - When you encounter conflicts and need to understand the situation
        - To coordinate with other agents working on the same project
        - To check if a specific file is available for editing
        
        USEFUL FOR: Understanding the current state of file locks and planning your work accordingly.
        
        Args:
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            
        Returns:
            Dictionary with locked files organized by agent, including lock reasons and expiration times
            
        Examples:
            # By project ID
            result = await get_locked_files(project_id="proj-456")
            
            # By project name
            result = await get_locked_files(project_name="My Project")
            
            # By workspace path
            result = await get_locked_files(workspace_path="/path/to/project")
        """
        return await context_tools.get_locked_files(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
    
    # ==================== Session & History Tools ====================
    
    @server.tool()
    async def get_context_history(agent_id: str, limit: int = 10):
        """
        Retrieve your recent file operation history and context entries.
        
        WHEN TO USE:
        - To review what files you've recently worked on
        - To understand the sequence of operations in your current session
        - When you need to remember what you did earlier in the conversation
        - To track the evolution of your work
        
        USEFUL FOR: Understanding your recent activity and maintaining continuity.
        
        Args:
            agent_id: Your agent_id from register_agent() (required)
            limit: Maximum number of history entries to retrieve (default: 10)
            
        Returns:
            Dictionary with chronological list of recent file operations
        """
        return await context_tools.get_context_history(agent_id, limit)
    
    @server.tool()
    async def get_session_log(agent_id: str, limit: int = 50):
        """
        Retrieve your complete session log with events and activities.
        
        WHEN TO USE:
        - To review the full history of your current and past sessions
        - To understand when contexts were started, switched, or ended
        - To track the duration and details of your work sessions
        - For debugging or understanding session state
        
        USEFUL FOR: Getting a comprehensive view of your session activity and timeline.
        
        Args:
            agent_id: Your agent_id from register_agent() (required)
            limit: Maximum number of log entries to retrieve (default: 50)
            
        Returns:
            Dictionary with chronological session log including context switches and events
        """
        return await context_tools.get_session_log(agent_id, limit)
    
    @server.tool()
    async def get_agents_in_project(
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None
    ):
        """
        Retrieve all agents currently active in a specific project.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - To check who else is working on this project right now
        - Before starting work to understand the current activity level
        - When coordinating multi-agent work
        - To see what other agents are focused on
        
        USEFUL FOR: Multi-agent coordination and understanding project activity.
        
        Args:
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            
        Returns:
            Dictionary with list of active agents and their current objectives
            
        Examples:
            # By project ID
            result = await get_agents_in_project(project_id="proj-456")
            
            # By project name
            result = await get_agents_in_project(project_name="My Project")
            
            # By workspace path
            result = await get_agents_in_project(workspace_path="/path/to/project")
        """
        return await context_tools.get_agents_in_project(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
    
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
    async def analyze_architecture(
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None
    ):
        """
        RECOMMENDED: Analyze and understand the current project architecture.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - At the start of work on an existing project to understand the architecture
        - Before making significant architectural changes
        - To identify potential improvements or issues in the codebase
        - When onboarding to a new codebase
        - To get an overview of modules, dependencies, and complexity
        
        THIS PROVIDES:
        - Overview of project structure and modules
        - Dependency analysis
        - Complexity metrics
        - Potential architectural issues
        - Recommendations for improvement
        
        RECOMMENDED: Call this early when working on an existing project to understand
        the architectural landscape before making changes.
        
        Args:
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            
        Returns:
            Dictionary with comprehensive architecture analysis and insights
            
        Examples:
            # By project ID
            result = await analyze_architecture(project_id="proj-456")
            
            # By project name
            result = await analyze_architecture(project_name="My Project")
            
            # By workspace path
            result = await analyze_architecture(workspace_path="/path/to/project")
        """
        return await architecture_tools.analyze_architecture(
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path
        )
    
    @server.tool()
    async def get_architecture_recommendation(
        feature_description: str,
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None,
        context: str = "",
        constraints: list = None,
        implementation_style: str = "modular"
    ):
        """
        RECOMMENDED: Get expert architectural guidance before implementing major features.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - Before implementing significant new features or capabilities
        - When you're unsure about the best architectural approach
        - For complex features that affect multiple parts of the system
        - When choosing between different implementation strategies
        - To ensure consistency with existing architecture
        - Before making structural changes to the codebase
        
        HIGHLY RECOMMENDED FOR:
        - New major features
        - Significant refactoring efforts
        - Integration with external systems
        - Changes to core architecture
        - Performance-critical implementations
        
        THIS PROVIDES:
        - Recommended approach and design patterns
        - File structure and organization suggestions
        - Technology and library recommendations
        - Implementation steps and considerations
        - Rationale for the recommendations
        
        AFTER RECEIVING RECOMMENDATIONS:
        1. Review the suggested approach
        2. Save the decision with save_decision() if you adopt the recommendation
        3. Implement following the suggested structure
        4. Update architecture tracking with update_architecture()
        
        Args:
            feature_description: Clear description of what you're building (required) - e.g., "User authentication system with JWT tokens"
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            context: Additional context - requirements, constraints, preferences (optional)
            constraints: List of constraints - e.g., ["must use PostgreSQL", "must be stateless"] (optional)
            implementation_style: Preferred approach - "modular", "monolithic", or "auto" (default: "modular")
            
        Returns:
            Dictionary with detailed architectural recommendations and implementation guidance
            
        Examples:
            # By project ID
            result = await get_architecture_recommendation(
                project_id="proj-456",
                feature_description="Add user authentication"
            )
            
            # By project name
            result = await get_architecture_recommendation(
                project_name="My Project",
                feature_description="Add user authentication"
            )
            
            # By workspace path
            result = await get_architecture_recommendation(
                workspace_path="/path/to/project",
                feature_description="Add user authentication"
            )
        """
        return await architecture_tools.get_architecture_recommendation(
            feature_description=feature_description,
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path,
            context=context,
            constraints=constraints,
            implementation_style=implementation_style
        )
    
    @server.tool()
    async def validate_code_structure(
        file_path: str,
        code_structure: dict,
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None,
        strict_mode: bool = False
    ):
        """
        Validate that your code structure follows the project's architectural guidelines.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - Before finalizing a new file or component structure
        - When creating significant new modules or services
        - To ensure consistency with existing codebase patterns
        - When you're unsure if your approach follows project conventions
        - Before committing major structural changes
        
        USEFUL FOR: Catching architectural violations early and maintaining codebase consistency.
        
        VALIDATION CHECKS:
        - Directory structure conventions
        - Naming conventions
        - Import/export patterns
        - Dependency management
        - Architectural pattern compliance
        
        Args:
            file_path: Path where code will be located (required) - e.g., "src/services/auth.ts"
            code_structure: Description of proposed structure (required) - Object with component details
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            strict_mode: Enforce strict validation (optional) - Set to True for critical architectural components
            
        Returns:
            Dictionary with validation results including any violations or suggestions
            
        Examples:
            # By project ID
            result = await validate_code_structure(
                project_id="proj-456",
                file_path="src/main.py",
                code_structure={...}
            )
            
            # By project name
            result = await validate_code_structure(
                project_name="My Project",
                file_path="src/main.py",
                code_structure={...}
            )
            
            # By workspace path
            result = await validate_code_structure(
                workspace_path="/path/to/project",
                file_path="src/main.py",
                code_structure={...}
            )
        """
        return await architecture_tools.validate_code_structure(
            file_path=file_path,
            code_structure=code_structure,
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path,
            strict_mode=strict_mode
        )
    
    @server.tool()
    async def get_design_patterns():
        """
        Browse the catalog of available design patterns and architectural approaches.
        
        WHEN TO USE:
        - When designing new features and considering architectural patterns
        - To learn about different design approaches and their use cases
        - When evaluating which pattern fits your current requirements
        - To understand best practices for common problems
        - As reference when making architectural decisions
        
        USEFUL FOR: Understanding available architectural patterns and when to apply them.
        
        Returns:
            Dictionary with catalog of design patterns including descriptions and best use cases
        """
        return await architecture_tools.get_design_patterns()
    
    @server.tool()
    async def update_architecture(
        recommendation_id: str,
        implementation_summary: str,
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None,
        actual_files_created: list = None,
        actual_files_modified: list = None
    ):
        """
        Update the project architecture tracking after implementing recommendations.
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - After implementing architectural recommendations from get_architecture_recommendation()
        - When completing significant structural changes to the codebase
        - To document what was actually built vs. what was recommended
        - To keep the architecture documentation in sync with the code
        
        IMPORTANT: Call this after implementing architectural recommendations to:
        - Log the implementation details
        - Track files created and modified
        - Update architecture history
        - Document any deviations from recommendations
        
        WORKFLOW:
        1. get_architecture_recommendation() - Get guidance
        2. Implement the recommendation
        3. log_change() - Log each file change
        4. update_architecture() - Update architecture tracking (THIS STEP)
        
        Args:
            recommendation_id: ID from get_architecture_recommendation() (required)
            implementation_summary: Brief summary of what was implemented (required)
            project_id: Project ID from create_project() (optional if project_name or workspace_path provided)
            project_name: Project name to look up (alternative to project_id)
            workspace_path: Workspace directory path (alternative to project_id)
            actual_files_created: List of new files created (optional) - e.g., ["src/auth.ts", "src/middleware/jwt.ts"]
            actual_files_modified: List of existing files modified (optional) - e.g., ["src/app.ts", "src/routes.ts"]
            
        Returns:
            Dictionary with success status and implementation tracking
            
        Examples:
            # By project ID
            result = await update_architecture(
                project_id="proj-456",
                recommendation_id="rec-789",
                implementation_summary="Added auth module"
            )
            
            # By project name
            result = await update_architecture(
                project_name="My Project",
                recommendation_id="rec-789",
                implementation_summary="Added auth module"
            )
            
            # By workspace path
            result = await update_architecture(
                workspace_path="/path/to/project",
                recommendation_id="rec-789",
                implementation_summary="Added auth module"
            )
        """
        return await architecture_tools.update_architecture(
            recommendation_id=recommendation_id,
            implementation_summary=implementation_summary,
            project_id=project_id,
            project_name=project_name,
            workspace_path=workspace_path,
            actual_files_created=actual_files_created,
            actual_files_modified=actual_files_modified
        )
    
    logger.debug("Architecture tools registered")


def _register_discovery_tools(server: FastMCP) -> None:
    """
    Register project and agent discovery tools.
    
    These tools enable agents to:
    - Discover existing projects by workspace path
    - Browse and search for projects
    - Find active agents and their activities
    - Get project information using flexible identifiers
    """
    logger.debug("Registering discovery tools...")
    
    # ==================== Project Discovery Tools ====================
    
    @server.tool()
    async def discover_project(
        path: str = None,
        max_parent_levels: int = 3
    ):
        """
        Discover a CoordMCP project by searching from a directory path.
        
        ESSENTIAL FOR: Joining existing projects, auto-discovering context
        
        This tool searches for a project associated with the given directory.
        It first checks for an exact match, then searches up to 3 parent directories.
        
        WHEN TO USE:
        - Starting work in a project directory and want to see if it's tracked
        - Navigating to a subdirectory and finding the parent project
        - Auto-discovering projects when you don't know the project_id
        - First step when joining an existing project
        
        WORKFLOW:
        1. discover_project() - Find the project
        2. register_agent() - Register yourself
        3. get_project_info() - Get full project details
        4. get_active_agents() - See who's working on it
        5. start_context() - Begin working
        
        Args:
            path: Directory path to search from (optional, defaults to current working directory)
            max_parent_levels: Maximum parent directories to search (default: 3)
            
        Returns:
            Dictionary with discovery results including project details if found
            
        Example:
            >>> # Auto-discover in current directory
            >>> result = await discover_project()
            >>> 
            >>> # Search from specific path
            >>> result = await discover_project(path="/home/user/projects/myapp/src/components")
        """
        return await discovery_tools.discover_project(path, max_parent_levels)
    
    @server.tool()
    async def get_project(
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None
    ):
        """
        Get project information by ID, name, or workspace path.
        
        ESSENTIAL FOR: Flexible project lookup when you have partial information
        
        This tool provides flexible project lookup. You can specify any combination
        of identifiers, and it will resolve to the matching project.
        
        Priority: project_id > workspace_path > project_name
        
        WHEN TO USE:
        - You know the project_id and want full details
        - You only know the project name
        - You have the workspace path and want to find the project
        - Validating that multiple identifiers point to the same project
        
        Args:
            project_id: Project ID (e.g., "proj-abc-123")
            project_name: Project name (e.g., "My App")
            workspace_path: Workspace directory path (e.g., "/home/user/projects/myapp")
            
        Returns:
            Dictionary with complete project details
            
        Examples:
            >>> # Get by ID
            >>> await get_project(project_id="proj-abc-123")
            >>> 
            >>> # Get by name
            >>> await get_project(project_name="My App")
            >>> 
            >>> # Get by path
            >>> await get_project(workspace_path="/home/user/projects/myapp")
        """
        return await discovery_tools.get_project(project_id, project_name, workspace_path)
    
    @server.tool()
    async def list_projects(
        status: str = "active",
        workspace_base: str = None,
        include_archived: bool = False
    ):
        """
        List all CoordMCP projects with optional filtering.
        
        ESSENTIAL FOR: Browsing available projects, finding work to join
        
        This tool provides a comprehensive view of all projects in the system.
        Useful for browsing available projects before selecting one to work on.
        
        WHEN TO USE:
        - See all projects in the system
        - Find projects under a specific directory
        - Check which projects are active vs archived
        - Get an overview of all tracked work
        
        Args:
            status: Filter by status - "active", "archived", or "all" (default: "active")
            workspace_base: Optional base directory to filter projects (e.g., "/home/user/projects")
            include_archived: Whether to include archived projects (default: False)
            
        Returns:
            Dictionary with list of projects including metadata
            
        Examples:
            >>> # List all active projects
            >>> await list_projects()
            >>> 
            >>> # List all projects including archived
            >>> await list_projects(include_archived=True)
            >>> 
            >>> # List projects under specific directory
            >>> await list_projects(workspace_base="/home/user/projects")
        """
        return await discovery_tools.list_projects(status, workspace_base, include_archived)
    
    # ==================== Agent Discovery Tools ====================
    
    @server.tool()
    async def get_active_agents(
        project_id: str = None,
        project_name: str = None,
        workspace_path: str = None
    ):
        """
        Get information about active agents.
        
        ESSENTIAL FOR: Understanding team activity and coordination
        
        This tool shows which agents are currently working, optionally filtered
        by a specific project. Useful for understanding team activity and
        coordinating with other agents.
        
        WHEN TO USE:
        - See all active agents across all projects
        - Check who's working on a specific project before joining
        - Monitor team activity and coordination opportunities
        - Find collaborators or check for potential conflicts
        
        Args:
            project_id: Optional project ID to filter by
            project_name: Optional project name to filter by
            workspace_path: Optional workspace path to filter by
            
        Returns:
            Dictionary with list of active agents and their current activities
            
        Examples:
            >>> # Get all active agents
            >>> await get_active_agents()
            >>> 
            >>> # Get agents working on specific project
            >>> await get_active_agents(project_id="proj-abc-123")
            >>> 
            >>> # Get agents by project name
            >>> await get_active_agents(project_name="My App")
        """
        return await discovery_tools.get_active_agents(project_id, project_name, workspace_path)
    
    logger.debug("Discovery tools registered")
