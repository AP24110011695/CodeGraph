"""Statistics builder for repository metrics.

Builds comprehensive statistics from existing analysis results.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.analyzers.architecture_models import ArchitectureResult
from app.parsers.ast_models import ProjectParsingResult
from app.quality.scoring_engine import QualityScores
from app.security.security_analyzer import SecurityAnalysisResult
from app.services.dependency_graph import GraphResult
from app.services.framework_detector import DetectionResult
from app.services.scanner_service import ScanResult
from app.smells.smell_detector import SmellDetectionResult

logger = logging.getLogger(__name__)


@dataclass
class RepositoryStatistics:
    """Comprehensive repository statistics."""

    # Basic counts
    total_files: int = 0
    total_directories: int = 0
    total_lines: int | None = None
    code_lines: int | None = None
    comment_lines: int | None = None
    blank_lines: int | None = None

    # Size metrics
    average_file_size: float | None = None
    total_size: int = 0

    # Language breakdown
    supported_languages: dict[str, int] = field(default_factory=dict)
    language_breakdown: dict[str, Any] = field(default_factory=dict)

    # Framework breakdown
    detected_frameworks: list[str] = field(default_factory=list)
    framework_breakdown: dict[str, Any] = field(default_factory=dict)

    # File distribution
    file_distribution: dict[str, int] = field(default_factory=dict)

    # Dependency statistics
    dependency_count: int = 0
    isolated_modules: int = 0
    dependency_density: float | None = None

    # Architecture statistics
    architecture_layers: list[str] = field(default_factory=list)
    architecture_modules: int = 0
    architecture_components: int = 0

    # Complexity metrics
    average_function_size: int | None = None
    average_class_size: int | None = None
    total_functions: int = 0
    total_classes: int = 0
    total_interfaces: int = 0

    # Quality summary
    quality_score: int | None = None
    quality_breakdown: dict[str, int] = field(default_factory=dict)

    # Security summary
    security_score: int | None = None
    security_summary: dict[str, int] = field(default_factory=dict)

    # Code smell summary
    smell_count: int = 0
    smell_summary: dict[str, int] = field(default_factory=dict)

    # Refactoring summary
    refactoring_count: int = 0
    refactoring_summary: dict[str, int] = field(default_factory=dict)


class StatisticsBuilder:
    """Builds comprehensive statistics from analysis results."""

    def __init__(self):
        """Initialize the statistics builder."""
        pass

    def build(
        self,
        scan_result: ScanResult,
        detection_result: DetectionResult | None = None,
        graph_result: GraphResult | None = None,
        architecture_result: ArchitectureResult | None = None,
        parsing_result: ProjectParsingResult | None = None,
        quality_scores: QualityScores | None = None,
        security_result: SecurityAnalysisResult | None = None,
        smell_result: SmellDetectionResult | None = None,
        refactoring_count: int = 0,
    ) -> RepositoryStatistics:
        """Build comprehensive statistics from all analysis results.

        Args:
            scan_result: Output from RepositoryScanner.
            detection_result: Output from FrameworkDetector.
            graph_result: Output from DependencyGraphBuilder.
            architecture_result: Output from ArchitectureBuilder.
            parsing_result: Output from ParserEngine.
            quality_scores: Output from ScoringEngine.
            security_result: Output from SecurityAnalyzer.
            smell_result: Output from SmellDetector.
            refactoring_count: Count of refactoring suggestions.

        Returns:
            RepositoryStatistics with all computed metrics.
        """
        stats = RepositoryStatistics()

        # Basic counts
        stats.total_files = scan_result.total_files
        stats.total_directories = scan_result.total_folders

        # Size metrics
        if scan_result.files:
            stats.total_size = sum(f.size for f in scan_result.files)
            stats.average_file_size = stats.total_size / len(scan_result.files)

        # Language breakdown
        stats.supported_languages = dict(scan_result.languages)
        stats.language_breakdown = self._build_language_breakdown(scan_result)

        # Framework breakdown
        if detection_result:
            stats.detected_frameworks = [f.name for f in detection_result.frameworks]
            stats.framework_breakdown = self._build_framework_breakdown(detection_result)

        # File distribution
        stats.file_distribution = self._build_file_distribution(scan_result)

        # Dependency statistics
        if graph_result:
            stats.dependency_count = len(graph_result.edges)
            stats.isolated_modules = graph_result.isolated_files
            if scan_result.total_files > 0:
                stats.dependency_density = stats.dependency_count / scan_result.total_files

        # Architecture statistics
        if architecture_result:
            stats.architecture_layers = architecture_result.layers
            stats.architecture_modules = architecture_result.statistics.get("modules", 0)
            stats.architecture_components = architecture_result.statistics.get("components", 0)

        # Complexity metrics
        if parsing_result:
            stats.total_functions = sum(len(f.functions) for f in parsing_result.files)
            stats.total_classes = sum(len(f.classes) for f in parsing_result.files)
            stats.total_interfaces = sum(len(f.interfaces) for f in parsing_result.files)

            if stats.total_functions > 0 and scan_result.total_files > 0:
                stats.average_function_size = stats.total_functions // scan_result.total_files
            if stats.total_classes > 0 and scan_result.total_files > 0:
                stats.average_class_size = stats.total_classes // scan_result.total_files

        # Quality summary
        if quality_scores:
            stats.quality_score = self._calculate_overall_quality(quality_scores)
            stats.quality_breakdown = {
                "architecture": quality_scores.architecture,
                "security": quality_scores.security,
                "documentation": quality_scores.documentation,
                "maintainability": quality_scores.maintainability,
                "testing": quality_scores.testing,
                "complexity": quality_scores.complexity,
                "readability": quality_scores.readability,
                "scalability": quality_scores.scalability,
            }

        # Security summary
        if security_result:
            stats.security_score = self._calculate_security_score(security_result)
            stats.security_summary = security_result.summary

        # Code smell summary
        if smell_result:
            stats.smell_count = smell_result.summary.get("total_smells", 0)
            stats.smell_summary = smell_result.summary

        # Refactoring summary
        stats.refactoring_count = refactoring_count
        stats.refactoring_summary = {"total_suggestions": refactoring_count}

        return stats

    def _build_language_breakdown(self, scan_result: ScanResult) -> dict[str, Any]:
        """Build detailed language breakdown."""
        total = sum(scan_result.languages.values())
        if total == 0:
            return {}

        breakdown = {}
        for language, count in scan_result.languages.items():
            breakdown[language] = {
                "count": count,
                "percentage": round((count / total) * 100, 2),
            }

        return breakdown

    def _build_framework_breakdown(self, detection_result: DetectionResult) -> dict[str, Any]:
        """Build detailed framework breakdown."""
        breakdown = {
            "frontend": [f.name for f in detection_result.frameworks],
            "backend": [f.name for f in detection_result.backend],
            "package_managers": detection_result.package_managers,
            "containerized": detection_result.containerized,
        }
        return breakdown

    def _build_file_distribution(self, scan_result: ScanResult) -> dict[str, int]:
        """Build file distribution by extension."""
        distribution: dict[str, int] = {}
        for file_info in scan_result.files:
            ext = file_info.extension or "no_extension"
            distribution[ext] = distribution.get(ext, 0) + 1
        return distribution

    def _calculate_overall_quality(self, quality_scores: QualityScores) -> int:
        """Calculate overall quality score from individual scores."""
        scores = [
            quality_scores.architecture,
            quality_scores.security,
            quality_scores.documentation,
            quality_scores.maintainability,
            quality_scores.testing,
            quality_scores.complexity,
            quality_scores.readability,
            quality_scores.scalability,
        ]
        return round(sum(scores) / len(scores)) if scores else 0

    def _calculate_security_score(self, security_result: SecurityAnalysisResult) -> int:
        """Calculate security score from security analysis result."""
        # Base score of 100, deduct for issues
        score = 100
        score -= security_result.summary.get("critical", 0) * 25
        score -= security_result.summary.get("high", 0) * 15
        score -= security_result.summary.get("medium", 0) * 5
        score -= security_result.summary.get("low", 0) * 2
        return max(0, min(100, score))


statistics_builder = StatisticsBuilder()
