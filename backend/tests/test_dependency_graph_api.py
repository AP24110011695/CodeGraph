"""Tests for the GET /dependency-graph/{upload_id} API endpoint."""

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
    upload_id = "test-upload-003"
    project = tmp_path / upload_id
    project.mkdir()

    src = project / "src"
    src.mkdir()
    
    (src / "main.py").write_text("import utils.logger", encoding="utf-8")
    
    utils = project / "utils"
    utils.mkdir()
    (utils / "logger.py").write_text("", encoding="utf-8")
    
    (project / "isolated.py").write_text("", encoding="utf-8")

    return upload_id, tmp_path


class TestDependencyGraphEndpoint:
    def test_build_graph_success(
        self, client: TestClient, extracted_project: tuple[str, Path]
    ) -> None:
        upload_id, base_dir = extracted_project

        with patch("app.api.dependency_graph.EXTRACTED_DIR", base_dir):
            response = client.get(f"/dependency-graph/{upload_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["project"]["name"] == upload_id
        assert data["summary"]["files"] == 3
        
        assert len(data["nodes"]) == 3
        
        edges = data["edges"]
        assert len(edges) == 1
        assert edges[0]["from"] == "src/main.py"
        assert edges[0]["to"] == "utils/logger.py"
        assert edges[0]["type"] == "import"

        assert data["statistics"]["nodes"] == 3
        assert data["statistics"]["edges"] == 1
        assert data["statistics"]["isolated_files"] == 1

    def test_build_not_found(self, client: TestClient, tmp_path: Path) -> None:
        with patch("app.api.dependency_graph.EXTRACTED_DIR", tmp_path):
            response = client.get("/dependency-graph/nonexistent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_build_not_a_directory(self, client: TestClient, tmp_path: Path) -> None:
        upload_id = "test-file"
        file_path = tmp_path / upload_id
        file_path.write_text("not a dir", encoding="utf-8")

        with patch("app.api.dependency_graph.EXTRACTED_DIR", tmp_path):
            response = client.get(f"/dependency-graph/{upload_id}")

        assert response.status_code == 400
        assert "not a directory" in response.json()["detail"].lower()
