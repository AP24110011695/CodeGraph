"""Tests for the POST /repositories/{repository_id}/scan API endpoint."""

import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from storage.repository_store import RepositoryStore

repository_store = RepositoryStore()


@pytest.fixture
def mock_extracted_dir(tmp_path: Path) -> Path:
    """Mock EXTRACTED_DIR to use tmp_path for testing."""
    with patch("app.api.scanner.EXTRACTED_DIR", tmp_path):
        yield tmp_path


@pytest.fixture
def client() -> TestClient:
    """Provide a synchronous test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def extracted_project(tmp_path: Path, mock_extracted_dir: Path) -> tuple[str, Path]:
    """Create a mock extracted project and patch EXTRACTED_DIR.

    Returns:
        A tuple of (upload_id, project_path).
    """
    upload_id = f"test-upload-{uuid.uuid4()}"
    project = mock_extracted_dir / upload_id
    project.mkdir()

    src = project / "src"
    src.mkdir()
    (src / "main.py").write_text("print('hello')", encoding="utf-8")
    (src / "app.ts").write_text("const x = 1;", encoding="utf-8")

    (project / "README.md").write_text("# Test", encoding="utf-8")

    node_modules = project / "node_modules"
    node_modules.mkdir()
    (node_modules / "pkg.js").write_text("module.exports = {};", encoding="utf-8")

    # Register repository with the exact path
    repository_store.register_upload(upload_id, str(project), name=upload_id)

    return upload_id, project


class TestScanEndpoint:
    """Tests for POST /scan/{upload_id}."""

    def test_scan_success(
        self, client: TestClient, extracted_project: tuple[str, Path]
    ) -> None:
        upload_id, _project = extracted_project

        response = client.post(f"/repositories/{upload_id}/scan")

        assert response.status_code == 200
        data = response.json()

        assert data["repository_id"] == upload_id
        assert data["status"] == "scanned"
        assert data["file_count"] == 3
        assert data["directory_count"] == 1  # src only (node_modules excluded)
        assert data["languages"]["Python"] == 1
        assert data["languages"]["TypeScript"] == 1
        assert data["languages"]["Markdown"] == 1

    def test_scan_skips_node_modules(
        self, client: TestClient, extracted_project: tuple[str, Path]
    ) -> None:
        upload_id, _project = extracted_project

        response = client.post(f"/repositories/{upload_id}/scan")

        data = response.json()
        # The scanner service should skip node_modules. We verify the file count is correct (excluding node_modules)
        assert data["file_count"] == 3  # main.py, app.ts, README.md (node_modules excluded)

    def test_scan_not_found(self, client: TestClient, tmp_path: Path) -> None:
        response = client.post("/repositories/nonexistent-id/scan")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_scan_empty_project(
        self, client: TestClient, tmp_path: Path, mock_extracted_dir: Path
    ) -> None:
        upload_id = f"empty-project-{uuid.uuid4()}"
        project = mock_extracted_dir / upload_id
        project.mkdir()

        # Register repository with the exact path
        repository_store.register_upload(upload_id, str(project), name=upload_id)

        response = client.post(f"/repositories/{upload_id}/scan")

        assert response.status_code == 200
        data = response.json()
        # Empty project should have 0 files
        assert data["file_count"] == 0
        assert data["directory_count"] == 0
        assert data["languages"] == {}

    def test_scan_response_file_fields(
        self, client: TestClient, extracted_project: tuple[str, Path]
    ) -> None:
        upload_id, _project = extracted_project

        response = client.post(f"/repositories/{upload_id}/scan")

        data = response.json()
        # Verify the response structure matches the API
        assert "repository_id" in data
        assert "status" in data
        assert "file_count" in data
        assert "directory_count" in data
        assert "languages" in data

    def test_scan_languages_sorted_descending(
        self, client: TestClient, tmp_path: Path, mock_extracted_dir: Path
    ) -> None:
        upload_id = f"sort-test-{uuid.uuid4()}"
        project = mock_extracted_dir / upload_id
        project.mkdir()

        for i in range(5):
            (project / f"file{i}.py").write_text("x = 1", encoding="utf-8")
        for i in range(3):
            (project / f"file{i}.ts").write_text("x = 1", encoding="utf-8")
        (project / "one.go").write_text("package main", encoding="utf-8")

        # Register repository with the exact path
        repository_store.register_upload(upload_id, str(project), name=upload_id)

        response = client.post(f"/repositories/{upload_id}/scan")

        data = response.json()
        keys = list(data["languages"].keys())
        assert keys == ["Python", "TypeScript", "Go"]
