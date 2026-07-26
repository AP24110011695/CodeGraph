"""Quality analyzer for CodeGraph.

Orchestrates the complete quality analysis pipeline by integrating
with existing services: Scanner, Parser, Architecture Builder,
Dependency Graph, Security Analyzer, Scoring Engine, and Recommendation Engine.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from app.analyzers.architecture_builder import architecture_builder
from app.parsers.parser_engine import ParserEngine
from app.quality.recommendations import QualityRecommendations, recommendation_engine
from app.quality.scoring_engine import QualityScores, scoring_engine
from app.security.security_analyzer import security_analyzer
from app.services.dependency_graph import graph_builder
from app.services.framework_detector import detector_service
from app.services.scanner_service import ScanResult, scanner_service

logger = logging.getLogger(__name__)


@dataclass
class QualityAnalysisResult:
    """Complete result from quality analysis."""

    project_name: str
    scores: QualityScores
    recommendations: QualityRecommendations
    metadata: dict = field(default_factory=dict)


class QualityAnalyzer:
    """Analyzes repositories for code quality metrics.

    Orchestrates the complete pipeline:
    1. Repository Scanner
    2. Framework Detector
    3. Dependency Graph Builder
    4. Parser Engine (optional)
    5. Architecture Builder
    6. Security Analyzer (optional)
    7. Scoring Engine
    8. Recommendation Engine
    """

    def __init__(self):
        """Initialize the quality analyzer."""
        self.scanner = scanner_service
        self.detector = detector_service
        self.graph_builder = graph_builder
        self.architecture_builder = architecture_builder
        self.security_analyzer = security_analyzer
        self.scoring_engine = scoring_engine
        self.recommendation_engine = recommendation_engine

    def analyze(
        self,
        project_path: Path,
        scan_result: ScanResult | None = None,
    ) -> QualityAnalysisResult:
        """Analyze a project for code quality.

        Args:
            project_path: Absolute path to the extracted project.
            scan_result: Optional pre-computed scan result.

        Returns:
            QualityAnalysisResult with scores and recommendations.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        # Step 1: Scan the repository (if not provided)
        if scan_result is None:
            logger.info(f"Scanning project: {project_path}")
            scan_result = self.scanner.scan(project_path)

        # Step 2: Detect frameworks
        logger.info("Detecting frameworks")
        detection_result = self.detector.detect(project_path, scan_result)

        # Step 3: Build dependency graph
        logger.info("Building dependency graph")
        graph_result = self.graph_builder.build(project_path, scan_result)

        # Step 4: Parse the project (optional, for additional context)
        logger.info("Parsing project for additional context")
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

        # Step 6: Analyze security (optional)
        logger.info("Analyzing security")
        try:
            security_result = self.security_analyzer.analyze(
                project_path, scan_result
            )
        except Exception as e:
            logger.warning(f"Failed to analyze security: {e}")
            security_result = None

        # Step 7: Calculate scores
        logger.info("Calculating quality scores")
        scores = self.scoring_engine.calculate_scores(
            scan_result=scan_result,
            detection_result=detection_result,
            architecture_result=architecture_result,
            graph_result=graph_result,
            parsing_result=parsing_result,
            security_result=security_result,
        )

        # Step 8: Generate recommendations
        logger.info("Generating recommendations")
        recommendations = self.recommendation_engine.generate_recommendations(
            scan_result=scan_result,
            detection_result=detection_result,
            architecture_result=architecture_result,
            graph_result=graph_result,
            parsing_result=parsing_result,
            security_result=security_result,
            scores=scores,
        )

        # Build metadata
        metadata = {
            "total_files": scan_result.total_files,
            "total_folders": scan_result.total_folders,
            "languages": scan_result.languages,
            "containerized": detection_result.containerized,
            "package_managers": detection_result.package_managers,
            "backend_frameworks": [f.name for f in detection_result.backend],
            "frontend_frameworks": [f.name for f in detection_result.frameworks],
        }

        return QualityAnalysisResult(
            project_name=scan_result.project_name,
            scores=scores,
            recommendations=recommendations,
            metadata=metadata,
        )


quality_analyzer = QualityAnalyzer()
