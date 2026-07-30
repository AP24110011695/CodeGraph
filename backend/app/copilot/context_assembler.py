"""Context assembler for AI Software Architect Copilot.

Assembles repository context for query processing.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ContextAssembler:
    """Assembles repository context.

    Collects relevant repository data for query processing.
    """

    def __init__(self):
        """Initialize the context assembler."""
        pass

    def assemble_context(
        self,
        upload_id: str,
        repository_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Assemble context for a repository.

        Args:
            upload_id: Repository upload ID.
            repository_data: Repository data.

        Returns:
            Dictionary with assembled context.
        """
        return {
            "upload_id": upload_id,
            "repository_name": repository_data.get("repository_name", "Unknown"),
            "languages": repository_data.get("languages", []),
            "frameworks": repository_data.get("frameworks", []),
            "architecture_score": repository_data.get("architecture_score", 0),
            "health_score": repository_data.get("health_score", 0),
            "quality_score": repository_data.get("quality_score", 0),
            "security_score": repository_data.get("security_score", 0),
            "risk_score": repository_data.get("risk_score", 0),
            "total_files": repository_data.get("total_files", 0),
            "status": repository_data.get("status", "UNKNOWN"),
        }

    def enrich_context_with_intent(
        self,
        context: dict[str, Any],
        intent: dict[str, Any],
    ) -> dict[str, Any]:
        """Enrich context with intent information.

        Args:
            context: Repository context.
            intent: Intent information.

        Returns:
            Enriched context.
        """
        context["intent"] = intent["intent"]
        context["module"] = intent["module"]
        context["confidence"] = intent["confidence"]
        context["matched_keyword"] = intent.get("matched_keyword")

        return context


context_assembler = ContextAssembler()
