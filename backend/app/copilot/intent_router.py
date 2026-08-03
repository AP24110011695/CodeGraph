"""Intent router for AI Software Architect Copilot.

Routes user queries to appropriate CodeGraph modules and builds the
execution plan consumed by CopilotEngine / ToolExecutor.
"""

from __future__ import annotations

import logging
from typing import Any

from app.copilot.capability_registry import CapabilityRegistry, capability_registry

logger = logging.getLogger(__name__)

# Phase 1 intent → ToolExecutor module names.
# All Phase 1 intents route through RAG Engine only.
_CAPABILITY_MODULES: dict[str, list[str]] = {
    # Phase 1 intents (RAG-only)
    "file_lookup": ["RAG Engine"],
    "code_explanation": ["RAG Engine"],
    "workflow": ["RAG Engine"],
    "architecture": ["RAG Engine"],
    "bug_analysis": ["RAG Engine"],
    "general_query": ["RAG Engine"],
    # Legacy intents — preserved so existing tests/tools don't break
    "language_analysis": ["Metrics Engine", "Language Analyzer"],
    "repository_overview": ["Repository Overview", "Metrics Engine"],
    "repository_info": ["Repository Overview", "Metrics Engine"],
    "metrics": ["Metrics Engine", "Language Analyzer"],
    "architecture_health": ["RAG Engine"],
    "architecture_recommendation": ["Architecture Analyzer", "Dependency Graph"],
    "architecture_drift": ["Architecture Analyzer", "Dependency Graph"],
    "dependency_graph": ["Dependency Graph", "Architecture Analyzer"],
    "dependency_health": ["Dependency Graph", "Metrics Engine"],
    "security_analysis": ["RAG Engine"],
    "quality_analysis": ["Engineering Reports"],
    "code_smells": ["Engineering Reports"],
    "risk_analysis": ["Engineering Reports", "Security Analyzer"],
    "impact_analysis": ["Impact Analysis Engine", "Knowledge Graph"],
    "repository_timeline": ["Timeline Intelligence Engine", "Repository Memory"],
    "engineering_reports": ["Engineering Reports"],
    "knowledge_graph": ["Knowledge Graph", "RAG Engine"],
    "bug_localization": ["RAG Engine"],
    "documentation": ["RAG Engine"],
    "api_documentation": ["RAG Engine"],
    "api_flow": ["RAG Engine"],
    "unknown": ["RAG Engine"],
}


class IntentRouter:
    """Routes user queries to appropriate modules.

    Uses the capability registry to determine intent, then expands that into
    an execution plan for ToolExecutor.
    """

    def __init__(self, capability_registry: CapabilityRegistry | None = None):
        self.capability_registry = capability_registry or CapabilityRegistry()

    def route_query(
        self,
        query: str,
        repository_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Route query to appropriate module."""
        intent = self.capability_registry.resolve_intent(query)

        if not intent:
            return {
                "query": query,
                "intent": "general_query",
                "module": "rag",
                "confidence": 0,
            }

        confidence = self._calculate_confidence(query, intent)

        return {
            "query": query,
            "intent": intent["capability"],
            "module": intent["module"],
            "matched_keyword": intent.get("matched_keyword"),
            "confidence": confidence,
        }

    def build_execution_plan(
        self,
        query: str,
        repository_id: str | None = None,
    ) -> dict[str, Any]:
        """Build a ToolExecutor-compatible plan from capability routing."""
        routing = self.route_query(query, {"repository_id": repository_id})
        intent = str(routing.get("intent") or "general_query")
        modules = list(_CAPABILITY_MODULES.get(intent, _CAPABILITY_MODULES["general_query"]))

        confidence = float(routing.get("confidence") or 0) / 100.0
        plan = {
            "query": query,
            "intent": intent,
            "required_modules": modules,
            "execution_order": modules,
            "retrieval_strategy": "IntentRouter",
            "reasoning_strategy": "CapabilityRegistry",
            "confidence_score": confidence,
            "estimated_cost": "Low" if modules == ["RAG Engine"] else "Medium",
            "planning_trace": [
                {
                    "step": "Intent Routing",
                    "description": (
                        f"Classified intent as {intent} "
                        f"(keyword={routing.get('matched_keyword')}, module={routing.get('module')})"
                    ),
                }
            ],
            "matched_keyword": routing.get("matched_keyword"),
            "primary_module": routing.get("module"),
            "repository_id": repository_id,
        }

        logger.info("QUERY: %s", query)
        logger.info("CLASSIFIED_INTENT: %s", intent)
        logger.info("CONFIDENCE: %.2f", confidence)
        logger.info("SELECTED_TOOLS: %s", modules)
        return plan

    def _calculate_confidence(
        self,
        query: str,
        intent: dict[str, Any],
    ) -> int:
        matched_keyword = intent.get("matched_keyword") or ""
        query_lower = query.lower()

        if matched_keyword and matched_keyword in query_lower:
            if query_lower.strip() == matched_keyword:
                return 100
            return 85

        if intent.get("capability") == "general_query":
            return 40

        return 70


intent_router = IntentRouter()
