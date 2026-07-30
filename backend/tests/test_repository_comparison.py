"""Tests for the Repository Comparison Engine."""

from pathlib import Path

import pytest

from app.repository_comparison.comparison_engine import ComparisonEngine
from app.repository_comparison.comparison_builder import ComparisonBuilder
from app.repository_comparison.score_comparator import ScoreComparator
from app.repository_comparison.similarity_engine import SimilarityEngine


@pytest.fixture
def score_comparator() -> ScoreComparator:
    """Provide a fresh ScoreComparator instance."""
    return ScoreComparator()


@pytest.fixture
def similarity_engine() -> SimilarityEngine:
    """Provide a fresh SimilarityEngine instance."""
    return SimilarityEngine()


@pytest.fixture
def comparison_builder() -> ComparisonBuilder:
    """Provide a fresh ComparisonBuilder instance."""
    return ComparisonBuilder()


@pytest.fixture
def comparison_engine() -> ComparisonEngine:
    """Provide a fresh ComparisonEngine instance."""
    return ComparisonEngine()


@pytest.fixture
def sample_repository_data() -> list[dict]:
    """Provide sample repository data for comparison."""
    return [
        {
            "upload_id": "repo_001",
            "repository_name": "repo1",
            "architecture_score": 85,
            "health_score": 90,
            "quality_score": 88,
            "security_score": 92,
            "risk_score": 15,
            "languages": ["Python", "JavaScript"],
            "frameworks": ["FastAPI", "React"],
        },
        {
            "upload_id": "repo_002",
            "repository_name": "repo2",
            "architecture_score": 75,
            "health_score": 80,
            "quality_score": 78,
            "security_score": 85,
            "risk_score": 25,
            "languages": ["Python"],
            "frameworks": ["Django"],
        },
        {
            "upload_id": "repo_003",
            "repository_name": "repo3",
            "architecture_score": 90,
            "health_score": 85,
            "quality_score": 92,
            "security_score": 95,
            "risk_score": 10,
            "languages": ["TypeScript", "Node.js"],
            "frameworks": ["Express"],
        },
    ]


class TestScoreComparator:
    """Tests for ScoreComparator."""

    def test_compare_scores(self, score_comparator: ScoreComparator) -> None:
        """Test score comparison."""
        repository_scores = {
            "repo_001": {"architecture_score": 85, "health_score": 90},
            "repo_002": {"architecture_score": 75, "health_score": 80},
        }

        result = score_comparator.compare_scores(repository_scores, "architecture_score")

        assert result["category"] == "architecture_score"
        assert "highest" in result
        assert "lowest" in result
        assert result["highest"]["repository"] == "repo_001"
        assert result["lowest"]["repository"] == "repo_002"

    def test_compare_scores_empty(self, score_comparator: ScoreComparator) -> None:
        """Test score comparison with empty data."""
        result = score_comparator.compare_scores({}, "architecture_score")

        assert result["category"] == "architecture_score"
        assert result["highest"] is None
        assert result["lowest"] is None

    def test_compare_multiple_categories(self, score_comparator: ScoreComparator) -> None:
        """Test multiple category comparison."""
        repository_scores = {
            "repo_001": {"architecture_score": 85, "health_score": 90},
            "repo_002": {"architecture_score": 75, "health_score": 80},
        }

        result = score_comparator.compare_multiple_categories(
            repository_scores,
            ["architecture_score", "health_score"],
        )

        assert len(result) == 2
        assert result[0]["category"] == "architecture_score"
        assert result[1]["category"] == "health_score"

    def test_generate_rankings(self, score_comparator: ScoreComparator) -> None:
        """Test ranking generation."""
        repository_scores = {
            "repo_001": {"architecture_score": 85},
            "repo_002": {"architecture_score": 75},
            "repo_003": {"architecture_score": 90},
        }

        result = score_comparator.generate_rankings(repository_scores, "architecture_score")

        assert len(result) == 3
        assert result[0]["rank"] == 1
        assert result[0]["repository"] == "repo_003"
        assert result[0]["score"] == 90

    def test_calculate_score_difference(self, score_comparator: ScoreComparator) -> None:
        """Test score difference calculation."""
        result = score_comparator.calculate_score_difference(85, 75)

        assert result["difference"] == 10
        assert "percentage_difference" in result
        assert "significance" in result


class TestSimilarityEngine:
    """Tests for SimilarityEngine."""

    def test_calculate_similarity(self, similarity_engine: SimilarityEngine, sample_repository_data: list[dict]) -> None:
        """Test similarity calculation."""
        result = similarity_engine.calculate_similarity(
            sample_repository_data[0],
            sample_repository_data[1],
        )

        assert "overall_similarity" in result
        assert "similarity_level" in result
        assert 0 <= result["overall_similarity"] <= 100

    def test_calculate_language_similarity(self, similarity_engine: SimilarityEngine, sample_repository_data: list[dict]) -> None:
        """Test language similarity calculation."""
        result = similarity_engine._calculate_language_similarity(
            sample_repository_data[0],
            sample_repository_data[1],
        )

        assert 0 <= result <= 100

    def test_calculate_framework_similarity(self, similarity_engine: SimilarityEngine, sample_repository_data: list[dict]) -> None:
        """Test framework similarity calculation."""
        result = similarity_engine._calculate_framework_similarity(
            sample_repository_data[0],
            sample_repository_data[1],
        )

        assert 0 <= result <= 100

    def test_calculate_multi_repository_similarity(self, similarity_engine: SimilarityEngine, sample_repository_data: list[dict]) -> None:
        """Test multi-repository similarity calculation."""
        result = similarity_engine.calculate_multi_repository_similarity(sample_repository_data)

        assert "matrix" in result
        assert "average_similarity" in result
        assert result["average_similarity"] >= 0

    def test_calculate_multi_repository_similarity_insufficient(self, similarity_engine: SimilarityEngine) -> None:
        """Test multi-repository similarity with insufficient repositories."""
        result = similarity_engine.calculate_multi_repository_similarity([])

        assert result["average_similarity"] == 0
        assert result["most_similar"] is None


class TestComparisonBuilder:
    """Tests for ComparisonBuilder."""

    def test_build_comparison_report(self, comparison_builder: ComparisonBuilder, sample_repository_data: list[dict]) -> None:
        """Test comparison report building."""
        score_comparisons = [
            {
                "category": "architecture_score",
                "scores": {"repo_001": 85, "repo_002": 75},
                "highest": {"repository": "repo_001", "score": 85},
                "lowest": {"repository": "repo_002", "score": 75},
                "average": 80,
                "spread": 10,
            }
        ]

        similarity_data = {
            "average_similarity": 50,
            "most_similar": 75,
            "least_similar": 25,
        }

        result = comparison_builder.build_comparison_report(
            sample_repository_data[:2],
            score_comparisons,
            similarity_data,
        )

        assert "summary" in result
        assert "comparisons" in result
        assert "recommendations" in result
        assert result["summary"]["repositories"] == 2

    def test_build_comparison_report_empty(self, comparison_builder: ComparisonBuilder) -> None:
        """Test comparison report building with empty data."""
        result = comparison_builder.build_comparison_report([], [], {})

        assert result["summary"]["repositories"] == 0
        assert result["comparisons"] == []

    def test_identify_strengths(self, comparison_builder: ComparisonBuilder) -> None:
        """Test strength identification."""
        score_comparisons = [
            {
                "category": "architecture_score",
                "scores": {"repo_001": 85, "repo_002": 75},
                "highest": {"repository": "repo_001", "score": 85},
                "lowest": {"repository": "repo_002", "score": 75},
            }
        ]

        result = comparison_builder._identify_strengths([], score_comparisons)

        assert len(result) > 0
        assert result[0]["repository"] == "repo_001"

    def test_identify_weaknesses(self, comparison_builder: ComparisonBuilder) -> None:
        """Test weakness identification."""
        score_comparisons = [
            {
                "category": "architecture_score",
                "scores": {"repo_001": 85, "repo_002": 75},
                "highest": {"repository": "repo_001", "score": 85},
                "lowest": {"repository": "repo_002", "score": 75},
            }
        ]

        result = comparison_builder._identify_weaknesses([], score_comparisons)

        assert len(result) > 0
        assert result[0]["repository"] == "repo_002"


class TestComparisonEngine:
    """Tests for ComparisonEngine."""

    def test_compare_repositories(self, comparison_engine: ComparisonEngine) -> None:
        """Test repository comparison."""
        # Register repositories first
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

        assert "similarity_score" in result
        assert "summary" in result
        assert result["summary"]["repositories"] == 2
        assert "comparisons" in result

    def test_compare_repositories_insufficient(self, comparison_engine: ComparisonEngine) -> None:
        """Test repository comparison with insufficient repositories."""
        result = comparison_engine.compare_repositories(["repo_001"])

        assert "error" in result
        assert "At least 2 repositories" in result["error"]

    def test_compare_multiple_repositories(self, comparison_engine: ComparisonEngine) -> None:
        """Test comparison of multiple repositories."""
        # Register three repositories
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
        comparison_engine.repository_registry.register_repository(
            repository_name="repo3",
            upload_id="repo_003",
            languages=["TypeScript"],
            frameworks=["Express"],
            architecture_score=90,
            health_score=85,
            status="READY",
        )

        result = comparison_engine.compare_repositories(["repo_001", "repo_002", "repo_003"])

        assert result["summary"]["repositories"] == 3
        assert "similarity_score" in result

    def test_compare_repositories_invalid(self, comparison_engine: ComparisonEngine) -> None:
        """Test comparison with invalid repository IDs."""
        result = comparison_engine.compare_repositories(["invalid_001", "invalid_002"])

        assert "error" in result


class TestRepositoryComparisonAPI:
    """Tests for the repository comparison API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_compare_repositories_api(self, client) -> None:
        """Test repository comparison API."""
        # Register repositories first
        from app.repository_comparison.comparison_engine import comparison_engine
        comparison_engine.repository_registry.register_repository(
            repository_name="repo1",
            upload_id="api_repo_001",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )
        comparison_engine.repository_registry.register_repository(
            repository_name="repo2",
            upload_id="api_repo_002",
            languages=["JavaScript"],
            frameworks=["React"],
            architecture_score=75,
            health_score=80,
            status="READY",
        )

        response = client.post(
            "/repository-comparison",
            json={
                "repositories": ["api_repo_001", "api_repo_002"],
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["similarity_score"] >= 0
        assert data["summary"]["repositories"] == 2

    def test_compare_repositories_insufficient_api(self, client) -> None:
        """Test comparison API with insufficient repositories."""
        response = client.post(
            "/repository-comparison",
            json={
                "repositories": ["repo_001"],
            }
        )

        assert response.status_code == 400

    def test_download_mode(self, client, tmp_path: Path) -> None:
        """Test download mode for comparison report."""
        from app.repository_comparison.comparison_engine import comparison_engine
        comparison_engine.repository_registry.register_repository(
            repository_name="repo1",
            upload_id="download_repo_001",
            languages=["Python"],
            frameworks=["FastAPI"],
            architecture_score=85,
            health_score=90,
            status="READY",
        )
        comparison_engine.repository_registry.register_repository(
            repository_name="repo2",
            upload_id="download_repo_002",
            languages=["JavaScript"],
            frameworks=["React"],
            architecture_score=75,
            health_score=80,
            status="READY",
        )

        # Change to temp directory for file creation
        import os
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        try:
            response = client.post(
                "/repository-comparison",
                json={
                    "repositories": ["download_repo_001", "download_repo_002"],
                },
                params={"download": True}
            )

            assert response.status_code == 200
            # Check that file was created
            assert (tmp_path / "repository_comparison_report.json").exists()
        finally:
            os.chdir(original_dir)


class TestRegression:
    """Regression tests to ensure existing functionality still works."""

    def test_github_integration_still_works(self):
        """Ensure GitHub integration still works after repository comparison addition."""
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
        """Ensure CI/CD integration still works after repository comparison addition."""
        from app.cicd.cicd_engine import cicd_engine
        result = cicd_engine.connect_repository("test-owner", "test-repo")
        assert "provider" in result
        assert "pipeline_health" in result

    def test_jira_integration_still_works(self):
        """Ensure Jira integration still works after repository comparison addition."""
        from app.jira.jira_engine import jira_engine
        result = jira_engine.connect_project("CG")
        assert result["project"]["key"] == "CG"

    def test_notifications_still_works(self):
        """Ensure notifications integration still works after repository comparison addition."""
        from app.notifications.notification_engine import notification_engine
        result = notification_engine.send_slack_notification(
            "architecture_report",
            {"repository_name": "test", "architecture_score": 80},
        )
        assert result["status"] == "SUCCESS"

    def test_team_analytics_still_works(self):
        """Ensure team analytics still works after repository comparison addition."""
        from app.team_analytics.analytics_engine import analytics_engine
        workspace = analytics_engine.workspace_manager.create_workspace("Test Workspace")
        workspace_id = workspace.workspace_id
        result = analytics_engine.generate_workspace_analytics(workspace_id)
        assert result["workspace_id"] == workspace_id
