"""Tests for the Jira Integration Engine."""

from pathlib import Path

import pytest

from app.jira.jira_client import JiraClient
from app.jira.jira_engine import JiraEngine
from app.jira.issue_mapper import IssueMapper
from app.jira.jira_models import JiraProject, JiraIssue, JiraEpic


@pytest.fixture
def jira_client() -> JiraClient:
    """Provide a fresh JiraClient instance."""
    return JiraClient()


@pytest.fixture
def issue_mapper() -> IssueMapper:
    """Provide a fresh IssueMapper instance."""
    return IssueMapper()


@pytest.fixture
def jira_engine() -> JiraEngine:
    """Provide a fresh JiraEngine instance."""
    return JiraEngine()


@pytest.fixture
def sample_issues() -> list[JiraIssue]:
    """Provide sample Jira issues for testing."""
    return [
        JiraIssue(
            key="CG-1",
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
            epic_key="CG-100",
            epic_name="Authentication overhaul",
            story_points=5,
            repository_links=["https://github.com/example/repo/pull/123", "https://github.com/example/repo"],
            project_key="CG",
        ),
        JiraIssue(
            key="CG-2",
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
            epic_key="CG-101",
            epic_name="User management",
            story_points=8,
            repository_links=["https://github.com/example/repo/branch/feature/user-profile", "https://github.com/example/repo"],
            project_key="CG",
        ),
        JiraIssue(
            key="CG-3",
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
            project_key="CG",
        ),
    ]


@pytest.fixture
def sample_epics() -> list[JiraEpic]:
    """Provide sample Jira epics for testing."""
    return [
        JiraEpic(
            key="CG-100",
            name="Authentication overhaul",
            summary="Redesign authentication system",
            status="In Progress",
            issue_count=5,
            completed_issues=2,
            project_key="CG",
        ),
        JiraEpic(
            key="CG-101",
            name="User management",
            summary="Implement user management features",
            status="In Progress",
            issue_count=8,
            completed_issues=3,
            project_key="CG",
        ),
    ]


class TestJiraClient:
    """Tests for JiraClient."""

    def test_get_project(self, jira_client: JiraClient) -> None:
        """Test getting project information."""
        project = jira_client.get_project("CG")

        assert project is not None
        assert project.key == "CG"
        assert project.name == "Project CG"
        assert project.issue_count == 124

    def test_get_issues(self, jira_client: JiraClient) -> None:
        """Test getting issues."""
        issues = jira_client.get_issues("CG")

        assert len(issues) > 0
        assert all(issue.project_key == "CG" for issue in issues)

    def test_get_issues_with_status_filter(self, jira_client: JiraClient) -> None:
        """Test getting issues with status filter."""
        issues = jira_client.get_issues("CG", status="Open")

        assert all(issue.status == "Open" for issue in issues)

    def test_get_issues_with_type_filter(self, jira_client: JiraClient) -> None:
        """Test getting issues with type filter."""
        issues = jira_client.get_issues("CG", issue_type="Bug")

        assert all(issue.issue_type == "Bug" for issue in issues)

    def test_get_epics(self, jira_client: JiraClient) -> None:
        """Test getting epics."""
        epics = jira_client.get_epics("CG")

        assert len(epics) > 0
        assert all(epic.project_key == "CG" for epic in epics)

    def test_search_issues(self, jira_client: JiraClient) -> None:
        """Test searching issues."""
        results = jira_client.search_issues("CG", "authentication")

        assert len(results) > 0
        assert any("authentication" in issue.summary.lower() for issue in results)


class TestIssueMapper:
    """Tests for IssueMapper."""

    def test_map_issues_to_repository(self, issue_mapper: IssueMapper, sample_issues: list[JiraIssue]) -> None:
        """Test mapping issues to repository."""
        mapping = issue_mapper.map_issues_to_repository(
            sample_issues,
            "example/repo",
            "https://github.com/example/repo",
        )

        assert mapping["repository"] == "example/repo"
        assert mapping["linked_issues"] > 0
        assert "link_rate" in mapping

    def test_map_issues_with_no_links(self, issue_mapper: IssueMapper) -> None:
        """Test mapping issues with no repository links."""
        issues = [
            JiraIssue(
                key="TEST-1",
                summary="Test issue",
                description="Test description",
                status="Open",
                priority="Medium",
                issue_type="Task",
                assignee="dev",
                reporter="tester",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
                resolved_at=None,
                labels=[],
                components=[],
                epic_key=None,
                epic_name=None,
                story_points=None,
                repository_links=[],
                project_key="TEST",
            )
        ]

        mapping = issue_mapper.map_issues_to_repository(issues, "example/repo")

        assert mapping["linked_issues"] == 0
        assert mapping["unlinked_issues"] == 1

    def test_calculate_engineering_risk(self, issue_mapper: IssueMapper, sample_issues: list[JiraIssue]) -> None:
        """Test engineering risk calculation."""
        risk = issue_mapper.calculate_engineering_risk(sample_issues)

        assert "risk_level" in risk
        assert "risk_score" in risk
        assert 0 <= risk["risk_score"] <= 100
        assert risk["risk_level"] in ["minimal", "low", "medium", "high", "critical"]

    def test_calculate_risk_with_critical_issues(self, issue_mapper: IssueMapper) -> None:
        """Test risk calculation with critical issues."""
        issues = [
            JiraIssue(
                key="TEST-1",
                summary="Critical bug",
                description="Critical bug description",
                status="Open",
                priority="Critical",
                issue_type="Bug",
                assignee="dev",
                reporter="tester",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
                resolved_at=None,
                labels=[],
                components=[],
                epic_key=None,
                epic_name=None,
                story_points=None,
                repository_links=[],
                project_key="TEST",
            )
        ]

        risk = issue_mapper.calculate_engineering_risk(issues)

        assert risk["critical_issues"] == 1
        assert risk["risk_score"] > 0

    def test_generate_priority_distribution(self, issue_mapper: IssueMapper, sample_issues: list[JiraIssue]) -> None:
        """Test priority distribution generation."""
        distribution = issue_mapper.generate_priority_distribution(sample_issues)

        assert "Critical" in distribution
        assert "High" in distribution
        assert "Medium" in distribution
        assert "Low" in distribution

    def test_generate_status_distribution(self, issue_mapper: IssueMapper, sample_issues: list[JiraIssue]) -> None:
        """Test status distribution generation."""
        distribution = issue_mapper.generate_status_distribution(sample_issues)

        assert len(distribution) > 0
        assert any(status in distribution for status in ["Open", "Closed", "In Progress"])

    def test_generate_issue_type_distribution(self, issue_mapper: IssueMapper, sample_issues: list[JiraIssue]) -> None:
        """Test issue type distribution generation."""
        distribution = issue_mapper.generate_issue_type_distribution(sample_issues)

        assert "Bug" in distribution
        assert "Story" in distribution
        assert "Task" in distribution

    def test_correlate_with_repository_health(self, issue_mapper: IssueMapper, sample_issues: list[JiraIssue]) -> None:
        """Test repository health correlation."""
        correlation = issue_mapper.correlate_with_repository_health(sample_issues, 60)

        assert "repository_health" in correlation
        assert correlation["repository_health"] == 60
        assert "health_impact" in correlation
        assert "recommendation" in correlation

    def test_generate_epic_summary(self, issue_mapper: IssueMapper, sample_epics: list[JiraEpic]) -> None:
        """Test epic summary generation."""
        summary = issue_mapper.generate_epic_summary(sample_epics)

        assert summary["total_epics"] == 2
        assert summary["total_issues"] == 13
        assert summary["completed_issues"] == 5
        assert "completion_rate" in summary


class TestJiraEngine:
    """Tests for JiraEngine."""

    def test_connect_project(self, jira_engine: JiraEngine) -> None:
        """Test connecting a Jira project."""
        result = jira_engine.connect_project("CG")

        assert "project" in result
        assert "summary" in result
        assert "risk" in result
        assert result["project"]["key"] == "CG"

    def test_connect_project_with_repository(self, jira_engine: JiraEngine) -> None:
        """Test connecting project with repository association."""
        # Register a repository first using the engine's registry
        repo_info = jira_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="test_jira_repo",
            languages=["Python"],
            frameworks=[],
            architecture_score=50,
            health_score=50,
            status="READY",
        )

        result = jira_engine.connect_project("CG", repository_id="test_jira_repo")

        assert result["project"]["key"] == "CG"
        assert result["repository_mapping"] is not None

    def test_get_project(self, jira_engine: JiraEngine) -> None:
        """Test getting project information."""
        project = jira_engine.get_project("CG")

        assert project is not None
        assert project["project"]["key"] == "CG"
        assert project["summary"] is not None

    def test_get_project_not_found(self, jira_engine: JiraEngine) -> None:
        """Test getting non-existent project."""
        project = jira_engine.get_project("NONEXISTENT")

        assert project is None

    def test_get_repository_issues(self, jira_engine: JiraEngine) -> None:
        """Test getting repository issues."""
        # Register a repository first using the engine's registry
        repo_info = jira_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="test_jira_repo_issues",
            languages=["Python"],
            frameworks=[],
            architecture_score=50,
            health_score=50,
            status="READY",
        )

        result = jira_engine.get_repository_issues("test_jira_repo_issues")

        assert result is not None
        assert result["repository"] == "example/repo"
        assert "linked_issues" in result

    def test_get_repository_issues_not_found(self, jira_engine: JiraEngine) -> None:
        """Test getting issues for non-existent repository."""
        result = jira_engine.get_repository_issues("nonexistent_repo")

        assert result is None

    def test_search_issues(self, jira_engine: JiraEngine) -> None:
        """Test searching issues."""
        result = jira_engine.search_issues("CG", "authentication")

        assert result["project_key"] == "CG"
        assert result["query"] == "authentication"
        assert "total_results" in result

    def test_generate_issue_summary(self, jira_engine: JiraEngine, sample_issues: list[JiraIssue]) -> None:
        """Test issue summary generation."""
        summary = jira_engine._generate_issue_summary(sample_issues)

        assert summary["total"] == 3
        assert summary["open"] == 2
        assert summary["closed"] == 1
        assert summary["bugs"] == 1


class TestJiraAPI:
    """Tests for the Jira API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_connect_project_api(self, client) -> None:
        """Test project connection API."""
        response = client.post(
            "/jira/connect",
            json={
                "project_key": "CG",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["project"]["key"] == "CG"
        assert data["summary"] is not None

    def test_connect_project_with_repository_api(self, client) -> None:
        """Test project connection with repository API."""
        # Register a repository first using the engine's registry
        from app.jira.jira_engine import jira_engine
        repo_info = jira_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="test_jira_api_repo",
            languages=["Python"],
            frameworks=[],
            architecture_score=50,
            health_score=50,
            status="READY",
        )

        response = client.post(
            "/jira/connect",
            json={
                "project_key": "CG",
                "repository_id": "test_jira_api_repo",
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["project"]["key"] == "CG"
        assert data["repository_mapping"] is not None

    def test_get_project_api(self, client) -> None:
        """Test getting project API."""
        response = client.get("/jira/project/CG")

        assert response.status_code == 200
        data = response.json()
        assert data["project"]["key"] == "CG"

    def test_get_project_not_found_api(self, client) -> None:
        """Test getting non-existent project API."""
        response = client.get("/jira/project/NONEXISTENT")

        assert response.status_code == 404

    def test_get_repository_issues_api(self, client) -> None:
        """Test getting repository issues API."""
        # Register a repository first using the engine's registry
        from app.jira.jira_engine import jira_engine
        repo_info = jira_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="test_jira_api_issues",
            languages=["Python"],
            frameworks=[],
            architecture_score=50,
            health_score=50,
            status="READY",
        )

        response = client.get("/jira/issues/test_jira_api_issues")

        assert response.status_code == 200
        data = response.json()
        assert data["repository"] == "example/repo"

    def test_get_repository_issues_not_found_api(self, client) -> None:
        """Test getting issues for non-existent repository API."""
        response = client.get("/jira/issues/nonexistent_repo")

        assert response.status_code == 404

    def test_search_issues_api(self, client) -> None:
        """Test searching issues API."""
        response = client.get("/jira/search/CG?query=authentication")

        assert response.status_code == 200
        data = response.json()
        assert data["project_key"] == "CG"
        assert data["query"] == "authentication"

    def test_connect_project_download_mode(self, client, tmp_path: Path) -> None:
        """Test download mode for project connection."""
        # Change to temp directory for file creation
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            response = client.post(
                "/jira/connect",
                json={
                    "project_key": "CG",
                },
                params={"download": True}
            )

            assert response.status_code == 200
            # Check that file was created
            assert (tmp_path / "jira_project_summary.json").exists()
        finally:
            os.chdir(original_dir)

    def test_get_project_download_mode(self, client, tmp_path: Path) -> None:
        """Test download mode for getting project."""
        # Change to temp directory for file creation
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            response = client.get(
                "/jira/project/CG",
                params={"download": True}
            )

            assert response.status_code == 200
            # Check that file was created
            assert (tmp_path / "jira_project_summary.json").exists()
        finally:
            os.chdir(original_dir)


class TestRegression:
    """Regression tests to ensure existing functionality still works."""

    def test_github_integration_still_works(self):
        """Ensure GitHub integration still works after Jira addition."""
        from app.github.github_engine import github_engine
        result = github_engine.connect_repository("test-owner", "test-repo")
        assert result["sync_status"] == "SUCCESS"

    def test_workspace_still_works(self):
        """Ensure workspace functionality still works."""
        from app.workspace.workspace_manager import workspace_manager
        workspace = workspace_manager.create_workspace("Test Workspace")
        assert workspace is not None
        assert workspace.name == "Test Workspace"

    def test_cicd_integration_still_works(self):
        """Ensure CI/CD integration still works after Jira addition."""
        from app.cicd.cicd_engine import cicd_engine
        result = cicd_engine.connect_repository("test-owner", "test-repo")
        assert "provider" in result
        assert "pipeline_health" in result
