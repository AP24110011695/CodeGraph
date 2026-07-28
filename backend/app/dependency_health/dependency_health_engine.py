"""Dependency health engine for dependency health dashboard.

Orchestrates dependency health analysis using all existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.dependency_health.dependency_health_analyzer import DependencyFinding, DependencyHealthAnalyzer, DependencyStatistics, dependency_health_analyzer
from app.dependency_health.dependency_health_scorer import DependencyHealthScorer, dependency_health_scorer
from app.indexing.index_manager import IndexManager
from app.metrics.metrics_engine import MetricsEngine, MetricsResult
from app.security.security_analyzer import SecurityAnalysisResult, security_analyzer
from app.services.dependency_graph import GraphResult, graph_builder
from app.services.scanner_service import ScanResult, scanner_service

logger = logging.getLogger(__name__)


@dataclass
class DependencyHealthResult:
    """Complete result from dependency health analysis."""

    project_name: str
    overall_health_score: int
    health_grade: str
    summary: dict[str, int | float] = field(default_factory=dict)
    findings: list[dict] = field(default_factory=list)
    critical_modules: list[str] = field(default_factory=list)
    high_risk_modules: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class DependencyHealthEngine:
    """Performs comprehensive dependency health analysis.

    Reuses all existing CodeGraph analysis modules:
    - Repository Scanner
    - Dependency Graph Builder
    - Security Analyzer
    - Metrics Engine
    """

    def __init__(
        self,
        index_manager: IndexManager | None = None,
        metrics_engine: MetricsEngine | None = None,
        dependency_health_analyzer: DependencyHealthAnalyzer | None = None,
        dependency_health_scorer: DependencyHealthScorer | None = None,
    ):
        """Initialize the dependency health engine.

        Args:
            index_manager: Optional IndexManager for accessing indexed repositories.
            metrics_engine: Optional MetricsEngine instance.
            dependency_health_analyzer: Optional DependencyHealthAnalyzer instance.
            dependency_health_scorer: Optional DependencyHealthScorer instance.
        """
        self.index_manager = index_manager
        self.metrics_engine = metrics_engine or MetricsEngine(index_manager=index_manager)
        self.dependency_health_analyzer = dependency_health_analyzer or DependencyHealthAnalyzer()
        self.dependency_health_scorer = dependency_health_scorer or DependencyHealthScorer()

        # Individual analyzers
        self.scanner = scanner_service
        self.graph_builder = graph_builder
        self.security_analyzer = security_analyzer

    def analyze(
        self,
        project_path: Path,
        upload_id: str | None = None,
    ) -> DependencyHealthResult:
        """Perform comprehensive dependency health analysis for a repository.

        Args:
            project_path: Absolute path to the project directory.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            DependencyHealthResult with comprehensive dependency health findings.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Starting dependency health analysis for project: {project_path}")

        # Step 1: Scan the repository
        logger.info("Scanning repository")
        scan_result = self.scanner.scan(project_path)

        if scan_result.total_files == 0:
            logger.warning("Repository is empty, returning minimal result")
            return self._build_empty_result(scan_result)

        # Step 2: Build dependency graph
        logger.info("Building dependency graph")
        graph_result = self.graph_builder.build(project_path, scan_result)

        # Step 3: Extract security issues
        logger.info("Extracting security issues")
        security_issues = self._extract_security_issues(project_path, scan_result)

        # Step 4: Generate metrics
        logger.info("Generating metrics")
        metrics_result = self.metrics_engine.generate(project_path, upload_id)

        # Step 5: Convert results to dict format for analyzer
        dependency_dict = self._graph_to_dict(graph_result)
        metrics_dict = self._metrics_to_dict(metrics_result)

        # Step 6: Analyze dependency health
        logger.info("Analyzing dependency health")
        findings, stats = self.dependency_health_analyzer.analyze(
            dependency_result=dependency_dict,
            security_issues=security_issues,
            metrics_result=metrics_dict,
        )

        # Step 7: Calculate overall health score
        logger.info("Calculating overall health score")
        overall_score = self.dependency_health_scorer.calculate_overall_score(
            cycle_count=stats.cycles,
            coupling_density=stats.coupling_density,
            isolated_count=stats.isolated_modules,
            fan_out_max=stats.fan_out_max,
            fan_in_max=stats.fan_in_max,
            external_count=stats.external_dependencies,
        )

        # Step 8: Determine health grade
        health_grade = self.dependency_health_scorer.calculate_grade(overall_score)

        # Step 9: Build response
        summary = {
            "internal_dependencies": stats.internal_dependencies,
            "external_dependencies": stats.external_dependencies,
            "cycles": stats.cycles,
            "critical_modules": stats.critical_modules,
            "high_risk_modules": stats.high_risk_modules,
            "coupling_density": stats.coupling_density,
            "fan_out_max": stats.fan_out_max,
            "fan_in_max": stats.fan_in_max,
            "isolated_modules": stats.isolated_modules,
        }

        serialized_findings = self._serialize_findings(findings)
        critical_modules = self._extract_critical_modules(findings)
        high_risk_modules = self._extract_high_risk_modules(findings)
        recommendations = self._generate_recommendations(findings, stats)

        return DependencyHealthResult(
            project_name=metrics_result.project_name,
            overall_health_score=overall_score,
            health_grade=health_grade,
            summary=summary,
            findings=serialized_findings,
            critical_modules=critical_modules,
            high_risk_modules=high_risk_modules,
            recommendations=recommendations,
        )

    def _build_empty_result(self, scan_result: ScanResult) -> DependencyHealthResult:
        """Build a minimal result for empty repositories."""
        return DependencyHealthResult(
            project_name=scan_result.project_name,
            overall_health_score=100,
            health_grade="A",
            summary={
                "internal_dependencies": 0,
                "external_dependencies": 0,
                "cycles": 0,
                "critical_modules": 0,
                "high_risk_modules": 0,
                "coupling_density": 0.0,
                "fan_out_max": 0,
                "fan_in_max": 0,
                "isolated_modules": 0,
            },
            findings=[],
            critical_modules=[],
            high_risk_modules=[],
            recommendations=[],
        )

    def _extract_security_issues(self, project_path: Path, scan_result: ScanResult) -> list[dict]:
        """Extract security issues from SecurityAnalyzer."""
        try:
            security_result = self.security_analyzer.analyze(project_path, scan_result)
            return [self._issue_to_dict(issue) for issue in security_result.issues]
        except Exception as e:
            logger.warning(f"Failed to extract security issues: {e}")
            return []

    def _graph_to_dict(self, graph_result: GraphResult) -> dict:
        """Convert GraphResult to dictionary."""
        return {
            "nodes": graph_result.nodes,
            "edges": [(edge.from_node, edge.to_node) for edge in graph_result.edges],
            "isolated_files": graph_result.isolated_files,
        }

    def _metrics_to_dict(self, metrics_result: MetricsResult) -> dict:
        """Convert MetricsResult to dictionary."""
        return {
            "statistics": {
                "total_files": metrics_result.statistics.total_files,
                "total_lines": metrics_result.statistics.total_lines,
                "quality_score": metrics_result.statistics.quality_score,
                "security_score": metrics_result.statistics.security_score,
                "smell_count": metrics_result.statistics.smell_count,
            },
        }

    def _issue_to_dict(self, issue: dict) -> dict:
        """Convert security issue to dictionary."""
        return {
            "severity": issue.get("severity", "medium"),
            "rule": issue.get("rule", "Unknown"),
            "description": issue.get("description", ""),
            "file": issue.get("file", ""),
            "line": issue.get("line", ""),
            "language": issue.get("language", ""),
        }

    def _serialize_findings(self, findings: list[DependencyFinding]) -> list[dict]:
        """Serialize findings to dictionary format."""
        return [
            {
                "title": finding.title,
                "category": finding.category,
                "severity": finding.severity,
                "score": finding.score,
                "evidence": finding.evidence,
                "affected_files": finding.affected_files,
                "recommendation": finding.recommendation,
            }
            for finding in findings
        ]

    def _extract_critical_modules(self, findings: list[DependencyFinding]) -> list[str]:
        """Extract critical modules from findings."""
        critical = [f.affected_files[0] for f in findings if f.category == "Security" and f.affected_files]
        return critical[:10]  # Limit to top 10

    def _extract_high_risk_modules(self, findings: list[DependencyFinding]) -> list[str]:
        """Extract high-risk modules from findings."""
        high_risk = [f.affected_files[0] for f in findings if f.severity in ["High", "Critical"] and f.affected_files]
        return high_risk[:10]  # Limit to top 10

    def _generate_recommendations(self, findings: list[DependencyFinding], stats: DependencyStatistics) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if stats.cycles > 0:
            recommendations.append(f"Address {stats.cycles} circular dependency cycle(s) to improve architecture stability")

        if stats.coupling_density > 3:
            recommendations.append("Reduce coupling density to improve maintainability")

        if stats.critical_modules > 0:
            recommendations.append(f"Review and fix security issues in {stats.critical_modules} critical module(s)")

        if stats.isolated_modules > 0:
            recommendations.append(f"Review {stats.isolated_modules} isolated module(s) and integrate or remove them")

        if stats.fan_out_max > 10:
            recommendations.append("Consider reducing fan-out for modules with excessive outgoing dependencies")

        if stats.fan_in_max > 10:
            recommendations.append("Consider applying facade pattern to modules with high fan-in")

        # Add general recommendations
        if stats.external_dependencies > 50:
            recommendations.append("Review external dependencies and consider reducing dependency bloat")

        return recommendations[:10]


dependency_health_engine = DependencyHealthEngine()
