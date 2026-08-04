"""Tool Router — determines which tools to run based on Intent."""

from __future__ import annotations

import logging
from typing import List

from app.copilot.tool_registry import tool_registry, ToolDefinition

logger = logging.getLogger(__name__)

# Map Phase 1 Intents to Tool Capabilities
_INTENT_CAPABILITIES = {
    "architecture": ["architecture"],
    "architecture_recommendation": ["architecture"],
    "architecture_drift": ["architecture"],
    
    "workflow": ["workflow"],
    "repository_timeline": ["workflow"],
    
    "api_flow": ["api"],
    "api_documentation": ["api"],
    
    "file_lookup": ["symbol"],
    "code_explanation": ["symbol"],
    
    "quality_analysis": ["quality"],
    "code_smells": ["quality"],
    
    "security_analysis": ["security"],
    "risk_analysis": ["security"],
    
    "impact_analysis": ["architecture", "workflow"],
    "dependency_graph": ["architecture"],
    "dependency_health": ["architecture", "quality"],
}


class ToolRouter:
    """Routes an intent to the appropriate set of tools based on capabilities."""

    def __init__(self, registry=None):
        self.registry = registry or tool_registry

    def resolve_tools(self, intent: str, query: str = "") -> List[ToolDefinition]:
        """Determine which tools should run for the given intent and query.
        
        This introduces a capability layer: Intent -> Capabilities -> Tool(s).
        """
        # Determine base capabilities from intent
        capabilities = list(_INTENT_CAPABILITIES.get(intent, []))
        
        # Complex multi-tool overrides based on query keywords
        q = query.lower()
        if "architecture" in q and "workflow" in q:
            if "workflow" not in capabilities: capabilities.append("workflow")
            if "architecture" not in capabilities: capabilities.append("architecture")
            
        if "architecture" in q and "upload" in q:
            if "workflow" not in capabilities: capabilities.append("workflow")
            if "api" not in capabilities: capabilities.append("api")
            if "architecture" not in capabilities: capabilities.append("architecture")
            
        if "quality" in q and "security" in q:
            if "quality" not in capabilities: capabilities.append("quality")
            if "security" not in capabilities: capabilities.append("security")
            
        if not capabilities:
            logger.info(f"No specific capabilities identified for intent '{intent}'")
            return []
            
        logger.info(f"Resolved capabilities: {capabilities} for intent '{intent}'")
        
        # Find all tools that match the requested capabilities
        tools = self.registry.find_tools_by_capabilities(capabilities)
        return tools

tool_router = ToolRouter()
