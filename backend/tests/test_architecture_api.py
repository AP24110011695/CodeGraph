"""Tests for the architecture analysis API endpoint."""

import json
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

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


class TestArchitectureAPI:
    """Tests for GET /architecture/{upload_id}."""

    def test_architecture_endpoint_success(
        self, client: TestClient, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test successful architecture analysis."""
        upload_id = "test-upload-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("from fastapi import FastAPI", encoding="utf-8")

        # Copy to extracted directory
        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        scan_result = scanner.scan(extracted_project)

        with patch("app.api.architecture.scanner_service.scan") as mock_scan:
            mock_scan.return_value = scan_result

            with patch("app.api.architecture.detector_service.detect") as mock_detect:
                from app.services.framework_detector import DetectionResult
                mock_detect.return_value = DetectionResult()

                with patch("app.api.architecture.graph_builder.build") as mock_graph:
                    from app.services.dependency_graph import GraphResult
                    mock_graph.return_value = GraphResult()

                    with patch("app.api.architecture.ParserEngine.parse_project") as mock_parse:
                        from app.parsers.ast_models import ProjectParsingResult
                        mock_parse.return_value = ProjectParsingResult(
                            project={"name": "test-project", "root_path": str(project), "total_files": 1}
                        )

                        with patch("app.api.architecture.architecture_builder.build") as mock_build:
                            from app.analyzers.architecture_models import ArchitectureResult
                            mock_build.return_value = ArchitectureResult(
                                project={"name": "test-project", "root_path": str(project)},
                                layers=["Backend"],
                                modules=[],
                                relationships=[],
                                statistics={"modules": 0, "components": 0, "relationships": 0},
                            )

                            response = client.get(f"/architecture/{upload_id}")

                            assert response.status_code == 200
                            data = response.json()
                            assert "project" in data
                            assert "layers" in data
                            assert "modules" in data
                            assert "relationships" in data
                            assert "statistics" in data

    def test_architecture_project_not_found(self, client: TestClient) -> None:
        """Test 404 when project does not exist."""
        response = client.get("/architecture/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_architecture_permission_denied(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test 403 when permission is denied during scanning."""
        upload_id = "test-permission-id"
        project = tmp_path / "test-project"
        project.mkdir()
        
        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        with patch("app.api.architecture.scanner_service.scan") as mock_scan:
            mock_scan.side_effect = PermissionError("Access denied")

            response = client.get(f"/architecture/{upload_id}")
            assert response.status_code == 403
            assert "permission denied" in response.json()["detail"].lower()

    def test_architecture_detection_error(
        self, client: TestClient, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test 500 when framework detection fails."""
        upload_id = "test-detection-error-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')", encoding="utf-8")
        
        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        scan_result = scanner.scan(extracted_project)

        with patch("app.api.architecture.scanner_service.scan") as mock_scan:
            mock_scan.return_value = scan_result

            with patch("app.api.architecture.detector_service.detect") as mock_detect:
                mock_detect.side_effect = Exception("Detection failed")

                response = client.get(f"/architecture/{upload_id}")
                assert response.status_code == 500

    def test_architecture_graph_error(
        self, client: TestClient, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test 500 when dependency graph building fails."""
        upload_id = "test-graph-error-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')", encoding="utf-8")
        
        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        scan_result = scanner.scan(extracted_project)

        with patch("app.api.architecture.scanner_service.scan") as mock_scan:
            mock_scan.return_value = scan_result

            with patch("app.api.architecture.detector_service.detect") as mock_detect:
                from app.services.framework_detector import DetectionResult
                mock_detect.return_value = DetectionResult()

                with patch("app.api.architecture.graph_builder.build") as mock_graph:
                    mock_graph.side_effect = Exception("Graph build failed")

                    response = client.get(f"/architecture/{upload_id}")
                    assert response.status_code == 500

    def test_architecture_parser_error(
        self, client: TestClient, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test 500 when parsing fails."""
        upload_id = "test-parser-error-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')", encoding="utf-8")
        
        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        scan_result = scanner.scan(extracted_project)

        with patch("app.api.architecture.scanner_service.scan") as mock_scan:
            mock_scan.return_value = scan_result

            with patch("app.api.architecture.detector_service.detect") as mock_detect:
                from app.services.framework_detector import DetectionResult
                mock_detect.return_value = DetectionResult()

                with patch("app.api.architecture.graph_builder.build") as mock_graph:
                    from app.services.dependency_graph import GraphResult
                    mock_graph.return_value = GraphResult()

                    with patch("app.api.architecture.ParserEngine.parse_project") as mock_parse:
                        mock_parse.side_effect = Exception("Parse failed")

                        response = client.get(f"/architecture/{upload_id}")
                        assert response.status_code == 500

    def test_architecture_builder_error(
        self, client: TestClient, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test 500 when architecture building fails."""
        upload_id = "test-builder-error-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')", encoding="utf-8")
        
        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        scan_result = scanner.scan(extracted_project)

        with patch("app.api.architecture.scanner_service.scan") as mock_scan:
            mock_scan.return_value = scan_result

            with patch("app.api.architecture.detector_service.detect") as mock_detect:
                from app.services.framework_detector import DetectionResult
                mock_detect.return_value = DetectionResult()

                with patch("app.api.architecture.graph_builder.build") as mock_graph:
                    from app.services.dependency_graph import GraphResult
                    mock_graph.return_value = GraphResult()

                with patch("app.api.architecture.ParserEngine.parse_project") as mock_parse:
                    from app.parsers.ast_models import ProjectParsingResult
                    mock_parse.return_value = ProjectParsingResult(
                        project={"name": "test-project", "root_path": str(extracted_project), "total_files": 1}
                    )

                    with patch("app.api.architecture.architecture_builder.build") as mock_build:
                        mock_build.side_effect = Exception("Architecture build failed")

                        response = client.get(f"/architecture/{upload_id}")
                        assert response.status_code == 500

    def test_architecture_response_structure(
        self, client: TestClient, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test that the response structure matches the schema."""
        upload_id = "test-response-structure-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')", encoding="utf-8")
        
        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        scan_result = scanner.scan(extracted_project)

        with patch("app.api.architecture.scanner_service.scan") as mock_scan:
            mock_scan.return_value = scan_result

            with patch("app.api.architecture.detector_service.detect") as mock_detect:
                from app.services.framework_detector import DetectionResult
                mock_detect.return_value = DetectionResult()

            with patch("app.api.architecture.graph_builder.build") as mock_graph:
                from app.services.dependency_graph import GraphResult
                mock_graph.return_value = GraphResult()

            with patch("app.api.architecture.ParserEngine.parse_project") as mock_parse:
                from app.parsers.ast_models import ProjectParsingResult
                mock_parse.return_value = ProjectParsingResult(
                    project={"name": "test-project", "root_path": str(extracted_project), "total_files": 1}
                )

                with patch("app.api.architecture.architecture_builder.build") as mock_build:
                    from app.analyzers.architecture_models import ArchitectureResult, ArchitectureModule, Component
                    mock_build.return_value = ArchitectureResult(
                        project={"name": "test-project", "root_path": str(extracted_project)},
                        layers=["Backend"],
                        modules=[
                            ArchitectureModule(
                                name="Test",
                                type="Backend Module",
                                files=["main.py"],
                                components=[Component(name="Main", type="Controller", file_path="main.py", language="Python")],
                                layer="Backend",
                            )
                        ],
                        relationships=[],
                        statistics={"modules": 1, "components": 1, "relationships": 0},
                    )

                    response = client.get(f"/architecture/{upload_id}")
                    assert response.status_code == 200

                    data = response.json()
                    assert data["project"]["name"] == "test-project"
                    assert data["layers"] == ["Backend"]
                    assert len(data["modules"]) == 1
                    assert data["modules"][0]["name"] == "Test"
                    assert data["modules"][0]["type"] == "Backend Module"
                    assert len(data["modules"][0]["components"]) == 1
                    assert data["statistics"]["modules"] == 1
                    assert data["statistics"]["components"] == 1
