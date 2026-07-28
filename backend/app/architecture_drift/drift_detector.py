"""Drift detector for architecture drift detection.

Detects architecture drift using existing architecture builder and dependency graph.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass
class DriftFinding:
    """An architecture drift finding."""

    title: str
    category: str
    severity: str
    score: int
    reason: str
    evidence: str
    affected_files: list[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class DriftStatistics:
    """Statistics about architecture drift."""

    violations: int = 0
    layer_violations: int = 0
    cross_layer_dependencies: int = 0
    circular_dependencies: int = 0
    high_coupling: int = 0
    god_modules: int = 0


class DriftDetector:
    """Detects architecture drift using existing architecture builder and dependency graph.

    Reuses outputs from:
    - Architecture Builder
    - Dependency Graph
    - Code Smell Detector
    """

    def __init__(self):
        """Initialize the drift detector."""
        pass

    def detect_drift(
        self,
        architecture_result: dict | None = None,
        dependency_result: dict | None = None,
        smell_issues: list[dict] | None = None,
    ) -> tuple[list[DriftFinding], DriftStatistics]:
        """Detect architecture drift.

        Args:
            architecture_result: Result from ArchitectureBuilder.
            dependency_result: Result from DependencyGraphBuilder.
            smell_issues: Issues from SmellDetector.

        Returns:
            Tuple of (findings, statistics).
        """
        findings: list[DriftFinding] = []
        stats = DriftStatistics()

        if not architecture_result and not dependency_result:
            return findings, stats

        # Detect layer violations
        layer_findings = self._detect_layer_violations(architecture_result, dependency_result)
        findings.extend(layer_findings)
        stats.layer_violations = len(layer_findings)

        # Detect cross-layer dependencies
        cross_layer_findings = self._detect_cross_layer_dependencies(architecture_result, dependency_result)
        findings.extend(cross_layer_findings)
        stats.cross_layer_dependencies = len(cross_layer_findings)

        # Detect circular dependencies
        circular_findings = self._detect_circular_dependencies(dependency_result)
        findings.extend(circular_findings)
        stats.circular_dependencies = len(circular_findings)

        # Detect high coupling
        coupling_findings = self._detect_high_coupling(dependency_result)
        findings.extend(coupling_findings)
        stats.high_coupling = len(coupling_findings)

        # Detect god modules from smells
        god_findings = self._detect_god_modules(smell_issues)
        findings.extend(god_findings)
        stats.god_modules = len(god_findings)

        # Update total violations
        stats.violations = len(findings)

        # Merge duplicate findings
        findings = self._merge_duplicate_findings(findings)

        return findings, stats

    def _detect_layer_violations(self, architecture_result: dict | None, dependency_result: dict | None) -> list[DriftFinding]:
        """Detect layer violations."""
        findings: list[DriftFinding] = []

        if not architecture_result:
            return findings

        # Check for detected layers
        layers = architecture_result.get("layers", [])
        if not layers:
            return findings

        # If we have fewer than expected layers, flag as potential issue
        if len(layers) < 3:
            # Handle both string layers and dict layers
            layer_names = []
            for layer in layers:
                if isinstance(layer, str):
                    layer_names.append(layer)
                elif isinstance(layer, dict):
                    layer_names.append(layer.get('name', 'unknown'))
                else:
                    layer_names.append(str(layer))

            finding = DriftFinding(
                title="Insufficient Layer Separation",
                category="Architecture",
                severity="Medium",
                score=65,
                reason=f"Only {len(layers)} architectural layers detected.",
                evidence=f"Detected layers: {layer_names}",
                affected_files=[],
                recommendation="Consider introducing additional layers (e.g., service, repository) for better separation of concerns.",
            )
            findings.append(finding)

        return findings

    def _detect_cross_layer_dependencies(self, architecture_result: dict | None, dependency_result: dict | None) -> list[DriftFinding]:
        """Detect cross-layer dependencies."""
        findings: list[DriftFinding] = []

        if not dependency_result:
            return findings

        edges = dependency_result.get("edges", [])

        # Infer layers from file paths
        layer_keywords = {
            "api": ["api", "controller", "handler", "view", "endpoint"],
            "service": ["service", "business", "logic", "usecase"],
            "repository": ["repository", "dao", "persistence", "database", "db", "model"],
            "util": ["util", "helper", "common", "shared"],
        }

        # Map files to inferred layers
        file_to_layer: dict[str, str] = {}
        for edge in edges:
            from_node = edge[0] if isinstance(edge, tuple) else edge.get("from_node", "")
            to_node = edge[1] if isinstance(edge, tuple) else edge.get("to_node", "")

            for node in [from_node, to_node]:
                if node not in file_to_layer:
                    node_lower = node.lower()
                    for layer, keywords in layer_keywords.items():
                        if any(keyword in node_lower for keyword in keywords):
                            file_to_layer[node] = layer
                            break
                    else:
                        file_to_layer[node] = "unknown"

        # Check for cross-layer dependencies (e.g., api directly to repository)
        for edge in edges:
            from_node = edge[0] if isinstance(edge, tuple) else edge.get("from_node", "")
            to_node = edge[1] if isinstance(edge, tuple) else edge.get("to_node", "")

            from_layer = file_to_layer.get(from_node, "unknown")
            to_layer = file_to_layer.get(to_node, "unknown")

            # Flag api -> repository as cross-layer violation
            if from_layer == "api" and to_layer == "repository":
                finding = DriftFinding(
                    title="Cross Layer Dependency: API to Repository",
                    category="Architecture",
                    severity="High",
                    score=88,
                    reason="Presentation layer directly imports persistence layer.",
                    evidence=f"Dependency: {from_node} -> {to_node}",
                    affected_files=[from_node, to_node],
                    recommendation="Introduce a service layer to remove direct dependency between API and repository layers.",
                )
                findings.append(finding)

        return findings

    def _detect_circular_dependencies(self, dependency_result: dict | None) -> list[DriftFinding]:
        """Detect circular dependencies."""
        findings: list[DriftFinding] = []

        if not dependency_result:
            return findings

        nodes = dependency_result.get("nodes", [])
        edges = dependency_result.get("edges", [])

        # Build adjacency list
        graph: dict[str, list[str]] = defaultdict(list)
        for edge in edges:
            from_node = edge[0] if isinstance(edge, tuple) else edge.get("from_node", "")
            to_node = edge[1] if isinstance(edge, tuple) else edge.get("to_node", "")
            graph[from_node].append(to_node)

        # Detect cycles using DFS
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node: str, path: list[str]) -> None:
            if node in rec_stack:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                dfs(neighbor, path + [node])

            rec_stack.remove(node)

        for node in nodes:
            node_id = node if isinstance(node, str) else node.get("id", "")
            if node_id not in visited:
                dfs(node_id, [])

        # Create findings for cycles
        for cycle in cycles:
            if len(cycle) > 1:
                finding = DriftFinding(
                    title="Circular Architecture Dependency",
                    category="Architecture",
                    severity="High",
                    score=90,
                    reason=f"Circular dependency detected in architecture.",
                    evidence=f"Cycle: {' -> '.join(cycle)}",
                    affected_files=cycle,
                    recommendation="Break the circular dependency using dependency inversion or refactoring.",
                )
                findings.append(finding)

        return findings

    def _detect_high_coupling(self, dependency_result: dict | None) -> list[DriftFinding]:
        """Detect high coupling."""
        findings: list[DriftFinding] = []

        if not dependency_result:
            return findings

        nodes = dependency_result.get("nodes", [])
        edges = dependency_result.get("edges", [])

        if len(nodes) > 0:
            coupling_density = len(edges) / len(nodes)

            if coupling_density > 3:
                score = min(90, 60 + (coupling_density - 3) * 10)
                finding = DriftFinding(
                    title="High Coupling Density",
                    category="Architecture",
                    severity="High" if coupling_density > 4 else "Medium",
                    score=round(score),
                    reason=f"High coupling density detected: {coupling_density:.2f} edges per node",
                    evidence=f"Total edges: {len(edges)}, Total nodes: {len(nodes)}",
                    affected_files=[],
                    recommendation="Consider refactoring to reduce coupling between modules.",
                )
                findings.append(finding)

        return findings

    def _detect_god_modules(self, smell_issues: list[dict] | None) -> list[DriftFinding]:
        """Detect god modules from code smells."""
        findings: list[DriftFinding] = []

        if not smell_issues:
            return findings

        # Look for God Class smells
        god_classes = [issue for issue in smell_issues if "god" in issue.get("type", "").lower() or "god" in issue.get("description", "").lower()]

        for issue in god_classes:
            finding = DriftFinding(
                title="God Module Detected",
                category="Architecture",
                severity="High",
                score=85,
                reason="Module has too many responsibilities (God Module anti-pattern).",
                evidence=issue.get("description", "God module detected"),
                affected_files=[issue.get("file", "")],
                recommendation="Refactor the module by extracting responsibilities into separate classes.",
            )
            findings.append(finding)

        return findings

    def _merge_duplicate_findings(self, findings: list[DriftFinding]) -> list[DriftFinding]:
        """Merge duplicate findings based on title and category."""
        seen: dict[str, DriftFinding] = {}

        for finding in findings:
            key = f"{finding.category}:{finding.title}"
            if key not in seen:
                seen[key] = finding
            else:
                # Merge affected files
                existing = seen[key]
                for file in finding.affected_files:
                    if file not in existing.affected_files:
                        existing.affected_files.append(file)

        return list(seen.values())


drift_detector = DriftDetector()
