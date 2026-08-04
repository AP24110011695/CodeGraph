"""Tool Registry — manages specialized analysis tools."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Callable, Any

from app.copilot.models.tool_models import ToolDefinition, ToolResult

logger = logging.getLogger(__name__)

# Type for a tool execution function
ToolHandler = Callable[[str, str, Dict[str, Any]], ToolResult]


class ToolRegistry:
    """Central registry for all specialized tools."""

    def __init__(self) -> None:
        self._definitions: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, ToolHandler] = {}

    def register_tool(self, definition: ToolDefinition, handler: ToolHandler) -> None:
        """Register a new tool."""
        self._definitions[definition.name] = definition
        self._handlers[definition.name] = handler
        logger.info(f"Registered tool: {definition.name}")

    def get_tool(self, name: str) -> Optional[ToolHandler]:
        """Get the execution handler for a specific tool."""
        return self._handlers.get(name)

    def get_definition(self, name: str) -> Optional[ToolDefinition]:
        """Get the metadata definition for a tool."""
        return self._definitions.get(name)

    def find_tools_by_capabilities(self, capabilities: List[str]) -> List[ToolDefinition]:
        """Find tools that provide ANY of the requested capabilities."""
        matched_tools = []
        for name, definition in self._definitions.items():
            # If there's any intersection between requested capabilities and the tool's capabilities
            if set(capabilities).intersection(set(definition.capabilities)):
                matched_tools.append(definition)
        return matched_tools

    def list_tools(self) -> List[ToolDefinition]:
        """List all registered tools."""
        return list(self._definitions.values())


# Singleton instance
tool_registry = ToolRegistry()
