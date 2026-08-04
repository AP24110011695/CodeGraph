"""Tools package — registers all specialized tools on import."""

# Importing each module causes the tool to self-register in the tool_registry singleton
from app.copilot.tools import (
    architecture_tool,
    workflow_tool,
    api_tool,
    symbol_tool,
    quality_tool,
    security_tool,
)

__all__ = [
    "architecture_tool",
    "workflow_tool",
    "api_tool",
    "symbol_tool",
    "quality_tool",
    "security_tool",
]
