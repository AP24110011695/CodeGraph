"""Jira client for Jira integration engine.

Handles Jira API interactions for project and issue metadata.
"""

import logging
from typing import Any

from app.jira.jira_models import JiraProject, JiraIssue, JiraEpic

logger = logging.getLogger(__name__)


class JiraClient:
    """Client for Jira API interactions.

    Note: This is a mock implementation for demonstration.
    In production, this would use the Jira REST API.
    """

    def __init__(self, base_url: str | None = None, token: str | None = None):
        """Initialize the Jira client.

        Args:
            base_url: Optional Jira instance base URL.
            token: Optional Jira API token.
        """
        self.base_url = base_url
        self.token = token

    def get_project(self, project_key: str) -> JiraProject | None:
        """Get project information from Jira.

        Args:
            project_key: Jira project key (e.g., "CG", "PROJ").

        Returns:
            JiraProject or None if not found.
        """
        # Mock implementation - in production, this would call Jira API
        # GET /rest/api/2/project/{key}
        logger.info(f"Getting Jira project: {project_key}")
        
        # Return None for specific test cases
        if project_key == "NONEXISTENT":
            return None
        
        return JiraProject(
            key=project_key,
            name=f"Project {project_key}",
            description=f"Mock project {project_key} for demonstration",
            project_type="Software",
            lead="project-lead",
            url=f"https://jira.example.com/browse/{project_key}",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-07-01T00:00:00Z",
            issue_count=124,
            open_issues=38,
            closed_issues=86,
        )

    def get_issues(
        self,
        project_key: str,
        status: str | None = None,
        issue_type: str | None = None,
    ) -> list[JiraIssue]:
        """Get issues from Jira project.

        Args:
            project_key: Jira project key.
            status: Optional status filter.
            issue_type: Optional issue type filter.

        Returns:
            List of JiraIssue objects.
        """
        # Mock implementation - in production, this would call Jira API
        # GET /rest/api/2/search?jql=project={key}
        logger.info(f"Getting issues for project: {project_key}")
        
        mock_issues = [
            JiraIssue(
                key=f"{project_key}-1",
                summary="Fix authentication bug",
                description="Authentication fails for expired tokens",
                status="Open",
                priority="Critical",
                issue_type="Bug",
                assignee="developer1",
                reporter="tester1",
                created_at="2024-06-01T00:00:00Z",
                updated_at="2024-07-01T00:00:00Z",
                resolved_at=None,
                labels=["authentication", "security"],
                components=["auth-service"],
                epic_key=f"{project_key}-100",
                epic_name="Authentication overhaul",
                story_points=5,
                repository_links=["https://github.com/example/repo/pull/123", "https://github.com/example/repo"],
                project_key=project_key,
            ),
            JiraIssue(
                key=f"{project_key}-2",
                summary="Add user profile feature",
                description="Implement user profile management",
                status="In Progress",
                priority="High",
                issue_type="Story",
                assignee="developer2",
                reporter="product-manager",
                created_at="2024-06-15T00:00:00Z",
                updated_at="2024-07-01T00:00:00Z",
                resolved_at=None,
                labels=["feature", "user-management"],
                components=["user-service"],
                epic_key=f"{project_key}-101",
                epic_name="User management",
                story_points=8,
                repository_links=["https://github.com/example/repo/branch/feature/user-profile", "https://github.com/example/repo"],
                project_key=project_key,
            ),
            JiraIssue(
                key=f"{project_key}-3",
                summary="Update documentation",
                description="Update API documentation",
                status="Closed",
                priority="Low",
                issue_type="Task",
                assignee="developer1",
                reporter="tech-lead",
                created_at="2024-05-01T00:00:00Z",
                updated_at="2024-06-01T00:00:00Z",
                resolved_at="2024-06-01T00:00:00Z",
                labels=["documentation"],
                components=["docs"],
                epic_key=None,
                epic_name=None,
                story_points=2,
                repository_links=[],
                project_key=project_key,
            ),
            JiraIssue(
                key=f"{project_key}-4",
                summary="Performance optimization",
                description="Optimize database queries",
                status="Open",
                priority="High",
                issue_type="Story",
                assignee="developer3",
                reporter="tech-lead",
                created_at="2024-06-20T00:00:00Z",
                updated_at="2024-07-01T00:00:00Z",
                resolved_at=None,
                labels=["performance", "database"],
                components=["database"],
                epic_key=f"{project_key}-102",
                epic_name="Performance improvements",
                story_points=13,
                repository_links=["https://github.com/example/repo/pull/456", "https://github.com/example/repo"],
                project_key=project_key,
            ),
            JiraIssue(
                key=f"{project_key}-5",
                summary="Security vulnerability fix",
                description="Fix XSS vulnerability in forms",
                status="Open",
                priority="Critical",
                issue_type="Bug",
                assignee="developer1",
                reporter="security-team",
                created_at="2024-06-25T00:00:00Z",
                updated_at="2024-07-01T00:00:00Z",
                resolved_at=None,
                labels=["security", "xss"],
                components=["web-ui"],
                epic_key=f"{project_key}-103",
                epic_name="Security fixes",
                story_points=8,
                repository_links=["https://github.com/example/repo/pull/789", "https://github.com/example/repo"],
                project_key=project_key,
            ),
        ]

        # Apply filters if provided
        if status:
            mock_issues = [issue for issue in mock_issues if issue.status == status]
        if issue_type:
            mock_issues = [issue for issue in mock_issues if issue.issue_type == issue_type]

        return mock_issues

    def get_epics(self, project_key: str) -> list[JiraEpic]:
        """Get epics from Jira project.

        Args:
            project_key: Jira project key.

        Returns:
            List of JiraEpic objects.
        """
        # Mock implementation - in production, this would call Jira API
        logger.info(f"Getting epics for project: {project_key}")
        
        return [
            JiraEpic(
                key=f"{project_key}-100",
                name="Authentication overhaul",
                summary="Redesign authentication system",
                status="In Progress",
                issue_count=5,
                completed_issues=2,
                project_key=project_key,
            ),
            JiraEpic(
                key=f"{project_key}-101",
                name="User management",
                summary="Implement user management features",
                status="In Progress",
                issue_count=8,
                completed_issues=3,
                project_key=project_key,
            ),
            JiraEpic(
                key=f"{project_key}-102",
                name="Performance improvements",
                summary="Optimize system performance",
                status="Open",
                issue_count=12,
                completed_issues=0,
                project_key=project_key,
            ),
            JiraEpic(
                key=f"{project_key}-103",
                name="Security fixes",
                summary="Address security vulnerabilities",
                status="Open",
                issue_count=6,
                completed_issues=1,
                project_key=project_key,
            ),
        ]

    def search_issues(
        self,
        project_key: str,
        query: str,
    ) -> list[JiraIssue]:
        """Search issues in Jira project.

        Args:
            project_key: Jira project key.
            query: Search query string.

        Returns:
            List of matching JiraIssue objects.
        """
        # Mock implementation - in production, this would call Jira API
        # GET /rest/api/2/search?jql=project={key} AND text~{query}
        logger.info(f"Searching issues in project {project_key} with query: {query}")
        
        all_issues = self.get_issues(project_key)
        
        # Simple text search in summary and description
        query_lower = query.lower()
        matching_issues = [
            issue for issue in all_issues
            if query_lower in issue.summary.lower() or
            (issue.description and query_lower in issue.description.lower())
        ]
        
        return matching_issues


jira_client = JiraClient()
