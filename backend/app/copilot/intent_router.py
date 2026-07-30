"""Intent router for AI Software Architect Copilot.

Routes user queries to appropriate CodeGraph modules.
"""

import logging
from typing import Any

from app.copilot.capability_registry import CapabilityRegistry, capability_registry

logger = logging.getLogger(__name__)


class IntentRouter:
    """Routes user queries to appropriate modules.

    Uses the capability registry to determine intent.
    """

    def __init__(self, capability_registry: CapabilityRegistry | None = None):
        """Initialize the intent router.

        Args:
            capability_registry: Optional CapabilityRegistry instance.
        """
        self.capability_registry = capability_registry or CapabilityRegistry()

    def route_query(
        self,
        query: str,
        repository_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Route query to appropriate module.

        Args:
            query: User query.
            repository_data: Repository data.

        Returns:
            Dictionary with routing information.
        """
        # Resolve intent
        intent = self.capability_registry.resolve_intent(query)

        if not intent:
            return {
                "query": query,
                "intent": "unknown",
                "module": None,
                "confidence": 0,
            }

        # Calculate confidence based on keyword match strength
        confidence = self._calculate_confidence(query, intent)

        return {
            "query": query,
            "intent": intent["capability"],
            "module": intent["module"],
            "matched_keyword": intent.get("matched_keyword"),
            "confidence": confidence,
        }

    def _calculate_confidence(
        self,
        query: str,
        intent: dict[str, Any],
    ) -> int:
        """Calculate confidence score for intent match.

        Args:
            query: User query.
            intent: Intent information.

        Returns:
            Confidence score (0-100).
        """
        matched_keyword = intent.get("matched_keyword", "")
        query_lower = query.lower()

        # Higher confidence if keyword appears multiple times or is exact match
        if matched_keyword in query_lower:
            if query_lower.strip() == matched_keyword:
                return 100
            return 85

        return 70


intent_router = IntentRouter()
