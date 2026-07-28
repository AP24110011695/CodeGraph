"""Architecture drift engine for architecture drift detection.

Orchestrates architecture drift detection using all existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.analyzers.architecture_builder import architecture_builder
from app.architecture_drift.architecture_comparator import ArchitectureComparator, architecture_comparator
from app.architecture_drift.drift_detector import DriftDetector, DriftFinding, DriftStatistics, drift_detector
from app.indexing.index_manager import IndexManager
from app.parsers.ast_models import ProjectParsingResult
from app.parsers.parser_engine import ParserEngine
from app.services.dependency_graph import graph_builder
from app.services.framework_detector import FrameworkDetector
from app.services.scanner_service import ScanResult, scanner_service
from app.smells.smell_detector import smell_detector

logger = logging.getLogger(__name__)


@dataclass
class ArchitectureDriftResult:
    """Complete result from architecture drift detection."""

    project_name: str
    architecture_health_score: int
    architecture_grade: str
    drift_score: int
    stability_score: int
    summary: dict[str, int] = field(default_factory=dict)
    findings: list[dict] = field(default_factory=list)
    top_violations: list[dict] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class ArchitectureDriftEngine:
    """Performs comprehensive architecture drift detection.

    Reuses all existing CodeGraph analysis modules:
    - Repository Scanner
    - Architecture Builder
    - Dependency Graph Builder
    - Code Smell Detector
    """

    def __init__(
        self,
        index_manager: IndexManager | None = None,
        drift_detector: DriftDetector | None = None,
        architecture_comparator: ArchitectureComparator | None = None,
    ):
        """Initialize the architecture drift engine.

        Args:
            index_manager: Optional IndexManager for accessing indexed repositories.
            drift_detector: Optional DriftDetector instance.
            architecture_comparator: Optional ArchitectureComparator instance.
        """
        self.index_manager = index_manager
        self.drift_detector = drift_detector or DriftDetector()
        self.architecture_comparator = architecture_comparator or ArchitectureComparator()

        # Individual analyzers
        self.scanner = scanner_service
        self.graph_builder = graph_builder
        self.architecture_builder = architecture_builder
        self.framework_detector = FrameworkDetector()
        self.parser_engine = ParserEngine
        self.smell_detector = smell_detector

    def analyze(
        self,
        project_path: Path,
        upload_id: str | None = None,
    ) -> ArchitectureDriftResult:
        """Perform comprehensive architecture drift detection for a repository.

        Args:
            project_path: Absolute path to the project directory.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            ArchitectureDriftResult with comprehensive architecture drift findings.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Starting architecture drift detection for project: {project_path}")

        # Step 1: Scan the repository
        logger.info("Scanning repository")
        scan_result = self.scanner.scan(project_path)

        if scan_result.total_files == 0:
            logger.warning("Repository is empty, returning minimal result")
            return self._build_empty_result(scan_result)

        # Step 2: Detect framework
        logger.info("Detecting framework")
        detection_result = self.framework_detector.detect(project_path, scan_result)

        # Step 3: Build dependency graph
        logger.info("Building dependency graph")
        graph_result = self.graph_builder.build(project_path, scan_result)

        # Step 4: Parse project
        logger.info("Parsing project")
        parsing_result = self.parser_engine.parse_project(project_path, scan_result)

        # Step 5: Build architecture
        logger.info("Building architecture")
        architecture_result = self.architecture_builder.build(
            scan_result=scan_result,
            detection_result=detection_result,
            graph_result=graph_result,
            parsing_result=parsing_result,
        )

        # Step 6: Detect code smells
        logger.info("Detecting code smells")
        smell_result = self.smell_detector.detect(project_path, scan_result, parsing_result, graph_result, architecture_result)

        # Step 7: Convert results to dict format for detector
        dependency_dict = self._graph_to_dict(graph_result)
        architecture_dict = self._architecture_to_dict(architecture_result)
        smell_issues = self._smell_to_list(smell_result)

        # Step 8: Detect drift
        logger.info("Detecting architecture drift")
        findings, stats = self.drift_detector.detect_drift(
            architecture_result=architecture_dict,
            dependency_result=dependency_dict,
            smell_issues=smell_issues,
        )

        # Step 9: Calculate scores
        logger.info("Calculating architecture health scores")
        health_score = self.architecture_comparator.calculate_health_score(
            violations=stats.violations,
            layer_violations=stats.layer_violations,
            cross_layer_dependencies=stats.cross_layer_dependencies,
            circular_dependencies=stats.circular_dependencies,
            high_coupling=stats.high_coupling,
            god_modules=stats.god_modules,
        )

        drift_score = self.architecture_comparator.calculate_drift_score(health_score)
        grade = self.architecture_comparator.calculate_grade(health_score)
        stability_score = self.architecture_comparator.get_stability_score(
            violations=stats.violations,
            circular_dependencies=stats.circular_dependencies,
            high_coupling=stats.high_coupling,
        )

        # Step 10: Build summary
        summary = {
            "violations": stats.violations,
            "layer_violations": stats.layer_violations,
            "cross_layer_dependencies": stats.cross_layer_dependencies,
            "circular_dependencies": stats.circular_dependencies,
            "high_coupling": stats.high_coupling,
            "god_modules": stats.god_modules,
        }

        # Step 11: Serialize findings
        serialized_findings = self._serialize_findings(findings)

        # Step 12: Extract top violations
        top_violations = self._extract_top_violations(findings)

        # Step 13: Generate recommendations
        recommendations = self._generate_recommendations(findings, stats)

        return ArchitectureDriftResult(
            project_name=scan_result.project_name,
            architecture_health_score=health_score,
            architecture_grade=grade,
            drift_score=drift_score,
            stability_score=stability_score,
            summary=summary,
            findings=serialized_findings,
            top_violations=top_violations,
            recommendations=recommendations,
        )

    def _build_empty_result(self, scan_result: ScanResult) -> ArchitectureDriftResult:
        """Build a minimal result for empty repositories."""
        return ArchitectureDriftResult(
            project_name=scan_result.project_name,
            architecture_health_score=100,
            architecture_grade="A",
            drift_score=0,
            stability_score=100,
            summary={
                "violations": 0,
                "layer_violations": 0,
                "cross_layer_dependencies": 0,
                "circular_dependencies": 0,
                "high_coupling": 0,
                "god_modules": 0,
            },
            findings=[],
            top_violations=[],
            recommendations=[],
        )

    def _graph_to_dict(self, graph_result) -> dict:
        """Convert GraphResult to dictionary."""
        return {
            "nodes": graph_result.nodes,
            "edges": [(edge.from_node, edge.to_node) for edge in graph_result.edges],
            "isolated_files": graph_result.isolated_files,
        }

    def _architecture_to_dict(self, architecture_result) -> dict:
        """Convert ArchitectureResult to dictionary."""
        return {
            "layers": architecture_result.layers,
            "modules": [module.name for module in architecture_result.modules],
            "components": [component.name for module in architecture_result.modules for component in module.components],
        }

    def _smell_to_list(self, smell_result) -> list[dict]:
        """Convert smell issues to list of dictionaries."""
        return [
            {
                "type": smell.type,
                "severity": smell.severity,
                "description": smell.description,
                "file": smell.file,
                "line": smell.line,
            }
            for smell in smell_result.smells
        ]

    def _serialize_findings(self, findings: list[DriftFinding]) -> list[dict]:
        """Serialize findings to dictionary format."""
        return [
            {
                "title": finding.title,
                "category": finding.category,
                "severity": finding.severity,
                "score": finding.score,
                "reason": finding.reason,
                "evidence": finding.evidence,
                "affected_files": finding.affected_files,
                "recommendation": finding.recommendation,
            }
            for finding in findings
        ]

    def _extract_top_violations(self, findings: list[DriftFinding]) -> list[dict]:
        """Extract top violations by score."""
        sorted_findings = sorted(findings, key=lambda f: f.score, reverse=True)
        top_violations = sorted_findings[:10]
        return self._serialize_findings(top_violations)

    def _generate_recommendations(self, findings: list[DriftFinding], stats: DriftStatistics) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if stats.circular_dependencies > 0:
            recommendations.append(f"Address {stats.circular_dependencies} circular dependency cycle(s) to improve architecture stability")

        if stats.cross_layer_dependencies > 0:
            recommendations.append(f"Refactor {stats.cross_layer_dependencies} cross-layer dependency(ies) to follow layered architecture principles")

        if stats.layer_violations > 0:
            recommendations.append(f"Review and fix {stats.layer_violations} layer violation(s) to improve separation of concerns")

        if stats.high_coupling > 0:
            recommendations.append("Reduce coupling between modules to improve maintainability")

        if stats.god_modules > 0:
            recommendations.append(f"Refactor {stats.god_modules} god module(s) by extracting responsibilities")

        # Add general recommendations
        if stats.violations > 5:
            recommendations.append("Consider a comprehensive architectural refactoring to address multiple violations")

        return recommendations[:10]


architecture_drift_engine = ArchitectureDriftEngine()
