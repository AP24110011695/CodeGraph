"""Issue prioritizer for code review.

Prioritizes and deduplicates issues from multiple analyzers.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ReviewIssue:
    """A code review issue with priority and severity."""

    title: str
    category: str
    severity: str  # critical, high, medium, low
    priority: str  # critical, high, medium, low
    description: str
    evidence: str
    affected_files: list[str] = field(default_factory=list)
    recommendation: str = ""
    estimated_impact: str = ""
    source: str = ""  # Which analyzer generated this


@dataclass
class PrioritizedIssues:
    """Result of issue prioritization."""

    issues: list[ReviewIssue] = field(default_factory=list)
    deduplication_stats: dict[str, int] = field(default_factory=dict)


class IssuePrioritizer:
    """Prioritizes and deduplicates issues from multiple analyzers."""

    def __init__(self):
        """Initialize the issue prioritizer."""
        # Severity to priority mapping
        self.severity_priority_map = {
            "critical": "critical",
            "high": "high",
            "major": "high",
            "medium": "medium",
            "minor": "low",
            "low": "low",
        }

    def prioritize(
        self,
        security_issues: list[dict] | None = None,
        smell_issues: list[dict] | None = None,
        quality_recommendations: list[dict] | None = None,
        refactoring_suggestions: list[dict] | None = None,
    ) -> PrioritizedIssues:
        """Prioritize and deduplicate issues from multiple analyzers.

        Args:
            security_issues: Issues from SecurityAnalyzer.
            smell_issues: Issues from SmellDetector.
            quality_recommendations: Recommendations from QualityAnalyzer.
            refactoring_suggestions: Suggestions from RefactoringEngine.

        Returns:
            PrioritizedIssues with deduplicated and prioritized issues.
        """
        all_issues: list[ReviewIssue] = []

        # Collect issues from all sources
        if security_issues:
            all_issues.extend(self._process_security_issues(security_issues))

        if smell_issues:
            all_issues.extend(self._process_smell_issues(smell_issues))

        if quality_recommendations:
            all_issues.extend(self._process_quality_recommendations(quality_recommendations))

        if refactoring_suggestions:
            all_issues.extend(self._process_refactoring_suggestions(refactoring_suggestions))

        # Deduplicate issues
        deduplicated = self._deduplicate_issues(all_issues)

        # Sort by priority and severity
        sorted_issues = self._sort_issues(deduplicated)

        # Calculate deduplication stats
        stats = {
            "total_input": len(all_issues),
            "after_deduplication": len(sorted_issues),
            "duplicates_removed": len(all_issues) - len(sorted_issues),
        }

        return PrioritizedIssues(issues=sorted_issues, deduplication_stats=stats)

    def _process_security_issues(self, security_issues: list[dict]) -> list[ReviewIssue]:
        """Process security issues into ReviewIssue format."""
        issues: list[ReviewIssue] = []

        for issue in security_issues:
            severity = issue.get("severity", "medium").lower()
            priority = self.severity_priority_map.get(severity, "medium")

            review_issue = ReviewIssue(
                title=f"Security Issue: {issue.get('rule', 'Unknown')}",
                category="Security",
                severity=severity,
                priority=priority,
                description=issue.get("description", ""),
                evidence=f"Detected in {issue.get('file', 'unknown')} at line {issue.get('line', 'unknown')}",
                affected_files=[issue.get("file", "")] if issue.get("file") else [],
                recommendation=self._get_security_recommendation(issue),
                estimated_impact=self._get_security_impact(severity),
                source="security_analyzer",
            )
            issues.append(review_issue)

        return issues

    def _process_smell_issues(self, smell_issues: list[dict]) -> list[ReviewIssue]:
        """Process code smell issues into ReviewIssue format."""
        issues: list[ReviewIssue] = []

        for issue in smell_issues:
            severity = issue.get("severity", "minor").lower()
            priority = self.severity_priority_map.get(severity, "low")

            review_issue = ReviewIssue(
                title=f"Code Smell: {issue.get('type', 'Unknown')}",
                category="Code Smell",
                severity=severity,
                priority=priority,
                description=issue.get("description", ""),
                evidence=f"Detected in {issue.get('file', 'unknown')}",
                affected_files=[issue.get("file", "")] if issue.get("file") else [],
                recommendation=self._get_smell_recommendation(issue),
                estimated_impact=self._get_smell_impact(severity),
                source="smell_detector",
            )
            issues.append(review_issue)

        return issues

    def _process_quality_recommendations(self, quality_recommendations: list[dict]) -> list[ReviewIssue]:
        """Process quality recommendations into ReviewIssue format."""
        issues: list[ReviewIssue] = []

        for rec in quality_recommendations:
            # Quality recommendations typically have category and priority
            category = rec.get("category", "Quality")
            priority = rec.get("priority", "medium").lower()
            severity = self._priority_to_severity(priority)

            review_issue = ReviewIssue(
                title=f"Quality Issue: {rec.get('title', 'Unknown')}",
                category=category,
                severity=severity,
                priority=priority,
                description=rec.get("description", ""),
                evidence=rec.get("evidence", ""),
                affected_files=rec.get("affected_files", []),
                recommendation=rec.get("recommendation", ""),
                estimated_impact=rec.get("impact", "Moderate"),
                source="quality_analyzer",
            )
            issues.append(review_issue)

        return issues

    def _process_refactoring_suggestions(self, refactoring_suggestions: list[dict]) -> list[ReviewIssue]:
        """Process refactoring suggestions into ReviewIssue format."""
        issues: list[ReviewIssue] = []

        for suggestion in refactoring_suggestions:
            priority = suggestion.get("priority", "medium").lower()
            severity = self._priority_to_severity(priority)

            review_issue = ReviewIssue(
                title=f"Refactoring Opportunity: {suggestion.get('type', 'Unknown')}",
                category="Refactoring",
                severity=severity,
                priority=priority,
                description=suggestion.get("description", ""),
                evidence=suggestion.get("evidence", ""),
                affected_files=suggestion.get("affected_files", []),
                recommendation=suggestion.get("recommendation", ""),
                estimated_impact=suggestion.get("impact", "Moderate"),
                source="refactoring_engine",
            )
            issues.append(review_issue)

        return issues

    def _deduplicate_issues(self, issues: list[ReviewIssue]) -> list[ReviewIssue]:
        """Deduplicate issues based on title and affected files."""
        seen: dict[str, ReviewIssue] = {}

        for issue in issues:
            # Create a key for deduplication
            key = f"{issue.title}:{','.join(sorted(issue.affected_files))}"

            if key not in seen:
                seen[key] = issue
            else:
                # Merge evidence if similar issue exists
                existing = seen[key]
                if issue.evidence and issue.evidence not in existing.evidence:
                    existing.evidence += f"; {issue.evidence}"

        return list(seen.values())

    def _sort_issues(self, issues: list[ReviewIssue]) -> list[ReviewIssue]:
        """Sort issues by priority and severity."""
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        return sorted(
            issues,
            key=lambda x: (
                priority_order.get(x.priority, 99),
                priority_order.get(x.severity, 99),
                x.title,
            ),
        )

    def _priority_to_severity(self, priority: str) -> str:
        """Convert priority to severity."""
        priority_severity_map = {
            "critical": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low",
        }
        return priority_severity_map.get(priority, "medium")

    def _get_security_recommendation(self, issue: dict) -> str:
        """Get recommendation for security issue."""
        rule = issue.get("rule", "").lower()
        if "sql" in rule:
            return "Use parameterized queries or ORM to prevent SQL injection."
        elif "xss" in rule:
            return "Sanitize and escape user input before rendering."
        elif "hardcoded" in rule or "secret" in rule:
            return "Move sensitive data to environment variables or secret management."
        elif "auth" in rule:
            return "Implement proper authentication and authorization mechanisms."
        else:
            return "Review and fix the security vulnerability according to best practices."

    def _get_security_impact(self, severity: str) -> str:
        """Get estimated impact for security issue."""
        impact_map = {
            "critical": "Severe - potential security breach",
            "high": "High - significant security risk",
            "medium": "Moderate - security concern",
            "low": "Low - minor security issue",
        }
        return impact_map.get(severity, "Moderate")

    def _get_smell_recommendation(self, issue: dict) -> str:
        """Get recommendation for code smell."""
        smell_type = issue.get("type", "").lower()
        if "large" in smell_type and "file" in smell_type:
            return "Consider splitting this file into smaller, more focused modules."
        elif "large" in smell_type and "class" in smell_type:
            return "Consider breaking down this class into smaller, single-responsibility classes."
        elif "duplicate" in smell_type:
            return "Remove duplicate code and extract common functionality."
        elif "circular" in smell_type:
            return "Refactor to eliminate circular dependencies."
        elif "unused" in smell_type or "dead" in smell_type:
            return "Remove unused code to improve maintainability."
        else:
            return "Review and refactor to improve code quality."

    def _get_smell_impact(self, severity: str) -> str:
        """Get estimated impact for code smell."""
        impact_map = {
            "critical": "Severe - significantly impacts maintainability",
            "major": "High - impacts code quality and maintainability",
            "medium": "Moderate - code quality concern",
            "minor": "Low - minor code quality issue",
        }
        return impact_map.get(severity, "Moderate")


issue_prioritizer = IssuePrioritizer()
