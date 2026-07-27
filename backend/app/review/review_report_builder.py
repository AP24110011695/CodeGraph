"""Review report builder for code review.

Builds comprehensive review reports from analysis results.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from app.metrics.metrics_engine import MetricsResult
from app.quality.scoring_engine import QualityScores
from app.review.issue_prioritizer import PrioritizedIssues, ReviewIssue

logger = logging.getLogger(__name__)


@dataclass
class ReviewSummary:
    """Summary of the code review."""

    overall_score: int
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    total_files: int
    total_lines: int | None = None
    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)


@dataclass
class ReviewCategory:
    """Review for a specific category."""

    category: str
    score: int
    issues: list[ReviewIssue] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class ReviewReport:
    """Complete code review report."""

    project_name: str
    summary: ReviewSummary
    overall_review: ReviewCategory
    architecture_review: ReviewCategory
    security_review: ReviewCategory
    maintainability_review: ReviewCategory
    performance_review: ReviewCategory
    dependency_review: ReviewCategory
    documentation_review: ReviewCategory
    testing_review: ReviewCategory
    scalability_review: ReviewCategory
    best_practices_review: ReviewCategory


class ReviewReportBuilder:
    """Builds comprehensive review reports from analysis results."""

    def __init__(self):
        """Initialize the review report builder."""
        pass

    def build(
        self,
        project_name: str,
        metrics_result: MetricsResult,
        prioritized_issues: PrioritizedIssues,
    ) -> ReviewReport:
        """Build a comprehensive review report.

        Args:
            project_name: Name of the project.
            metrics_result: Result from MetricsEngine.
            prioritized_issues: Prioritized issues from IssuePrioritizer.

        Returns:
            ReviewReport with all review categories.
        """
        # Build summary
        summary = self._build_summary(metrics_result, prioritized_issues)

        # Categorize issues
        categorized_issues = self._categorize_issues(prioritized_issues.issues)

        # Build category reviews
        overall_review = self._build_overall_review(summary, prioritized_issues)
        architecture_review = self._build_architecture_review(metrics_result, categorized_issues)
        security_review = self._build_security_review(metrics_result, categorized_issues)
        maintainability_review = self._build_maintainability_review(metrics_result, categorized_issues)
        performance_review = self._build_performance_review(metrics_result, categorized_issues)
        dependency_review = self._build_dependency_review(metrics_result, categorized_issues)
        documentation_review = self._build_documentation_review(metrics_result, categorized_issues)
        testing_review = self._build_testing_review(metrics_result, categorized_issues)
        scalability_review = self._build_scalability_review(metrics_result, categorized_issues)
        best_practices_review = self._build_best_practices_review(metrics_result, categorized_issues)

        return ReviewReport(
            project_name=project_name,
            summary=summary,
            overall_review=overall_review,
            architecture_review=architecture_review,
            security_review=security_review,
            maintainability_review=maintainability_review,
            performance_review=performance_review,
            dependency_review=dependency_review,
            documentation_review=documentation_review,
            testing_review=testing_review,
            scalability_review=scalability_review,
            best_practices_review=best_practices_review,
        )

    def _build_summary(self, metrics_result: MetricsResult, prioritized_issues: PrioritizedIssues) -> ReviewSummary:
        """Build review summary."""
        # Count issues by severity
        critical = sum(1 for issue in prioritized_issues.issues if issue.severity == "critical")
        high = sum(1 for issue in prioritized_issues.issues if issue.severity in ["high", "major"])
        medium = sum(1 for issue in prioritized_issues.issues if issue.severity == "medium")
        low = sum(1 for issue in prioritized_issues.issues if issue.severity in ["minor", "low"])

        # Calculate overall score
        overall_score = self._calculate_overall_score(metrics_result, prioritized_issues)

        return ReviewSummary(
            overall_score=overall_score,
            total_issues=len(prioritized_issues.issues),
            critical_issues=critical,
            high_issues=high,
            medium_issues=medium,
            low_issues=low,
            total_files=metrics_result.statistics.total_files,
            total_lines=metrics_result.statistics.total_lines,
            languages=list(metrics_result.statistics.supported_languages.keys()),
            frameworks=metrics_result.statistics.detected_frameworks,
        )

    def _calculate_overall_score(self, metrics_result: MetricsResult, prioritized_issues: PrioritizedIssues) -> int:
        """Calculate overall review score."""
        # Base score from quality metrics
        quality_score = metrics_result.statistics.quality_score or 50
        security_score = metrics_result.statistics.security_score or 50

        # Deduct points for issues
        deduction = 0
        for issue in prioritized_issues.issues:
            if issue.severity == "critical":
                deduction += 10
            elif issue.severity in ["high", "major"]:
                deduction += 5
            elif issue.severity == "medium":
                deduction += 2
            elif issue.severity in ["minor", "low"]:
                deduction += 1

        # Average quality and security, then deduct
        base = (quality_score + security_score) / 2
        final_score = max(0, min(100, base - deduction))

        return round(final_score)

    def _categorize_issues(self, issues: list[ReviewIssue]) -> dict[str, list[ReviewIssue]]:
        """Categorize issues by review category."""
        categories: dict[str, list[ReviewIssue]] = {
            "architecture": [],
            "security": [],
            "maintainability": [],
            "performance": [],
            "dependency": [],
            "documentation": [],
            "testing": [],
            "scalability": [],
            "best_practices": [],
        }

        for issue in issues:
            category = issue.category.lower()

            if "security" in category:
                categories["security"].append(issue)
            elif "smell" in category or "maintain" in category:
                categories["maintainability"].append(issue)
            elif "architecture" in category or "layer" in category:
                categories["architecture"].append(issue)
            elif "dependency" in category or "coupling" in category:
                categories["dependency"].append(issue)
            elif "performance" in category or "complex" in category:
                categories["performance"].append(issue)
            elif "documentation" in category or "comment" in category:
                categories["documentation"].append(issue)
            elif "test" in category:
                categories["testing"].append(issue)
            elif "scalability" in category or "scale" in category:
                categories["scalability"].append(issue)
            else:
                categories["best_practices"].append(issue)

        return categories

    def _build_overall_review(self, summary: ReviewSummary, prioritized_issues: PrioritizedIssues) -> ReviewCategory:
        """Build overall review category."""
        strengths: list[str] = []
        recommendations: list[str] = []

        if summary.overall_score >= 80:
            strengths.append("Overall code quality is good")
        if summary.critical_issues == 0:
            strengths.append("No critical issues found")
        if summary.total_files > 0:
            strengths.append(f"Project has {summary.total_files} files with clear structure")

        if summary.critical_issues > 0:
            recommendations.append(f"Address {summary.critical_issues} critical issues immediately")
        if summary.high_issues > 0:
            recommendations.append(f"Review {summary.high_issues} high-priority issues")
        if summary.overall_score < 60:
            recommendations.append("Overall code quality needs improvement")

        return ReviewCategory(
            category="Overall",
            score=summary.overall_score,
            issues=prioritized_issues.issues[:10],  # Top 10 issues
            strengths=strengths,
            recommendations=recommendations,
        )

    def _build_architecture_review(self, metrics_result: MetricsResult, categorized_issues: dict[str, list[ReviewIssue]]) -> ReviewCategory:
        """Build architecture review category."""
        issues = categorized_issues["architecture"]
        stats = metrics_result.statistics

        # Calculate architecture score
        score = 70  # Base score
        if len(stats.architecture_layers) >= 3:
            score += 15
        if stats.architecture_modules >= 5:
            score += 10
        if stats.dependency_count > 0 and stats.isolated_modules == 0:
            score += 5
        if len(issues) > 0:
            score -= len(issues) * 5

        score = max(0, min(100, score))

        strengths: list[str] = []
        recommendations: list[str] = []

        if len(stats.architecture_layers) >= 2:
            strengths.append(f"Has {len(stats.architecture_layers)} architectural layers")
        if stats.architecture_modules >= 3:
            strengths.append(f"Organized into {stats.architecture_modules} modules")
        if stats.isolated_modules == 0:
            strengths.append("No isolated modules in dependency graph")

        if stats.isolated_modules > 0:
            recommendations.append(f"Review {stats.isolated_modules} isolated modules")
        if len(stats.architecture_layers) < 2:
            recommendations.append("Consider implementing layered architecture")
        if stats.dependency_density and stats.dependency_density > 3:
            recommendations.append("High dependency density - consider decoupling")

        return ReviewCategory(
            category="Architecture",
            score=score,
            issues=issues,
            strengths=strengths,
            recommendations=recommendations,
        )

    def _build_security_review(self, metrics_result: MetricsResult, categorized_issues: dict[str, list[ReviewIssue]]) -> ReviewCategory:
        """Build security review category."""
        issues = categorized_issues["security"]
        score = metrics_result.statistics.security_score or 50

        strengths: list[str] = []
        recommendations: list[str] = []

        if score >= 80:
            strengths.append("Good security posture")
        if len(issues) == 0:
            strengths.append("No security issues detected")

        if len(issues) > 0:
            critical_count = sum(1 for issue in issues if issue.severity == "critical")
            if critical_count > 0:
                recommendations.append(f"Address {critical_count} critical security issues")
            else:
                recommendations.append(f"Review {len(issues)} security issues")

        return ReviewCategory(
            category="Security",
            score=score,
            issues=issues,
            strengths=strengths,
            recommendations=recommendations,
        )

    def _build_maintainability_review(self, metrics_result: MetricsResult, categorized_issues: dict[str, list[ReviewIssue]]) -> ReviewCategory:
        """Build maintainability review category."""
        issues = categorized_issues["maintainability"]
        stats = metrics_result.statistics

        # Calculate maintainability score
        score = 60  # Base score
        if stats.smell_count == 0:
            score += 20
        elif stats.smell_count < 5:
            score += 10
        if stats.average_file_size and stats.average_file_size < 5000:
            score += 10
        if len(stats.supported_languages) <= 2:
            score += 10
        if len(issues) > 0:
            score -= min(20, len(issues) * 2)

        score = max(0, min(100, score))

        strengths: list[str] = []
        recommendations: list[str] = []

        if stats.smell_count == 0:
            strengths.append("No code smells detected")
        elif stats.smell_count < 5:
            strengths.append("Low code smell count")
        if len(stats.supported_languages) <= 2:
            strengths.append("Consistent language usage")

        if stats.smell_count > 10:
            recommendations.append(f"Address {stats.smell_count} code smells")
        if stats.average_file_size and stats.average_file_size > 10000:
            recommendations.append("Some files are large - consider splitting")

        return ReviewCategory(
            category="Maintainability",
            score=score,
            issues=issues,
            strengths=strengths,
            recommendations=recommendations,
        )

    def _build_performance_review(self, metrics_result: MetricsResult, categorized_issues: dict[str, list[ReviewIssue]]) -> ReviewCategory:
        """Build performance review category."""
        issues = categorized_issues["performance"]
        stats = metrics_result.statistics

        # Calculate performance score
        score = 70  # Base score
        if stats.total_files < 100:
            score += 15
        if stats.average_file_size and stats.average_file_size < 10000:
            score += 10
        if len(issues) == 0:
            score += 5

        score = max(0, min(100, score))

        strengths: list[str] = []
        recommendations: list[str] = []

        if stats.total_files < 50:
            strengths.append("Small codebase - good for performance")
        if stats.average_file_size and stats.average_file_size < 5000:
            strengths.append("Reasonable file sizes")

        if stats.total_files > 500:
            recommendations.append("Large codebase - consider performance optimization")
        if len(issues) > 0:
            recommendations.append(f"Review {len(issues)} performance-related issues")

        return ReviewCategory(
            category="Performance",
            score=score,
            issues=issues,
            strengths=strengths,
            recommendations=recommendations,
        )

    def _build_dependency_review(self, metrics_result: MetricsResult, categorized_issues: dict[str, list[ReviewIssue]]) -> ReviewCategory:
        """Build dependency review category."""
        issues = categorized_issues["dependency"]
        stats = metrics_result.statistics

        # Calculate dependency score
        score = 70  # Base score
        if stats.isolated_modules == 0:
            score += 15
        if stats.dependency_density and 0.5 <= stats.dependency_density <= 2:
            score += 10
        if len(issues) == 0:
            score += 5

        score = max(0, min(100, score))

        strengths: list[str] = []
        recommendations: list[str] = []

        if stats.isolated_modules == 0:
            strengths.append("No isolated modules")
        if stats.dependency_density and stats.dependency_density < 2:
            strengths.append("Reasonable dependency density")

        if stats.isolated_modules > 0:
            recommendations.append(f"Review {stats.isolated_modules} isolated modules")
        if stats.dependency_density and stats.dependency_density > 3:
            recommendations.append("High dependency density - consider refactoring")

        return ReviewCategory(
            category="Dependency",
            score=score,
            issues=issues,
            strengths=strengths,
            recommendations=recommendations,
        )

    def _build_documentation_review(self, metrics_result: MetricsResult, categorized_issues: dict[str, list[ReviewIssue]]) -> ReviewCategory:
        """Build documentation review category."""
        issues = categorized_issues["documentation"]
        stats = metrics_result.statistics

        # Calculate documentation score
        score = 50  # Base score
        if stats.quality_breakdown.get("documentation", 0) > 70:
            score += 30
        elif stats.quality_breakdown.get("documentation", 0) > 50:
            score += 15
        if len(issues) == 0:
            score += 10

        score = max(0, min(100, score))

        strengths: list[str] = []
        recommendations: list[str] = []

        if stats.quality_breakdown.get("documentation", 0) > 70:
            strengths.append("Good documentation coverage")
        if len(issues) == 0:
            strengths.append("No documentation issues detected")

        if stats.quality_breakdown.get("documentation", 0) < 50:
            recommendations.append("Improve documentation coverage")
        if len(issues) > 0:
            recommendations.append(f"Address {len(issues)} documentation issues")

        return ReviewCategory(
            category="Documentation",
            score=score,
            issues=issues,
            strengths=strengths,
            recommendations=recommendations,
        )

    def _build_testing_review(self, metrics_result: MetricsResult, categorized_issues: dict[str, list[ReviewIssue]]) -> ReviewCategory:
        """Build testing review category."""
        issues = categorized_issues["testing"]
        stats = metrics_result.statistics

        # Calculate testing score
        score = 50  # Base score
        if stats.quality_breakdown.get("testing", 0) > 70:
            score += 30
        elif stats.quality_breakdown.get("testing", 0) > 50:
            score += 15
        if len(issues) == 0:
            score += 10

        score = max(0, min(100, score))

        strengths: list[str] = []
        recommendations: list[str] = []

        if stats.quality_breakdown.get("testing", 0) > 70:
            strengths.append("Good test coverage")
        if len(issues) == 0:
            strengths.append("No testing issues detected")

        if stats.quality_breakdown.get("testing", 0) < 50:
            recommendations.append("Improve test coverage")
        if len(issues) > 0:
            recommendations.append(f"Address {len(issues)} testing issues")

        return ReviewCategory(
            category="Testing",
            score=score,
            issues=issues,
            strengths=strengths,
            recommendations=recommendations,
        )

    def _build_scalability_review(self, metrics_result: MetricsResult, categorized_issues: dict[str, list[ReviewIssue]]) -> ReviewCategory:
        """Build scalability review category."""
        issues = categorized_issues["scalability"]
        stats = metrics_result.statistics

        # Calculate scalability score
        score = 60  # Base score
        if stats.quality_breakdown.get("scalability", 0) > 70:
            score += 25
        elif stats.quality_breakdown.get("scalability", 0) > 50:
            score += 10
        if len(stats.architecture_layers) >= 3:
            score += 10
        if len(issues) == 0:
            score += 5

        score = max(0, min(100, score))

        strengths: list[str] = []
        recommendations: list[str] = []

        if stats.quality_breakdown.get("scalability", 0) > 70:
            strengths.append("Good scalability characteristics")
        if len(stats.architecture_layers) >= 3:
            strengths.append("Layered architecture supports scalability")

        if stats.quality_breakdown.get("scalability", 0) < 50:
            recommendations.append("Review scalability concerns")
        if len(issues) > 0:
            recommendations.append(f"Address {len(issues)} scalability issues")

        return ReviewCategory(
            category="Scalability",
            score=score,
            issues=issues,
            strengths=strengths,
            recommendations=recommendations,
        )

    def _build_best_practices_review(self, metrics_result: MetricsResult, categorized_issues: dict[str, list[ReviewIssue]]) -> ReviewCategory:
        """Build best practices review category."""
        issues = categorized_issues["best_practices"]
        stats = metrics_result.statistics

        # Calculate best practices score
        score = 70  # Base score
        if stats.quality_score and stats.quality_score > 70:
            score += 20
        if len(issues) == 0:
            score += 10

        score = max(0, min(100, score))

        strengths: list[str] = []
        recommendations: list[str] = []

        if stats.quality_score and stats.quality_score > 70:
            strengths.append("Good overall quality score")
        if len(issues) == 0:
            strengths.append("No best practice issues detected")

        if stats.quality_score and stats.quality_score < 60:
            recommendations.append("Review code quality best practices")
        if len(issues) > 0:
            recommendations.append(f"Address {len(issues)} best practice issues")

        return ReviewCategory(
            category="Best Practices",
            score=score,
            issues=issues,
            strengths=strengths,
            recommendations=recommendations,
        )


review_report_builder = ReviewReportBuilder()
