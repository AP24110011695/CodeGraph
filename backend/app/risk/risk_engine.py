"""Risk engine for repository risk analysis.

Orchestrates risk analysis using all existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import concurrent.futures

from app.analyzers.architecture_builder import architecture_builder
from app.indexing.index_manager import IndexManager
from app.knowledge_graph.graph_builder import KnowledgeGraphBuilder, knowledge_graph_builder
from app.metrics.metrics_engine import MetricsEngine, MetricsResult
from app.quality.quality_analyzer import QualityAnalysisResult, quality_analyzer
from app.refactoring.refactoring_engine import refactoring_engine
from app.review.review_engine import ReviewEngine, review_engine
from app.risk.risk_calculator import RiskCalculationResult, RiskCalculator, risk_calculator
from app.risk.risk_classifier import RiskClassifier, risk_classifier
from app.security.security_analyzer import SecurityAnalysisResult, security_analyzer
from app.services.dependency_graph import graph_builder
from app.services.framework_detector import detector_service
from app.services.scanner_service import ScanResult, scanner_service
from app.smells.smell_detector import SmellDetectionResult, smell_detector

logger = logging.getLogger(__name__)


@dataclass
class RiskAnalysisResult:
    """Complete result from risk analysis."""

    project_name: str
    overall_risk_score: int
    overall_level: str
    summary: dict[str, int] = field(default_factory=dict)
    risks: list[dict] = field(default_factory=list)
    top_risks: list[dict] = field(default_factory=list)
    priority_recommendations: list[str] = field(default_factory=list)


class RiskEngine:
    """Performs comprehensive repository risk analysis.

    Reuses all existing CodeGraph analysis modules:
    - Repository Scanner
    - Framework Detector
    - Parser Engine
    - Architecture Builder
    - Dependency Graph
    - Security Analyzer
    - Quality Analyzer
    - Code Smell Detector
    - Refactoring Engine
    - Metrics Engine
    - Code Review Engine
    - Knowledge Graph Engine
    """

    def __init__(
        self,
        index_manager: IndexManager | None = None,
        metrics_engine: MetricsEngine | None = None,
        review_engine: ReviewEngine | None = None,
        risk_calculator: RiskCalculator | None = None,
        risk_classifier: RiskClassifier | None = None,
    ):
        """Initialize the risk engine.

        Args:
            index_manager: Optional IndexManager for accessing indexed repositories.
            metrics_engine: Optional MetricsEngine instance.
            review_engine: Optional ReviewEngine instance.
            risk_calculator: Optional RiskCalculator instance.
            risk_classifier: Optional RiskClassifier instance.
        """
        self.index_manager = index_manager
        self.metrics_engine = metrics_engine or MetricsEngine(index_manager=index_manager)
        self.review_engine = review_engine or ReviewEngine(index_manager=index_manager)
        self.risk_calculator = risk_calculator or RiskCalculator()
        self.risk_classifier = risk_classifier or RiskClassifier()

        # Individual analyzers for risk extraction
        self.security_analyzer = security_analyzer
        self.smell_detector = smell_detector
        self.quality_analyzer = quality_analyzer
        self.refactoring_engine = refactoring_engine
        self.scanner = scanner_service
        self.knowledge_graph_builder = knowledge_graph_builder
        self.detector = detector_service
        self.graph_builder = graph_builder

    def analyze(
        self,
        project_path: Path,
        upload_id: str | None = None,
    ) -> RiskAnalysisResult:
        """Perform comprehensive risk analysis for a repository.

        Args:
            project_path: Absolute path to the project directory.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            RiskAnalysisResult with comprehensive risk findings.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Starting risk analysis for project: {project_path}")

        # Step 1 & 2: Generate metrics and extract risk evidence concurrently
        logger.info("Extracting risk evidence from analyzers concurrently")
        with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
            future_metrics = executor.submit(self.metrics_engine.generate, project_path, upload_id)
            future_security = executor.submit(self._extract_security_issues, project_path)
            future_quality = executor.submit(self._extract_quality_recommendations, project_path)
            future_smells = executor.submit(self._extract_smell_issues, project_path)
            future_arch = executor.submit(self._extract_architecture_result, project_path)
            future_dep = executor.submit(self._extract_dependency_result, project_path)
            future_review = executor.submit(self._extract_review_issues, project_path, upload_id)

            metrics_result = future_metrics.result()
            security_issues = future_security.result()
            quality_recommendations = future_quality.result()
            smell_issues = future_smells.result()
            architecture_result = future_arch.result()
            dependency_result = future_dep.result()
            review_issues = future_review.result()

        # Step 3: Convert metrics to dict format for calculator
        metrics_dict = self._metrics_to_dict(metrics_result)

        # Step 4: Calculate risks
        logger.info("Calculating risks")
        calculation_result = self.risk_calculator.calculate(
            security_issues=security_issues,
            quality_recommendations=quality_recommendations,
            smell_issues=smell_issues,
            metrics_result=metrics_dict,
            architecture_result=architecture_result,
            dependency_result=dependency_result,
            review_issues=review_issues,
        )

        # Step 5: Determine overall risk level
        overall_level = self.risk_classifier.classify(calculation_result.overall_score)

        # Step 6: Build response
        summary = {
            "critical": calculation_result.summary.critical,
            "high": calculation_result.summary.high,
            "medium": calculation_result.summary.medium,
            "low": calculation_result.summary.low,
        }

        risks = self._serialize_risks(calculation_result.risks)
        top_risks = self._get_top_risks(calculation_result.risks, limit=10)
        priority_recommendations = self._generate_priority_recommendations(calculation_result.risks)

        return RiskAnalysisResult(
            project_name=metrics_result.project_name,
            overall_risk_score=calculation_result.overall_score,
            overall_level=overall_level,
            summary=summary,
            risks=risks,
            top_risks=top_risks,
            priority_recommendations=priority_recommendations,
        )

    def _extract_security_issues(self, project_path: Path) -> list[dict]:
        """Extract security issues from SecurityAnalyzer."""
        try:
            scan_result = self.scanner.scan(project_path)
            security_result = self.security_analyzer.analyze(project_path, scan_result)
            return [self._issue_to_dict(issue) for issue in security_result.issues]
        except Exception as e:
            logger.warning(f"Failed to extract security issues: {e}")
            return []

    def _extract_quality_recommendations(self, project_path: Path) -> list[dict]:
        """Extract quality recommendations from QualityAnalyzer."""
        try:
            scan_result = self.scanner.scan(project_path)
            quality_result = self.quality_analyzer.analyze(project_path, scan_result)
            recommendations = []
            if quality_result.recommendations and quality_result.recommendations.recommendations:
                for rec in quality_result.recommendations.recommendations[:20]:
                    if isinstance(rec, dict):
                        recommendations.append(rec)
                    else:
                        recommendations.append({"title": str(rec), "description": str(rec)})
            return recommendations
        except Exception as e:
            logger.warning(f"Failed to extract quality recommendations: {e}")
            return []

    def _extract_smell_issues(self, project_path: Path) -> list[dict]:
        """Extract code smell issues from SmellDetector."""
        try:
            scan_result = self.scanner.scan(project_path)
            smell_result = self.smell_detector.detect(project_path, scan_result)
            return [self._smell_to_dict(smell) for smell in smell_result.smells]
        except Exception as e:
            logger.warning(f"Failed to extract smell issues: {e}")
            return []

    def _extract_architecture_result(self, project_path: Path) -> dict | None:
        """Extract architecture result."""
        try:
            scan_result = self.scanner.scan(project_path)
            detection_result = self.detector.detect(project_path, scan_result)
            graph_result = self.graph_builder.build(project_path, scan_result)
            parsing_result = self._try_parse_project(project_path, scan_result)
            architecture_result = architecture_builder.build(scan_result, detection_result, graph_result, parsing_result)
            return self._architecture_to_dict(architecture_result)
        except Exception as e:
            logger.warning(f"Failed to extract architecture result: {e}")
            return None

    def _extract_dependency_result(self, project_path: Path) -> dict | None:
        """Extract dependency result."""
        try:
            scan_result = self.scanner.scan(project_path)
            graph_result = self.graph_builder.build(project_path, scan_result)
            return {
                "nodes": graph_result.nodes,
                "edges": graph_result.edges,
                "isolated_files": graph_result.isolated_files,
            }
        except Exception as e:
            logger.warning(f"Failed to extract dependency result: {e}")
            return None

    def _extract_review_issues(self, project_path: Path, upload_id: str | None) -> list[dict]:
        """Extract review issues from ReviewEngine."""
        try:
            review_result = self.review_engine.review(project_path, upload_id)
            return review_result.issues
        except Exception as e:
            logger.warning(f"Failed to extract review issues: {e}")
            return []

    def _try_parse_project(self, project_path: Path, scan_result: ScanResult):
        """Try to parse the project."""
        try:
            from app.parsers.parser_engine import ParserEngine
            return ParserEngine.parse_project(project_path, scan_result)
        except Exception as e:
            logger.warning(f"Failed to parse project: {e}")
            return None

    def _metrics_to_dict(self, metrics_result: MetricsResult) -> dict:
        """Convert MetricsResult to dictionary."""
        return {
            "statistics": {
                "total_files": metrics_result.statistics.total_files,
                "total_lines": metrics_result.statistics.total_lines,
                "quality_score": metrics_result.statistics.quality_score,
                "security_score": metrics_result.statistics.security_score,
                "average_file_size": metrics_result.statistics.average_file_size,
                "dependency_count": metrics_result.statistics.dependency_count,
                "smell_count": metrics_result.statistics.smell_count,
                "quality_breakdown": metrics_result.statistics.quality_breakdown,
            },
        }

    def _architecture_to_dict(self, architecture_result) -> dict:
        """Convert ArchitectureResult to dictionary."""
        return {
            "layers": [layer for layer in architecture_result.layers],
            "modules": [
                {
                    "name": module.name,
                    "type": module.type,
                    "layer": module.layer,
                    "file_count": len(module.files),
                }
                for module in architecture_result.modules
            ],
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

    def _smell_to_dict(self, smell) -> dict:
        """Convert code smell to dictionary."""
        return {
            "type": smell.type,
            "severity": smell.severity,
            "description": smell.description,
            "file": smell.file,
            "line": smell.line,
        }

    def _serialize_risks(self, risks) -> list[dict]:
        """Serialize risks to dictionary format."""
        return [
            {
                "title": risk.title,
                "category": risk.category,
                "risk_level": risk.risk_level,
                "score": risk.score,
                "reason": risk.reason,
                "evidence": risk.evidence,
                "affected_files": risk.affected_files,
                "recommendation": risk.recommendation,
                "potential_impact": risk.potential_impact,
                "source": risk.source,
            }
            for risk in risks
        ]

    def _get_top_risks(self, risks, limit: int = 10) -> list[dict]:
        """Get top risks by score."""
        sorted_risks = sorted(risks, key=lambda x: x.score, reverse=True)
        return self._serialize_risks(sorted_risks[:limit])

    def _generate_priority_recommendations(self, risks) -> list[str]:
        """Generate priority recommendations from risks."""
        recommendations = []

        # Get critical and high risks
        critical_high = [r for r in risks if r.risk_level in ["CRITICAL", "HIGH"]]

        for risk in critical_high[:5]:
            if risk.recommendation:
                recommendations.append(f"[{risk.risk_level}] {risk.recommendation}")

        # Add general recommendations based on risk categories
        categories = set(r.category for r in risks)
        if "Security" in categories:
            recommendations.append("Review and address all security vulnerabilities immediately")
        if "Architecture" in categories:
            recommendations.append("Consider architectural refactoring to reduce coupling")
        if "Technical Debt" in categories:
            recommendations.append("Prioritize reducing technical debt to improve maintainability")

        return recommendations[:10]


risk_engine = RiskEngine()
