"""Communication analyzer for microservice boundary detection engine.

Analyzes communication patterns between modules.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CommunicationPattern:
    """A communication pattern between modules."""

    source: str
    target: str
    pattern: str
    frequency: int


@dataclass
class CommunicationAnalysis:
    """Analysis of communication patterns."""

    patterns: list[CommunicationPattern]
    shared_components: list[str]
    cross_domain_dependencies: list[str]
    service_independence_score: int


class CommunicationAnalyzer:
    """Analyzes communication patterns from repository analysis.

    Reuses outputs from:
    - Dependency Graph
    - Architecture Builder
    - Repository Scanner
    """

    def __init__(self):
        """Initialize the communication analyzer."""
        pass

    def analyze_communication(
        self,
        project_path: Path,
        dependency_graph: dict | None = None,
        architecture_result: dict | None = None,
    ) -> CommunicationAnalysis:
        """Analyze communication patterns in the repository.

        Args:
            project_path: The project path.
            dependency_graph: The dependency graph.
            architecture_result: The architecture result.

        Returns:
            CommunicationAnalysis with communication patterns.
        """
        patterns: list[CommunicationPattern] = []

        # Detect communication patterns from dependency graph
        if dependency_graph:
            patterns = self._detect_communication_patterns(dependency_graph)

        # Detect shared components
        shared_components = self._detect_shared_components(project_path)

        # Detect cross-domain dependencies
        cross_domain_dependencies = self._detect_cross_domain_dependencies(
            project_path, dependency_graph
        )

        # Calculate service independence score
        service_independence_score = self._calculate_service_independence_score(
            patterns, shared_components, cross_domain_dependencies
        )

        return CommunicationAnalysis(
            patterns=patterns,
            shared_components=shared_components,
            cross_domain_dependencies=cross_domain_dependencies,
            service_independence_score=service_independence_score,
        )

    def _detect_communication_patterns(
        self,
        dependency_graph: dict | None,
    ) -> list[CommunicationPattern]:
        """Detect communication patterns from dependency graph.

        Args:
            dependency_graph: The dependency graph.

        Returns:
            List of communication patterns.
        """
        patterns: list[CommunicationPattern] = []

        if dependency_graph:
            # Handle GraphResult object
            if hasattr(dependency_graph, 'edges'):
                edges = dependency_graph.edges
            else:
                edges = dependency_graph.get("edges", [])

            # Analyze edges for patterns
            edge_count: dict[str, int] = {}
            for edge in edges:
                if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                    source = str(edge[0])
                    target = str(edge[1])
                    key = f"{source}->{target}"
                    edge_count[key] = edge_count.get(key, 0) + 1

            # Create patterns from frequent edges
            for key, count in edge_count.items():
                if count > 1:
                    source, target = key.split("->")
                    patterns.append(
                        CommunicationPattern(
                            source=source,
                            target=target,
                            pattern="direct",
                            frequency=count,
                        )
                    )

        return patterns

    def _detect_shared_components(self, project_path: Path) -> list[str]:
        """Detect shared components in the repository.

        Args:
            project_path: The project path.

        Returns:
            List of shared component names.
        """
        shared_components: list[str] = []

        # Look for common shared component folders
        shared_keywords = ["shared", "common", "utils", "helpers", "core", "base"]

        for item in project_path.iterdir():
            if item.is_dir():
                if any(keyword in item.name.lower() for keyword in shared_keywords):
                    shared_components.append(item.name)

        return shared_components

    def _detect_cross_domain_dependencies(
        self,
        project_path: Path,
        dependency_graph: dict | None,
    ) -> list[str]:
        """Detect cross-domain dependencies.

        Args:
            project_path: The project path.
            dependency_graph: The dependency graph.

        Returns:
            List of cross-domain dependency descriptions.
        """
        cross_domain: list[str] = []

        # Look for cross-domain imports
        domain_keywords = ["auth", "user", "payment", "order", "product", "inventory"]

        for file in project_path.rglob("*"):
            if file.is_file() and file.suffix in [".py", ".java", ".ts", ".js"]:
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    for domain in domain_keywords:
                        if domain in content.lower():
                            cross_domain.append(f"{file.name} depends on {domain} domain")
                            break
                except Exception:
                    continue

        return cross_domain[:10]  # Limit to 10

    def _calculate_service_independence_score(
        self,
        patterns: list[CommunicationPattern],
        shared_components: list[str],
        cross_domain_dependencies: list[str],
    ) -> int:
        """Calculate service independence score.

        Args:
            patterns: Communication patterns.
            shared_components: Shared components.
            cross_domain_dependencies: Cross-domain dependencies.

        Returns:
            Service independence score (0-100).
        """
        # Start with 100 and deduct for dependencies
        score = 100

        # Deduct for shared components (they reduce independence)
        score -= len(shared_components) * 5

        # Deduct for cross-domain dependencies
        score -= len(cross_domain_dependencies) * 3

        # Deduct for frequent communication patterns
        high_freq_patterns = [p for p in patterns if p.frequency > 5]
        score -= len(high_freq_patterns) * 2

        return max(0, score)


communication_analyzer = CommunicationAnalyzer()
