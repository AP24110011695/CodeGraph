"""Change analyzer for pull request review engine.

Analyzes changed files and their impact on the repository.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ChangeImpact:
    """Impact analysis for a changed file."""

    file: str
    change_type: str  # ADDED, MODIFIED, DELETED
    architecture_impact: int = 0
    dependency_impact: int = 0
    security_impact: int = 0
    quality_impact: int = 0
    risk_increase: int = 0
    maintainability_impact: int = 0
    documentation_impact: int = 0
    testing_impact: int = 0
    performance_impact: int = 0


class ChangeAnalyzer:
    """Analyzes changed files and their impact.

    Reuses outputs from:
    - Architecture Drift Engine
    - Dependency Health Engine
    - Security Analyzer
    - Code Smell Detector
    - Risk Engine
    - Quality Analyzer
    """

    def __init__(self):
        """Initialize the change analyzer."""
        pass

    def analyze_changes(
        self,
        changed_files: list[str],
        project_path: Path,
        architecture_result: dict | None = None,
        dependency_result: dict | None = None,
        security_findings: list[dict] | None = None,
        smell_findings: list[dict] | None = None,
        risk_findings: list[dict] | None = None,
        quality_findings: list[dict] | None = None,
    ) -> list[ChangeImpact]:
        """Analyze the impact of changed files.

        Args:
            changed_files: List of changed file paths.
            project_path: Absolute path to the project directory.
            architecture_result: Result from architecture drift engine.
            dependency_result: Result from dependency health engine.
            security_findings: Findings from security analyzer.
            smell_findings: Findings from code smell detector.
            risk_findings: Findings from risk engine.
            quality_findings: Findings from quality analyzer.

        Returns:
            List of change impacts for each file.
        """
        impacts: list[ChangeImpact] = []

        for file_path in changed_files:
            impact = ChangeImpact(
                file=file_path,
                change_type="MODIFIED",  # Default to MODIFIED
            )

            # Analyze architecture impact
            if architecture_result:
                impact.architecture_impact = self._analyze_architecture_impact(file_path, architecture_result)

            # Analyze dependency impact
            if dependency_result:
                impact.dependency_impact = self._analyze_dependency_impact(file_path, dependency_result)

            # Analyze security impact
            if security_findings:
                impact.security_impact = self._analyze_security_impact(file_path, security_findings)

            # Analyze quality impact
            if smell_findings:
                impact.quality_impact = self._analyze_quality_impact(file_path, smell_findings)

            # Analyze risk increase
            if risk_findings:
                impact.risk_increase = self._analyze_risk_increase(file_path, risk_findings)

            # Analyze maintainability impact
            if quality_findings:
                impact.maintainability_impact = self._analyze_maintainability_impact(file_path, quality_findings)

            impacts.append(impact)

        return impacts

    def _analyze_architecture_impact(self, file_path: str, architecture_result: dict) -> int:
        """Analyze architecture impact of a changed file."""
        layers = architecture_result.get("layers", [])
        modules = architecture_result.get("modules", [])

        # Check if file is in a critical layer
        for layer in layers:
            if isinstance(layer, str) and layer.lower() in file_path.lower():
                return 70

        # Check if file is in a critical module
        for module in modules:
            if isinstance(module, str) and module.lower() in file_path.lower():
                return 60

        return 30

    def _analyze_dependency_impact(self, file_path: str, dependency_result: dict) -> int:
        """Analyze dependency impact of a changed file."""
        nodes = dependency_result.get("nodes", [])
        edges = dependency_result.get("edges", [])

        # Check if file is a high-degree node
        node_degree: dict[str, int] = {}
        for edge in edges:
            source = edge[0] if isinstance(edge, (list, tuple)) else edge.get("source", "")
            target = edge[1] if isinstance(edge, (list, tuple)) else edge.get("target", "")
            node_degree[source] = node_degree.get(source, 0) + 1
            node_degree[target] = node_degree.get(target, 0) + 1

        if file_path in node_degree and node_degree[file_path] > 3:
            return 80

        return 40

    def _analyze_security_impact(self, file_path: str, security_findings: list[dict]) -> int:
        """Analyze security impact of a changed file."""
        for finding in security_findings:
            affected_files = finding.get("affected_files", [])
            if file_path in affected_files:
                severity = finding.get("severity", "Medium")
                if severity.lower() == "critical":
                    return 95
                elif severity.lower() == "high":
                    return 80
                elif severity.lower() == "medium":
                    return 60
                else:
                    return 40

        return 20

    def _analyze_quality_impact(self, file_path: str, smell_findings: list[dict]) -> int:
        """Analyze quality impact of a changed file."""
        impact = 0
        for finding in smell_findings:
            if finding.get("file") == file_path:
                severity = finding.get("severity", "Medium")
                if severity.lower() == "critical":
                    impact += 30
                elif severity.lower() == "high":
                    impact += 20
                elif severity.lower() == "medium":
                    impact += 10
                else:
                    impact += 5

        return min(100, impact)

    def _analyze_risk_increase(self, file_path: str, risk_findings: list[dict]) -> int:
        """Analyze risk increase from a changed file."""
        for finding in risk_findings:
            affected_files = finding.get("affected_files", [])
            if file_path in affected_files:
                level = finding.get("level", finding.get("severity", "Medium"))
                if level.lower() == "critical":
                    return 90
                elif level.lower() == "high":
                    return 70
                elif level.lower() == "medium":
                    return 50
                else:
                    return 30

        return 20

    def _analyze_maintainability_impact(self, file_path: str, quality_findings: list[dict]) -> int:
        """Analyze maintainability impact of a changed file."""
        for finding in quality_findings:
            if finding.get("file") == file_path:
                score = finding.get("score", 50)
                # Lower score = higher impact
                return 100 - score

        return 30


change_analyzer = ChangeAnalyzer()
