"""Copilot engine for AI Software Architect Copilot.

Orchestrates all CodeGraph modules to answer user queries.
"""

import logging
from typing import Any

from app.copilot.intent_router import IntentRouter, intent_router
from app.copilot.context_assembler import ContextAssembler, context_assembler
from app.copilot.response_builder import ResponseBuilder, response_builder
from app.copilot.capability_registry import CapabilityRegistry, capability_registry
from app.workspace.repository_registry import RepositoryRegistry, repository_registry

logger = logging.getLogger(__name__)


class CopilotEngine:
    """Performs copilot query operations.

    Orchestrates all CodeGraph modules to answer user queries.
    """

    def __init__(
        self,
        intent_router: IntentRouter | None = None,
        context_assembler: ContextAssembler | None = None,
        response_builder: ResponseBuilder | None = None,
        capability_registry: CapabilityRegistry | None = None,
        repository_registry: RepositoryRegistry | None = None,
    ):
        """Initialize the copilot engine.

        Args:
            intent_router: Optional IntentRouter instance.
            context_assembler: Optional ContextAssembler instance.
            response_builder: Optional ResponseBuilder instance.
            capability_registry: Optional CapabilityRegistry instance.
            repository_registry: Optional RepositoryRegistry instance.
        """
        self.intent_router = intent_router or IntentRouter()
        self.context_assembler = context_assembler or ContextAssembler()
        self.response_builder = response_builder or ResponseBuilder()
        self.capability_registry = capability_registry or CapabilityRegistry()
        self.repository_registry = repository_registry or RepositoryRegistry()

    def process_query(
        self,
        upload_id: str,
        query: str,
    ) -> dict[str, Any]:
        """Process a user query about a repository.

        Args:
            upload_id: Repository upload ID.
            query: User query.

        Returns:
            Dictionary with copilot response.
        """
        # Fetch repository data
        repo_info = self.repository_registry.get_repository(upload_id)

        if not repo_info:
            return {
                "error": f"Repository not found: {upload_id}",
                "upload_id": upload_id,
                "query": query,
            }

        # Build repository data
        repository_data = self._build_repository_data(repo_info)

        # Assemble context
        context = self.context_assembler.assemble_context(upload_id, repository_data)

        # Route query to appropriate module
        routing = self.intent_router.route_query(query, repository_data)

        # Enrich context with intent
        context = self.context_assembler.enrich_context_with_intent(context, routing)

        # Get module output (in a real implementation, this would call the actual module)
        module_output = self._get_module_output(context, routing)

        # Build response
        response = self.response_builder.build_response(context, module_output)

        return {
            "upload_id": upload_id,
            "query": query,
            "intent": routing.get("intent"),
            "module": routing.get("module"),
            "confidence": routing.get("confidence"),
            "answer": response.get("answer"),
            "sources": response.get("sources"),
            "evidence": response.get("evidence"),
            "related_modules": response.get("related_modules"),
        }

    def _build_repository_data(
        self,
        repo_info: Any,
    ) -> dict[str, Any]:
        """Build repository data for copilot.

        Args:
            repo_info: Repository information from registry.

        Returns:
            Dictionary with repository data.
        """
        return {
            "upload_id": repo_info.upload_id,
            "repository_name": repo_info.repository_name,
            "architecture_score": repo_info.architecture_score if repo_info.architecture_score else 50,
            "health_score": repo_info.health_score if repo_info.health_score else 50,
            "quality_score": repo_info.architecture_score if repo_info.architecture_score else 50,
            "security_score": 70,
            "risk_score": 100 - (repo_info.health_score if repo_info.health_score else 50),
            "languages": repo_info.languages if repo_info.languages else [],
            "frameworks": repo_info.frameworks if repo_info.frameworks else [],
            "total_files": 100,
            "status": repo_info.status if repo_info.status else "UNKNOWN",
        }

    def _get_module_output(
        self,
        context: dict[str, Any],
        routing: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Get output from the appropriate module.

        Args:
            context: Repository context.
            routing: Routing information.

        Returns:
            Module output or None.
        """
        # In a real implementation, this would call the actual module
        # For now, we return None and let the response builder handle it
        # This ensures we don't perform duplicate analysis
        return None


copilot_engine = CopilotEngine()
