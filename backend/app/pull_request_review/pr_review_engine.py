"""Pull request review engine for CodeGraph.

Orchestrates pull request review using all existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.architecture_drift.architecture_drift_engine import ArchitectureDriftEngine, architecture_drift_engine
from app.dependency_health.dependency_health_engine import DependencyHealthEngine, dependency_health_engine
from app.indexing.index_manager import IndexManager
from app.pull_request_review.change_analyzer import ChangeAnalyzer, ChangeImpact, change_analyzer
from app.pull_request_review.review_comment_generator import ReviewComment, ReviewCommentGenerator, review_comment_generator
from app.risk.risk_engine import RiskEngine, risk_engine
from app.security.security_analyzer import security_analyzer
from app.services.scanner_service import ScanResult, scanner_service
from app.smells.smell_detector import smell_detector

logger = logging.getLogger(__name__)


@dataclass
class PRReviewRequest:
    """Request for pull request review."""

    changed_files: list[str]
    diff: str | None = None
    modified_functions: list[str] = field(default_factory=list)
    added_files: list[str] = field(default_factory=list)
    deleted_files: list[str] = field(default_factory=list)


@dataclass
class PRReviewResult:
    """Complete result from pull request review."""

    overall_score: int
    approval: str
    summary: dict[str, int] = field(default_factory=dict)
    comments: list[dict] = field(default_factory=list)
    suggested_improvements: list[str] = field(default_factory=list)
    risk_assessment: dict[str, Any] = field(default_factory=dict)


class PRReviewEngine:
    """Performs comprehensive pull request review.

    Reuses all existing CodeGraph analysis modules:
    - Repository Scanner
    - Architecture Drift Engine
    - Dependency Health Engine
    - Security Analyzer
    - Code Smell Detector
    - Risk Engine
    """

    def __init__(
        self,
        index_manager: IndexManager | None = None,
        change_analyzer: ChangeAnalyzer | None = None,
        review_comment_generator: ReviewCommentGenerator | None = None,
    ):
        """Initialize the PR review engine.

        Args:
            index_manager: Optional IndexManager for accessing indexed repositories.
            change_analyzer: Optional ChangeAnalyzer instance.
            review_comment_generator: Optional ReviewCommentGenerator instance.
        """
        self.index_manager = index_manager
        self.change_analyzer = change_analyzer or ChangeAnalyzer()
        self.review_comment_generator = review_comment_generator or ReviewCommentGenerator()

        # Individual analyzers
        self.scanner = scanner_service
        self.architecture_drift_engine = architecture_drift_engine
        self.dependency_health_engine = dependency_health_engine
        self.security_analyzer = security_analyzer
        self.smell_detector = smell_detector
        self.risk_engine = risk_engine

    def review(
        self,
        project_path: Path,
        request: PRReviewRequest,
        upload_id: str | None = None,
    ) -> PRReviewResult:
        """Perform comprehensive pull request review for a repository.

        Args:
            project_path: Absolute path to the project directory.
            request: PRReviewRequest with PR details.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            PRReviewResult with comprehensive PR review.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Starting PR review for project: {project_path}")
        logger.info(f"Changed files: {len(request.changed_files)}")

        # Step 1: Scan the repository
        logger.info("Scanning repository")
        scan_result = self.scanner.scan(project_path)

        if scan_result.total_files == 0:
            logger.warning("Repository is empty, returning minimal result")
            return self._build_empty_result(request)

        # Step 2: Analyze architecture drift
        logger.info("Analyzing architecture drift")
        architecture_result = self.architecture_drift_engine.analyze(project_path, upload_id)

        # Step 3: Analyze dependency health
        logger.info("Analyzing dependency health")
        dependency_result = self.dependency_health_engine.analyze(project_path, upload_id)

        # Step 4: Analyze security
        logger.info("Analyzing security")
        security_result = self.security_analyzer.analyze(project_path, scan_result)

        # Step 5: Detect code smells
        logger.info("Detecting code smells")
        smell_result = self.smell_detector.detect(project_path, scan_result)

        # Step 6: Analyze risk
        logger.info("Analyzing risk")
        risk_result = self.risk_engine.analyze(project_path, upload_id)

        # Step 7: Convert results to dict format
        architecture_findings = architecture_result.findings
        dependency_findings = dependency_result.findings
        security_findings = self._security_to_list(security_result)
        smell_findings = self._smell_to_list(smell_result)
        risk_findings = risk_result.risks

        # Step 8: Analyze change impacts
        logger.info("Analyzing change impacts")
        change_impacts = self.change_analyzer.analyze_changes(
            changed_files=request.changed_files,
            project_path=project_path,
            architecture_result=None,  # Pass None, use findings instead
            dependency_result=None,  # Pass None, use findings instead
            security_findings=security_findings,
            smell_findings=smell_findings,
            risk_findings=risk_findings,
        )

        # Step 9: Generate review comments
        logger.info("Generating review comments")
        comments = self.review_comment_generator.generate_comments(
            change_impacts=change_impacts,
            architecture_findings=architecture_findings,
            dependency_findings=dependency_findings,
            security_findings=security_findings,
            smell_findings=smell_findings,
            risk_findings=risk_findings,
        )

        # Step 10: Calculate overall score
        logger.info("Calculating overall score")
        overall_score = self._calculate_overall_score(change_impacts, comments)

        # Step 11: Determine approval recommendation
        logger.info("Determining approval recommendation")
        approval = self._determine_approval(overall_score, comments)

        # Step 12: Build summary
        logger.info("Building summary")
        summary = self._build_summary(comments, change_impacts)

        # Step 13: Generate suggested improvements
        logger.info("Generating suggested improvements")
        suggested_improvements = self._generate_suggested_improvements(comments)

        # Step 14: Generate risk assessment
        logger.info("Generating risk assessment")
        risk_assessment = self._generate_risk_assessment(change_impacts, risk_findings)

        # Step 15: Serialize comments
        serialized_comments = self._serialize_comments(comments)

        return PRReviewResult(
            overall_score=overall_score,
            approval=approval,
            summary=summary,
            comments=serialized_comments,
            suggested_improvements=suggested_improvements,
            risk_assessment=risk_assessment,
        )

    def _build_empty_result(self, request: PRReviewRequest) -> PRReviewResult:
        """Build a minimal result for empty repositories."""
        return PRReviewResult(
            overall_score=100,
            approval="APPROVED",
            summary={
                "total_comments": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
            comments=[],
            suggested_improvements=[],
            risk_assessment={"overall_risk": "Low"},
        )

    def _security_to_list(self, security_result) -> list[dict]:
        """Convert security result to list of dictionaries."""
        if hasattr(security_result, 'issues'):
            return [
                {
                    "title": issue.title if hasattr(issue, 'title') else "Security Issue",
                    "severity": issue.severity if hasattr(issue, 'severity') else "Medium",
                    "evidence": issue.evidence if hasattr(issue, 'evidence') else "",
                    "affected_files": issue.affected_files if hasattr(issue, 'affected_files') else [],
                }
                for issue in security_result.issues
            ]
        return []

    def _smell_to_list(self, smell_result) -> list[dict]:
        """Convert smell result to list of dictionaries."""
        if hasattr(smell_result, 'smells'):
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
        return []

    def _calculate_overall_score(self, change_impacts: list[ChangeImpact], comments: list[ReviewComment]) -> int:
        """Calculate overall review score.

        Args:
            change_impacts: List of change impacts.
            comments: List of review comments.

        Returns:
            Overall score (0-100).
        """
        if not change_impacts:
            return 100

        # Calculate average impact scores
        avg_architecture = sum(imp.architecture_impact for imp in change_impacts) / len(change_impacts)
        avg_dependency = sum(imp.dependency_impact for imp in change_impacts) / len(change_impacts)
        avg_security = sum(imp.security_impact for imp in change_impacts) / len(change_impacts)
        avg_quality = sum(imp.quality_impact for imp in change_impacts) / len(change_impacts)
        avg_risk = sum(imp.risk_increase for imp in change_impacts) / len(change_impacts)

        # Calculate weighted score
        weights = {
            "architecture": 0.2,
            "dependency": 0.2,
            "security": 0.25,
            "quality": 0.2,
            "risk": 0.15,
        }

        weighted_impact = (
            avg_architecture * weights["architecture"] +
            avg_dependency * weights["dependency"] +
            avg_security * weights["security"] +
            avg_quality * weights["quality"] +
            avg_risk * weights["risk"]
        )

        # Invert impact to get score (higher impact = lower score)
        score = 100 - weighted_impact

        # Penalize for critical comments
        critical_count = sum(1 for c in comments if c.severity == "Critical")
        score -= critical_count * 10

        return max(0, min(100, int(score)))

    def _determine_approval(self, overall_score: int, comments: list[ReviewComment]) -> str:
        """Determine approval recommendation.

        Args:
            overall_score: Overall review score.
            comments: List of review comments.

        Returns:
            Approval recommendation.
        """
        critical_count = sum(1 for c in comments if c.severity == "Critical")
        high_count = sum(1 for c in comments if c.severity == "High")

        if critical_count > 0:
            return "CHANGES_REQUESTED"
        elif high_count > 2:
            return "CHANGES_REQUESTED"
        elif overall_score >= 90:
            return "APPROVED"
        elif overall_score >= 70:
            return "APPROVED_WITH_SUGGESTIONS"
        else:
            return "CHANGES_REQUESTED"

    def _build_summary(self, comments: list[ReviewComment], change_impacts: list[ChangeImpact]) -> dict[str, int]:
        """Build review summary."""
        summary = {
            "total_comments": len(comments),
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "files_changed": len(change_impacts),
        }

        for comment in comments:
            severity = comment.severity.lower()
            if severity in summary:
                summary[severity] += 1

        return summary

    def _generate_suggested_improvements(self, comments: list[ReviewComment]) -> list[str]:
        """Generate suggested improvements from comments."""
        improvements = []

        for comment in comments:
            if comment.recommendation and comment.recommendation not in improvements:
                improvements.append(comment.recommendation)

        return improvements[:10]  # Limit to top 10

    def _generate_risk_assessment(self, change_impacts: list[ChangeImpact], risk_findings: list[dict]) -> dict[str, Any]:
        """Generate risk assessment."""
        if not change_impacts:
            return {"overall_risk": "Low"}

        avg_risk = sum(imp.risk_increase for imp in change_impacts) / len(change_impacts)

        if avg_risk >= 70:
            overall_risk = "High"
        elif avg_risk >= 40:
            overall_risk = "Medium"
        else:
            overall_risk = "Low"

        return {
            "overall_risk": overall_risk,
            "average_risk_score": round(avg_risk),
            "risk_findings_count": len(risk_findings),
        }

    def _serialize_comments(self, comments: list[ReviewComment]) -> list[dict]:
        """Serialize comments to dictionary format."""
        return [
            {
                "title": comment.title,
                "category": comment.category,
                "severity": comment.severity,
                "priority": comment.priority,
                "affected_file": comment.affected_file,
                "affected_function": comment.affected_function,
                "evidence": comment.evidence,
                "recommendation": comment.recommendation,
            }
            for comment in comments
        ]


pr_review_engine = PRReviewEngine()
