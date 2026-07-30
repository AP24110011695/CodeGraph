"""Capability registry for AI Software Architect Copilot.

Registers all available CodeGraph capabilities for routing queries.
"""

import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class CapabilityRegistry:
    """Registry of CodeGraph capabilities.

    Maps query intents to appropriate modules.
    """

    def __init__(self):
        """Initialize the capability registry."""
        self.capabilities = {}
        self._register_capabilities()

    def _register_capabilities(self) -> None:
        """Register all available capabilities."""
        # Architecture capabilities
        self.register_capability(
            "architecture_health",
            ["architecture", "health", "structure", "design"],
            "architecture_report",
        )
        self.register_capability(
            "architecture_recommendation",
            ["recommendation", "improvement", "suggestion"],
            "architecture_recommendation",
        )
        self.register_capability(
            "architecture_drift",
            ["drift", "change", "evolution"],
            "architecture_drift",
        )

        # Quality capabilities
        self.register_capability(
            "quality_analysis",
            ["quality", "code quality", "maintainability"],
            "quality_analyzer",
        )
        self.register_capability(
            "code_smells",
            ["smell", "code smell", "anti-pattern"],
            "code_generation",
        )

        # Security capabilities
        self.register_capability(
            "security_analysis",
            ["security", "vulnerability", "threat"],
            "security",
        )

        # Risk capabilities
        self.register_capability(
            "risk_analysis",
            ["risk", "technical debt", "danger"],
            "risk",
        )

        # Dependency capabilities
        self.register_capability(
            "dependency_health",
            ["dependency", "package", "library"],
            "dependency_health",
        )
        self.register_capability(
            "dependency_graph",
            ["graph", "dependency map", "connections"],
            "dependency_graph",
        )

        # Bug localization
        self.register_capability(
            "bug_localization",
            ["bug", "error", "issue", "debug"],
            "bug_localization",
        )

        # Metrics
        self.register_capability(
            "metrics",
            ["metric", "measurement", "stat"],
            "metrics",
        )

        # Design patterns
        self.register_capability(
            "design_patterns",
            ["pattern", "design pattern", "implementation"],
            "design_patterns",
        )

        # SOLID principles
        self.register_capability(
            "solid_principles",
            ["solid", "oop", "principle"],
            "solid",
        )

        # Microservices
        self.register_capability(
            "microservices",
            ["microservice", "service boundary", "service"],
            "microservices",
        )

        # Database schema
        self.register_capability(
            "database_schema",
            ["database", "schema", "sql", "table"],
            "database_schema",
        )

        # API flow
        self.register_capability(
            "api_flow",
            ["api", "endpoint", "route", "rest"],
            "api_flow",
        )

        # Documentation
        self.register_capability(
            "documentation",
            ["readme", "docs", "api docs"],
            "readme",
        )
        self.register_capability(
            "api_documentation",
            ["api docs", "swagger", "openapi"],
            "apidocs",
        )

        # UML diagrams
        self.register_capability(
            "uml_diagrams",
            ["uml", "diagram", "class diagram", "sequence"],
            "uml",
        )

        # Knowledge graph
        self.register_capability(
            "knowledge_graph",
            ["knowledge", "graph", "entity", "relationship"],
            "knowledge_graph",
        )

        # Repository comparison
        self.register_capability(
            "repository_comparison",
            ["compare", "difference", "versus", "against"],
            "repository_comparison",
        )

        # Release notes
        self.register_capability(
            "release_notes",
            ["release", "changelog", "version"],
            "release_notes",
        )

        # Dashboard
        self.register_capability(
            "dashboard",
            ["dashboard", "overview", "summary", "executive"],
            "dashboard",
        )

        # Team analytics
        self.register_capability(
            "team_analytics",
            ["team", "analytics", "workspace", "metrics"],
            "team_analytics",
        )

        # CI/CD
        self.register_capability(
            "cicd",
            ["cicd", "pipeline", "build", "deploy"],
            "cicd",
        )

        # GitHub
        self.register_capability(
            "github",
            ["github", "commit", "pr", "pull request"],
            "github",
        )

        # Jira
        self.register_capability(
            "jira",
            ["jira", "issue", "ticket", "project"],
            "jira",
        )

        # General repository info
        self.register_capability(
            "repository_info",
            ["repository", "repo", "info", "overview"],
            "scanner",
        )

    def register_capability(
        self,
        capability_name: str,
        keywords: list[str],
        module_name: str,
    ) -> None:
        """Register a capability.

        Args:
            capability_name: Name of the capability.
            keywords: Keywords that trigger this capability.
            module_name: Module that provides this capability.
        """
        self.capabilities[capability_name] = {
            "keywords": keywords,
            "module": module_name,
        }

    def resolve_intent(
        self,
        query: str,
    ) -> dict[str, Any] | None:
        """Resolve query intent to capability.

        Args:
            query: User query.

        Returns:
            Dictionary with capability info or None.
        """
        query_lower = query.lower()

        # Check for keyword matches
        for capability_name, capability_info in self.capabilities.items():
            for keyword in capability_info["keywords"]:
                if keyword in query_lower:
                    return {
                        "capability": capability_name,
                        "module": capability_info["module"],
                        "matched_keyword": keyword,
                    }

        # Default to general repository info
        return {
            "capability": "repository_info",
            "module": "scanner",
            "matched_keyword": "repository",
        }

    def get_capability_handler(
        self,
        capability_name: str,
    ) -> Callable | None:
        """Get handler for a capability.

        Args:
            capability_name: Name of the capability.

        Returns:
            Handler function or None.
        """
        # In a real implementation, this would return actual module handlers
        # For now, return None as we'll handle routing in the engine
        return None


capability_registry = CapabilityRegistry()
