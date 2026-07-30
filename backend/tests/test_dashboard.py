"""Tests for the Executive Engineering Dashboard."""

from pathlib import Path

import pytest

from app.dashboard.dashboard_engine import DashboardEngine
from app.dashboard.executive_summary import ExecutiveSummary
from app.dashboard.dashboard_builder import DashboardBuilder
from app.dashboard.widget_builder import WidgetBuilder


@pytest.fixture
def widget_builder() -> WidgetBuilder:
    """Provide a fresh WidgetBuilder instance."""
    return WidgetBuilder()


@pytest.fixture
def executive_summary() -> ExecutiveSummary:
    """Provide a fresh ExecutiveSummary instance."""
    return ExecutiveSummary()


@pytest.fixture
def dashboard_builder() -> DashboardBuilder:
    """Provide a fresh DashboardBuilder instance."""
    return DashboardBuilder()


@pytest.fixture
def dashboard_engine() -> DashboardEngine:
    """Provide a fresh DashboardEngine instance."""
    return DashboardEngine()


@pytest.fixture
def sample_team_analytics() -> dict:
    """Provide sample team analytics data."""
    return {
        "engineering_score": 89,
        "workspace_health": 91,
        "summary": {
            "repositories": 3,
            "overall_quality": 88,
            "overall_security": 90,
            "overall_risk": 18,
        },
        "quality_metrics": {
            "overall_quality": 88,
            "average_quality": 88.5,
            "quality_trend": "improving",
            "repository_count": 3,
        },
        "risk_metrics": {
            "overall_risk": 18,
            "average_risk": 18.2,
            "risk_trend": "decreasing",
            "high_risk_count": 0,
            "repository_count": 3,
        },
        "security_metrics": {
            "overall_security": 90,
            "average_security": 90.0,
            "security_trend": "improving",
            "vulnerability_count": 8,
            "repository_count": 3,
        },
        "technology_distribution": {
            "languages": {
                "Python": 2,
                "JavaScript": 1,
            },
            "frameworks": {
                "FastAPI": 1,
                "React": 1,
            },
            "dominant_language": "Python",
            "technology_diversity": 4,
        },
        "cicd_health": {
            "overall_ci_health": 85,
            "average_ci_health": 85.0,
            "pipelines_configured": 3,
            "automated_tests": 2,
            "repository_count": 3,
        },
        "repository_rankings": [
            {
                "repository": "repo1",
                "engineering_score": 94,
                "level": "excellent",
                "upload_id": "upload_1",
            },
            {
                "repository": "repo2",
                "engineering_score": 88,
                "level": "good",
                "upload_id": "upload_2",
            },
        ],
        "top_improvements": [
            "Improve dependency health",
            "Increase automated test coverage",
        ],
        "repository_summaries": [
            {
                "repository_name": "repo1",
                "upload_id": "upload_1",
                "architecture_score": 95,
                "health_score": 90,
                "quality_score": 92,
                "security_score": 95,
                "risk_score": 10,
            },
            {
                "repository_name": "repo2",
                "upload_id": "upload_2",
                "architecture_score": 85,
                "health_score": 80,
                "quality_score": 88,
                "security_score": 85,
                "risk_score": 20,
            },
        ],
    }


class TestWidgetBuilder:
    """Tests for WidgetBuilder."""

    def test_build_score_card(self, widget_builder: WidgetBuilder) -> None:
        """Test building score card widget."""
        result = widget_builder.build_score_card("Test Score", 85, "quality")

        assert result["type"] == "score_card"
        assert result["title"] == "Test Score"
        assert result["value"] == 85
        assert result["level"] == "good"

    def test_build_list_widget(self, widget_builder: WidgetBuilder) -> None:
        """Test building list widget."""
        items = ["Item 1", "Item 2", "Item 3"]
        result = widget_builder.build_list_widget("Test List", items)

        assert result["type"] == "list"
        assert result["title"] == "Test List"
        assert result["count"] == 3

    def test_build_repository_card(self, widget_builder: WidgetBuilder) -> None:
        """Test building repository card widget."""
        result = widget_builder.build_repository_card(
            "test/repo",
            85,
            90,
            88,
            92,
            15,
        )

        assert result["type"] == "repository_card"
        assert result["repository_name"] == "test/repo"
        assert result["overall_score"] > 0

    def test_build_kpi_widget(self, widget_builder: WidgetBuilder) -> None:
        """Test building KPI widget."""
        metrics = {"Quality": 85, "Security": 90}
        result = widget_builder.build_kpi_widget("Test KPI", metrics)

        assert result["type"] == "kpi"
        assert result["title"] == "Test KPI"
        assert result["metrics"]["Quality"] == 85

    def test_build_chart_widget(self, widget_builder: WidgetBuilder) -> None:
        """Test building chart widget."""
        data = [{"label": "A", "value": 10}, {"label": "B", "value": 20}]
        result = widget_builder.build_chart_widget("Test Chart", "bar", data)

        assert result["type"] == "chart"
        assert result["chart_type"] == "bar"


class TestExecutiveSummary:
    """Tests for ExecutiveSummary."""

    def test_generate_executive_summary(self, executive_summary: ExecutiveSummary, sample_team_analytics: dict) -> None:
        """Test generating executive summary."""
        workspace_data = {"workspace_id": "test", "workspace_name": "Test Workspace"}
        result = executive_summary.generate_executive_summary(workspace_data, sample_team_analytics)

        assert result["executive_score"] == 89
        assert result["workspace_health"] == 91
        assert "overall_health" in result
        assert "summary" in result
        assert "key_insights" in result
        assert "recommendations" in result

    def test_determine_overall_health(self, executive_summary: ExecutiveSummary) -> None:
        """Test determining overall health."""
        result = executive_summary._determine_overall_health(95, 90)

        assert result == "excellent"

    def test_generate_key_insights(self, executive_summary: ExecutiveSummary, sample_team_analytics: dict) -> None:
        """Test generating key insights."""
        result = executive_summary._generate_key_insights(sample_team_analytics)

        assert isinstance(result, list)

    def test_generate_executive_recommendations(self, executive_summary: ExecutiveSummary, sample_team_analytics: dict) -> None:
        """Test generating executive recommendations."""
        result = executive_summary._generate_executive_recommendations(sample_team_analytics)

        assert isinstance(result, list)


class TestDashboardBuilder:
    """Tests for DashboardBuilder."""

    def test_build_dashboard(self, dashboard_builder: DashboardBuilder, sample_team_analytics: dict) -> None:
        """Test building complete dashboard."""
        workspace_data = {"workspace_id": "test", "workspace_name": "Test Workspace"}
        repository_summaries = sample_team_analytics.get("repository_summaries", [])

        result = dashboard_builder.build_dashboard(
            workspace_data,
            sample_team_analytics,
            repository_summaries,
        )

        assert "repository_cards" in result
        assert "top_risks" in result
        assert "top_improvements" in result
        assert "technology_stack" in result
        assert "engineering_kpis" in result

    def test_build_repository_cards(self, dashboard_builder: DashboardBuilder, sample_team_analytics: dict) -> None:
        """Test building repository cards."""
        repository_summaries = sample_team_analytics.get("repository_summaries", [])

        result = dashboard_builder._build_repository_cards(repository_summaries)

        assert len(result) == 2
        assert result[0]["type"] == "repository_card"

    def test_build_top_risks(self, dashboard_builder: DashboardBuilder, sample_team_analytics: dict) -> None:
        """Test building top risks widget."""
        result = dashboard_builder._build_top_risks(sample_team_analytics)

        assert result["type"] == "list"
        assert result["title"] == "Top Risks"

    def test_build_top_improvements(self, dashboard_builder: DashboardBuilder, sample_team_analytics: dict) -> None:
        """Test building top improvements widget."""
        result = dashboard_builder._build_top_improvements(sample_team_analytics)

        assert result["type"] == "list"
        assert result["title"] == "Top Improvements"


class TestDashboardEngine:
    """Tests for DashboardEngine."""

    def test_generate_dashboard(self, dashboard_engine: DashboardEngine) -> None:
        """Test generating dashboard."""
        # Create workspace with repositories
        workspace = dashboard_engine.workspace_manager.create_workspace("Test Dashboard Workspace")
        workspace_id = workspace.workspace_id

        dashboard_engine.workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name="repo1",
            upload_id="dashboard_repo_1",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )
        dashboard_engine.workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name="repo2",
            upload_id="dashboard_repo_2",
            languages=["JavaScript"],
            frameworks=["React"],
            architecture_score=75,
            health_score=80,
            status="READY",
        )

        result = dashboard_engine.generate_dashboard(workspace_id)

        assert result["workspace_id"] == workspace_id
        assert result["executive_score"] > 0
        assert "score_cards" in result
        assert "widgets" in result

    def test_generate_dashboard_not_found(self, dashboard_engine: DashboardEngine) -> None:
        """Test generating dashboard for non-existent workspace."""
        result = dashboard_engine.generate_dashboard("nonexistent_workspace")

        assert "error" in result

    def test_generate_dashboard_empty_workspace(self, dashboard_engine: DashboardEngine) -> None:
        """Test generating dashboard for empty workspace."""
        workspace = dashboard_engine.workspace_manager.create_workspace("Empty Dashboard Workspace")
        workspace_id = workspace.workspace_id

        result = dashboard_engine.generate_dashboard(workspace_id)

        assert result["workspace_id"] == workspace_id
        assert result["executive_score"] == 0

    def test_build_score_cards(self, dashboard_engine: DashboardEngine, sample_team_analytics: dict) -> None:
        """Test building score cards."""
        result = dashboard_engine._build_score_cards(sample_team_analytics)

        assert len(result) == 5
        assert result[0]["type"] == "score_card"


class TestDashboardAPI:
    """Tests for the dashboard API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_generate_dashboard_api(self, client) -> None:
        """Test dashboard API."""
        from app.dashboard.dashboard_engine import dashboard_engine
        workspace = dashboard_engine.workspace_manager.create_workspace("API Dashboard Workspace")
        workspace_id = workspace.workspace_id

        dashboard_engine.workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name="repo1",
            upload_id="api_dashboard_repo_1",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )

        response = client.post(f"/dashboard/{workspace_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["workspace_id"] == workspace_id
        assert data["executive_score"] > 0

    def test_generate_dashboard_not_found_api(self, client) -> None:
        """Test dashboard API for non-existent workspace."""
        response = client.post("/dashboard/nonexistent_workspace")

        assert response.status_code == 404

    def test_download_mode(self, client, tmp_path: Path) -> None:
        """Test download mode for dashboard."""
        from app.dashboard.dashboard_engine import dashboard_engine
        workspace = dashboard_engine.workspace_manager.create_workspace("Download Dashboard Workspace")
        workspace_id = workspace.workspace_id

        dashboard_engine.workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name="repo1",
            upload_id="download_dashboard_repo_1",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )

        # Change to temp directory for file creation
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            response = client.post(
                f"/dashboard/{workspace_id}",
                params={"download": True}
            )

            assert response.status_code == 200
            # Check that file was created
            assert (tmp_path / "executive_dashboard.json").exists()
        finally:
            os.chdir(original_dir)


class TestRegression:
    """Regression tests to ensure existing functionality still works."""

    def test_github_integration_still_works(self):
        """Ensure GitHub integration still works after dashboard addition."""
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
        """Ensure CI/CD integration still works after dashboard addition."""
        from app.cicd.cicd_engine import cicd_engine
        result = cicd_engine.connect_repository("test-owner", "test-repo")
        assert "provider" in result
        assert "pipeline_health" in result

    def test_jira_integration_still_works(self):
        """Ensure Jira integration still works after dashboard addition."""
        from app.jira.jira_engine import jira_engine
        result = jira_engine.connect_project("CG")
        assert result["project"]["key"] == "CG"

    def test_notifications_still_works(self):
        """Ensure notifications integration still works after dashboard addition."""
        from app.notifications.notification_engine import notification_engine
        result = notification_engine.send_slack_notification(
            "architecture_report",
            {"repository_name": "test", "architecture_score": 80},
        )
        assert result["status"] == "SUCCESS"

    def test_team_analytics_still_works(self):
        """Ensure team analytics still works after dashboard addition."""
        from app.team_analytics.analytics_engine import analytics_engine
        workspace = analytics_engine.workspace_manager.create_workspace("Test Workspace")
        workspace_id = workspace.workspace_id
        result = analytics_engine.generate_workspace_analytics(workspace_id)
        assert result["workspace_id"] == workspace_id

    def test_repository_comparison_still_works(self):
        """Ensure repository comparison still works after dashboard addition."""
        from app.repository_comparison.comparison_engine import comparison_engine
        comparison_engine.repository_registry.register_repository(
            repository_name="repo1",
            upload_id="repo_001",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )
        comparison_engine.repository_registry.register_repository(
            repository_name="repo2",
            upload_id="repo_002",
            languages=["JavaScript"],
            frameworks=["React"],
            architecture_score=75,
            health_score=80,
            status="READY",
        )
        result = comparison_engine.compare_repositories(["repo_001", "repo_002"])
        assert result["similarity_score"] >= 0

    def test_release_notes_still_works(self):
        """Ensure release notes still works after dashboard addition."""
        from app.release_notes.release_notes_engine import release_notes_engine
        release_notes_engine.repository_registry.register_repository(
            repository_name="example/repo",
            upload_id="repo_001",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )
        result = release_notes_engine.generate_release_notes("repo_001", "v1.0.0")
        assert result["version"] == "v1.0.0"
