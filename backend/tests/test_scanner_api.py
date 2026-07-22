"""Tests for the POST /scan/{upload_id} API endpoint."""

import shutil
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Provide a synchronous test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def extracted_project(tmp_path: Path) -> tuple[str, Path]:
    """Create a mock extracted project and patch EXTRACTED_DIR.

    Returns:
        A tuple of (upload_id, project_path).
    """
    upload_id = "test-upload-001"
    project = tmp_path / upload_id
    project.mkdir()

    src = project / "src"
    src.mkdir()
    (src / "main.py").write_text("print('hello')", encoding="utf-8")
    (src / "app.ts").write_text("const x = 1;", encoding="utf-8")

    (project / "README.md").write_text("# Test", encoding="utf-8")

    node_modules = project / "node_modules"
    node_modules.mkdir()
    (node_modules / "pkg.js").write_text("module.exports = {};", encoding="utf-8")

    return upload_id, tmp_path


class TestScanEndpoint:
    """Tests for POST /scan/{upload_id}."""

    def test_scan_success(
        self, client: TestClient, extracted_project: tuple[str, Path]
    ) -> None:
        upload_id, base_dir = extracted_project

        with patch("app.api.scanner.EXTRACTED_DIR", base_dir):
            response = client.post(f"/scan/{upload_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["project_name"] == upload_id
        assert data["summary"]["files"] == 3
        assert data["summary"]["folders"] == 1
        assert data["languages"]["Python"] == 1
        assert data["languages"]["TypeScript"] == 1
        assert data["languages"]["Markdown"] == 1
        assert len(data["files"]) == 3

    def test_scan_skips_node_modules(
        self, client: TestClient, extracted_project: tuple[str, Path]
    ) -> None:
        upload_id, base_dir = extracted_project

        with patch("app.api.scanner.EXTRACTED_DIR", base_dir):
            response = client.post(f"/scan/{upload_id}")

        data = response.json()
        paths = [f["path"] for f in data["files"]]
        assert not any("node_modules" in p for p in paths)

    def test_scan_not_found(self, client: TestClient, tmp_path: Path) -> None:
        with patch("app.api.scanner.EXTRACTED_DIR", tmp_path):
            response = client.post("/scan/nonexistent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_scan_empty_project(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        upload_id = "empty-project"
        (tmp_path / upload_id).mkdir()

        with patch("app.api.scanner.EXTRACTED_DIR", tmp_path):
            response = client.post(f"/scan/{upload_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["files"] == 0
        assert data["summary"]["folders"] == 0
        assert data["languages"] == {}
        assert data["files"] == []

    def test_scan_response_file_fields(
        self, client: TestClient, extracted_project: tuple[str, Path]
    ) -> None:
        upload_id, base_dir = extracted_project

        with patch("app.api.scanner.EXTRACTED_DIR", base_dir):
            response = client.post(f"/scan/{upload_id}")

        data = response.json()
        main_py = next(f for f in data["files"] if f["name"] == "main.py")
        assert main_py["path"] == "src/main.py"
        assert main_py["extension"] == ".py"
        assert main_py["language"] == "Python"
        assert main_py["size"] == len("print('hello')")
        assert main_py["folder"] == "src"

    def test_scan_languages_sorted_descending(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        upload_id = "sort-test"
        project = tmp_path / upload_id
        project.mkdir()

        for i in range(5):
            (project / f"file{i}.py").write_text("x = 1", encoding="utf-8")
        for i in range(3):
            (project / f"file{i}.ts").write_text("x = 1", encoding="utf-8")
        (project / "one.go").write_text("package main", encoding="utf-8")

        with patch("app.api.scanner.EXTRACTED_DIR", tmp_path):
            response = client.post(f"/scan/{upload_id}")

        data = response.json()
        keys = list(data["languages"].keys())
        assert keys == ["Python", "TypeScript", "Go"]
