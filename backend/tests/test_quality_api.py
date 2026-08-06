"""Tests for the POST /repositories/{repository_id}/quality API endpoint."""

import shutil
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.indexing.index_manager import get_shared_index_manager
from app.main import app
from app.services.scanner_service import RepositoryScanner
from storage.repository_store import RepositoryStore

EXTRACTED_DIR = Path("storage/extracted")
repository_store = RepositoryStore()


@pytest.fixture
def client() -> TestClient:
    """Provide a test client for the FastAPI app."""
    return TestClient(app)


class TestQualityApiEndpoint:
    """Tests for POST /quality/{upload_id}."""

    def test_quality_endpoint_success(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test successful quality analysis."""
        upload_id = f"test-quality-{uuid.uuid4()}"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("from fastapi import FastAPI", encoding="utf-8")
        (project / "README.md").write_text("# Test Project", encoding="utf-8")

        # Register repository
        repository_store.register_upload(upload_id, str(project), name=f"test-quality-{uuid.uuid4()}")

        # Index repository with force=True to avoid state conflicts
        index_manager = get_shared_index_manager()
        index_manager.create_index(project, upload_id, force=True)

        response = client.post(f"/repositories/{upload_id}/quality")

        assert response.status_code == 200
        data = response.json()
        assert "project_name" in data
        assert "scores" in data
        assert "recommendations" in data
        assert "metadata" in data

    def test_quality_project_not_found(self, client: TestClient) -> None:
        """Test 400 when project does not exist (non-indexed repos return 400)."""
        response = client.post("/repositories/nonexistent-id/quality")
        assert response.status_code == 400
        assert "indexed" in response.json()["detail"].lower()

    def test_quality_permission_denied(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test 403 when permission is denied during analysis."""
        upload_id = f"test-permission-{uuid.uuid4()}"
        project = tmp_path / "test-project"
        project.mkdir()
        # Add minimal content to avoid indexing error
        (project / "main.py").write_text("print('hello')", encoding="utf-8")

        # Register repository
        repository_store.register_upload(upload_id, str(project), name=f"test-permission-{uuid.uuid4()}")

        # Index repository with force=True to avoid state conflicts
        index_manager = get_shared_index_manager()
        index_manager.create_index(project, upload_id, force=True)

        with patch("app.api.quality.quality_analyzer.analyze") as mock_analyze:
            mock_analyze.side_effect = PermissionError("Access denied")

            response = client.post(f"/repositories/{upload_id}/quality")
            assert response.status_code == 403
            assert "permission denied" in response.json()["detail"].lower()

    def test_quality_analysis_error(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test 500 when quality analysis fails."""
        upload_id = f"test-error-{uuid.uuid4()}"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')", encoding="utf-8")

        # Register repository
        repository_store.register_upload(upload_id, str(project), name=f"test-error-{uuid.uuid4()}")

        # Index repository with force=True to avoid state conflicts
        index_manager = get_shared_index_manager()
        index_manager.create_index(project, upload_id, force=True)

        with patch("app.api.quality.quality_analyzer.analyze") as mock_analyze:
            mock_analyze.side_effect = Exception("Analysis failed")

            response = client.post(f"/repositories/{upload_id}/quality")
            assert response.status_code == 500

    def test_quality_response_structure(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test that the response structure matches the schema."""
        upload_id = f"test-structure-{uuid.uuid4()}"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')", encoding="utf-8")

        # Register repository
        repository_store.register_upload(upload_id, str(project), name=f"test-structure-{uuid.uuid4()}")

        # Index repository with force=True to avoid state conflicts
        index_manager = get_shared_index_manager()
        index_manager.create_index(project, upload_id, force=True)

        response = client.post(f"/repositories/{upload_id}/quality")
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

        # Check metadata structure
        assert "total_files" in data["metadata"]
        assert "total_folders" in data["metadata"]
        assert "languages" in data["metadata"]
        assert "containerized" in data["metadata"]
        assert "package_managers" in data["metadata"]
        assert "backend_frameworks" in data["metadata"]
        assert "frontend_frameworks" in data["metadata"]

    def test_quality_scores_range(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test that all scores are within valid range (0-100)."""
        upload_id = f"test-scores-{uuid.uuid4()}"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')", encoding="utf-8")

        # Register repository
        repository_store.register_upload(upload_id, str(project), name=f"test-scores-{uuid.uuid4()}")

        # Index repository with force=True to avoid state conflicts
        index_manager = get_shared_index_manager()
        index_manager.create_index(project, upload_id, force=True)

        response = client.post(f"/repositories/{upload_id}/quality")
        assert response.status_code == 200

        data = response.json()
        scores = data["scores"]
        for score in scores.values():
            assert 0 <= score <= 100

    def test_quality_empty_project(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test quality analysis for empty project."""
        upload_id = f"test-empty-{uuid.uuid4()}"
        project = tmp_path / "test-project"
        project.mkdir()

        # Register repository
        repository_store.register_upload(upload_id, str(project), name=f"test-empty-{uuid.uuid4()}")

        # Add minimal file to make project indexable (empty projects can't be indexed)
        (project / ".gitkeep").write_text("", encoding="utf-8")

        # Index repository with force=True to handle edge cases
        index_manager = get_shared_index_manager()
        index_manager.create_index(project, upload_id, force=True)

        response = client.post(f"/repositories/{upload_id}/quality")
        assert response.status_code == 200

        data = response.json()
        # .gitkeep will be counted as a file
        assert data["metadata"]["total_files"] >= 1
