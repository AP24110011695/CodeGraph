"""Tests for the Team Analytics Engine."""

from pathlib import Path

import pytest

from app.team_analytics.analytics_engine import AnalyticsEngine
from app.team_analytics.metrics_aggregator import MetricsAggregator
from app.team_analytics.engineering_score import EngineeringScore
from app.team_analytics.trend_builder import TrendBuilder


@pytest.fixture
def metrics_aggregator() -> MetricsAggregator:
    """Provide a fresh MetricsAggregator instance."""
    return MetricsAggregator()


@pytest.fixture
def engineering_score() -> EngineeringScore:
    """Provide a fresh EngineeringScore instance."""
    return EngineeringScore()


@pytest.fixture
def trend_builder() -> TrendBuilder:
    """Provide a fresh TrendBuilder instance."""
    return TrendBuilder()


@pytest.fixture
def analytics_engine() -> AnalyticsEngine:
    """Provide a fresh AnalyticsEngine instance."""
    return AnalyticsEngine()


@pytest.fixture
def sample_repository_metrics() -> list[dict]:
    """Provide sample repository metrics."""
    return [
        {
            "repository_name": "repo1",
            "quality_score": 85,
            "risk_score": 25,
            "security_score": 90,
            "architecture_score": 80,
            "health_score": 85,
            "languages": ["Python", "JavaScript"],
            "frameworks": ["FastAPI", "React"],
            "has_pipeline": True,
            "has_test": True,
            "pipeline_health": 80,
            "vulnerability_count": 2,
        },
        {
            "repository_name": "repo2",
            "quality_score": 70,
            "risk_score": 40,
            "security_score": 75,
            "architecture_score": 65,
            "health_score": 70,
            "languages": ["Python"],
            "frameworks": ["Django"],
            "has_pipeline": True,
            "has_test": False,
            "pipeline_health": 60,
            "vulnerability_count": 5,
        },
        {
            "repository_name": "repo3",
            "quality_score": 90,
            "risk_score": 15,
            "security_score": 95,
            "architecture_score": 85,
            "health_score": 90,
            "languages": ["TypeScript", "Node.js"],
            "frameworks": ["Express"],
            "has_pipeline": True,
            "has_test": True,
            "pipeline_health": 90,
            "vulnerability_count": 1,
        },
    ]


class TestEngineeringScore:
    """Tests for EngineeringScore."""

    def test_calculate_engineering_score_full(self, engineering_score: EngineeringScore) -> None:
        """Test engineering score calculation with all metrics."""
        result = engineering_score.calculate_engineering_score(
            architecture_score=80,
            health_score=85,
            quality_score=75,
            risk_score=30,
            security_score=90,
        )

        assert result["engineering_score"] > 0
        assert "breakdown" in result
        assert result["score_count"] == 5
        assert "level" in result

    def test_calculate_engineering_score_partial(self, engineering_score: EngineeringScore) -> None:
        """Test engineering score calculation with partial metrics."""
        result = engineering_score.calculate_engineering_score(
            architecture_score=80,
            health_score=85,
            quality_score=None,
            risk_score=None,
            security_score=None,
        )

        assert result["engineering_score"] > 0
        assert result["score_count"] == 2

    def test_calculate_engineering_score_no_metrics(self, engineering_score: EngineeringScore) -> None:
        """Test engineering score calculation with no metrics."""
        result = engineering_score.calculate_engineering_score()

        assert result["engineering_score"] == 0
        assert result["score_count"] == 0
        assert result["level"] == "unknown"

    def test_calculate_team_score(self, engineering_score: EngineeringScore) -> None:
        """Test team score calculation."""
        repository_scores = [
            {"engineering_score": 85},
            {"engineering_score": 70},
            {"engineering_score": 90},
        ]

        result = engineering_score.calculate_team_score(repository_scores)

        assert result["team_score"] > 0
        assert result["repository_count"] == 3
        assert "highest_score" in result
        assert "lowest_score" in result

    def test_calculate_team_score_empty(self, engineering_score: EngineeringScore) -> None:
        """Test team score calculation with no repositories."""
        result = engineering_score.calculate_team_score([])

        assert result["team_score"] == 0
        assert result["repository_count"] == 0


class TestMetricsAggregator:
    """Tests for MetricsAggregator."""

    def test_aggregate_quality_metrics(self, metrics_aggregator: MetricsAggregator, sample_repository_metrics: list[dict]) -> None:
        """Test quality metrics aggregation."""
        result = metrics_aggregator.aggregate_quality_metrics(sample_repository_metrics)

        assert result["overall_quality"] > 0
        assert result["repository_count"] == 3
        assert "quality_trend" in result

    def test_aggregate_quality_metrics_empty(self, metrics_aggregator: MetricsAggregator) -> None:
        """Test quality metrics aggregation with no repositories."""
        result = metrics_aggregator.aggregate_quality_metrics([])

        assert result["overall_quality"] == 0
        assert result["repository_count"] == 0

    def test_aggregate_risk_metrics(self, metrics_aggregator: MetricsAggregator, sample_repository_metrics: list[dict]) -> None:
        """Test risk metrics aggregation."""
        result = metrics_aggregator.aggregate_risk_metrics(sample_repository_metrics)

        assert result["overall_risk"] >= 0
        assert result["repository_count"] == 3
        assert "risk_trend" in result

    def test_aggregate_security_metrics(self, metrics_aggregator: MetricsAggregator, sample_repository_metrics: list[dict]) -> None:
        """Test security metrics aggregation."""
        result = metrics_aggregator.aggregate_security_metrics(sample_repository_metrics)

        assert result["overall_security"] > 0
        assert result["repository_count"] == 3
        assert "security_trend" in result

    def test_aggregate_technology_distribution(self, metrics_aggregator: MetricsAggregator, sample_repository_metrics: list[dict]) -> None:
        """Test technology distribution aggregation."""
        result = metrics_aggregator.aggregate_technology_distribution(sample_repository_metrics)

        assert "languages" in result
        assert "frameworks" in result
        assert "technology_diversity" in result
        assert result["technology_diversity"] > 0

    def test_aggregate_ci_cd_health(self, metrics_aggregator: MetricsAggregator, sample_repository_metrics: list[dict]) -> None:
        """Test CI/CD health aggregation."""
        result = metrics_aggregator.aggregate_ci_cd_health(sample_repository_metrics)

        assert result["overall_ci_health"] > 0
        assert result["repository_count"] == 3
        assert "pipelines_configured" in result


class TestTrendBuilder:
    """Tests for TrendBuilder."""

    def test_build_quality_trend(self, trend_builder: TrendBuilder, sample_repository_metrics: list[dict]) -> None:
        """Test quality trend building."""
        result = trend_builder.build_quality_trend(sample_repository_metrics)

        assert "trend" in result
        assert "improvement_rate" in result
        assert "declining_repos" in result
        assert "improving_repos" in result

    def test_build_quality_trend_empty(self, trend_builder: TrendBuilder) -> None:
        """Test quality trend building with no repositories."""
        result = trend_builder.build_quality_trend([])

        assert result["trend"] == "unknown"
        assert result["improvement_rate"] == 0

    def test_build_risk_trend(self, trend_builder: TrendBuilder, sample_repository_metrics: list[dict]) -> None:
        """Test risk trend building."""
        result = trend_builder.build_risk_trend(sample_repository_metrics)

        assert "trend" in result
        assert "risk_increase_rate" in result
        assert "high_risk_repos" in result

    def test_build_security_trend(self, trend_builder: TrendBuilder, sample_repository_metrics: list[dict]) -> None:
        """Test security trend building."""
        result = trend_builder.build_security_trend(sample_repository_metrics)

        assert "trend" in result
        assert "security_improvement_rate" in result
        assert "vulnerable_repos" in result

    def test_build_engineering_trend(self, trend_builder: TrendBuilder, sample_repository_metrics: list[dict]) -> None:
        """Test engineering trend building."""
        result = trend_builder.build_engineering_trend(sample_repository_metrics)

        assert "trend" in result
        assert "overall_direction" in result
        assert "improving_count" in result


class TestAnalyticsEngine:
    """Tests for AnalyticsEngine."""

    def test_generate_workspace_analytics(self, analytics_engine: AnalyticsEngine) -> None:
        """Test generating workspace analytics."""
        # Create a workspace with repositories
        workspace = analytics_engine.workspace_manager.create_workspace("Test Workspace")
        workspace_id = workspace.workspace_id

        # Add repositories to workspace
        analytics_engine.workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name="repo1",
            upload_id="upload_1",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=80,
            health_score=85,
            status="READY",
        )
        analytics_engine.workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name="repo2",
            upload_id="upload_2",
            languages=["JavaScript"],
            frameworks=["React"],
            architecture_score=70,
            health_score=75,
            status="READY",
        )

        result = analytics_engine.generate_workspace_analytics(workspace_id)

        assert result["workspace_id"] == workspace_id
        assert result["workspace_name"] == "Test Workspace"
        assert result["engineering_score"] > 0
        assert result["workspace_health"] > 0
        assert result["summary"]["repositories"] == 2

    def test_generate_workspace_analytics_empty(self, analytics_engine: AnalyticsEngine) -> None:
        """Test generating analytics for empty workspace."""
        workspace = analytics_engine.workspace_manager.create_workspace("Empty Workspace")
        workspace_id = workspace.workspace_id

        result = analytics_engine.generate_workspace_analytics(workspace_id)

        assert result["workspace_id"] == workspace_id
        assert result["engineering_score"] == 0
        assert result["workspace_health"] == 0
        assert result["summary"]["repositories"] == 0

    def test_generate_workspace_analytics_not_found(self, analytics_engine: AnalyticsEngine) -> None:
        """Test generating analytics for non-existent workspace."""
        result = analytics_engine.generate_workspace_analytics("nonexistent_workspace")

        assert "error" in result
        assert result["workspace_id"] == "nonexistent_workspace"

    def test_repository_rankings(self, analytics_engine: AnalyticsEngine) -> None:
        """Test repository rankings generation."""
        workspace = analytics_engine.workspace_manager.create_workspace("Ranking Test")
        workspace_id = workspace.workspace_id

        # Add repositories with different scores
        analytics_engine.workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name="high_score_repo",
            upload_id="upload_1",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=90,
            health_score=95,
            status="READY",
        )
        analytics_engine.workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name="low_score_repo",
            upload_id="upload_2",
            languages=["JavaScript"],
            frameworks=["React"],
            architecture_score=50,
            health_score=55,
            status="READY",
        )

        result = analytics_engine.generate_workspace_analytics(workspace_id)

        assert len(result["repository_rankings"]) == 2
        assert result["repository_rankings"][0]["engineering_score"] >= result["repository_rankings"][1]["engineering_score"]

    def test_single_repository_workspace(self, analytics_engine: AnalyticsEngine) -> None:
        """Test analytics for single repository workspace."""
        workspace = analytics_engine.workspace_manager.create_workspace("Single Repo")
        workspace_id = workspace.workspace_id

        analytics_engine.workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name="single_repo",
            upload_id="upload_1",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=80,
            status="READY",
        )

        result = analytics_engine.generate_workspace_analytics(workspace_id)

        assert result["summary"]["repositories"] == 1
        assert result["engineering_score"] > 0
        assert len(result["repository_summaries"]) == 1


class TestTeamAnalyticsAPI:
    """Tests for the team analytics API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_generate_workspace_analytics_api(self, client) -> None:
        """Test workspace analytics API."""
        # Create a workspace first
        from app.team_analytics.analytics_engine import analytics_engine
        workspace = analytics_engine.workspace_manager.create_workspace("API Test Workspace")
        workspace_id = workspace.workspace_id

        analytics_engine.workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name="repo1",
            upload_id="upload_1",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=80,
            health_score=85,
            status="READY",
        )

        response = client.post(f"/team-analytics/{workspace_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["workspace_id"] == workspace_id
        assert data["engineering_score"] > 0

    def test_generate_workspace_analytics_not_found_api(self, client) -> None:
        """Test analytics API for non-existent workspace."""
        response = client.post("/team-analytics/nonexistent_workspace")

        assert response.status_code == 404

    def test_empty_workspace_analytics_api(self, client) -> None:
        """Test analytics API for empty workspace."""
        from app.team_analytics.analytics_engine import analytics_engine
        workspace = analytics_engine.workspace_manager.create_workspace("Empty API Workspace")
        workspace_id = workspace.workspace_id

        response = client.post(f"/team-analytics/{workspace_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["repositories"] == 0

    def test_download_mode(self, client, tmp_path: Path) -> None:
        """Test download mode for analytics report."""
        from app.team_analytics.analytics_engine import analytics_engine
        workspace = analytics_engine.workspace_manager.create_workspace("Download Test")
        workspace_id = workspace.workspace_id

        analytics_engine.workspace_manager.add_repository_to_workspace(
            workspace_id=workspace_id,
            repository_name="repo1",
            upload_id="upload_1",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=80,
            health_score=85,
            status="READY",
        )

        # Change to temp directory for file creation
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            response = client.post(
                f"/team-analytics/{workspace_id}",
                params={"download": True}
            )

            assert response.status_code == 200
            # Check that file was created
            assert (tmp_path / "team_analytics_report.json").exists()
        finally:
            os.chdir(original_dir)


class TestRegression:
    """Regression tests to ensure existing functionality still works."""

    def test_github_integration_still_works(self):
        """Ensure GitHub integration still works after team analytics addition."""
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
        """Ensure CI/CD integration still works after team analytics addition."""
        from app.cicd.cicd_engine import cicd_engine
        result = cicd_engine.connect_repository("test-owner", "test-repo")
        assert "provider" in result
        assert "pipeline_health" in result

    def test_jira_integration_still_works(self):
        """Ensure Jira integration still works after team analytics addition."""
        from app.jira.jira_engine import jira_engine
        result = jira_engine.connect_project("CG")
        assert result["project"]["key"] == "CG"

    def test_notifications_still_works(self):
        """Ensure notifications integration still works after team analytics addition."""
        from app.notifications.notification_engine import notification_engine
        result = notification_engine.send_slack_notification(
            "architecture_report",
            {"repository_name": "test", "architecture_score": 80},
        )
        assert result["status"] == "SUCCESS"
