"""Tests for the GET /frameworks/{upload_id} API endpoint."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def extracted_project(tmp_path: Path) -> tuple[str, Path]:
    """Create a mock extracted project for detection."""
    upload_id = "test-upload-002"
    project = tmp_path / upload_id
    project.mkdir()

    src = project / "src"
    src.mkdir()
    (src / "main.py").write_text("from fastapi import FastAPI\napp = FastAPI()", encoding="utf-8")
    (src / "App.tsx").write_text("export default function App() {}", encoding="utf-8")

    (project / "package.json").write_text(
        json.dumps({"dependencies": {"react": "^18", "express": "^4"}}), encoding="utf-8"
    )
    (project / "requirements.txt").write_text("fastapi\nuvicorn\n", encoding="utf-8")
    (project / "Dockerfile").write_text("FROM python:3.12", encoding="utf-8")
    (project / "yarn.lock").write_text("", encoding="utf-8")

    return upload_id, tmp_path


class TestFrameworkEndpoint:
    def test_detect_frameworks_success(
        self, client: TestClient, extracted_project: tuple[str, Path]
    ) -> None:
        upload_id, base_dir = extracted_project

        with patch("app.api.framework.EXTRACTED_DIR", base_dir):
            response = client.get(f"/frameworks/{upload_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["project"]["name"] == upload_id
        assert data["project"]["root_path"] == str((base_dir / upload_id).resolve())
        assert data["summary"]["files"] == 6
        assert data["summary"]["folders"] == 1
        
        assert data["languages"]["Python"] == 1
        assert data["languages"]["TypeScript"] == 1
        assert data["languages"]["JSON"] == 1
        assert data["languages"]["Docker"] == 1

        frameworks = {f["name"]: f["confidence"] for f in data["frameworks"]}
        assert "React" in frameworks
        assert frameworks["React"] == 95

        backend = {b["name"]: b["confidence"] for b in data["backend"]}
        assert "FastAPI" in backend
        assert "Express" in backend

        assert "yarn" in data["package_managers"]
        assert "pip" in data["package_managers"]
        assert data["containerized"] is True
        
        assert "python" in data["parser_targets"]
        assert "typescript" in data["parser_targets"]

    def test_detect_not_found(self, client: TestClient, tmp_path: Path) -> None:
        with patch("app.api.framework.EXTRACTED_DIR", tmp_path):
            response = client.get("/frameworks/nonexistent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_detect_not_a_directory(self, client: TestClient, tmp_path: Path) -> None:
        upload_id = "test-file"
        file_path = tmp_path / upload_id
        file_path.write_text("not a dir", encoding="utf-8")

        with patch("app.api.framework.EXTRACTED_DIR", tmp_path):
            response = client.get(f"/frameworks/{upload_id}")

        assert response.status_code == 400
        assert "not a directory" in response.json()["detail"].lower()
