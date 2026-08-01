"""Capability registry for AI Software Architect Copilot.

Registers all available CodeGraph capabilities for routing queries.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Callable

logger = logging.getLogger(__name__)


def _keyword_matches(keyword: str, query_lower: str) -> bool:
    """Match multi-word phrases by substring; single tokens by word boundary."""
    keyword = keyword.lower().strip()
    if not keyword:
        return False
    if " " in keyword:
        return keyword in query_lower
    return re.search(rf"\b{re.escape(keyword)}\b", query_lower) is not None


class CapabilityRegistry:
    """Registry of CodeGraph capabilities.

    Maps query intents to appropriate modules.
    """

    def __init__(self):
        """Initialize the capability registry."""
        self.capabilities: dict[str, dict[str, Any]] = {}
        self._register_capabilities()

    def _register_capabilities(self) -> None:
        """Register all available capabilities.

        Order matters: more specific phrases / capabilities first.
        """
        # Language / metrics (before generic "repository" and short tokens like "pr")
        self.register_capability(
            "language_analysis",
            [
                "programming language",
                "programming languages",
                "what language",
                "which language",
                "languages used",
                "language used",
                "languages",
                "language",
                "tech stack",
                "frameworks",
                "framework",
            ],
            "metrics",
        )
        self.register_capability(
            "repository_overview",
            [
                "how many files",
                "number of files",
                "file count",
                "files in the repository",
                "files in repository",
                "total files",
                "how many folders",
            ],
            "metrics",
        )

        # Architecture
        self.register_capability(
            "architecture_health",
            ["architecture", "architectural", "structure", "design", "summarize architecture"],
            "architecture_report",
        )
        self.register_capability(
            "architecture_recommendation",
            ["recommendation", "improvement", "suggestion"],
            "architecture_recommendation",
        )
        self.register_capability(
            "architecture_drift",
            ["drift", "evolution"],
            "architecture_drift",
        )
        self.register_capability(
            "repository_timeline",
            [
                "timeline",
                "what changed",
                "hotspot",
                "unstable",
                "ownership",
                "evolve together",
                "tightly coupled",
                "repository history",
            ],
            "timeline",
        )
        self.register_capability(
            "impact_analysis",
            [
                "impact",
                "what breaks",
                "blast radius",
                "propagation",
                "depend on this",
                "change risk",
                "if i modify",
            ],
            "impact_analysis",
        )
        self.register_capability(
            "engineering_reports",
            [
                "engineering report",
                "executive report",
                "health report",
                "technical debt report",
                "repository health",
            ],
            "engineering_reports",
        )

        # Quality
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

        # Security (before generic "risk")
        self.register_capability(
            "security_analysis",
            ["security", "vulnerability", "vulnerabilities", "threat", "cve", "exploit"],
            "security",
        )

        # Risk
        self.register_capability(
            "risk_analysis",
            ["risks", "risk", "technical debt", "danger"],
            "risk",
        )

        # Dependency
        self.register_capability(
            "dependency_health",
            ["package", "library", "dependency health"],
            "dependency_health",
        )
        self.register_capability(
            "dependency_graph",
            ["dependency graph", "dependency map", "connections", "dependencies"],
            "dependency_graph",
        )

        # Bug localization
        self.register_capability(
            "bug_localization",
            ["bug", "error", "issue", "debug"],
            "bug_localization",
        )

        # Metrics (generic)
        self.register_capability(
            "metrics",
            ["metric", "measurement", "statistics", "stats"],
            "metrics",
        )

        # Design patterns / SOLID / microservices / schema / API
        self.register_capability(
            "design_patterns",
            ["design pattern", "patterns", "pattern", "implementation"],
            "design_patterns",
        )
        self.register_capability(
            "solid_principles",
            ["solid", "oop", "principle"],
            "solid",
        )
        self.register_capability(
            "microservices",
            ["microservice", "service boundary"],
            "microservices",
        )
        self.register_capability(
            "database_schema",
            ["database", "schema", "sql", "table"],
            "database_schema",
        )
        self.register_capability(
            "api_flow",
            ["api", "endpoint", "route", "rest"],
            "api_flow",
        )

        # Documentation
        self.register_capability(
            "documentation",
            ["readme", "docs", "documentation"],
            "readme",
        )
        self.register_capability(
            "api_documentation",
            ["api docs", "swagger", "openapi"],
            "apidocs",
        )

        # UML / knowledge graph
        self.register_capability(
            "uml_diagrams",
            ["uml", "diagram", "class diagram", "sequence"],
            "uml",
        )
        self.register_capability(
            "knowledge_graph",
            ["knowledge graph", "entity", "relationship"],
            "knowledge_graph",
        )

        # Repository comparison / release notes / dashboard / team
        self.register_capability(
            "repository_comparison",
            ["compare", "difference", "versus", "against"],
            "repository_comparison",
        )
        self.register_capability(
            "release_notes",
            ["release", "changelog", "version"],
            "release_notes",
        )
        self.register_capability(
            "dashboard",
            ["dashboard", "executive summary"],
            "dashboard",
        )
        self.register_capability(
            "team_analytics",
            ["team", "analytics", "workspace"],
            "team_analytics",
        )

        # CI/CD / GitHub / Jira — avoid short ambiguous tokens like bare "pr"
        self.register_capability(
            "cicd",
            ["cicd", "ci/cd", "pipeline", "build", "deploy"],
            "cicd",
        )
        self.register_capability(
            "github",
            ["github", "commit", "pull request", "pull-request"],
            "github",
        )
        self.register_capability(
            "jira",
            ["jira", "ticket"],
            "jira",
        )

        # Generic repository info (last among repository phrases)
        self.register_capability(
            "repository_info",
            ["repository info", "repo info", "overview"],
            "scanner",
        )

    def register_capability(
        self,
        capability_name: str,
        keywords: list[str],
        module_name: str,
    ) -> None:
        """Register a capability."""
        self.capabilities[capability_name] = {
            "keywords": keywords,
            "module": module_name,
        }

    def resolve_intent(
        self,
        query: str,
    ) -> dict[str, Any] | None:
        """Resolve query intent to capability."""
        query_lower = query.lower()

        # Prefer longer keyword matches first across all capabilities
        candidates: list[tuple[int, str, dict[str, Any], str]] = []
        for capability_name, capability_info in self.capabilities.items():
            for keyword in capability_info["keywords"]:
                if _keyword_matches(keyword, query_lower):
                    candidates.append(
                        (
                            len(keyword),
                            capability_name,
                            capability_info,
                            keyword,
                        )
                    )

        if candidates:
            candidates.sort(key=lambda item: item[0], reverse=True)
            _, capability_name, capability_info, keyword = candidates[0]
            return {
                "capability": capability_name,
                "module": capability_info["module"],
                "matched_keyword": keyword,
            }

        # Default: general RAG explanation (not scanner/memory)
        return {
            "capability": "general_query",
            "module": "rag",
            "matched_keyword": None,
        }

    def get_capability_handler(
        self,
        capability_name: str,
    ) -> Callable | None:
        """Get handler for a capability."""
        return None


capability_registry = CapabilityRegistry()
