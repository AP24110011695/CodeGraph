"""Tests for the POST /smells/{upload_id} API endpoint."""

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


class TestSmellsApiEndpoint:
    """Tests for POST /smells/{upload_id}."""

    def test_smells_endpoint_success(
        self, client: TestClient, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test successful smell detection."""
        upload_id = "test-smells-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("from fastapi import FastAPI", encoding="utf-8")

        # Copy to extracted directory
        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        response = client.post(f"/smells/{upload_id}")

        assert response.status_code == 200
        data = response.json()
        assert "technical_debt" in data
        assert "estimated_effort" in data
        assert "summary" in data
        assert "smells" in data
        assert "total_smells" in data["summary"]
        assert "critical" in data["summary"]
        assert "major" in data["summary"]
        assert "minor" in data["summary"]

    def test_smells_project_not_found(self, client: TestClient) -> None:
        """Test 404 when project does not exist."""
        response = client.post("/smells/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_smells_permission_denied(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test 403 when permission is denied during scanning."""
        upload_id = "test-permission-id"
        project = tmp_path / "test-project"
        project.mkdir()

        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        with patch("app.api.smells.scanner_service.scan") as mock_scan:
            mock_scan.side_effect = PermissionError("Access denied")

            response = client.post(f"/smells/{upload_id}")
            assert response.status_code == 403
            assert "permission denied" in response.json()["detail"].lower()

    def test_smells_detection_error(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test 500 when smell detection fails."""
        upload_id = "test-error-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')", encoding="utf-8")

        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        with patch("app.api.smells.smell_detector.detect") as mock_detect:
            mock_detect.side_effect = Exception("Detection failed")

            response = client.post(f"/smells/{upload_id}")
            assert response.status_code == 500

    def test_smells_response_structure(
        self, client: TestClient, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test that the response structure matches the schema."""
        upload_id = "test-structure-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')", encoding="utf-8")

        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        response = client.post(f"/smells/{upload_id}")
        assert response.status_code == 200

        data = response.json()
        # Check summary structure
        assert "total_smells" in data["summary"]
        assert "critical" in data["summary"]
        assert "major" in data["summary"]
        assert "minor" in data["summary"]

        # Check smells structure
        if data["smells"]:
            smell = data["smells"][0]
            assert "type" in smell
            assert "severity" in smell
            assert "file" in smell
            assert "description" in smell

    def test_smells_empty_project(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test smell detection for empty project."""
        upload_id = "test-empty-id"
        project = tmp_path / "test-project"
        project.mkdir()

        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        response = client.post(f"/smells/{upload_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["summary"]["total_smells"] >= 0
        assert data["technical_debt"] in ["low", "medium", "high", "critical"]

    def test_smells_large_function(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test detection of large function smell."""
        upload_id = "test-large-function"
        project = tmp_path / "test-project"
        project.mkdir()

        # Create a file with many functions
        code = "\n".join([f"def func{i}(): pass" for i in range(60)])
        (project / "large.py").write_text(code, encoding="utf-8")

        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        response = client.post(f"/smells/{upload_id}")
        assert response.status_code == 200

        data = response.json()
        # Should detect large function smell
        smell_types = [s["type"] for s in data["smells"]]
        assert "Large Function" in smell_types

    def test_smells_no_smells(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test project with no smells."""
        upload_id = "test-no-smells"
        project = tmp_path / "test-project"
        project.mkdir()

        # Create a simple, clean file
        (project / "clean.py").write_text("def hello(): return 'world'", encoding="utf-8")

        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        response = client.post(f"/smells/{upload_id}")
        assert response.status_code == 200

        data = response.json()
        # May have some smells due to missing docs, but should be minimal
        assert data["technical_debt"] in ["low", "medium"]
