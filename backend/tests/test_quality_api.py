"""Tests for the POST /quality/{upload_id} API endpoint."""

import shutil
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.scanner_service import RepositoryScanner

EXTRACTED_DIR = Path("storage/extracted")


@pytest.fixture
def client() -> TestClient:
    """Provide a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def scanner() -> RepositoryScanner:
    """Provide a fresh RepositoryScanner instance."""
    return RepositoryScanner()


@pytest.fixture(autouse=True)
def setup_extracted_dir():
    """Create and clean up the extracted directory for tests."""
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    yield
    if EXTRACTED_DIR.exists():
        shutil.rmtree(EXTRACTED_DIR)


class TestQualityApiEndpoint:
    """Tests for POST /quality/{upload_id}."""

    def test_quality_endpoint_success(
        self, client: TestClient, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test successful quality analysis."""
        upload_id = "test-quality-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("from fastapi import FastAPI", encoding="utf-8")
        (project / "README.md").write_text("# Test Project", encoding="utf-8")

        # Copy to extracted directory
        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        scan_result = scanner.scan(extracted_project)

        with patch("app.api.quality.quality_analyzer.analyze") as mock_analyze:
            from app.quality.quality_analyzer import QualityAnalysisResult
            from app.quality.scoring_engine import QualityScores
            from app.quality.recommendations import QualityRecommendations

            mock_analyze.return_value = QualityAnalysisResult(
                project_name="test-project",
                scores=QualityScores(
                    architecture=75,
                    security=80,
                    documentation=90,
                    maintainability=70,
                    testing=60,
                    complexity=85,
                    readability=75,
                    scalability=70,
                ),
                recommendations=QualityRecommendations(
                    strengths=["Well-structured code"],
                    weaknesses=["Limited test coverage"],
                    recommendations=["Add more unit tests"],
                ),
                metadata={
                    "total_files": 2,
                    "total_folders": 0,
                    "languages": {"Python": 1, "Markdown": 1},
                    "containerized": False,
                    "package_managers": [],
                    "backend_frameworks": [],
                    "frontend_frameworks": [],
                },
            )

            response = client.post(f"/quality/{upload_id}")

            assert response.status_code == 200
            data = response.json()
            assert "project_name" in data
            assert "scores" in data
            assert "recommendations" in data
            assert "metadata" in data
            assert data["project_name"] == "test-project"
            assert data["scores"]["architecture"] == 75
            assert len(data["recommendations"]["strengths"]) == 1
            assert data["metadata"]["total_files"] == 2

    def test_quality_project_not_found(self, client: TestClient) -> None:
        """Test 404 when project does not exist."""
        response = client.post("/quality/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_quality_permission_denied(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test 403 when permission is denied during analysis."""
        upload_id = "test-permission-id"
        project = tmp_path / "test-project"
        project.mkdir()

        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        with patch("app.api.quality.quality_analyzer.analyze") as mock_analyze:
            mock_analyze.side_effect = PermissionError("Access denied")

            response = client.post(f"/quality/{upload_id}")
            assert response.status_code == 403
            assert "permission denied" in response.json()["detail"].lower()

    def test_quality_analysis_error(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test 500 when quality analysis fails."""
        upload_id = "test-error-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')", encoding="utf-8")

        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        with patch("app.api.quality.quality_analyzer.analyze") as mock_analyze:
            mock_analyze.side_effect = Exception("Analysis failed")

            response = client.post(f"/quality/{upload_id}")
            assert response.status_code == 500

    def test_quality_response_structure(
        self, client: TestClient, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test that the response structure matches the schema."""
        upload_id = "test-structure-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')", encoding="utf-8")

        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        scan_result = scanner.scan(extracted_project)

        with patch("app.api.quality.quality_analyzer.analyze") as mock_analyze:
            from app.quality.quality_analyzer import QualityAnalysisResult
            from app.quality.scoring_engine import QualityScores
            from app.quality.recommendations import QualityRecommendations

            mock_analyze.return_value = QualityAnalysisResult(
                project_name="test-project",
                scores=QualityScores(
                    architecture=50,
                    security=50,
                    documentation=50,
                    maintainability=50,
                    testing=50,
                    complexity=50,
                    readability=50,
                    scalability=50,
                ),
                recommendations=QualityRecommendations(
                    strengths=["Strength 1", "Strength 2"],
                    weaknesses=["Weakness 1"],
                    recommendations=["Recommendation 1"],
                ),
                metadata={
                    "total_files": 1,
                    "total_folders": 0,
                    "languages": {"Python": 1},
                    "containerized": True,
                    "package_managers": ["pip"],
                    "backend_frameworks": ["FastAPI"],
                    "frontend_frameworks": [],
                },
            )

            response = client.post(f"/quality/{upload_id}")
            assert response.status_code == 200

            data = response.json()
            # Check scores structure
            assert "architecture" in data["scores"]
            assert "security" in data["scores"]
            assert "documentation" in data["scores"]
            assert "maintainability" in data["scores"]
            assert "testing" in data["scores"]
            assert "complexity" in data["scores"]
            assert "readability" in data["scores"]
            assert "scalability" in data["scores"]

            # Check recommendations structure
            assert "strengths" in data["recommendations"]
            assert "weaknesses" in data["recommendations"]
            assert "recommendations" in data["recommendations"]
            assert len(data["recommendations"]["strengths"]) == 2
            assert len(data["recommendations"]["weaknesses"]) == 1
            assert len(data["recommendations"]["recommendations"]) == 1

            # Check metadata structure
            assert "total_files" in data["metadata"]
            assert "total_folders" in data["metadata"]
            assert "languages" in data["metadata"]
            assert "containerized" in data["metadata"]
            assert "package_managers" in data["metadata"]
            assert "backend_frameworks" in data["metadata"]
            assert "frontend_frameworks" in data["metadata"]
            assert data["metadata"]["containerized"] is True
            assert data["metadata"]["package_managers"] == ["pip"]
            assert data["metadata"]["backend_frameworks"] == ["FastAPI"]

    def test_quality_scores_range(
        self, client: TestClient, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test that all scores are within valid range (0-100)."""
        upload_id = "test-scores-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')", encoding="utf-8")

        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        with patch("app.api.quality.quality_analyzer.analyze") as mock_analyze:
            from app.quality.quality_analyzer import QualityAnalysisResult
            from app.quality.scoring_engine import QualityScores
            from app.quality.recommendations import QualityRecommendations

            mock_analyze.return_value = QualityAnalysisResult(
                project_name="test-project",
                scores=QualityScores(
                    architecture=100,
                    security=0,
                    documentation=50,
                    maintainability=75,
                    testing=25,
                    complexity=90,
                    readability=80,
                    scalability=10,
                ),
                recommendations=QualityRecommendations(
                    strengths=[],
                    weaknesses=[],
                    recommendations=[],
                ),
                metadata={
                    "total_files": 1,
                    "total_folders": 0,
                    "languages": {"Python": 1},
                    "containerized": False,
                    "package_managers": [],
                    "backend_frameworks": [],
                    "frontend_frameworks": [],
                },
            )

            response = client.post(f"/quality/{upload_id}")
            assert response.status_code == 200

            data = response.json()
            scores = data["scores"]
            for score in scores.values():
                assert 0 <= score <= 100

    def test_quality_empty_project(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test quality analysis for empty project."""
        upload_id = "test-empty-id"
        project = tmp_path / "test-project"
        project.mkdir()

        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        with patch("app.api.quality.quality_analyzer.analyze") as mock_analyze:
            from app.quality.quality_analyzer import QualityAnalysisResult
            from app.quality.scoring_engine import QualityScores
            from app.quality.recommendations import QualityRecommendations

            mock_analyze.return_value = QualityAnalysisResult(
                project_name="test-project",
                scores=QualityScores(
                    architecture=50,
                    security=50,
                    documentation=0,
                    maintainability=50,
                    testing=0,
                    complexity=50,
                    readability=50,
                    scalability=50,
                ),
                recommendations=QualityRecommendations(
                    strengths=[],
                    weaknesses=["Missing README", "No test files"],
                    recommendations=["Add README", "Add tests"],
                ),
                metadata={
                    "total_files": 0,
                    "total_folders": 0,
                    "languages": {},
                    "containerized": False,
                    "package_managers": [],
                    "backend_frameworks": [],
                    "frontend_frameworks": [],
                },
            )

            response = client.post(f"/quality/{upload_id}")
            assert response.status_code == 200

            data = response.json()
            assert data["metadata"]["total_files"] == 0
            assert data["scores"]["documentation"] == 0
            assert data["scores"]["testing"] == 0
