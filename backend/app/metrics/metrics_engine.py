"""Metrics engine for repository analytics.

Orchestrates the generation of comprehensive repository metrics
by reusing existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.analyzers.architecture_builder import architecture_builder
from app.indexing.index_manager import IndexManager, IndexNotFoundError
from app.metrics.statistics_builder import RepositoryStatistics, statistics_builder
from app.metrics.trend_analyzer import TrendAnalysis, trend_analyzer
from app.parsers.parser_engine import ParserEngine
from app.quality.quality_analyzer import QualityAnalysisResult, quality_analyzer
from app.refactoring.refactoring_engine import refactoring_engine
from app.security.security_analyzer import security_analyzer
from app.services.dependency_graph import graph_builder
from app.services.framework_detector import detector_service
from app.services.scanner_service import ScanResult, scanner_service
from app.smells.smell_detector import SmellDetectionResult, smell_detector

logger = logging.getLogger(__name__)


@dataclass
class MetricsResult:
    """Complete result from metrics generation."""

    project_name: str
    summary: dict[str, Any] = field(default_factory=dict)
    statistics: RepositoryStatistics = field(default_factory=RepositoryStatistics)
    quality: dict[str, Any] = field(default_factory=dict)
    security: dict[str, Any] = field(default_factory=dict)
    architecture: dict[str, Any] = field(default_factory=dict)
    smells: dict[str, Any] = field(default_factory=dict)
    refactoring: dict[str, Any] = field(default_factory=dict)
    trends: TrendAnalysis | None = None


class MetricsEngine:
    """Generates comprehensive repository metrics using existing analysis modules.

    Reuses:
    - Repository Scanner
    - Framework Detection
    - Parser Engine
    - Architecture Builder
    - Dependency Graph
    - Quality Analyzer
    - Security Analyzer
    - Code Smell Detector
    - Refactoring Engine
    """

    def __init__(self, index_manager: IndexManager | None = None):
        """Initialize the metrics engine.

        Args:
            index_manager: Optional IndexManager for accessing indexed repositories.
        """
        self.index_manager = index_manager
        self.scanner = scanner_service
        self.detector = detector_service
        self.graph_builder = graph_builder
        self.architecture_builder = architecture_builder
        self.quality_analyzer = quality_analyzer
        self.security_analyzer = security_analyzer
        self.smell_detector = smell_detector
        self.refactoring_engine = refactoring_engine
        self.statistics_builder = statistics_builder
        self.trend_analyzer = trend_analyzer

    def generate(
        self,
        project_path: Path,
        upload_id: str | None = None,
    ) -> MetricsResult:
        """Generate comprehensive metrics for a repository.

        Args:
            project_path: Absolute path to the project directory.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            MetricsResult with all generated metrics.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Generating metrics for project: {project_path}")

        # Step 1: Scan the repository
        logger.info("Scanning repository")
        scan_result = self.scanner.scan(project_path)

        # Check if repository is empty
        if scan_result.total_files == 0:
            logger.warning("Repository is empty, returning minimal metrics")
            return self._build_empty_result(scan_result.project_name)

        # Step 2: Detect frameworks
        logger.info("Detecting frameworks")
        detection_result = self.detector.detect(project_path, scan_result)

        # Step 3: Build dependency graph
        logger.info("Building dependency graph")
        graph_result = self.graph_builder.build(project_path, scan_result)

        # Step 4: Parse the project
        logger.info("Parsing project")
        try:
            parsing_result = ParserEngine.parse_project(project_path, scan_result)
        except Exception as e:
            logger.warning(f"Failed to parse project: {e}")
            parsing_result = None

        # Step 5: Build architecture
        logger.info("Building architecture")
        architecture_result = self.architecture_builder.build(
            scan_result, detection_result, graph_result, parsing_result
        )

        # Step 6: Analyze quality
        logger.info("Analyzing quality")
        try:
            quality_result = self.quality_analyzer.analyze(project_path, scan_result)
        except Exception as e:
            logger.warning(f"Failed to analyze quality: {e}")
            quality_result = None

        # Step 7: Analyze security
        logger.info("Analyzing security")
        try:
            security_result = self.security_analyzer.analyze(project_path, scan_result)
        except Exception as e:
            logger.warning(f"Failed to analyze security: {e}")
            security_result = None

        # Step 8: Detect code smells
        logger.info("Detecting code smells")
        try:
            smell_result = self.smell_detector.detect(
                project_path,
                scan_result,
                parsing_result,
                graph_result,
                architecture_result,
            )
        except Exception as e:
            logger.warning(f"Failed to detect code smells: {e}")
            smell_result = None

        # Step 9: Generate refactoring suggestions
        logger.info("Generating refactoring suggestions")
        try:
            refactoring_result = self.refactoring_engine.analyze(project_path)
            refactoring_count = refactoring_result.summary.total_suggestions
        except Exception as e:
            logger.warning(f"Failed to generate refactoring suggestions: {e}")
            refactoring_count = 0

        # Step 10: Build comprehensive statistics
        logger.info("Building statistics")
        quality_scores = quality_result.scores if quality_result else None
        statistics = self.statistics_builder.build(
            scan_result=scan_result,
            detection_result=detection_result,
            graph_result=graph_result,
            architecture_result=architecture_result,
            parsing_result=parsing_result,
            quality_scores=quality_scores,
            security_result=security_result,
            smell_result=smell_result,
            refactoring_count=refactoring_count,
        )

        # Step 11: Build summary
        summary = self._build_summary(
            scan_result, detection_result, statistics
        )

        # Step 12: Build quality section
        quality_section = self._build_quality_section(quality_result, statistics)

        # Step 13: Build security section
        security_section = self._build_security_section(security_result, statistics)

        # Step 14: Build architecture section
        architecture_section = self._build_architecture_section(architecture_result, statistics)

        # Step 15: Build smells section
        smells_section = self._build_smells_section(smell_result, statistics)

        # Step 16: Build refactoring section
        refactoring_section = self._build_refactoring_section(refactoring_count, statistics)

        # Step 17: Analyze trends (if historical data available)
        trends = None
        if upload_id and self.index_manager:
            try:
                index = self.index_manager.get_index(upload_id)
                if index:
                    # For now, we don't store historical metrics
                    # This can be extended in the future
                    trends = self.trend_analyzer.analyze({})
            except Exception as e:
                logger.warning(f"Failed to analyze trends: {e}")

        return MetricsResult(
            project_name=scan_result.project_name,
            summary=summary,
            statistics=statistics,
            quality=quality_section,
            security=security_section,
            architecture=architecture_section,
            smells=smells_section,
            refactoring=refactoring_section,
            trends=trends,
        )

    def _build_empty_result(self, project_name: str) -> MetricsResult:
        """Build a minimal result for empty repositories."""
        return MetricsResult(
            project_name=project_name,
            summary={
                "total_files": 0,
                "total_directories": 0,
                "status": "empty",
            },
            statistics=RepositoryStatistics(),
            quality={"status": "not_available"},
            security={"status": "not_available"},
            architecture={"status": "not_available"},
            smells={"status": "not_available"},
            refactoring={"status": "not_available"},
        )

    def _build_summary(
        self,
        scan_result: ScanResult,
        detection_result,
        statistics: RepositoryStatistics,
    ) -> dict[str, Any]:
        """Build the summary section."""
        return {
            "total_files": statistics.total_files,
            "total_directories": statistics.total_directories,
            "total_size": statistics.total_size,
            "average_file_size": statistics.average_file_size,
            "supported_languages": list(statistics.supported_languages.keys()),
            "detected_frameworks": statistics.detected_frameworks,
            "containerized": detection_result.containerized if detection_result else False,
            "package_managers": detection_result.package_managers if detection_result else [],
        }

    def _build_quality_section(
        self,
        quality_result: QualityAnalysisResult | None,
        statistics: RepositoryStatistics,
    ) -> dict[str, Any]:
        """Build the quality section."""
        if not quality_result:
            return {
                "status": "not_available",
                "quality_score": statistics.quality_score,
            }

        return {
            "quality_score": statistics.quality_score,
            "breakdown": statistics.quality_breakdown,
            "recommendations_count": len(quality_result.recommendations.recommendations) if quality_result.recommendations else 0,
        }

    def _build_security_section(
        self,
        security_result,
        statistics: RepositoryStatistics,
    ) -> dict[str, Any]:
        """Build the security section."""
        return {
            "security_score": statistics.security_score,
            "summary": statistics.security_summary,
            "total_issues": security_result.total_issues if security_result else 0,
        }

    def _build_architecture_section(
        self,
        architecture_result,
        statistics: RepositoryStatistics,
    ) -> dict[str, Any]:
        """Build the architecture section."""
        return {
            "layers": statistics.architecture_layers,
            "modules": statistics.architecture_modules,
            "components": statistics.architecture_components,
            "relationships": architecture_result.statistics.get("relationships", 0) if architecture_result else 0,
        }

    def _build_smells_section(
        self,
        smell_result: SmellDetectionResult | None,
        statistics: RepositoryStatistics,
    ) -> dict[str, Any]:
        """Build the code smells section."""
        if smell_result:
            return {
                "smell_count": statistics.smell_count,
                "summary": statistics.smell_summary,
                "debt_estimate": {
                    "level": smell_result.debt_estimate.level,
                    "estimated_effort": smell_result.debt_estimate.estimated_effort,
                    "affected_files": smell_result.debt_estimate.affected_files,
                    "refactoring_priority": smell_result.debt_estimate.refactoring_priority,
                },
            }
        return {
            "smell_count": statistics.smell_count,
            "summary": statistics.smell_summary,
            "debt_estimate": None,
        }

    def _build_refactoring_section(
        self,
        refactoring_count: int,
        statistics: RepositoryStatistics,
    ) -> dict[str, Any]:
        """Build the refactoring section."""
        return {
            "refactoring_count": refactoring_count,
            "summary": statistics.refactoring_summary,
        }


metrics_engine = MetricsEngine()
