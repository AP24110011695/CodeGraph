"""Recommendation engine for architecture recommendation engine.

Orchestrates architecture recommendation generation using all existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.architecture_drift.architecture_drift_engine import ArchitectureDriftEngine, architecture_drift_engine
from app.architecture_recommendation.architecture_advisor import ArchitectureAdvisor, architecture_advisor
from app.architecture_recommendation.recommendation_builder import Recommendation, RecommendationBuilder, recommendation_builder
from app.dependency_health.dependency_health_engine import DependencyHealthEngine, dependency_health_engine
from app.indexing.index_manager import IndexManager
from app.risk.risk_engine import RiskEngine, risk_engine
from app.security.security_analyzer import security_analyzer
from app.services.scanner_service import ScanResult, scanner_service
from app.smells.smell_detector import smell_detector

logger = logging.getLogger(__name__)


@dataclass
class RecommendationResult:
    """Complete result from architecture recommendation generation."""

    project_name: str
    overall_architecture_score: int
    summary: dict[str, int] = field(default_factory=dict)
    recommendations: list[dict] = field(default_factory=list)


class RecommendationEngine:
    """Performs comprehensive architecture recommendation generation.

    Reuses all existing CodeGraph analysis modules:
    - Repository Scanner
    - Architecture Drift Engine
    - Dependency Health Engine
    - Risk Engine
    - Security Analyzer
    - Code Smell Detector
    """

    def __init__(
        self,
        index_manager: IndexManager | None = None,
        recommendation_builder: RecommendationBuilder | None = None,
        architecture_advisor: ArchitectureAdvisor | None = None,
    ):
        """Initialize the recommendation engine.

        Args:
            index_manager: Optional IndexManager for accessing indexed repositories.
            recommendation_builder: Optional RecommendationBuilder instance.
            architecture_advisor: Optional ArchitectureAdvisor instance.
        """
        self.index_manager = index_manager
        self.recommendation_builder = recommendation_builder or RecommendationBuilder()
        self.architecture_advisor = architecture_advisor or ArchitectureAdvisor()

        # Individual analyzers
        self.scanner = scanner_service
        self.architecture_drift_engine = architecture_drift_engine
        self.dependency_health_engine = dependency_health_engine
        self.risk_engine = risk_engine
        self.security_analyzer = security_analyzer
        self.smell_detector = smell_detector

    def analyze(
        self,
        project_path: Path,
        upload_id: str | None = None,
    ) -> RecommendationResult:
        """Perform comprehensive architecture recommendation generation for a repository.

        Args:
            project_path: Absolute path to the project directory.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            RecommendationResult with comprehensive architecture recommendations.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Starting architecture recommendation generation for project: {project_path}")

        # Step 1: Scan the repository
        logger.info("Scanning repository")
        scan_result = self.scanner.scan(project_path)

        if scan_result.total_files == 0:
            logger.warning("Repository is empty, returning minimal result")
            return self._build_empty_result(scan_result)

        # Step 2: Run architecture drift analysis
        logger.info("Running architecture drift analysis")
        drift_result = self.architecture_drift_engine.analyze(project_path, upload_id)

        # Step 3: Run dependency health analysis
        logger.info("Running dependency health analysis")
        dependency_health_result = self.dependency_health_engine.analyze(project_path, upload_id)

        # Step 4: Run risk analysis
        logger.info("Running risk analysis")
        risk_result = self.risk_engine.analyze(project_path, upload_id)

        # Step 5: Run security analysis
        logger.info("Running security analysis")
        security_result = self.security_analyzer.analyze(project_path, scan_result)

        # Step 6: Run code smell detection
        logger.info("Running code smell detection")
        smell_result = self.smell_detector.detect(project_path, scan_result)

        # Step 7: Convert results to dict format for builder
        drift_findings = drift_result.findings
        dependency_findings = dependency_health_result.findings
        risk_findings = risk_result.risks
        security_findings = self._security_to_list(security_result)
        smell_findings = self._smell_to_list(smell_result)

        # Step 8: Build recommendations
        logger.info("Building recommendations")
        recommendations = self.recommendation_builder.build_recommendations(
            drift_findings=drift_findings,
            dependency_findings=dependency_findings,
            risk_findings=risk_findings,
            security_findings=security_findings,
            smell_findings=smell_findings,
        )

        # Step 9: Calculate overall architecture score
        logger.info("Calculating overall architecture score")
        overall_score = self._calculate_overall_score(
            drift_result.architecture_health_score,
            dependency_health_result.overall_health_score,
            risk_result.overall_risk_score,
        )

        # Step 10: Build summary
        summary = self._build_summary(recommendations)

        # Step 11: Serialize recommendations
        serialized_recommendations = self._serialize_recommendations(recommendations)

        return RecommendationResult(
            project_name=scan_result.project_name,
            overall_architecture_score=overall_score,
            summary=summary,
            recommendations=serialized_recommendations,
        )

    def _build_empty_result(self, scan_result: ScanResult) -> RecommendationResult:
        """Build a minimal result for empty repositories."""
        return RecommendationResult(
            project_name=scan_result.project_name,
            overall_architecture_score=100,
            summary={
                "recommendations": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
            recommendations=[],
        )

    def _security_to_list(self, security_result) -> list[dict]:
        """Convert security result to list of dictionaries."""
        if hasattr(security_result, 'issues'):
            return [
                {
                    "title": issue.title,
                    "category": "Security",
                    "severity": issue.severity,
                    "evidence": issue.evidence,
                    "affected_files": issue.affected_files,
                    "recommendation": issue.recommendation,
                }
                for issue in security_result.issues
            ]
        return []

    def _smell_to_list(self, smell_result) -> list[dict]:
        """Convert smell result to list of dictionaries."""
        if hasattr(smell_result, 'smells'):
            return [
                {
                    "title": f"Code Smell: {smell.type}",
                    "category": "Code Quality",
                    "severity": smell.severity,
                    "evidence": smell.description,
                    "affected_files": [smell.file],
                    "recommendation": "Review and refactor the code smell.",
                }
                for smell in smell_result.smells
            ]
        return []

    def _calculate_overall_score(
        self,
        drift_score: int,
        dependency_score: int,
        risk_score: int,
    ) -> int:
        """Calculate overall architecture score.

        Args:
            drift_score: Architecture drift health score.
            dependency_score: Dependency health score.
            risk_score: Risk score (inverted for architecture score).

        Returns:
            Overall architecture score (0-100).
        """
        # Weighted average
        weights = {
            "drift": 0.4,
            "dependency": 0.3,
            "risk": 0.3,
        }

        # Invert risk score (higher risk = lower architecture score)
        inverted_risk_score = 100 - risk_score

        overall_score = (
            drift_score * weights["drift"] +
            dependency_score * weights["dependency"] +
            inverted_risk_score * weights["risk"]
        )

        return round(overall_score)

    def _build_summary(self, recommendations: list[Recommendation]) -> dict[str, int]:
        """Build summary statistics."""
        summary = {
            "recommendations": len(recommendations),
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }

        for recommendation in recommendations:
            priority = recommendation.priority
            if priority in summary:
                summary[priority] += 1

        return summary

    def _serialize_recommendations(self, recommendations: list[Recommendation]) -> list[dict]:
        """Serialize recommendations to dictionary format."""
        return [
            {
                "title": recommendation.title,
                "category": recommendation.category,
                "priority": recommendation.priority,
                "impact": recommendation.impact,
                "confidence": recommendation.confidence,
                "reason": recommendation.reason,
                "evidence": recommendation.evidence,
                "affected_files": recommendation.affected_files,
                "recommendation": recommendation.recommendation,
                "expected_benefit": recommendation.expected_benefit,
            }
            for recommendation in recommendations
        ]


recommendation_engine = RecommendationEngine()
