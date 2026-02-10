"""
Architecture-related FastMCP resources for CoordMCP.

Resources:
- arch-recommendation://{recommendation_id} - Complete architecture recommendation
- design-patterns://list - All available design patterns
- design-patterns://{pattern_name} - Specific pattern details
"""

from coordmcp.architecture.patterns import get_pattern, get_all_patterns
from coordmcp.logger import get_logger

logger = get_logger("resources.architecture")


async def handle_architecture_resource(uri: str) -> str:
    """
    Handle architecture-related resources.
    
    Supported URIs:
    - design-patterns://list - List all patterns
    - design-patterns://{pattern_name} - Specific pattern details
    """
    try:
        if uri.startswith("design-patterns://"):
            pattern_id = uri.replace("design-patterns://", "")
            
            if pattern_id == "list":
                return _format_all_patterns()
            else:
                return _format_pattern_details(pattern_id)
        
        return f"# Error\n\nUnknown architecture resource: {uri}"
        
    except Exception as e:
        logger.error(f"Error handling architecture resource {uri}: {e}")
        return f"# Error\n\nFailed to load resource: {str(e)}"


def _format_all_patterns() -> str:
    """Format all design patterns as markdown."""
    patterns = get_all_patterns()
    
    lines = [
        "# Design Patterns Reference",
        "",
        f"Total patterns available: {len(patterns)}",
        "",
        "## Quick Reference",
        "",
    ]
    
    for name, info in patterns.items():
        lines.append(f"- **{name}** - {info.get('description', 'No description')}")
    
    lines.extend([
        "",
        "## Detailed Patterns",
        "",
    ])
    
    for name, info in patterns.items():
        lines.extend([
            f"### {name}",
            "",
            f"{info.get('description', 'No description')}",
            "",
        ])
        
        if info.get('best_for'):
            lines.append(f"**Best for:** {', '.join(info['best_for'])}")
            lines.append("")
        
        if info.get('modules'):
            lines.append(f"**Typical modules:** {', '.join(info['modules'])}")
            lines.append("")
        
        # Add link to full details
        lines.append(f"*Use `design-patterns://{name}` for full details*")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def _format_pattern_details(pattern_name: str) -> str:
    """Format specific pattern details as markdown."""
    pattern = get_pattern(pattern_name)
    
    if not pattern:
        return f"# Pattern Not Found\n\nPattern '{pattern_name}' not found.\n\nUse `design-patterns://list` to see available patterns."
    
    lines = [
        f"# {pattern_name} Pattern",
        "",
        f"{pattern.get('description', 'No description')}",
        "",
    ]
    
    if pattern.get('best_for'):
        lines.extend([
            "## Best Used For",
            "",
        ])
        for use_case in pattern['best_for']:
            lines.append(f"- {use_case}")
        lines.append("")
    
    if pattern.get('structure'):
        lines.extend([
            "## Structure",
            "",
        ])
        structure = pattern['structure']
        
        if structure.get('files'):
            lines.append("### Files")
            for file_info in structure['files']:
                lines.append(f"- `{file_info.get('path', 'unknown')}` - {file_info.get('purpose', 'No purpose')}")
            lines.append("")
        
        if structure.get('classes'):
            lines.append("### Classes")
            for cls in structure['classes']:
                lines.append(f"- **{cls.get('name', 'Unknown')}** - {cls.get('purpose', 'No purpose')}")
                if cls.get('methods'):
                    lines.append("  - Methods:")
                    for method in cls['methods']:
                        lines.append(f"    - `{method}`")
            lines.append("")
    
    if pattern.get('modules'):
        lines.extend([
            "## Recommended Modules",
            "",
        ])
        for module in pattern['modules']:
            lines.append(f"- {module}")
        lines.append("")
    
    if pattern.get('example'):
        lines.extend([
            "## Example",
            "",
            "```python",
            pattern['example'],
            "```",
            "",
        ])
    
    if pattern.get('best_practices'):
        lines.extend([
            "## Best Practices",
            "",
        ])
        for practice in pattern['best_practices']:
            lines.append(f"- {practice}")
        lines.append("")
    
    if pattern.get('common_pitfalls'):
        lines.extend([
            "## Common Pitfalls",
            "",
        ])
        for pitfall in pattern['common_pitfalls']:
            lines.append(f"- {pitfall}")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "📚 *Use `design-patterns://list` to see all patterns*",
    ])
    
    return "\n".join(lines)
