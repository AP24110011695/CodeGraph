"""Review engine for comprehensive code review.

Orchestrates repository-wide code review using all existing CodeGraph analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.indexing.index_manager import IndexManager
from app.metrics.metrics_engine import MetricsEngine, MetricsResult
from app.quality.quality_analyzer import QualityAnalysisResult, quality_analyzer
from app.refactoring.refactoring_engine import refactoring_engine
from app.review.issue_prioritizer import IssuePrioritizer, PrioritizedIssues
from app.review.review_report_builder import ReviewReportBuilder, ReviewReport
from app.security.security_analyzer import SecurityAnalysisResult, security_analyzer
from app.services.scanner_service import ScanResult, scanner_service
from app.smells.smell_detector import SmellDetectionResult, smell_detector

logger = logging.getLogger(__name__)


@dataclass
class ReviewResult:
    """Complete result from code review."""

    project_name: str
    overall_score: int
    summary: dict[str, Any] = field(default_factory=dict)
    issues: list[dict] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=dict)
    report: ReviewReport | None = None


class ReviewEngine:
    """Performs comprehensive repository-wide code review.

    Reuses all existing CodeGraph analysis modules:
    - Repository Scanner
    - Framework Detector
    - Parser Engine
    - Dependency Graph
    - Architecture Builder
    - Security Analyzer
    - Quality Analyzer
    - Code Smell Detector
    - Refactoring Engine
    - Metrics Engine
    """

    def __init__(
        self,
        index_manager: IndexManager | None = None,
        metrics_engine: MetricsEngine | None = None,
        issue_prioritizer: IssuePrioritizer | None = None,
        report_builder: ReviewReportBuilder | None = None,
    ):
        """Initialize the review engine.

        Args:
            index_manager: Optional IndexManager for accessing indexed repositories.
            metrics_engine: Optional MetricsEngine instance.
            issue_prioritizer: Optional IssuePrioritizer instance.
            report_builder: Optional ReviewReportBuilder instance.
        """
        self.index_manager = index_manager
        self.metrics_engine = metrics_engine or MetricsEngine(index_manager=index_manager)
        self.issue_prioritizer = issue_prioritizer or IssuePrioritizer()
        self.report_builder = report_builder or ReviewReportBuilder()

        # Individual analyzers for issue extraction
        self.security_analyzer = security_analyzer
        self.smell_detector = smell_detector
        self.quality_analyzer = quality_analyzer
        self.refactoring_engine = refactoring_engine
        self.scanner = scanner_service

    def review(
        self,
        project_path: Path,
        upload_id: str | None = None,
    ) -> ReviewResult:
        """Perform comprehensive code review for a repository.

        Args:
            project_path: Absolute path to the project directory.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            ReviewResult with comprehensive review findings.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Starting code review for project: {project_path}")

        # Step 1: Generate comprehensive metrics (this runs all analyzers)
        logger.info("Generating metrics")
        metrics_result = self.metrics_engine.generate(project_path, upload_id)

        # Step 2: Extract issues from individual analyzers
        logger.info("Extracting issues from analyzers")
        security_issues = self._extract_security_issues(project_path)
        smell_issues = self._extract_smell_issues(project_path)
        quality_recommendations = self._extract_quality_recommendations(project_path)
        refactoring_suggestions = self._extract_refactoring_suggestions(project_path)

        # Step 3: Prioritize and deduplicate issues
        logger.info("Prioritizing and deduplicating issues")
        prioritized_issues = self.issue_prioritizer.prioritize(
            security_issues=security_issues,
            smell_issues=smell_issues,
            quality_recommendations=quality_recommendations,
            refactoring_suggestions=refactoring_suggestions,
        )

        # Step 4: Build comprehensive review report
        logger.info("Building review report")
        report = self.report_builder.build(
            project_name=metrics_result.project_name,
            metrics_result=metrics_result,
            prioritized_issues=prioritized_issues,
        )

        # Step 5: Build response
        summary = self._build_summary(report.summary, metrics_result)
        issues = self._serialize_issues(prioritized_issues.issues)
        strengths = self._collect_strengths(report)
        recommendations = self._collect_recommendations(report)

        return ReviewResult(
            project_name=metrics_result.project_name,
            overall_score=report.summary.overall_score,
            summary=summary,
            issues=issues,
            strengths=strengths,
            recommendations=recommendations,
            report=report,
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

    def _extract_smell_issues(self, project_path: Path) -> list[dict]:
        """Extract code smell issues from SmellDetector."""
        try:
            scan_result = self.scanner.scan(project_path)
            smell_result = self.smell_detector.detect(project_path, scan_result)
            return [self._smell_to_dict(smell) for smell in smell_result.smells]
        except Exception as e:
            logger.warning(f"Failed to extract smell issues: {e}")
            return []

    def _extract_quality_recommendations(self, project_path: Path) -> list[dict]:
        """Extract quality recommendations from QualityAnalyzer."""
        try:
            scan_result = self.scanner.scan(project_path)
            quality_result = self.quality_analyzer.analyze(project_path, scan_result)
            recommendations = []
            if quality_result.recommendations and quality_result.recommendations.recommendations:
                for rec in quality_result.recommendations.recommendations[:20]:  # Limit to top 20
                    recommendations.append({
                        "title": rec.get("title", "Quality Issue"),
                        "category": rec.get("category", "Quality"),
                        "priority": rec.get("priority", "medium"),
                        "description": rec.get("description", ""),
                        "evidence": rec.get("evidence", ""),
                        "affected_files": rec.get("affected_files", []),
                        "recommendation": rec.get("recommendation", ""),
                        "impact": rec.get("impact", "Moderate"),
                    })
            return recommendations
        except Exception as e:
            logger.warning(f"Failed to extract quality recommendations: {e}")
            return []

    def _extract_refactoring_suggestions(self, project_path: Path) -> list[dict]:
        """Extract refactoring suggestions from RefactoringEngine."""
        try:
            refactoring_result = self.refactoring_engine.analyze(project_path)
            suggestions = []
            for suggestion in refactoring_result.suggestions[:20]:  # Limit to top 20
                suggestions.append({
                    "title": f"Refactoring: {suggestion.get('type', 'Unknown')}",
                    "category": "Refactoring",
                    "priority": suggestion.get("priority", "medium"),
                    "description": suggestion.get("description", ""),
                    "evidence": suggestion.get("evidence", ""),
                    "affected_files": suggestion.get("affected_files", []),
                    "recommendation": suggestion.get("recommendation", ""),
                    "impact": suggestion.get("impact", "Moderate"),
                })
            return suggestions
        except Exception as e:
            logger.warning(f"Failed to extract refactoring suggestions: {e}")
            return []

    def _issue_to_dict(self, issue: dict) -> dict:
        """Convert security issue to dictionary."""
        return {
            "title": f"Security: {issue.get('rule', 'Unknown')}",
            "category": "Security",
            "severity": issue.get("severity", "medium"),
            "priority": issue.get("severity", "medium"),
            "description": issue.get("description", ""),
            "evidence": f"File: {issue.get('file', 'unknown')}, Line: {issue.get('line', 'unknown')}",
            "affected_files": [issue.get("file", "")] if issue.get("file") else [],
            "recommendation": "",
            "estimated_impact": "",
        }

    def _smell_to_dict(self, smell) -> dict:
        """Convert code smell to dictionary."""
        return {
            "title": f"Code Smell: {smell.type}",
            "category": "Code Smell",
            "severity": smell.severity,
            "priority": smell.severity,
            "description": smell.description,
            "evidence": f"File: {smell.file}",
            "affected_files": [smell.file] if smell.file else [],
            "recommendation": "",
            "estimated_impact": "",
        }

    def _build_summary(self, summary, metrics_result: MetricsResult) -> dict[str, Any]:
        """Build summary section."""
        return {
            "overall_score": summary.overall_score,
            "total_issues": summary.total_issues,
            "critical_issues": summary.critical_issues,
            "high_issues": summary.high_issues,
            "medium_issues": summary.medium_issues,
            "low_issues": summary.low_issues,
            "total_files": summary.total_files,
            "total_lines": summary.total_lines,
            "languages": summary.languages,
            "frameworks": summary.frameworks,
            "quality_score": metrics_result.statistics.quality_score,
            "security_score": metrics_result.statistics.security_score,
        }

    def _serialize_issues(self, issues) -> list[dict]:
        """Serialize issues to dictionary format."""
        return [
            {
                "title": issue.title,
                "category": issue.category,
                "severity": issue.severity,
                "priority": issue.priority,
                "description": issue.description,
                "evidence": issue.evidence,
                "affected_files": issue.affected_files,
                "recommendation": issue.recommendation,
                "estimated_impact": issue.estimated_impact,
                "source": issue.source,
            }
            for issue in issues
        ]

    def _collect_strengths(self, report: ReviewReport) -> list[str]:
        """Collect strengths from all review categories."""
        strengths = []
        for category in [
            report.overall_review,
            report.architecture_review,
            report.security_review,
            report.maintainability_review,
            report.performance_review,
            report.dependency_review,
            report.documentation_review,
            report.testing_review,
            report.scalability_review,
            report.best_practices_review,
        ]:
            strengths.extend(category.strengths)
        return strengths

    def _collect_recommendations(self, report: ReviewReport) -> dict[str, list[str]]:
        """Collect recommendations from all review categories."""
        recommendations = {}
        for category in [
            ("Overall", report.overall_review),
            ("Architecture", report.architecture_review),
            ("Security", report.security_review),
            ("Maintainability", report.maintainability_review),
            ("Performance", report.performance_review),
            ("Dependency", report.dependency_review),
            ("Documentation", report.documentation_review),
            ("Testing", report.testing_review),
            ("Scalability", report.scalability_review),
            ("Best Practices", report.best_practices_review),
        ]:
            recommendations[category[0]] = category[1].recommendations
        return recommendations


review_engine = ReviewEngine()
