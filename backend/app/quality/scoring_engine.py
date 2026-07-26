"""Scoring engine for project quality analysis.

Calculates deterministic scores for various quality metrics
based on detected project characteristics.
"""

import logging
from dataclasses import dataclass
from typing import Any

from app.analyzers.architecture_models import ArchitectureResult
from app.parsers.ast_models import ProjectParsingResult
from app.services.dependency_graph import GraphResult
from app.services.framework_detector import DetectionResult
from app.services.scanner_service import ScanResult
from app.security.security_analyzer import SecurityAnalysisResult

logger = logging.getLogger(__name__)


@dataclass
class QualityScores:
    """Individual quality scores."""

    architecture: int = 0
    security: int = 0
    documentation: int = 0
    maintainability: int = 0
    testing: int = 0
    complexity: int = 0
    readability: int = 0
    scalability: int = 0


class ScoringEngine:
    """Calculates deterministic quality scores based on project analysis."""

    def calculate_scores(
        self,
        scan_result: ScanResult,
        detection_result: DetectionResult,
        architecture_result: ArchitectureResult,
        graph_result: GraphResult,
        parsing_result: ProjectParsingResult | None,
        security_result: SecurityAnalysisResult | None,
    ) -> QualityScores:
        """Calculate all quality scores.

        Args:
            scan_result: Output from RepositoryScanner.
            detection_result: Output from FrameworkDetector.
            architecture_result: Output from ArchitectureBuilder.
            graph_result: Output from DependencyGraphBuilder.
            parsing_result: Output from ParserEngine (optional).
            security_result: Output from SecurityAnalyzer (optional).

        Returns:
            QualityScores with individual metric scores (0-100).
        """
        scores = QualityScores()

        # Calculate individual scores
        scores.architecture = self._score_architecture(
            architecture_result, detection_result
        )
        scores.security = self._score_security(security_result)
        scores.documentation = self._score_documentation(scan_result)
        scores.maintainability = self._score_maintainability(
            scan_result, architecture_result, graph_result
        )
        scores.testing = self._score_testing(scan_result)
        scores.complexity = self._score_complexity(
            scan_result, graph_result, parsing_result
        )
        scores.readability = self._score_readability(scan_result, parsing_result)
        scores.scalability = self._score_scalability(
            detection_result, architecture_result, graph_result
        )

        return scores

    def _score_architecture(
        self, architecture_result: ArchitectureResult, detection_result: DetectionResult
    ) -> int:
        """Score architecture quality (0-100)."""
        score = 50  # Base score

        # Check for layered architecture
        if len(architecture_result.layers) >= 3:
            score += 20
        elif len(architecture_result.layers) >= 2:
            score += 10

        # Check for modular structure
        if architecture_result.statistics.get("modules", 0) >= 5:
            score += 15
        elif architecture_result.statistics.get("modules", 0) >= 3:
            score += 8

        # Check for framework usage
        if detection_result.backend:
            score += 10

        # Check for relationships (coupling)
        relationships = architecture_result.statistics.get("relationships", 0)
        if relationships > 0:
            # Penalize excessive coupling
            if relationships > 50:
                score -= 10
            elif relationships > 30:
                score -= 5

        return min(max(score, 0), 100)

    def _score_security(self, security_result: SecurityAnalysisResult | None) -> int:
        """Score security quality (0-100)."""
        if security_result is None:
            return 50  # Neutral score if security analysis not available

        score = 100

        # Deduct points for critical issues
        critical_count = security_result.summary.get("critical", 0)
        score -= critical_count * 25

        # Deduct points for high issues
        high_count = security_result.summary.get("high", 0)
        score -= high_count * 15

        # Deduct points for medium issues
        medium_count = security_result.summary.get("medium", 0)
        score -= medium_count * 5

        # Deduct points for low issues
        low_count = security_result.summary.get("low", 0)
        score -= low_count * 2

        return min(max(score, 0), 100)

    def _score_documentation(self, scan_result: ScanResult) -> int:
        """Score documentation quality (0-100)."""
        score = 0

        # Check for README
        has_readme = any(
            f.name.lower().startswith("readme") for f in scan_result.files
        )
        if has_readme:
            score += 30

        # Check for documentation files
        doc_files = [
            f for f in scan_result.files
            if f.extension in [".md", ".rst", ".txt"]
            and "doc" in f.path.lower()
        ]
        if len(doc_files) >= 3:
            score += 30
        elif len(doc_files) >= 1:
            score += 15

        # Check for inline comments (estimate from file count)
        if scan_result.total_files > 0:
            # Assume some level of documentation exists
            score += 20

        # Check for LICENSE
        has_license = any(
            f.name.lower().startswith("license") for f in scan_result.files
        )
        if has_license:
            score += 20

        return min(score, 100)

    def _score_maintainability(
        self,
        scan_result: ScanResult,
        architecture_result: ArchitectureResult,
        graph_result: GraphResult,
    ) -> int:
        """Score maintainability quality (0-100)."""
        score = 50  # Base score

        # Check for code organization (modules)
        modules = architecture_result.statistics.get("modules", 0)
        if modules >= 5:
            score += 20
        elif modules >= 3:
            score += 10

        # Check for dependency complexity
        total_files = scan_result.total_files
        edges = len(graph_result.edges)
        isolated = graph_result.isolated_files

        # Good: moderate dependencies, few isolated files
        if total_files > 0:
            dependency_ratio = edges / total_files if total_files > 0 else 0
            if 0.5 <= dependency_ratio <= 2.0:
                score += 15
            elif dependency_ratio > 4.0:
                score -= 10  # Too many dependencies

        # Penalize isolated files
        if total_files > 0:
            isolated_ratio = isolated / total_files
            if isolated_ratio > 0.3:
                score -= 15
            elif isolated_ratio > 0.1:
                score -= 5

        # Check for language consistency
        languages = len(scan_result.languages)
        if languages <= 2:
            score += 10
        elif languages > 5:
            score -= 10

        return min(max(score, 0), 100)

    def _score_testing(self, scan_result: ScanResult) -> int:
        """Score testing quality (0-100)."""
        score = 0

        # Check for test directories
        test_dirs = [
            f.folder for f in scan_result.files if "test" in f.folder.lower()
        ]
        if len(test_dirs) >= 2:
            score += 40
        elif len(test_dirs) >= 1:
            score += 20

        # Check for test files
        test_files = [
            f for f in scan_result.files
            if "test" in f.name.lower() or "spec" in f.name.lower()
        ]
        if len(test_files) >= 5:
            score += 30
        elif len(test_files) >= 2:
            score += 15

        # Check for test frameworks in dependencies
        # This is a heuristic based on file names
        test_framework_files = [
            f for f in scan_result.files
            if any(
                fw in f.name.lower()
                for fw in ["pytest", "jest", "mocha", "junit", "rspec"]
            )
        ]
        if test_framework_files:
            score += 30

        return min(score, 100)

    def _score_complexity(
        self,
        scan_result: ScanResult,
        graph_result: GraphResult,
        parsing_result: ProjectParsingResult | None,
    ) -> int:
        """Score complexity quality (0-100)."""
        score = 50  # Base score

        total_files = scan_result.total_files

        # Score based on file count (smaller is simpler)
        if total_files <= 10:
            score += 30
        elif total_files <= 50:
            score += 20
        elif total_files <= 100:
            score += 10
        elif total_files > 500:
            score -= 20

        # Score based on dependency graph complexity
        edges = len(graph_result.edges)
        if total_files > 0:
            edge_ratio = edges / total_files
            if edge_ratio <= 1.0:
                score += 20
            elif edge_ratio <= 2.0:
                score += 10
            elif edge_ratio > 4.0:
                score -= 15

        # Score based on average file size
        if scan_result.files:
            avg_size = sum(f.size for f in scan_result.files) / len(scan_result.files)
            if avg_size <= 5000:  # 5KB
                score += 10
            elif avg_size > 20000:  # 20KB
                score -= 10

        return min(max(score, 0), 100)

    def _score_readability(
        self, scan_result: ScanResult, parsing_result: ProjectParsingResult | None
    ) -> int:
        """Score readability quality (0-100)."""
        score = 50  # Base score

        # Check for consistent naming (heuristic)
        # Files with consistent extensions and naming patterns
        extensions = set(f.extension for f in scan_result.files if f.extension)
        if len(extensions) <= 3:
            score += 15

        # Check for code organization
        folders = set(f.folder for f in scan_result.files)
        if len(folders) >= 3:
            score += 15

        # Check for function/class counts (if parsing available)
        if parsing_result:
            total_functions = sum(len(f.functions) for f in parsing_result.files)
            total_classes = sum(len(f.classes) for f in parsing_result.files)

            # Moderate function count is good
            if 10 <= total_functions <= 100:
                score += 10

            # Some classes indicate OOP structure
            if total_classes >= 3:
                score += 10

        return min(max(score, 0), 100)

    def _score_scalability(
        self,
        detection_result: DetectionResult,
        architecture_result: ArchitectureResult,
        graph_result: GraphResult,
    ) -> int:
        """Score scalability quality (0-100)."""
        score = 50  # Base score

        # Check for containerization
        if detection_result.containerized:
            score += 20

        # Check for layered architecture
        if len(architecture_result.layers) >= 3:
            score += 15

        # Check for modular structure
        modules = architecture_result.statistics.get("modules", 0)
        if modules >= 5:
            score += 15

        # Check for dependency graph health
        edges = len(graph_result.edges)
        nodes = len(graph_result.nodes)
        if nodes > 0:
            avg_degree = (2 * edges) / nodes  # Average degree in undirected graph
            if avg_degree <= 3:
                score += 10
            elif avg_degree > 6:
                score -= 10

        # Check for package managers (indicates dependency management)
        if detection_result.package_managers:
            score += 10

        return min(max(score, 0), 100)


scoring_engine = ScoringEngine()
