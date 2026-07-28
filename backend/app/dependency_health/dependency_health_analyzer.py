"""Dependency health analyzer for dependency health dashboard.

Analyzes dependency health using existing dependency graph and analyzers.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DependencyFinding:
    """A dependency health finding."""

    title: str
    category: str
    severity: str
    score: int
    evidence: str
    affected_files: list[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class DependencyStatistics:
    """Statistics about dependencies."""

    internal_dependencies: int = 0
    external_dependencies: int = 0
    cycles: int = 0
    critical_modules: int = 0
    high_risk_modules: int = 0
    coupling_density: float = 0.0
    fan_out_max: int = 0
    fan_in_max: int = 0
    isolated_modules: int = 0


class DependencyHealthAnalyzer:
    """Analyzes dependency health using existing dependency graph and analyzers.

    Reuses outputs from:
    - Dependency Graph Builder
    - Architecture Builder
    - Security Analyzer
    - Quality Analyzer
    - Metrics Engine
    """

    def __init__(self):
        """Initialize the dependency health analyzer."""
        pass

    def analyze(
        self,
        dependency_result: dict | None = None,
        architecture_result: dict | None = None,
        security_issues: list[dict] | None = None,
        metrics_result: dict | None = None,
    ) -> tuple[list[DependencyFinding], DependencyStatistics]:
        """Analyze dependency health.

        Args:
            dependency_result: Result from DependencyGraphBuilder.
            architecture_result: Result from ArchitectureBuilder.
            security_issues: Issues from SecurityAnalyzer.
            metrics_result: Result from MetricsEngine.

        Returns:
            Tuple of (findings, statistics).
        """
        findings: list[DependencyFinding] = []
        stats = DependencyStatistics()

        if not dependency_result:
            return findings, stats

        # Calculate basic statistics
        stats = self._calculate_statistics(dependency_result)

        # Analyze cycles
        cycle_findings = self._analyze_cycles(dependency_result)
        findings.extend(cycle_findings)
        stats.cycles = len(cycle_findings)

        # Analyze coupling
        coupling_findings = self._analyze_coupling(dependency_result)
        findings.extend(coupling_findings)

        # Analyze fan-out
        fan_out_findings = self._analyze_fan_out(dependency_result)
        findings.extend(fan_out_findings)

        # Analyze fan-in
        fan_in_findings = self._analyze_fan_in(dependency_result)
        findings.extend(fan_in_findings)

        # Analyze isolated modules
        isolated_findings = self._analyze_isolated_modules(dependency_result)
        findings.extend(isolated_findings)

        # Analyze critical modules
        critical_findings = self._analyze_critical_modules(dependency_result, security_issues)
        findings.extend(critical_findings)
        stats.critical_modules = len(critical_findings)

        # Analyze high-risk modules
        high_risk_findings = self._analyze_high_risk_modules(dependency_result, metrics_result)
        findings.extend(high_risk_findings)
        stats.high_risk_modules = len(high_risk_findings)

        # Merge duplicate findings
        findings = self._merge_duplicate_findings(findings)

        return findings, stats

    def _calculate_statistics(self, dependency_result: dict) -> DependencyStatistics:
        """Calculate basic dependency statistics."""
        stats = DependencyStatistics()

        nodes = dependency_result.get("nodes", [])
        edges = dependency_result.get("edges", [])

        # Count internal vs external dependencies
        for node in nodes:
            # Handle both string nodes and dict nodes with 'id' field
            node_id = node if isinstance(node, str) else node.get("id", "")
            if node_id.startswith("node:"):
                stats.internal_dependencies += 1
            else:
                stats.external_dependencies += 1

        # Calculate coupling density
        if len(nodes) > 0:
            stats.coupling_density = len(edges) / len(nodes)

        # Count isolated modules
        stats.isolated_modules = dependency_result.get("isolated_files", 0)

        # Calculate fan-in and fan-out
        fan_in: dict[str, int] = defaultdict(int)
        fan_out: dict[str, int] = defaultdict(int)

        for edge in edges:
            # Handle tuple edges, dict edges, and object edges
            if isinstance(edge, tuple):
                from_node = edge[0]
                to_node = edge[1]
            elif isinstance(edge, dict):
                from_node = edge.get("from_node", "")
                to_node = edge.get("to_node", "")
            else:
                # Assume object with from_node and to_node attributes
                from_node = getattr(edge, "from_node", "")
                to_node = getattr(edge, "to_node", "")

            fan_out[from_node] += 1
            fan_in[to_node] += 1

        if fan_out:
            stats.fan_out_max = max(fan_out.values())
        if fan_in:
            stats.fan_in_max = max(fan_in.values())

        return stats

    def _analyze_cycles(self, dependency_result: dict) -> list[DependencyFinding]:
        """Analyze dependency cycles."""
        findings: list[DependencyFinding] = []

        # Simple cycle detection using DFS
        nodes = dependency_result.get("nodes", [])
        edges = dependency_result.get("edges", [])

        # Build adjacency list
        graph: dict[str, list[str]] = defaultdict(list)
        for edge in edges:
            # Handle tuple edges, dict edges, and object edges
            if isinstance(edge, tuple):
                from_node = edge[0]
                to_node = edge[1]
            elif isinstance(edge, dict):
                from_node = edge.get("from_node", "")
                to_node = edge.get("to_node", "")
            else:
                # Assume object with from_node and to_node attributes
                from_node = getattr(edge, "from_node", "")
                to_node = getattr(edge, "to_node", "")
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
            # Handle both string nodes and dict nodes with 'id' field
            node_id = node if isinstance(node, str) else node.get("id", "")
            if node_id not in visited:
                dfs(node_id, [])

        # Create findings for cycles
        for cycle in cycles:
            if len(cycle) > 1:
                finding = DependencyFinding(
                    title="Circular Dependency Detected",
                    category="Architecture",
                    severity="High",
                    score=90,
                    evidence=f"Cycle detected: {' -> '.join(cycle)}",
                    affected_files=cycle,
                    recommendation="Break the circular dependency using dependency inversion or refactoring",
                )
                findings.append(finding)

        return findings

    def _analyze_coupling(self, dependency_result: dict) -> list[DependencyFinding]:
        """Analyze coupling density."""
        findings: list[DependencyFinding] = []

        nodes = dependency_result.get("nodes", [])
        edges = dependency_result.get("edges", [])

        if len(nodes) > 0:
            coupling_density = len(edges) / len(nodes)

            if coupling_density > 3:
                score = min(90, 60 + (coupling_density - 3) * 10)
                finding = DependencyFinding(
                    title="High Coupling Density",
                    category="Architecture",
                    severity="High" if coupling_density > 4 else "Medium",
                    score=round(score),
                    evidence=f"Coupling density: {coupling_density:.2f} edges per node",
                    affected_files=[],
                    recommendation="Consider refactoring to reduce coupling between modules",
                )
                findings.append(finding)

        return findings

    def _analyze_fan_out(self, dependency_result: dict) -> list[DependencyFinding]:
        """Analyze fan-out (outgoing dependencies)."""
        findings: list[DependencyFinding] = []

        edges = dependency_result.get("edges", [])

        fan_out: dict[str, int] = defaultdict(int)
        for edge in edges:
            # Handle tuple edges, dict edges, and object edges
            if isinstance(edge, tuple):
                from_node = edge[0]
            elif isinstance(edge, dict):
                from_node = edge.get("from_node", "")
            else:
                # Assume object with from_node and to_node attributes
                from_node = getattr(edge, "from_node", "")
            fan_out[from_node] += 1

        for node, count in fan_out.items():
            if count > 10:
                score = min(85, 50 + (count - 10) * 3)
                finding = DependencyFinding(
                    title=f"High Fan-Out: {node}",
                    category="Architecture",
                    severity="Medium",
                    score=round(score),
                    evidence=f"Module has {count} outgoing dependencies",
                    affected_files=[node],
                    recommendation="Consider reducing dependencies by extracting interfaces or using dependency injection",
                )
                findings.append(finding)

        return findings

    def _analyze_fan_in(self, dependency_result: dict) -> list[DependencyFinding]:
        """Analyze fan-in (incoming dependencies)."""
        findings: list[DependencyFinding] = []

        edges = dependency_result.get("edges", [])

        fan_in: dict[str, int] = defaultdict(int)
        for edge in edges:
            # Handle tuple edges, dict edges, and object edges
            if isinstance(edge, tuple):
                to_node = edge[1]
            elif isinstance(edge, dict):
                to_node = edge.get("to_node", "")
            else:
                # Assume object with from_node and to_node attributes
                to_node = getattr(edge, "to_node", "")
            fan_in[to_node] += 1

        for node, count in fan_in.items():
            if count > 10:
                score = min(80, 50 + (count - 10) * 2)
                finding = DependencyFinding(
                    title=f"High Fan-In: {node}",
                    category="Architecture",
                    severity="Medium",
                    score=round(score),
                    evidence=f"Module is depended on by {count} other modules",
                    affected_files=[node],
                    recommendation="Consider splitting this module or using facade pattern to reduce coupling",
                )
                findings.append(finding)

        return findings

    def _analyze_isolated_modules(self, dependency_result: dict) -> list[DependencyFinding]:
        """Analyze isolated modules."""
        findings: list[DependencyFinding] = []

        isolated_count = dependency_result.get("isolated_files", 0)

        if isolated_count > 0:
            score = min(70, 40 + isolated_count * 5)
            finding = DependencyFinding(
                title=f"Isolated Modules Detected ({isolated_count})",
                category="Architecture",
                severity="Low",
                score=round(score),
                evidence=f"{isolated_count} modules have no dependencies",
                affected_files=[],
                recommendation="Review isolated modules and integrate them or remove if unused",
            )
            findings.append(finding)

        return findings

    def _analyze_critical_modules(self, dependency_result: dict, security_issues: list[dict] | None) -> list[DependencyFinding]:
        """Analyze critical modules based on security issues."""
        findings: list[DependencyFinding] = []

        if not security_issues:
            return findings

        # Group security issues by file
        file_issues: dict[str, int] = defaultdict(int)
        for issue in security_issues:
            file = issue.get("file", "")
            if file:
                file_issues[file] += 1

        # Identify critical modules (files with multiple security issues)
        for file, count in file_issues.items():
            if count >= 2:
                finding = DependencyFinding(
                    title=f"Critical Module: {file}",
                    category="Security",
                    severity="High",
                    score=85,
                    evidence=f"Module has {count} security issues",
                    affected_files=[file],
                    recommendation="Review and fix all security issues in this module",
                )
                findings.append(finding)

        return findings

    def _analyze_high_risk_modules(self, dependency_result: dict, metrics_result: dict | None) -> list[DependencyFinding]:
        """Analyze high-risk modules based on metrics."""
        findings: list[DependencyFinding] = []

        if not metrics_result:
            return findings

        stats = metrics_result.get("statistics", {})
        smell_count = stats.get("smell_count", 0)

        if smell_count > 10:
            finding = DependencyFinding(
                title="High Code Smell Count",
                category="Maintainability",
                severity="Medium",
                score=70,
                evidence=f"Repository has {smell_count} code smells",
                affected_files=[],
                recommendation="Address code smells to improve maintainability",
            )
            findings.append(finding)

        return findings

    def _merge_duplicate_findings(self, findings: list[DependencyFinding]) -> list[DependencyFinding]:
        """Merge duplicate findings based on title and category."""
        seen: dict[str, DependencyFinding] = {}

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


dependency_health_analyzer = DependencyHealthAnalyzer()
