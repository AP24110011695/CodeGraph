"""Tests for the POST /apidocs/{upload_id} API endpoint."""

import json
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
def fastapi_project(tmp_path: Path) -> tuple[str, Path]:
    """Create a mock FastAPI project for API documentation generation."""
    upload_id = "test-fastapi-001"
    project = tmp_path / upload_id
    project.mkdir()

    src = project / "src"
    src.mkdir()

    # Create a FastAPI app file with endpoints
    main_py = """
from fastapi import FastAPI, Depends
from pydantic import BaseModel

app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

@app.post("/login")
async def login_user(request: LoginRequest) -> TokenResponse:
    return {"access_token": "test", "token_type": "bearer"}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

@app.get("/items")
async def get_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
"""
    (src / "main.py").write_text(main_py, encoding="utf-8")

    (project / "requirements.txt").write_text("fastapi\nuvicorn\n", encoding="utf-8")

    return upload_id, tmp_path


@pytest.fixture
def flask_project(tmp_path: Path) -> tuple[str, Path]:
    """Create a mock Flask project for API documentation generation."""
    upload_id = "test-flask-001"
    project = tmp_path / upload_id
    project.mkdir()

    src = project / "src"
    src.mkdir()

    # Create a Flask app file with endpoints
    app_py = """
from flask import Flask

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    return {'status': 'ok'}

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return {'user_id': user_id}
"""
    (src / "app.py").write_text(app_py, encoding="utf-8")

    (project / "requirements.txt").write_text("flask\n", encoding="utf-8")

    return upload_id, tmp_path


@pytest.fixture
def express_project(tmp_path: Path) -> tuple[str, Path]:
    """Create a mock Express project for API documentation generation."""
    upload_id = "test-express-001"
    project = tmp_path / upload_id
    project.mkdir()

    src = project / "src"
    src.mkdir()

    # Create an Express app file with endpoints
    server_js = """
const express = require('express');
const app = express();

app.get('/users', (req, res) => {
    res.json({users: []});
});

app.post('/login', (req, res) => {
    res.json({token: 'test'});
});

app.listen(3000);
"""
    (src / "server.js").write_text(server_js, encoding="utf-8")

    (project / "package.json").write_text(
        json.dumps({"dependencies": {"express": "^4"}}), encoding="utf-8"
    )

    return upload_id, tmp_path


@pytest.fixture
def no_backend_project(tmp_path: Path) -> tuple[str, Path]:
    """Create a project with no backend framework."""
    upload_id = "test-no-backend"
    project = tmp_path / upload_id
    project.mkdir()

    (project / "index.html").write_text("<html></html>", encoding="utf-8")

    return upload_id, tmp_path


@pytest.fixture
def empty_project(tmp_path: Path) -> tuple[str, Path]:
    """Create an empty project."""
    upload_id = "test-empty"
    project = tmp_path / upload_id
    project.mkdir()

    return upload_id, tmp_path


class TestApiDocsEndpoint:
    """Tests for POST /apidocs/{upload_id}."""

    def test_fastapi_json_response(
        self, client: TestClient, fastapi_project: tuple[str, Path]
    ) -> None:
        """Test JSON response for FastAPI project."""
        upload_id, base_dir = fastapi_project

        with patch("app.api.apidocs.EXTRACTED_DIR", base_dir):
            response = client.post(f"/apidocs/{upload_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["framework"] == "FastAPI"
        assert data["total_endpoints"] > 0
        assert len(data["endpoints"]) > 0

        # Check endpoint structure
        endpoint = data["endpoints"][0]
        assert "method" in endpoint
        assert "path" in endpoint
        assert "handler" in endpoint

    def test_fastapi_download_mode(
        self, client: TestClient, fastapi_project: tuple[str, Path]
    ) -> None:
        """Test markdown download mode for FastAPI project."""
        upload_id, base_dir = fastapi_project

        with patch("app.api.apidocs.EXTRACTED_DIR", base_dir):
            response = client.post(f"/apidocs/{upload_id}?download=true")

        assert response.status_code == 200
        # Response should be markdown string, not JSON
        content = response.text
        assert "# API Documentation" in content
        assert "FastAPI" in content

    def test_flask_json_response(
        self, client: TestClient, flask_project: tuple[str, Path]
    ) -> None:
        """Test JSON response for Flask project."""
        upload_id, base_dir = flask_project

        with patch("app.api.apidocs.EXTRACTED_DIR", base_dir):
            response = client.post(f"/apidocs/{upload_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["framework"] == "Flask"
        assert data["total_endpoints"] > 0

    def test_express_json_response(
        self, client: TestClient, express_project: tuple[str, Path]
    ) -> None:
        """Test JSON response for Express project."""
        upload_id, base_dir = express_project

        with patch("app.api.apidocs.EXTRACTED_DIR", base_dir):
            response = client.post(f"/apidocs/{upload_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["framework"] == "Express"
        assert data["total_endpoints"] > 0

    def test_no_backend_framework(
        self, client: TestClient, no_backend_project: tuple[str, Path]
    ) -> None:
        """Test response when no API framework is detected."""
        upload_id, base_dir = no_backend_project

        with patch("app.api.apidocs.EXTRACTED_DIR", base_dir):
            response = client.post(f"/apidocs/{upload_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["framework"] == "None"
        assert data["total_endpoints"] == 0
        assert len(data["endpoints"]) == 0

    def test_no_backend_download_mode(
        self, client: TestClient, no_backend_project: tuple[str, Path]
    ) -> None:
        """Test markdown download mode when no framework is detected."""
        upload_id, base_dir = no_backend_project

        with patch("app.api.apidocs.EXTRACTED_DIR", base_dir):
            response = client.post(f"/apidocs/{upload_id}?download=true")

        assert response.status_code == 200
        content = response.text
        assert "No API framework detected" in content

    def test_empty_project(
        self, client: TestClient, empty_project: tuple[str, Path]
    ) -> None:
        """Test response for empty project."""
        upload_id, base_dir = empty_project

        with patch("app.api.apidocs.EXTRACTED_DIR", base_dir):
            response = client.post(f"/apidocs/{upload_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["total_endpoints"] == 0

    def test_repository_not_found(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test 404 error when repository is not found."""
        with patch("app.api.apidocs.EXTRACTED_DIR", tmp_path):
            response = client.post("/apidocs/nonexistent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_not_a_directory(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test 400 error when path is not a directory."""
        upload_id = "test-file"
        file_path = tmp_path / upload_id
        file_path.write_text("not a dir", encoding="utf-8")

        with patch("app.api.apidocs.EXTRACTED_DIR", tmp_path):
            response = client.post(f"/apidocs/{upload_id}")

        assert response.status_code == 400
        assert "not a directory" in response.json()["detail"].lower()

    def test_endpoint_structure(
        self, client: TestClient, fastapi_project: tuple[str, Path]
    ) -> None:
        """Test that endpoint structure matches schema."""
        upload_id, base_dir = fastapi_project

        with patch("app.api.apidocs.EXTRACTED_DIR", base_dir):
            response = client.post(f"/apidocs/{upload_id}")

        data = response.json()
        endpoint = data["endpoints"][0]

        # Verify all expected fields
        expected_fields = [
            "method", "path", "handler", "controller", "authentication",
            "middleware", "request", "response", "tags", "parameters",
            "query_params", "path_params", "file_path"
        ]

        for field in expected_fields:
            assert field in endpoint

    def test_markdown_format(
        self, client: TestClient, fastapi_project: tuple[str, Path]
    ) -> None:
        """Test that markdown output is properly formatted."""
        upload_id, base_dir = fastapi_project

        with patch("app.api.apidocs.EXTRACTED_DIR", base_dir):
            response = client.post(f"/apidocs/{upload_id}?download=true")

        content = response.text

        # Check for markdown headers
        assert "# API Documentation" in content
        assert "##" in content or "###" in content

        # Check for endpoint information
        assert "GET" in content or "POST" in content

    def test_large_repository(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test handling of a repository with many files."""
        upload_id = "test-large"
        project = tmp_path / upload_id
        project.mkdir()

        src = project / "src"
        src.mkdir()

        # Create many Python files
        for i in range(50):
            (src / f"file{i}.py").write_text("def test(): pass", encoding="utf-8")

        (project / "requirements.txt").write_text("fastapi\n", encoding="utf-8")

        with patch("app.api.apidocs.EXTRACTED_DIR", tmp_path):
            response = client.post(f"/apidocs/{upload_id}")

        assert response.status_code == 200
        data = response.json()
        # Should complete without error even with many files
        assert "framework" in data

    def test_no_endpoints_detected(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test when framework is detected but no endpoints are found."""
        upload_id = "test-no-endpoints"
        project = tmp_path / upload_id
        project.mkdir()

        # FastAPI but no routes
        (project / "main.py").write_text(
            "from fastapi import FastAPI\napp = FastAPI()\n# No routes defined",
            encoding="utf-8"
        )
        (project / "requirements.txt").write_text("fastapi\n", encoding="utf-8")

        with patch("app.api.apidocs.EXTRACTED_DIR", tmp_path):
            response = client.post(f"/apidocs/{upload_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["framework"] == "FastAPI"
        assert data["total_endpoints"] == 0

    def test_no_endpoints_download_mode(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test markdown download mode when no endpoints are detected."""
        upload_id = "test-no-endpoints"
        project = tmp_path / upload_id
        project.mkdir()

        (project / "main.py").write_text(
            "from fastapi import FastAPI\napp = FastAPI()",
            encoding="utf-8"
        )
        (project / "requirements.txt").write_text("fastapi\n", encoding="utf-8")

        with patch("app.api.apidocs.EXTRACTED_DIR", tmp_path):
            response = client.post(f"/apidocs/{upload_id}?download=true")

        assert response.status_code == 200
        content = response.text
        assert "No public API endpoints detected" in content
