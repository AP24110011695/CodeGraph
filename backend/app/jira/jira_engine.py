"""Jira engine for Jira integration engine.

Orchestrates Jira integration operations using all existing modules.
"""

import logging
from typing import Any

from app.jira.jira_client import JiraClient, jira_client
from app.jira.issue_mapper import IssueMapper, issue_mapper
from app.jira.jira_models import JiraProject, JiraIssue, JiraEpic
from app.workspace.repository_registry import RepositoryRegistry, repository_registry

logger = logging.getLogger(__name__)


class JiraEngine:
    """Performs comprehensive Jira integration operations.

    Reuses all existing CodeGraph modules:
    - Workspace Engine (via repository_registry)
    - Repository Search (via repository registry)
    - Risk Engine (via issue_mapper risk calculation)
    """

    def __init__(
        self,
        jira_client: JiraClient | None = None,
        issue_mapper: IssueMapper | None = None,
        repository_registry: RepositoryRegistry | None = None,
    ):
        """Initialize the Jira engine.

        Args:
            jira_client: Optional JiraClient instance.
            issue_mapper: Optional IssueMapper instance.
            repository_registry: Optional RepositoryRegistry instance.
        """
        self.jira_client = jira_client or JiraClient()
        self.issue_mapper = issue_mapper or IssueMapper()
        self.repository_registry = repository_registry or RepositoryRegistry()

    def connect_project(
        self,
        project_key: str,
        repository_id: str | None = None,
        workspace_id: str | None = None,
    ) -> dict[str, Any]:
        """Connect a Jira project and analyze its issues.

        Args:
            project_key: Jira project key.
            repository_id: Optional repository ID to associate with.
            workspace_id: Optional workspace ID to associate with.

        Returns:
            Dictionary with Jira analysis results.
        """
        # Get project information
        project = self.jira_client.get_project(project_key)

        if not project:
            return {
                "project": None,
                "error": f"Project not found: {project_key}",
            }

        # Get all issues
        issues = self.jira_client.get_issues(project_key)

        # Get epics
        epics = self.jira_client.get_epics(project_key)

        # Generate summary
        summary = self._generate_issue_summary(issues)

        # Calculate engineering risk
        risk = self.issue_mapper.calculate_engineering_risk(issues)

        # Generate distributions
        priority_distribution = self.issue_mapper.generate_priority_distribution(issues)
        status_distribution = self.issue_mapper.generate_status_distribution(issues)
        issue_type_distribution = self.issue_mapper.generate_issue_type_distribution(issues)

        # Generate epic summary
        epic_summary = self.issue_mapper.generate_epic_summary(epics)

        # Map to repository if provided
        repository_mapping = None
        if repository_id:
            repo_info = self.repository_registry.get_repository(repository_id)
            if repo_info:
                repository_mapping = self.issue_mapper.map_issues_to_repository(
                    issues,
                    repo_info.repository_name,
                    f"https://github.com/{repo_info.repository_name}",
                )

        # Correlate with repository health if repository provided
        health_correlation = None
        if repository_id:
            repo_info = self.repository_registry.get_repository(repository_id)
            if repo_info:
                health_correlation = self.issue_mapper.correlate_with_repository_health(
                    issues,
                    repo_info.health_score,
                )

        return {
            "project": project.to_dict(),
            "summary": summary,
            "risk": risk,
            "priority_distribution": priority_distribution,
            "status_distribution": status_distribution,
            "issue_type_distribution": issue_type_distribution,
            "epic_summary": epic_summary,
            "repository_mapping": repository_mapping,
            "health_correlation": health_correlation,
            "recommendations": self._generate_recommendations(
                summary,
                risk,
                repository_mapping,
                health_correlation,
            ),
        }

    def get_project(
        self,
        project_key: str,
    ) -> dict[str, Any] | None:
        """Get Jira project information.

        Args:
            project_key: Jira project key.

        Returns:
            Project information or None if not found.
        """
        project = self.jira_client.get_project(project_key)

        if not project:
            return None

        issues = self.jira_client.get_issues(project_key)
        epics = self.jira_client.get_epics(project_key)

        summary = self._generate_issue_summary(issues)
        risk = self.issue_mapper.calculate_engineering_risk(issues)

        return {
            "project": project.to_dict(),
            "summary": summary,
            "risk": risk,
        }

    def get_repository_issues(
        self,
        repository_id: str,
    ) -> dict[str, Any] | None:
        """Get Jira issues for a repository.

        Args:
            repository_id: Repository ID.

        Returns:
            Jira issues for repository or None if not found.
        """
        repo_info = self.repository_registry.get_repository(repository_id)

        if not repo_info:
            return None

        # Extract project key from repository name or use default
        # For this implementation, we'll use a default project
        project_key = "CG"  # Default project key

        issues = self.jira_client.get_issues(project_key)

        # Map issues to repository
        repository_mapping = self.issue_mapper.map_issues_to_repository(
            issues,
            repo_info.repository_name,
            f"https://github.com/{repo_info.repository_name}",
        )

        # Get linked issues
        linked_issue_keys = repository_mapping.get("linked_issue_keys", [])
        linked_issues = [issue for issue in issues if issue.key in linked_issue_keys]

        # Generate summary for linked issues
        summary = self._generate_issue_summary(linked_issues)
        risk = self.issue_mapper.calculate_engineering_risk(linked_issues)

        return {
            "repository": repo_info.repository_name,
            "repository_id": repository_id,
            "project_key": project_key,
            "linked_issues": len(linked_issues),
            "summary": summary,
            "risk": risk,
            "issues": [issue.to_dict() for issue in linked_issues],
            "repository_mapping": repository_mapping,
        }

    def search_issues(
        self,
        project_key: str,
        query: str,
    ) -> dict[str, Any]:
        """Search issues in Jira project.

        Args:
            project_key: Jira project key.
            query: Search query.

        Returns:
            Search results.
        """
        issues = self.jira_client.search_issues(project_key, query)

        return {
            "project_key": project_key,
            "query": query,
            "total_results": len(issues),
            "issues": [issue.to_dict() for issue in issues],
        }

    def _generate_issue_summary(self, issues: list[JiraIssue]) -> dict[str, Any]:
        """Generate issue summary.

        Args:
            issues: List of Jira issues.

        Returns:
            Issue summary dictionary.
        """
        if not issues:
            return {
                "total": 0,
                "open": 0,
                "closed": 0,
                "critical": 0,
                "high": 0,
                "bugs": 0,
                "stories": 0,
                "tasks": 0,
            }

        open_issues = [issue for issue in issues if issue.status != "Closed"]
        closed_issues = [issue for issue in issues if issue.status == "Closed"]
        critical_issues = [issue for issue in issues if issue.priority == "Critical"]
        high_issues = [issue for issue in issues if issue.priority == "High"]
        bugs = [issue for issue in issues if issue.issue_type == "Bug"]
        stories = [issue for issue in issues if issue.issue_type == "Story"]
        tasks = [issue for issue in issues if issue.issue_type == "Task"]

        return {
            "total": len(issues),
            "open": len(open_issues),
            "closed": len(closed_issues),
            "critical": len(critical_issues),
            "high": len(high_issues),
            "bugs": len(bugs),
            "stories": len(stories),
            "tasks": len(tasks),
        }

    def _generate_recommendations(
        self,
        summary: dict[str, Any],
        risk: dict[str, Any],
        repository_mapping: dict[str, Any] | None,
        health_correlation: dict[str, Any] | None,
    ) -> list[str]:
        """Generate recommendations based on analysis.

        Args:
            summary: Issue summary.
            risk: Risk assessment.
            repository_mapping: Repository mapping results.
            health_correlation: Health correlation results.

        Returns:
            List of recommendation strings.
        """
        recommendations = []

        # Risk-based recommendations
        if risk["risk_level"] == "critical":
            recommendations.append("Critical risk level detected. Address critical and high-priority issues immediately.")
        elif risk["risk_level"] == "high":
            recommendations.append("High risk level detected. Prioritize bug fixes and critical issues.")

        # Bug-based recommendations
        if summary["bugs"] > 5:
            recommendations.append(f"High bug count ({summary['bugs']}). Consider dedicated bug-sprint.")

        # Open issues recommendations
        if summary["open"] > 50:
            recommendations.append("Large backlog of open issues. Consider issue triage and cleanup.")

        # Repository mapping recommendations
        if repository_mapping:
            link_rate = repository_mapping.get("link_rate", 0)
            if link_rate < 0.5:
                recommendations.append("Low repository link rate. Improve issue-to-repository traceability.")

        # Health correlation recommendations
        if health_correlation:
            if health_correlation.get("health_impact") == "high":
                recommendations.append(health_correlation.get("recommendation", ""))

        # Priority distribution recommendations
        if summary["critical"] > 3:
            recommendations.append("Multiple critical issues. Focus on resolution planning.")

        return recommendations


jira_engine = JiraEngine()
