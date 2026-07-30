"""Issue mapper for Jira integration engine.

Maps Jira issues to repository intelligence and correlates engineering metrics.
"""

import logging
from typing import Any

from app.jira.jira_models import JiraIssue, JiraEpic

logger = logging.getLogger(__name__)


class IssueMapper:
    """Maps Jira issues to repository intelligence.

    Correlates Jira metadata with repository analysis results.
    """

    def __init__(self):
        """Initialize the issue mapper."""
        pass

    def map_issues_to_repository(
        self,
        issues: list[JiraIssue],
        repository_name: str,
        repository_url: str | None = None,
    ) -> dict[str, Any]:
        """Map Jira issues to a repository.

        Args:
            issues: List of Jira issues.
            repository_name: Repository name.
            repository_url: Optional repository URL.

        Returns:
            Dictionary with mapping results.
        """
        linked_issues = []
        unlinked_issues = []

        for issue in issues:
            # Check if issue has repository links
            if self._is_linked_to_repository(issue, repository_name, repository_url):
                linked_issues.append(issue)
            else:
                unlinked_issues.append(issue)

        return {
            "repository": repository_name,
            "linked_issues": len(linked_issues),
            "unlinked_issues": len(unlinked_issues),
            "linked_issue_keys": [issue.key for issue in linked_issues],
            "unlinked_issue_keys": [issue.key for issue in unlinked_issues],
            "link_rate": len(linked_issues) / len(issues) if issues else 0,
        }

    def _is_linked_to_repository(
        self,
        issue: JiraIssue,
        repository_name: str,
        repository_url: str | None = None,
    ) -> bool:
        """Check if issue is linked to repository.

        Args:
            issue: Jira issue.
            repository_name: Repository name.
            repository_url: Optional repository URL.

        Returns:
            True if issue is linked to repository.
        """
        # Check repository links
        if issue.repository_links:
            for link in issue.repository_links:
                if repository_name in link or (repository_url and repository_url in link):
                    return True

        # Check labels for repository references
        if issue.labels:
            for label in issue.labels:
                if repository_name.lower() in label.lower():
                    return True

        # Check components for repository references
        if issue.components:
            for component in issue.components:
                if repository_name.lower() in component.lower():
                    return True

        return False

    def calculate_engineering_risk(
        self,
        issues: list[JiraIssue],
    ) -> dict[str, Any]:
        """Calculate engineering risk from Jira issues.

        Args:
            issues: List of Jira issues.

        Returns:
            Dictionary with risk assessment.
        """
        if not issues:
            return {
                "risk_level": "unknown",
                "risk_score": 0,
                "critical_issues": 0,
                "high_priority_issues": 0,
                "open_bugs": 0,
                "stale_issues": 0,
            }

        critical_issues = [issue for issue in issues if issue.priority == "Critical"]
        high_priority_issues = [issue for issue in issues if issue.priority == "High"]
        open_bugs = [issue for issue in issues if issue.issue_type == "Bug" and issue.status != "Closed"]
        
        # Calculate stale issues (open for more than 30 days)
        from datetime import datetime, timedelta, timezone
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        stale_issues = [
            issue for issue in issues
            if issue.status != "Closed" and
            datetime.fromisoformat(issue.created_at.replace("Z", "+00:00")) < thirty_days_ago
        ]

        # Calculate risk score
        risk_score = 0
        risk_score += len(critical_issues) * 10
        risk_score += len(high_priority_issues) * 5
        risk_score += len(open_bugs) * 7
        risk_score += len(stale_issues) * 3

        # Normalize to 0-100
        risk_score = min(100, risk_score)

        # Determine risk level
        if risk_score >= 70:
            risk_level = "critical"
        elif risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "medium"
        elif risk_score >= 10:
            risk_level = "low"
        else:
            risk_level = "minimal"

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "critical_issues": len(critical_issues),
            "high_priority_issues": len(high_priority_issues),
            "open_bugs": len(open_bugs),
            "stale_issues": len(stale_issues),
        }

    def generate_priority_distribution(
        self,
        issues: list[JiraIssue],
    ) -> dict[str, int]:
        """Generate priority distribution from issues.

        Args:
            issues: List of Jira issues.

        Returns:
            Dictionary with priority counts.
        """
        distribution = {
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0,
        }

        for issue in issues:
            if issue.priority in distribution:
                distribution[issue.priority] += 1

        return distribution

    def generate_status_distribution(
        self,
        issues: list[JiraIssue],
    ) -> dict[str, int]:
        """Generate status distribution from issues.

        Args:
            issues: List of Jira issues.

        Returns:
            Dictionary with status counts.
        """
        distribution = {}

        for issue in issues:
            if issue.status not in distribution:
                distribution[issue.status] = 0
            distribution[issue.status] += 1

        return distribution

    def generate_issue_type_distribution(
        self,
        issues: list[JiraIssue],
    ) -> dict[str, int]:
        """Generate issue type distribution from issues.

        Args:
            issues: List of Jira issues.

        Returns:
            Dictionary with issue type counts.
        """
        distribution = {}

        for issue in issues:
            if issue.issue_type not in distribution:
                distribution[issue.issue_type] = 0
            distribution[issue.issue_type] += 1

        return distribution

    def correlate_with_repository_health(
        self,
        jira_issues: list[JiraIssue],
        repository_health: int,
    ) -> dict[str, Any]:
        """Correlate Jira issues with repository health.

        Args:
            jira_issues: List of Jira issues.
            repository_health: Repository health score (0-100).

        Returns:
            Dictionary with correlation analysis.
        """
        open_issues = [issue for issue in jira_issues if issue.status != "Closed"]
        open_bugs = [issue for issue in jira_issues if issue.issue_type == "Bug" and issue.status != "Closed"]

        # Calculate correlation
        bug_ratio = len(open_bugs) / len(open_issues) if open_issues else 0
        health_impact = "low"

        if repository_health < 50 and bug_ratio > 0.3:
            health_impact = "high"
        elif repository_health < 70 and bug_ratio > 0.2:
            health_impact = "medium"

        return {
            "repository_health": repository_health,
            "open_issues": len(open_issues),
            "open_bugs": len(open_bugs),
            "bug_ratio": bug_ratio,
            "health_impact": health_impact,
            "recommendation": self._generate_health_recommendation(
                repository_health,
                bug_ratio,
                health_impact,
            ),
        }

    def _generate_health_recommendation(
        self,
        repository_health: int,
        bug_ratio: float,
        health_impact: str,
    ) -> str:
        """Generate health recommendation.

        Args:
            repository_health: Repository health score.
            bug_ratio: Ratio of open bugs to open issues.
            health_impact: Health impact level.

        Returns:
            Recommendation string.
        """
        if health_impact == "high":
            return "High bug ratio combined with low repository health indicates quality issues. Focus on resolving critical bugs."
        elif health_impact == "medium":
            return "Moderate bug ratio suggests quality concerns. Consider prioritizing bug fixes."
        elif repository_health < 70:
            return "Repository health below target. Review Jira issues for quality improvements."
        else:
            return "Repository health is good. Continue monitoring Jira issues for trends."

    def generate_epic_summary(
        self,
        epics: list[JiraEpic],
    ) -> dict[str, Any]:
        """Generate epic summary.

        Args:
            epics: List of Jira epics.

        Returns:
            Dictionary with epic summary.
        """
        if not epics:
            return {
                "total_epics": 0,
                "open_epics": 0,
                "completed_epics": 0,
                "total_issues": 0,
                "completed_issues": 0,
                "completion_rate": 0,
            }

        open_epics = [epic for epic in epics if epic.status != "Done"]
        completed_epics = [epic for epic in epics if epic.status == "Done"]
        
        total_issues = sum(epic.issue_count for epic in epics)
        completed_issues = sum(epic.completed_issues for epic in epics)

        completion_rate = (completed_issues / total_issues * 100) if total_issues > 0 else 0

        return {
            "total_epics": len(epics),
            "open_epics": len(open_epics),
            "completed_epics": len(completed_epics),
            "total_issues": total_issues,
            "completed_issues": completed_issues,
            "completion_rate": completion_rate,
        }


issue_mapper = IssueMapper()
