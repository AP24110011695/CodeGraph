"""Boundary detection engine for microservice boundary detection engine.

Orchestrates microservice boundary detection using all existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.indexing.index_manager import IndexManager
from app.parsers.parser_engine import ParserEngine
from app.services.dependency_graph import graph_builder
from app.services.scanner_service import ScanResult, scanner_service
from app.microservices.communication_analyzer import CommunicationAnalysis, CommunicationAnalyzer, communication_analyzer
from app.microservices.service_cluster_detector import ServiceCluster, ServiceClusterDetector, service_cluster_detector

logger = logging.getLogger(__name__)


@dataclass
class ServiceCandidate:
    """A potential microservice candidate."""

    service_name: str
    confidence: int
    boundary_score: int
    reason: str
    evidence: str
    included_modules: list[str]
    dependencies: list[str]
    migration_difficulty: str
    recommendation: str


@dataclass
class BoundaryDetectionResult:
    """Complete result from boundary detection."""

    overall_score: int
    summary: dict[str, int]
    candidates: list[dict] = field(default_factory=list)
    communication_recommendations: list[str] = field(default_factory=list)


class BoundaryDetectionEngine:
    """Performs comprehensive microservice boundary detection.

    Reuses all existing CodeGraph analysis modules:
    - Repository Scanner
    - Parser Engine
    - Dependency Graph Builder
    - Architecture Builder
    """

    def __init__(
        self,
        index_manager: IndexManager | None = None,
        service_cluster_detector: ServiceClusterDetector | None = None,
        communication_analyzer: CommunicationAnalyzer | None = None,
    ):
        """Initialize the boundary detection engine.

        Args:
            index_manager: Optional IndexManager for accessing indexed repositories.
            service_cluster_detector: Optional ServiceClusterDetector instance.
            communication_analyzer: Optional CommunicationAnalyzer instance.
        """
        self.index_manager = index_manager
        self.service_cluster_detector = service_cluster_detector or ServiceClusterDetector()
        self.communication_analyzer = communication_analyzer or CommunicationAnalyzer()

        # Individual analyzers
        self.scanner = scanner_service
        self.parser = ParserEngine()
        self.graph_builder = graph_builder

    def detect_boundaries(
        self,
        project_path: Path,
        upload_id: str | None = None,
    ) -> BoundaryDetectionResult:
        """Perform comprehensive boundary detection for a repository.

        Args:
            project_path: Absolute path to the project directory.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            BoundaryDetectionResult with microservice candidates.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Starting boundary detection for project: {project_path}")

        # Step 1: Scan the repository
        logger.info("Scanning repository")
        scan_result = self.scanner.scan(project_path)

        if scan_result.total_files == 0:
            logger.warning("Repository is empty, returning minimal result")
            return self._build_empty_result()

        # Step 2: Parse the repository
        logger.info("Parsing repository")
        parsing_result = self.parser.parse_project(project_path, scan_result)

        # Step 3: Build dependency graph
        logger.info("Building dependency graph")
        dependency_graph = self.graph_builder.build(project_path, scan_result)

        # Step 4: Get architecture result
        logger.info("Getting architecture result")
        architecture_result = self._get_architecture_result(project_path)

        # Step 5: Detect service clusters
        logger.info("Detecting service clusters")
        clusters = self.service_cluster_detector.detect_clusters(
            project_path=project_path,
            dependency_graph=dependency_graph,
            architecture_result=architecture_result,
        )

        # Step 6: Analyze communication patterns
        logger.info("Analyzing communication patterns")
        communication_analysis = self.communication_analyzer.analyze_communication(
            project_path=project_path,
            dependency_graph=dependency_graph,
            architecture_result=architecture_result,
        )

        # Step 7: Generate service candidates
        logger.info("Generating service candidates")
        candidates = self._generate_candidates(
            clusters, communication_analysis
        )

        # Step 8: Calculate overall score
        logger.info("Calculating overall score")
        overall_score = self._calculate_overall_score(candidates)

        # Step 9: Build summary
        logger.info("Building summary")
        summary = self._build_summary(candidates)

        # Step 10: Generate communication recommendations
        logger.info("Generating communication recommendations")
        communication_recommendations = self._generate_communication_recommendations(
            communication_analysis
        )

        # Step 11: Serialize candidates
        serialized_candidates = self._serialize_candidates(candidates)

        return BoundaryDetectionResult(
            overall_score=overall_score,
            summary=summary,
            candidates=serialized_candidates,
            communication_recommendations=communication_recommendations,
        )

    def _build_empty_result(self) -> BoundaryDetectionResult:
        """Build a minimal result for empty repositories."""
        return BoundaryDetectionResult(
            overall_score=0,
            summary={
                "service_candidates": 0,
                "recommended": 0,
            },
            candidates=[],
            communication_recommendations=[],
        )

    def _get_architecture_result(self, project_path: Path) -> dict:
        """Get architecture result.

        Args:
            project_path: The project path.

        Returns:
            Architecture result dictionary.
        """
        try:
            from app.analyzers.architecture_builder import architecture_builder
            architecture_result = architecture_builder.build(project_path)
            return {
                "layers": architecture_result.layers if hasattr(architecture_result, 'layers') else [],
                "modules": architecture_result.modules if hasattr(architecture_result, 'modules') else [],
            }
        except Exception as e:
            logger.warning(f"Failed to get architecture result: {e}")
            return {"layers": [], "modules": []}

    def _generate_candidates(
        self,
        clusters: list[ServiceCluster],
        communication_analysis: CommunicationAnalysis,
    ) -> list[ServiceCandidate]:
        """Generate service candidates from clusters.

        Args:
            clusters: Detected service clusters.
            communication_analysis: Communication analysis.

        Returns:
            List of service candidates.
        """
        candidates: list[ServiceCandidate] = []

        for cluster in clusters:
            # Calculate confidence based on boundary score and independence
            confidence = (cluster.boundary_score + communication_analysis.service_independence_score) // 2

            # Determine migration difficulty
            if cluster.coupling_score < 30:
                migration_difficulty = "Low"
            elif cluster.coupling_score < 60:
                migration_difficulty = "Medium"
            else:
                migration_difficulty = "High"

            # Determine recommendation
            if confidence >= 80:
                recommendation = "Extract into an independent service."
            elif confidence >= 60:
                recommendation = "Consider extracting as a service after refactoring."
            else:
                recommendation = "Not recommended for extraction at this time."

            candidate = ServiceCandidate(
                service_name=cluster.name,
                confidence=confidence,
                boundary_score=cluster.boundary_score,
                reason=f"{cluster.name} has high cohesion ({cluster.cohesion_score}) and low coupling ({cluster.coupling_score}).",
                evidence=f"Module cluster with {len(cluster.modules)} modules.",
                included_modules=cluster.modules,
                dependencies=[],
                migration_difficulty=migration_difficulty,
                recommendation=recommendation,
            )
            candidates.append(candidate)

        return candidates

    def _calculate_overall_score(self, candidates: list[ServiceCandidate]) -> int:
        """Calculate overall boundary detection score.

        Args:
            candidates: Service candidates.

        Returns:
            Overall score (0-100).
        """
        if not candidates:
            return 0

        # Average confidence of all candidates
        avg_confidence = sum(c.confidence for c in candidates) / len(candidates)

        return int(avg_confidence)

    def _build_summary(self, candidates: list[ServiceCandidate]) -> dict[str, int]:
        """Build summary statistics.

        Args:
            candidates: Service candidates.

        Returns:
            Summary dictionary.
        """
        recommended = sum(1 for c in candidates if c.confidence >= 80)

        return {
            "service_candidates": len(candidates),
            "recommended": recommended,
        }

    def _generate_communication_recommendations(
        self,
        communication_analysis: CommunicationAnalysis,
    ) -> list[str]:
        """Generate communication recommendations.

        Args:
            communication_analysis: Communication analysis.

        Returns:
            List of recommendations.
        """
        recommendations = []

        if communication_analysis.shared_components:
            recommendations.append(
                f"Consider refactoring shared components ({', '.join(communication_analysis.shared_components)}) into separate services."
            )

        if communication_analysis.cross_domain_dependencies:
            recommendations.append(
                f"Reduce cross-domain dependencies ({len(communication_analysis.cross_domain_dependencies)} found) to improve service independence."
            )

        if communication_analysis.service_independence_score < 70:
            recommendations.append(
                "Improve service independence by reducing shared dependencies."
            )

        return recommendations

    def _serialize_candidates(self, candidates: list[ServiceCandidate]) -> list[dict]:
        """Serialize candidates to dictionary format.

        Args:
            candidates: List of service candidates.

        Returns:
            List of serialized candidate data.
        """
        return [
            {
                "service_name": candidate.service_name,
                "confidence": candidate.confidence,
                "boundary_score": candidate.boundary_score,
                "reason": candidate.reason,
                "evidence": candidate.evidence,
                "included_modules": candidate.included_modules,
                "dependencies": candidate.dependencies,
                "migration_difficulty": candidate.migration_difficulty,
                "recommendation": candidate.recommendation,
            }
            for candidate in candidates
        ]


boundary_detection_engine = BoundaryDetectionEngine()
