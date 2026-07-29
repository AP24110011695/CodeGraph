"""Review comment generator for pull request review engine.

Generates review comments based on change impact analysis.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ReviewComment:
    """A review comment for a pull request."""

    title: str
    category: str
    severity: str
    priority: str
    affected_file: str
    affected_function: str | None = None
    evidence: str = ""
    recommendation: str = ""


class ReviewCommentGenerator:
    """Generates review comments based on change impact.

    Uses evidence from multiple sources to generate actionable comments.
    """

    def __init__(self):
        """Initialize the review comment generator."""
        pass

    def generate_comments(
        self,
        change_impacts: list,
        architecture_findings: list[dict] | None = None,
        dependency_findings: list[dict] | None = None,
        security_findings: list[dict] | None = None,
        smell_findings: list[dict] | None = None,
        risk_findings: list[dict] | None = None,
    ) -> list[ReviewComment]:
        """Generate review comments from change impacts.

        Args:
            change_impacts: List of change impacts.
            architecture_findings: Findings from architecture drift engine.
            dependency_findings: Findings from dependency health engine.
            security_findings: Findings from security analyzer.
            smell_findings: Findings from code smell detector.
            risk_findings: Findings from risk engine.

        Returns:
            List of review comments.
        """
        comments: list[ReviewComment] = []

        for impact in change_impacts:
            # Generate comments based on impact scores
            if impact.architecture_impact > 60:
                comments.append(self._generate_architecture_comment(impact))

            if impact.dependency_impact > 60:
                comments.append(self._generate_dependency_comment(impact))

            if impact.security_impact > 60:
                comments.append(self._generate_security_comment(impact))

            if impact.quality_impact > 50:
                comments.append(self._generate_quality_comment(impact))

            if impact.risk_increase > 60:
                comments.append(self._generate_risk_comment(impact))

        # Generate comments from specific findings
        if architecture_findings:
            comments.extend(self._generate_from_architecture_findings(architecture_findings))

        if dependency_findings:
            comments.extend(self._generate_from_dependency_findings(dependency_findings))

        if security_findings:
            comments.extend(self._generate_from_security_findings(security_findings))

        if smell_findings:
            comments.extend(self._generate_from_smell_findings(smell_findings))

        if risk_findings:
            comments.extend(self._generate_from_risk_findings(risk_findings))

        # Merge duplicate comments
        comments = self._merge_duplicate_comments(comments)

        return comments

    def _generate_architecture_comment(self, impact) -> ReviewComment:
        """Generate architecture-related comment."""
        severity = self._impact_to_severity(impact.architecture_impact)
        priority = self._impact_to_priority(impact.architecture_impact)

        return ReviewComment(
            title="Architecture Impact Detected",
            category="Architecture",
            severity=severity,
            priority=priority,
            affected_file=impact.file,
            affected_function=None,
            evidence=f"Architecture impact score: {impact.architecture_impact}",
            recommendation="Review architectural implications of this change.",
        )

    def _generate_dependency_comment(self, impact) -> ReviewComment:
        """Generate dependency-related comment."""
        severity = self._impact_to_severity(impact.dependency_impact)
        priority = self._impact_to_priority(impact.dependency_impact)

        return ReviewComment(
            title="High Dependency Impact",
            category="Dependency",
            severity=severity,
            priority=priority,
            affected_file=impact.file,
            affected_function=None,
            evidence=f"Dependency impact score: {impact.dependency_impact}",
            recommendation="Review dependency changes and potential side effects.",
        )

    def _generate_security_comment(self, impact) -> ReviewComment:
        """Generate security-related comment."""
        severity = self._impact_to_severity(impact.security_impact)
        priority = self._impact_to_priority(impact.security_impact)

        return ReviewComment(
            title="Security Impact Detected",
            category="Security",
            severity=severity,
            priority=priority,
            affected_file=impact.file,
            affected_function=None,
            evidence=f"Security impact score: {impact.security_impact}",
            recommendation="Review security implications of this change.",
        )

    def _generate_quality_comment(self, impact) -> ReviewComment:
        """Generate quality-related comment."""
        severity = self._impact_to_severity(impact.quality_impact)
        priority = self._impact_to_priority(impact.quality_impact)

        return ReviewComment(
            title="Quality Impact Detected",
            category="Quality",
            severity=severity,
            priority=priority,
            affected_file=impact.file,
            affected_function=None,
            evidence=f"Quality impact score: {impact.quality_impact}",
            recommendation="Review code quality implications of this change.",
        )

    def _generate_risk_comment(self, impact) -> ReviewComment:
        """Generate risk-related comment."""
        severity = self._impact_to_severity(impact.risk_increase)
        priority = self._impact_to_priority(impact.risk_increase)

        return ReviewComment(
            title="Risk Increase Detected",
            category="Risk",
            severity=severity,
            priority=priority,
            affected_file=impact.file,
            affected_function=None,
            evidence=f"Risk increase score: {impact.risk_increase}",
            recommendation="Review risk implications of this change.",
        )

    def _generate_from_architecture_findings(self, findings: list[dict]) -> list[ReviewComment]:
        """Generate comments from architecture findings."""
        comments: list[ReviewComment] = []

        for finding in findings:
            severity = finding.get("severity", "Medium")
            priority = self._severity_to_priority(severity)

            comment = ReviewComment(
                title=finding.get("title", "Architecture Issue"),
                category="Architecture",
                severity=severity,
                priority=priority,
                affected_file=finding.get("affected_files", [""])[0] if finding.get("affected_files") else "",
                affected_function=None,
                evidence=finding.get("evidence", ""),
                recommendation=finding.get("recommendation", "Review architectural issue."),
            )
            comments.append(comment)

        return comments

    def _generate_from_dependency_findings(self, findings: list[dict]) -> list[ReviewComment]:
        """Generate comments from dependency findings."""
        comments: list[ReviewComment] = []

        for finding in findings:
            severity = finding.get("severity", "Medium")
            priority = self._severity_to_priority(severity)

            comment = ReviewComment(
                title=finding.get("title", "Dependency Issue"),
                category="Dependency",
                severity=severity,
                priority=priority,
                affected_file=finding.get("affected_files", [""])[0] if finding.get("affected_files") else "",
                affected_function=None,
                evidence=finding.get("evidence", ""),
                recommendation=finding.get("recommendation", "Review dependency issue."),
            )
            comments.append(comment)

        return comments

    def _generate_from_security_findings(self, findings: list[dict]) -> list[ReviewComment]:
        """Generate comments from security findings."""
        comments: list[ReviewComment] = []

        for finding in findings:
            severity = finding.get("severity", "Medium")
            priority = self._severity_to_priority(severity)

            comment = ReviewComment(
                title=f"Security: {finding.get('title', 'Security Issue')}",
                category="Security",
                severity=severity,
                priority=priority,
                affected_file=finding.get("affected_files", [""])[0] if finding.get("affected_files") else "",
                affected_function=None,
                evidence=finding.get("evidence", ""),
                recommendation=finding.get("recommendation", "Review security issue."),
            )
            comments.append(comment)

        return comments

    def _generate_from_smell_findings(self, findings: list[dict]) -> list[ReviewComment]:
        """Generate comments from code smell findings."""
        comments: list[ReviewComment] = []

        for finding in findings:
            severity = finding.get("severity", "Medium")
            priority = self._severity_to_priority(severity)

            comment = ReviewComment(
                title=f"Code Smell: {finding.get('type', finding.get('title', 'Code Smell'))}",
                category="Quality",
                severity=severity,
                priority=priority,
                affected_file=finding.get("file", ""),
                affected_function=finding.get("function", None),
                evidence=finding.get("description", ""),
                recommendation="Review and refactor code smell.",
            )
            comments.append(comment)

        return comments

    def _generate_from_risk_findings(self, findings: list[dict]) -> list[ReviewComment]:
        """Generate comments from risk findings."""
        comments: list[ReviewComment] = []

        for finding in findings:
            level = finding.get("level", finding.get("severity", "Medium"))
            priority = self._severity_to_priority(level)

            comment = ReviewComment(
                title=f"Risk: {finding.get('title', 'Risk Issue')}",
                category="Risk",
                severity=level,
                priority=priority,
                affected_file=finding.get("affected_files", [""])[0] if finding.get("affected_files") else "",
                affected_function=None,
                evidence=finding.get("evidence", ""),
                recommendation=finding.get("recommendation", "Review risk issue."),
            )
            comments.append(comment)

        return comments

    def _impact_to_severity(self, impact: int) -> str:
        """Map impact score to severity."""
        if impact >= 80:
            return "Critical"
        elif impact >= 60:
            return "High"
        elif impact >= 40:
            return "Medium"
        else:
            return "Low"

    def _impact_to_priority(self, impact: int) -> str:
        """Map impact score to priority."""
        if impact >= 80:
            return "P1"
        elif impact >= 60:
            return "P2"
        elif impact >= 40:
            return "P3"
        else:
            return "P4"

    def _severity_to_priority(self, severity: str) -> str:
        """Map severity to priority."""
        severity_lower = severity.lower()
        if severity_lower == "critical":
            return "P1"
        elif severity_lower == "high":
            return "P2"
        elif severity_lower == "medium":
            return "P3"
        else:
            return "P4"

    def _merge_duplicate_comments(self, comments: list[ReviewComment]) -> list[ReviewComment]:
        """Merge duplicate comments based on title and affected file."""
        seen: dict[str, ReviewComment] = {}

        for comment in comments:
            key = f"{comment.title}:{comment.affected_file}"
            if key not in seen:
                seen[key] = comment

        return list(seen.values())


review_comment_generator = ReviewCommentGenerator()
