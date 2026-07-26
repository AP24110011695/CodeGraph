"""Recommendation engine for project quality analysis.

Generates deterministic recommendations based on detected
project characteristics and scores.
"""

import logging
from dataclasses import dataclass

from app.analyzers.architecture_models import ArchitectureResult
from app.parsers.ast_models import ProjectParsingResult
from app.quality.scoring_engine import QualityScores
from app.services.dependency_graph import GraphResult
from app.services.framework_detector import DetectionResult
from app.services.scanner_service import ScanResult
from app.security.security_analyzer import SecurityAnalysisResult

logger = logging.getLogger(__name__)


@dataclass
class QualityRecommendations:
    """Complete recommendations output."""

    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]


class RecommendationEngine:
    """Generates recommendations based on project analysis."""

    def generate_recommendations(
        self,
        scan_result: ScanResult,
        detection_result: DetectionResult,
        architecture_result: ArchitectureResult,
        graph_result: GraphResult,
        parsing_result: ProjectParsingResult | None,
        security_result: SecurityAnalysisResult | None,
        scores: QualityScores,
    ) -> QualityRecommendations:
        """Generate strengths, weaknesses, and recommendations.

        Args:
            scan_result: Output from RepositoryScanner.
            detection_result: Output from FrameworkDetector.
            architecture_result: Output from ArchitectureBuilder.
            graph_result: Output from DependencyGraphBuilder.
            parsing_result: Output from ParserEngine (optional).
            security_result: Output from SecurityAnalyzer (optional).
            scores: Calculated quality scores.

        Returns:
            QualityRecommendations with lists of strengths, weaknesses, and recommendations.
        """
        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []

        # Architecture recommendations
        self._analyze_architecture(
            architecture_result, detection_result, scores.architecture, strengths, weaknesses, recommendations
        )

        # Security recommendations
        if security_result:
            self._analyze_security(
                security_result, scores.security, strengths, weaknesses, recommendations
            )

        # Documentation recommendations
        self._analyze_documentation(
            scan_result, scores.documentation, strengths, weaknesses, recommendations
        )

        # Maintainability recommendations
        self._analyze_maintainability(
            scan_result, architecture_result, graph_result, scores.maintainability, strengths, weaknesses, recommendations
        )

        # Testing recommendations
        self._analyze_testing(
            scan_result, scores.testing, strengths, weaknesses, recommendations
        )

        # Complexity recommendations
        self._analyze_complexity(
            scan_result, graph_result, scores.complexity, strengths, weaknesses, recommendations
        )

        # Readability recommendations
        self._analyze_readability(
            scan_result, parsing_result, scores.readability, strengths, weaknesses, recommendations
        )

        # Scalability recommendations
        self._analyze_scalability(
            detection_result, architecture_result, graph_result, scores.scalability, strengths, weaknesses, recommendations
        )

        return QualityRecommendations(
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
        )

    def _analyze_architecture(
        self,
        architecture_result: ArchitectureResult,
        detection_result: DetectionResult,
        score: int,
        strengths: list[str],
        weaknesses: list[str],
        recommendations: list[str],
    ) -> None:
        """Analyze architecture quality."""
        if len(architecture_result.layers) >= 3:
            strengths.append("Well-structured layered architecture with clear separation of concerns")
        elif len(architecture_result.layers) < 2:
            weaknesses.append("Lack of clear architectural layers")
            recommendations.append("Consider implementing a layered architecture (e.g., presentation, business logic, data access)")

        modules = architecture_result.statistics.get("modules", 0)
        if modules >= 5:
            strengths.append(f"Modular structure with {modules} distinct modules")
        elif modules < 3:
            weaknesses.append("Limited modularization")
            recommendations.append("Break down the codebase into smaller, focused modules")

        if detection_result.backend:
            strengths.append(f"Uses backend framework(s): {', '.join([f.name for f in detection_result.backend])}")

        relationships = architecture_result.statistics.get("relationships", 0)
        if relationships > 50:
            weaknesses.append("High coupling between components")
            recommendations.append("Reduce coupling by implementing dependency injection and interfaces")

    def _analyze_security(
        self,
        security_result: SecurityAnalysisResult,
        score: int,
        strengths: list[str],
        weaknesses: list[str],
        recommendations: list[str],
    ) -> None:
        """Analyze security quality."""
        if score >= 90:
            strengths.append("Excellent security posture with minimal vulnerabilities")
        elif score >= 70:
            strengths.append("Good security posture with manageable vulnerabilities")
        elif score < 50:
            weaknesses.append("Poor security posture with multiple vulnerabilities")

        critical = security_result.summary.get("critical", 0)
        if critical > 0:
            weaknesses.append(f"{critical} critical security issue(s) detected")
            recommendations.append("Immediately address critical security vulnerabilities")

        high = security_result.summary.get("high", 0)
        if high > 0:
            weaknesses.append(f"{high} high-severity security issue(s) detected")
            recommendations.append("Prioritize fixing high-severity security issues")

        medium = security_result.summary.get("medium", 0)
        if medium > 5:
            weaknesses.append(f"{medium} medium-severity security issues detected")
            recommendations.append("Review and address medium-severity security issues")

    def _analyze_documentation(
        self,
        scan_result: ScanResult,
        score: int,
        strengths: list[str],
        weaknesses: list[str],
        recommendations: list[str],
    ) -> None:
        """Analyze documentation quality."""
        has_readme = any(f.name.lower().startswith("readme") for f in scan_result.files)
        if has_readme:
            strengths.append("README file present")
        else:
            weaknesses.append("Missing README file")
            recommendations.append("Create a comprehensive README.md with project overview, setup instructions, and usage examples")

        has_license = any(f.name.lower().startswith("license") for f in scan_result.files)
        if has_license:
            strengths.append("License file present")
        else:
            weaknesses.append("Missing license file")
            recommendations.append("Add a LICENSE file to specify the project's licensing terms")

        doc_files = [f for f in scan_result.files if f.extension in [".md", ".rst"] and "doc" in f.path.lower()]
        if len(doc_files) >= 3:
            strengths.append("Comprehensive documentation with multiple documentation files")
        elif len(doc_files) == 0:
            weaknesses.append("Lack of dedicated documentation")
            recommendations.append("Create documentation for API endpoints, architecture, and contribution guidelines")

    def _analyze_maintainability(
        self,
        scan_result: ScanResult,
        architecture_result: ArchitectureResult,
        graph_result: GraphResult,
        score: int,
        strengths: list[str],
        weaknesses: list[str],
        recommendations: list[str],
    ) -> None:
        """Analyze maintainability quality."""
        modules = architecture_result.statistics.get("modules", 0)
        if modules >= 5:
            strengths.append("Good modularization supports maintainability")

        total_files = scan_result.total_files
        edges = len(graph_result.edges)
        isolated = graph_result.isolated_files

        if total_files > 0:
            dependency_ratio = edges / total_files
            if 0.5 <= dependency_ratio <= 2.0:
                strengths.append("Balanced dependency structure")
            elif dependency_ratio > 4.0:
                weaknesses.append("Excessive dependencies between files")
                recommendations.append("Reduce dependencies by implementing the facade pattern or service layers")

        if total_files > 0:
            isolated_ratio = isolated / total_files
            if isolated_ratio > 0.3:
                weaknesses.append(f"{isolated} isolated files detected")
                recommendations.append("Integrate isolated files into the main codebase or remove unused code")

        languages = len(scan_result.languages)
        if languages <= 2:
            strengths.append("Consistent technology stack")
        elif languages > 5:
            weaknesses.append("High language diversity may increase maintenance burden")
            recommendations.append("Consider consolidating the technology stack where possible")

    def _analyze_testing(
        self,
        scan_result: ScanResult,
        score: int,
        strengths: list[str],
        weaknesses: list[str],
        recommendations: list[str],
    ) -> None:
        """Analyze testing quality."""
        test_dirs = [f.folder for f in scan_result.files if "test" in f.folder.lower()]
        if len(test_dirs) >= 2:
            strengths.append("Organized test directory structure")
        elif len(test_dirs) == 0:
            weaknesses.append("No dedicated test directories found")
            recommendations.append("Create dedicated test directories following project conventions")

        test_files = [f for f in scan_result.files if "test" in f.name.lower() or "spec" in f.name.lower()]
        if len(test_files) >= 5:
            strengths.append(f"Good test coverage with {len(test_files)} test files")
        elif len(test_files) == 0:
            weaknesses.append("No test files detected")
            recommendations.append("Implement unit tests for critical functionality")

        test_framework_files = [
            f for f in scan_result.files
            if any(fw in f.name.lower() for fw in ["pytest", "jest", "mocha", "junit", "rspec"])
        ]
        if test_framework_files:
            strengths.append("Test framework configured")

    def _analyze_complexity(
        self,
        scan_result: ScanResult,
        graph_result: GraphResult,
        score: int,
        strengths: list[str],
        weaknesses: list[str],
        recommendations: list[str],
    ) -> None:
        """Analyze complexity quality."""
        total_files = scan_result.total_files

        if total_files <= 10:
            strengths.append("Small, manageable codebase")
        elif total_files > 500:
            weaknesses.append("Large codebase may be difficult to navigate")
            recommendations.append("Consider splitting the project into smaller, focused sub-projects")

        edges = len(graph_result.edges)
        if total_files > 0:
            edge_ratio = edges / total_files
            if edge_ratio <= 1.0:
                strengths.append("Low coupling between files")
            elif edge_ratio > 4.0:
                weaknesses.append("High coupling complexity")
                recommendations.append("Refactor to reduce interdependencies between files")

        if scan_result.files:
            avg_size = sum(f.size for f in scan_result.files) / len(scan_result.files)
            if avg_size <= 5000:
                strengths.append("Files are reasonably sized")
            elif avg_size > 20000:
                weaknesses.append("Large average file size may indicate need for refactoring")
                recommendations.append("Break down large files into smaller, focused modules")

    def _analyze_readability(
        self,
        scan_result: ScanResult,
        parsing_result: ProjectParsingResult | None,
        score: int,
        strengths: list[str],
        weaknesses: list[str],
        recommendations: list[str],
    ) -> None:
        """Analyze readability quality."""
        extensions = set(f.extension for f in scan_result.files if f.extension)
        if len(extensions) <= 3:
            strengths.append("Consistent file extensions and naming")

        folders = set(f.folder for f in scan_result.files)
        if len(folders) >= 3:
            strengths.append("Well-organized folder structure")
        elif len(folders) < 2:
            weaknesses.append("Flat directory structure")
            recommendations.append("Organize code into logical directories and subdirectories")

        if parsing_result:
            total_functions = sum(len(f.functions) for f in parsing_result.files)
            total_classes = sum(len(f.classes) for f in parsing_result.files)

            if 10 <= total_functions <= 100:
                strengths.append("Reasonable function count suggests good decomposition")
            elif total_functions > 500:
                weaknesses.append("High function count may indicate complex code")
                recommendations.append("Consider simplifying complex functions and reducing code duplication")

            if total_classes >= 3:
                strengths.append("Object-oriented structure with defined classes")

    def _analyze_scalability(
        self,
        detection_result: DetectionResult,
        architecture_result: ArchitectureResult,
        graph_result: GraphResult,
        score: int,
        strengths: list[str],
        weaknesses: list[str],
        recommendations: list[str],
    ) -> None:
        """Analyze scalability quality."""
        if detection_result.containerized:
            strengths.append("Containerization supports deployment scalability")
        else:
            weaknesses.append("Not containerized")
            recommendations.append("Consider containerizing the application with Docker for easier scaling")

        if len(architecture_result.layers) >= 3:
            strengths.append("Layered architecture supports horizontal scaling")

        modules = architecture_result.statistics.get("modules", 0)
        if modules >= 5:
            strengths.append("Modular architecture enables independent scaling")

        edges = len(graph_result.edges)
        nodes = len(graph_result.nodes)
        if nodes > 0:
            avg_degree = (2 * edges) / nodes
            if avg_degree <= 3:
                strengths.append("Low coupling supports independent scaling")
            elif avg_degree > 6:
                weaknesses.append("High coupling may hinder scaling")
                recommendations.append("Reduce coupling to enable independent component scaling")

        if detection_result.package_managers:
            strengths.append("Package manager configured for dependency management")


recommendation_engine = RecommendationEngine()
