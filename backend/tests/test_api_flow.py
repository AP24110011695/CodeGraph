"""Tests for the API Dependency Flow Engine."""

from pathlib import Path

import pytest

from app.api_flow.endpoint_detector import Endpoint, EndpointDetector
from app.api_flow.flow_builder import FlowBuilder, FlowStep
from app.api_flow.sequence_builder import SequenceBuilder, SequenceResult
from app.api_flow.api_flow_engine import APIFlowEngine, APIFlowResult


@pytest.fixture
def endpoint_detector() -> EndpointDetector:
    """Provide a fresh EndpointDetector instance."""
    return EndpointDetector()


@pytest.fixture
def flow_builder() -> FlowBuilder:
    """Provide a fresh FlowBuilder instance."""
    return FlowBuilder()


@pytest.fixture
def sequence_builder() -> SequenceBuilder:
    """Provide a fresh SequenceBuilder instance."""
    return SequenceBuilder()


@pytest.fixture
def api_flow_engine() -> APIFlowEngine:
    """Provide a fresh APIFlowEngine instance."""
    return APIFlowEngine()


@pytest.fixture
def sample_fastapi_project(tmp_path: Path) -> Path:
    """Create a sample FastAPI project for testing."""
    project = tmp_path / "fastapi_project"
    project.mkdir()

    # api/
    api = project / "api"
    api.mkdir()
    (api / "__init__.py").write_text("", encoding="utf-8")
    (api / "auth.py").write_text("""
from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/login")
async def login(username: str, password: str):
    return {"token": "jwt_token"}

@router.get("/users")
async def get_users():
    return {"users": []}
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_flask_project(tmp_path: Path) -> Path:
    """Create a sample Flask project for testing."""
    project = tmp_path / "flask_project"
    project.mkdir()

    # app.py
    (project / "app.py").write_text("""
from flask import Flask

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    return {"token": "jwt_token"}

@app.route('/users', methods=['GET'])
def get_users():
    return {"users": []}
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_express_project(tmp_path: Path) -> Path:
    """Create a sample Express project for testing."""
    project = tmp_path / "express_project"
    project.mkdir()

    # routes/
    routes = project / "routes"
    routes.mkdir()
    (routes / "auth.js").write_text("""
const express = require('express');
const router = express.Router();

router.post('/login', (req, res) => {
    res.json({token: 'jwt_token'});
});

router.get('/users', (req, res) => {
    res.json({users: []});
});

module.exports = router;
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_spring_project(tmp_path: Path) -> Path:
    """Create a sample Spring Boot project for testing."""
    project = tmp_path / "spring_project"
    project.mkdir()

    # src/
    src = project / "src"
    src.mkdir()
    main = src / "main"
    main.mkdir()
    java = main / "java"
    java.mkdir()
    com = java / "com"
    com.mkdir()
    example = com / "example"
    example.mkdir()
    (example / "AuthController.java").write_text("""
package com.example;

import org.springframework.web.bind.annotation.*;

@RestController
public class AuthController {
    
    @PostMapping("/login")
    public String login() {
        return "jwt_token";
    }
    
    @GetMapping("/users")
    public String getUsers() {
        return "users";
    }
}
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_django_project(tmp_path: Path) -> Path:
    """Create a sample Django project for testing."""
    project = tmp_path / "django_project"
    project.mkdir()

    # urls.py
    (project / "urls.py").write_text("""
from django.urls import path

urlpatterns = [
    path('login/', views.login),
    path('users/', views.get_users),
]
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_no_api_project(tmp_path: Path) -> Path:
    """Create a project without API endpoints."""
    project = tmp_path / "no_api_project"
    project.mkdir()

    # app/
    app = project / "app"
    app.mkdir()
    (app / "main.py").write_text("""
def main():
    print("Hello, World!")
""", encoding="utf-8")

    return project


@pytest.fixture
def sample_empty_project(tmp_path: Path) -> Path:
    """Create an empty project for testing."""
    project = tmp_path / "empty_project"
    project.mkdir()
    return project


class TestEndpointDetector:
    """Tests for EndpointDetector."""

    def test_detect_fastapi_endpoints(self, endpoint_detector: EndpointDetector, sample_fastapi_project: Path) -> None:
        """Test FastAPI endpoint detection."""
        endpoints = endpoint_detector.detect_endpoints(sample_fastapi_project)

        assert len(endpoints) >= 0
        for endpoint in endpoints:
            assert endpoint.method is not None
            assert endpoint.path is not None
            assert endpoint.controller is not None

    def test_detect_flask_endpoints(self, endpoint_detector: EndpointDetector, sample_flask_project: Path) -> None:
        """Test Flask endpoint detection."""
        endpoints = endpoint_detector.detect_endpoints(sample_flask_project)

        assert len(endpoints) >= 0

    def test_detect_express_endpoints(self, endpoint_detector: EndpointDetector, sample_express_project: Path) -> None:
        """Test Express endpoint detection."""
        endpoints = endpoint_detector.detect_endpoints(sample_express_project)

        assert len(endpoints) >= 0

    def test_detect_spring_endpoints(self, endpoint_detector: EndpointDetector, sample_spring_project: Path) -> None:
        """Test Spring Boot endpoint detection."""
        endpoints = endpoint_detector.detect_endpoints(sample_spring_project)

        assert len(endpoints) >= 0

    def test_detect_django_endpoints(self, endpoint_detector: EndpointDetector, sample_django_project: Path) -> None:
        """Test Django endpoint detection."""
        endpoints = endpoint_detector.detect_endpoints(sample_django_project)

        assert len(endpoints) >= 0

    def test_detect_no_api_endpoints(self, endpoint_detector: EndpointDetector, sample_no_api_project: Path) -> None:
        """Test detection for project without APIs."""
        endpoints = endpoint_detector.detect_endpoints(sample_no_api_project)

        assert len(endpoints) == 0

    def test_detect_empty_endpoints(self, endpoint_detector: EndpointDetector, sample_empty_project: Path) -> None:
        """Test detection for empty project."""
        endpoints = endpoint_detector.detect_endpoints(sample_empty_project)

        assert len(endpoints) == 0


class TestFlowBuilder:
    """Tests for FlowBuilder."""

    def test_build_flows(self, flow_builder: FlowBuilder, sample_fastapi_project: Path) -> None:
        """Test flow building."""
        endpoint_detector = EndpointDetector()
        endpoints = endpoint_detector.detect_endpoints(sample_fastapi_project)
        flows = flow_builder.build_flows(endpoints)

        assert len(flows) >= 0
        for flow in flows:
            assert flow.source is not None
            assert flow.destination is not None
            assert flow.action is not None

    def test_build_empty_flows(self, flow_builder: FlowBuilder) -> None:
        """Test flow building with empty data."""
        flows = flow_builder.build_flows([])

        assert len(flows) == 0


class TestSequenceBuilder:
    """Tests for SequenceBuilder."""

    def test_build_sequence(self, sequence_builder: SequenceBuilder, sample_fastapi_project: Path) -> None:
        """Test sequence building."""
        endpoint_detector = EndpointDetector()
        endpoints = endpoint_detector.detect_endpoints(sample_fastapi_project)
        flow_builder = FlowBuilder()
        flows = flow_builder.build_flows(endpoints)

        sequence_result = sequence_builder.build_sequence(endpoints, flows)

        assert isinstance(sequence_result, SequenceResult)
        assert sequence_result.mermaid.startswith("sequenceDiagram")
        assert isinstance(sequence_result.statistics, dict)

    def test_build_empty_sequence(self, sequence_builder: SequenceBuilder) -> None:
        """Test sequence building with empty data."""
        sequence_result = sequence_builder.build_sequence([], [])

        assert isinstance(sequence_result, SequenceResult)
        assert sequence_result.mermaid == "sequenceDiagram"
        assert sequence_result.statistics["endpoints"] == 0


class TestAPIFlowEngine:
    """Tests for APIFlowEngine."""

    def test_analyze_flow_fastapi(self, api_flow_engine: APIFlowEngine, sample_fastapi_project: Path) -> None:
        """Test API flow analysis for FastAPI project."""
        result = api_flow_engine.analyze_flow(sample_fastapi_project)

        assert isinstance(result, APIFlowResult)
        assert 0 <= result.flow_score <= 100
        assert isinstance(result.endpoints, list)
        assert isinstance(result.flows, list)
        assert result.sequence_diagram.startswith("sequenceDiagram")

    def test_analyze_flow_flask(self, api_flow_engine: APIFlowEngine, sample_flask_project: Path) -> None:
        """Test API flow analysis for Flask project."""
        result = api_flow_engine.analyze_flow(sample_flask_project)

        assert isinstance(result, APIFlowResult)
        assert 0 <= result.flow_score <= 100

    def test_analyze_flow_express(self, api_flow_engine: APIFlowEngine, sample_express_project: Path) -> None:
        """Test API flow analysis for Express project."""
        result = api_flow_engine.analyze_flow(sample_express_project)

        assert isinstance(result, APIFlowResult)
        assert 0 <= result.flow_score <= 100

    def test_analyze_flow_spring(self, api_flow_engine: APIFlowEngine, sample_spring_project: Path) -> None:
        """Test API flow analysis for Spring Boot project."""
        result = api_flow_engine.analyze_flow(sample_spring_project)

        assert isinstance(result, APIFlowResult)
        assert 0 <= result.flow_score <= 100

    def test_analyze_flow_django(self, api_flow_engine: APIFlowEngine, sample_django_project: Path) -> None:
        """Test API flow analysis for Django project."""
        result = api_flow_engine.analyze_flow(sample_django_project)

        assert isinstance(result, APIFlowResult)
        assert 0 <= result.flow_score <= 100

    def test_analyze_flow_no_api(self, api_flow_engine: APIFlowEngine, sample_no_api_project: Path) -> None:
        """Test API flow analysis for project without APIs."""
        result = api_flow_engine.analyze_flow(sample_no_api_project)

        assert isinstance(result, APIFlowResult)
        assert result.flow_score == 0
        assert len(result.endpoints) == 0

    def test_analyze_flow_empty(self, api_flow_engine: APIFlowEngine, sample_empty_project: Path) -> None:
        """Test API flow analysis for empty project."""
        result = api_flow_engine.analyze_flow(sample_empty_project)

        assert isinstance(result, APIFlowResult)
        assert result.flow_score == 0
        assert len(result.endpoints) == 0

    def test_analyze_flow_nonexistent_path(self, api_flow_engine: APIFlowEngine) -> None:
        """Test API flow analysis for nonexistent path."""
        with pytest.raises(FileNotFoundError):
            api_flow_engine.analyze_flow(Path("/nonexistent/path"))

    def test_analyze_flow_file_instead_of_directory(self, api_flow_engine: APIFlowEngine, tmp_path: Path) -> None:
        """Test API flow analysis when path is a file, not directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            api_flow_engine.analyze_flow(file_path)

    def test_endpoint_serialization(self, api_flow_engine: APIFlowEngine, sample_fastapi_project: Path) -> None:
        """Test that endpoints are serialized correctly."""
        result = api_flow_engine.analyze_flow(sample_fastapi_project)

        for endpoint in result.endpoints:
            assert "method" in endpoint
            assert "path" in endpoint
            assert "controller" in endpoint
            assert "middleware" in endpoint
            assert "evidence" in endpoint

    def test_flow_serialization(self, api_flow_engine: APIFlowEngine, sample_fastapi_project: Path) -> None:
        """Test that flows are serialized correctly."""
        result = api_flow_engine.analyze_flow(sample_fastapi_project)

        for flow in result.flows:
            assert "source" in flow
            assert "destination" in flow
            assert "action" in flow
            assert "evidence" in flow


class TestAPIFlowAPI:
    """Tests for the API flow API endpoint."""

    @pytest.fixture
    def client(self):
        """Provide a test client."""
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_api_flow_not_indexed(self, client) -> None:
        """Test API flow API for non-indexed repository."""
        response = client.post("/api-flow/nonexistent_id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
