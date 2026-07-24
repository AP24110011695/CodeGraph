"""Tests for the diagram generation API endpoint."""

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


class TestDiagramsAPI:
    """Tests for GET /diagrams/{upload_id}."""

    def test_diagrams_endpoint_success(
        self, client: TestClient, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test successful diagram generation."""
        upload_id = "test-upload-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("from fastapi import FastAPI", encoding="utf-8")

        # Copy to extracted directory
        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        scan_result = scanner.scan(extracted_project)

        with patch("app.api.diagrams.scanner_service.scan") as mock_scan:
            mock_scan.return_value = scan_result

            with patch("app.api.diagrams.detector_service.detect") as mock_detect:
                from app.services.framework_detector import DetectionResult
                mock_detect.return_value = DetectionResult()

            with patch("app.api.diagrams.graph_builder.build") as mock_graph:
                from app.services.dependency_graph import GraphResult
                mock_graph.return_value = GraphResult()

            with patch("app.api.diagrams.ParserEngine.parse_project") as mock_parse:
                from app.parsers.ast_models import ProjectParsingResult
                mock_parse.return_value = ProjectParsingResult(
                    project={"name": "test-project", "root_path": str(extracted_project), "total_files": 1}
                )

            with patch("app.api.diagrams.architecture_builder.build") as mock_build:
                from app.analyzers.architecture_models import ArchitectureResult
                mock_build.return_value = ArchitectureResult(
                    project={"name": "test-project", "root_path": str(extracted_project)},
                    layers=[],
                    modules=[],
                    relationships=[],
                )

            with patch("app.api.diagrams.diagram_generator.build") as mock_diagram:
                from app.visualization.diagram_models import DiagramOutput
                mock_diagram.return_value = DiagramOutput(
                    project={"name": "test-project", "root_path": str(extracted_project)},
                    mermaid={
                        "system": "flowchart TD\n    Test",
                        "modules": "flowchart TD\n    Test",
                        "components": "flowchart TD\n    Test",
                        "dependencies": "flowchart TD\n    Test",
                        "layers": "flowchart TD\n    Test",
                    },
                    plantuml={
                        "system": "@startuml\n@enduml",
                        "modules": "@startuml\n@enduml",
                        "components": "@startuml\n@enduml",
                        "dependencies": "@startuml\n@enduml",
                        "layers": "@startuml\n@enduml",
                    },
                    statistics={"nodes": 1, "edges": 0},
                )

                response = client.get(f"/diagrams/{upload_id}")

                assert response.status_code == 200
                data = response.json()
                assert "project" in data
                assert "mermaid" in data
                assert "plantuml" in data
                assert "statistics" in data
                assert "system" in data["mermaid"]
                assert "modules" in data["mermaid"]
                assert "components" in data["mermaid"]
                assert "dependencies" in data["mermaid"]
                assert "layers" in data["mermaid"]
                assert "system" in data["plantuml"]
                assert "modules" in data["plantuml"]
                assert "components" in data["plantuml"]
                assert "dependencies" in data["plantuml"]
                assert "layers" in data["plantuml"]

    def test_diagrams_project_not_found(self, client: TestClient) -> None:
        """Test 404 when project does not exist."""
        response = client.get("/diagrams/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_diagrams_permission_denied(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test 403 when permission is denied during scanning."""
        upload_id = "test-permission-id"
        project = tmp_path / "test-project"
        project.mkdir()

        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        with patch("app.api.diagrams.scanner_service.scan") as mock_scan:
            mock_scan.side_effect = PermissionError("Access denied")

            response = client.get(f"/diagrams/{upload_id}")
            assert response.status_code == 403
            assert "permission denied" in response.json()["detail"].lower()

    def test_diagrams_detection_error(
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

        with patch("app.api.diagrams.scanner_service.scan") as mock_scan:
            mock_scan.return_value = scan_result

            with patch("app.api.diagrams.detector_service.detect") as mock_detect:
                mock_detect.side_effect = Exception("Detection failed")

                response = client.get(f"/diagrams/{upload_id}")
                assert response.status_code == 500

    def test_diagrams_graph_error(
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

        with patch("app.api.diagrams.scanner_service.scan") as mock_scan:
            mock_scan.return_value = scan_result

            with patch("app.api.diagrams.detector_service.detect") as mock_detect:
                from app.services.framework_detector import DetectionResult
                mock_detect.return_value = DetectionResult()

            with patch("app.api.diagrams.graph_builder.build") as mock_graph:
                mock_graph.side_effect = Exception("Graph build failed")

                response = client.get(f"/diagrams/{upload_id}")
                assert response.status_code == 500

    def test_diagrams_parser_error(
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

        with patch("app.api.diagrams.scanner_service.scan") as mock_scan:
            mock_scan.return_value = scan_result

            with patch("app.api.diagrams.detector_service.detect") as mock_detect:
                from app.services.framework_detector import DetectionResult
                mock_detect.return_value = DetectionResult()

            with patch("app.api.diagrams.graph_builder.build") as mock_graph:
                from app.services.dependency_graph import GraphResult
                mock_graph.return_value = GraphResult()

            with patch("app.api.diagrams.ParserEngine.parse_project") as mock_parse:
                mock_parse.side_effect = Exception("Parse failed")

                response = client.get(f"/diagrams/{upload_id}")
                assert response.status_code == 500

    def test_diagrams_architecture_error(
        self, client: TestClient, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test 500 when architecture building fails."""
        upload_id = "test-architecture-error-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')", encoding="utf-8")

        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        scan_result = scanner.scan(extracted_project)

        with patch("app.api.diagrams.scanner_service.scan") as mock_scan:
            mock_scan.return_value = scan_result

            with patch("app.api.diagrams.detector_service.detect") as mock_detect:
                from app.services.framework_detector import DetectionResult
                mock_detect.return_value = DetectionResult()

            with patch("app.api.diagrams.graph_builder.build") as mock_graph:
                from app.services.dependency_graph import GraphResult
                mock_graph.return_value = GraphResult()

            with patch("app.api.diagrams.ParserEngine.parse_project") as mock_parse:
                from app.parsers.ast_models import ProjectParsingResult
                mock_parse.return_value = ProjectParsingResult(
                    project={"name": "test-project", "root_path": str(extracted_project), "total_files": 1}
                )

            with patch("app.api.diagrams.architecture_builder.build") as mock_build:
                mock_build.side_effect = Exception("Architecture build failed")

                response = client.get(f"/diagrams/{upload_id}")
                assert response.status_code == 500

    def test_diagrams_generator_error(
        self, client: TestClient, scanner: RepositoryScanner, tmp_path: Path
    ) -> None:
        """Test 500 when diagram generation fails."""
        upload_id = "test-generator-error-id"
        project = tmp_path / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')", encoding="utf-8")

        extracted_project = EXTRACTED_DIR / upload_id
        shutil.copytree(project, extracted_project)

        scan_result = scanner.scan(extracted_project)

        with patch("app.api.diagrams.scanner_service.scan") as mock_scan:
            mock_scan.return_value = scan_result

            with patch("app.api.diagrams.detector_service.detect") as mock_detect:
                from app.services.framework_detector import DetectionResult
                mock_detect.return_value = DetectionResult()

            with patch("app.api.diagrams.graph_builder.build") as mock_graph:
                from app.services.dependency_graph import GraphResult
                mock_graph.return_value = GraphResult()

            with patch("app.api.diagrams.ParserEngine.parse_project") as mock_parse:
                from app.parsers.ast_models import ProjectParsingResult
                mock_parse.return_value = ProjectParsingResult(
                    project={"name": "test-project", "root_path": str(extracted_project), "total_files": 1}
                )

            with patch("app.api.diagrams.architecture_builder.build") as mock_build:
                from app.analyzers.architecture_models import ArchitectureResult
                mock_build.return_value = ArchitectureResult(
                    project={"name": "test-project", "root_path": str(extracted_project)},
                    layers=[],
                    modules=[],
                    relationships=[],
                )

            with patch("app.api.diagrams.diagram_generator.build") as mock_diagram:
                mock_diagram.side_effect = Exception("Diagram generation failed")

                response = client.get(f"/diagrams/{upload_id}")
                assert response.status_code == 500

    def test_diagrams_response_structure(
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

        with patch("app.api.diagrams.scanner_service.scan") as mock_scan:
            mock_scan.return_value = scan_result

            with patch("app.api.diagrams.detector_service.detect") as mock_detect:
                from app.services.framework_detector import DetectionResult
                mock_detect.return_value = DetectionResult()

            with patch("app.api.diagrams.graph_builder.build") as mock_graph:
                from app.services.dependency_graph import GraphResult
                mock_graph.return_value = GraphResult()

            with patch("app.api.diagrams.ParserEngine.parse_project") as mock_parse:
                from app.parsers.ast_models import ProjectParsingResult
                mock_parse.return_value = ProjectParsingResult(
                    project={"name": "test-project", "root_path": str(extracted_project), "total_files": 1}
                )

            with patch("app.api.diagrams.architecture_builder.build") as mock_build:
                from app.analyzers.architecture_models import ArchitectureResult
                mock_build.return_value = ArchitectureResult(
                    project={"name": "test-project", "root_path": str(extracted_project)},
                    layers=["Backend"],
                    modules=[],
                    relationships=[],
                )

            with patch("app.api.diagrams.diagram_generator.build") as mock_diagram:
                from app.visualization.diagram_models import DiagramOutput
                mock_diagram.return_value = DiagramOutput(
                    project={"name": "test-project", "root_path": str(extracted_project)},
                    mermaid={
                        "system": "flowchart TD\n    Project",
                        "modules": "flowchart TD\n    Module",
                        "components": "flowchart TD\n    Component",
                        "dependencies": "flowchart TD\n    Dependency",
                        "layers": "flowchart TD\n    Layer",
                    },
                    plantuml={
                        "system": "@startuml\n@enduml",
                        "modules": "@startuml\n@enduml",
                        "components": "@startuml\n@enduml",
                        "dependencies": "@startuml\n@enduml",
                        "layers": "@startuml\n@enduml",
                    },
                    statistics={"nodes": 5, "edges": 3},
                )

                response = client.get(f"/diagrams/{upload_id}")
                assert response.status_code == 200

                data = response.json()
                assert data["project"]["name"] == "test-project"
                assert "flowchart TD" in data["mermaid"]["system"]
                assert "flowchart TD" in data["mermaid"]["modules"]
                assert "flowchart TD" in data["mermaid"]["components"]
                assert "flowchart TD" in data["mermaid"]["dependencies"]
                assert "flowchart TD" in data["mermaid"]["layers"]
                assert "@startuml" in data["plantuml"]["system"]
                assert "@enduml" in data["plantuml"]["system"]
                assert data["statistics"]["nodes"] == 5
                assert data["statistics"]["edges"] == 3
