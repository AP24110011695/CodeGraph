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
        # File Lookup
        self.register_capability(
            "file_lookup",
            [
                "where is",
                "find file",
                "find function",
                "where do we",
                "location of",
                "which file",
            ],
            "rag",
        )

        # Code Explanation
        self.register_capability(
            "code_explanation",
            [
                "explain this function",
                "explain this code",
                "what does this do",
                "how does this work",
                "explain",
                "walk me through",
            ],
            "rag",
        )

        # Workflow
        self.register_capability(
            "workflow",
            [
                "upload flow",
                "workflow",
                "flow",
                "lifecycle",
                "process",
                "pipeline",
                "step by step",
            ],
            "rag",
        )

        # Architecture
        self.register_capability(
            "architecture",
            [
                "architecture",
                "architectural",
                "structure",
                "design",
                "components",
                "relationships",
                "data flow",
            ],
            "rag",
        )

        # Bug Analysis
        self.register_capability(
            "bug_analysis",
            [
                "bug",
                "issue",
                "problem",
                "error",
                "vulnerability",
                "wrong",
                "fail",
                "fix",
            ],
            "rag",
        )

        # General Query (Fallback)
        self.register_capability(
            "general_query",
            ["repository info", "overview"],
            "rag",
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

        # Deterministic intent rules (pre-check before keyword matching)
        deterministic_match = self._apply_deterministic_rules(query_lower)
        if deterministic_match:
            logger.info(f"Deterministic rule matched: {deterministic_match['capability']}")
            return deterministic_match

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

        # Default: general RAG explanation
        return {
            "capability": "general_query",
            "module": "rag",
            "matched_keyword": None,
        }

    def _apply_deterministic_rules(self, query_lower: str) -> dict[str, Any] | None:
        """Apply deterministic intent rules before keyword matching.

        Maps specific query patterns to Phase 1 intents:
        file_lookup, code_explanation, workflow, architecture, bug_analysis.
        """
        # File Lookup: "where is X", "find X", "which file", "location of"
        file_lookup_patterns = [
            "where is",
            "where are",
            "find file",
            "find function",
            "find class",
            "where do we",
            "location of",
            "which file",
            "which module",
            "what file",
            "implemented in",
        ]
        for pattern in file_lookup_patterns:
            if pattern in query_lower:
                return {
                    "capability": "file_lookup",
                    "module": "rag",
                    "matched_keyword": pattern,
                }

        # Workflow: step-by-step trace of a request/operation flow
        workflow_patterns = [
            "upload flow",
            "indexing flow",
            "how does upload",
            "how does indexing",
            "step by step",
            "end to end",
            "end-to-end",
            "explain the flow",
            "trace the flow",
            "explain the process",
            "how does the",
        ]
        for pattern in workflow_patterns:
            if pattern in query_lower:
                return {
                    "capability": "workflow",
                    "module": "rag",
                    "matched_keyword": pattern,
                }

        # Bug Analysis: bugs, problems, issues, vulnerabilities
        bug_patterns = [
            "find bugs",
            "find issues",
            "possible issues",
            "possible bugs",
            "what is wrong",
            "what could go wrong",
            "security vulnerability",
            "security issue",
            "vulnerability",
            "vulnerabilities",
        ]
        for pattern in bug_patterns:
            if pattern in query_lower:
                return {
                    "capability": "bug_analysis",
                    "module": "rag",
                    "matched_keyword": pattern,
                }

        # Architecture: high-level structure and design
        architecture_patterns = [
            "explain the architecture",
            "explain architecture",
            "system architecture",
            "project architecture",
            "codebase architecture",
            "overall architecture",
            "high level",
            "high-level",
            "module structure",
            "component structure",
        ]
        for pattern in architecture_patterns:
            if pattern in query_lower:
                return {
                    "capability": "architecture",
                    "module": "rag",
                    "matched_keyword": pattern,
                }

        # Code Explanation: explain a function/class/module
        code_explanation_patterns = [
            "explain this function",
            "explain this class",
            "explain this code",
            "what does this function",
            "what does this class",
            "what does this do",
            "how does this work",
            "walk me through",
        ]
        for pattern in code_explanation_patterns:
            if pattern in query_lower:
                return {
                    "capability": "code_explanation",
                    "module": "rag",
                    "matched_keyword": pattern,
                }

        return None

    def get_capability_handler(
        self,
        capability_name: str,
    ) -> Callable | None:
        """Get handler for a capability."""
        return None


capability_registry = CapabilityRegistry()
