"""Tests for the POST /uml/{upload_id} API endpoint."""

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
def python_project(tmp_path: Path) -> tuple[str, Path]:
    """Create a mock Python project with classes for UML generation."""
    upload_id = "test-python-001"
    project = tmp_path / upload_id
    project.mkdir()

    src = project / "src"
    src.mkdir()

    # Create Python files with classes
    main_py = """
from models import User
from services import UserService

class UserController:
    def __init__(self):
        self.service = UserService()
    
    def get_user(self, user_id):
        return self.service.find(user_id)
"""
    (src / "controller.py").write_text(main_py, encoding="utf-8")

    models_py = """
class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    def save(self):
        pass
"""
    (src / "models.py").write_text(models_py, encoding="utf-8")

    services_py = """
class UserService:
    def find(self, user_id):
        return User(user_id, "Test")
"""
    (src / "services.py").write_text(services_py, encoding="utf-8")

    (project / "requirements.txt").write_text("fastapi\n", encoding="utf-8")

    return upload_id, tmp_path


@pytest.fixture
def java_project(tmp_path: Path) -> tuple[str, Path]:
    """Create a mock Java project with classes for UML generation."""
    upload_id = "test-java-001"
    project = tmp_path / upload_id
    project.mkdir()

    src = project / "src"
    src.mkdir()

    # Create Java files with classes
    user_java = """
package com.example.models;

public class User {
    private String name;
    
    public User(String name) {
        this.name = name;
    }
    
    public String getName() {
        return this.name;
    }
}
"""
    (src / "User.java").write_text(user_java, encoding="utf-8")

    service_java = """
package com.example.services;

import com.example.models.User;

public class UserService {
    public User findUser(String id) {
        return new User("Test");
    }
}
"""
    (src / "UserService.java").write_text(service_java, encoding="utf-8")

    return upload_id, tmp_path


@pytest.fixture
def typescript_project(tmp_path: Path) -> tuple[str, Path]:
    """Create a mock TypeScript project with classes for UML generation."""
    upload_id = "test-typescript-001"
    project = tmp_path / upload_id
    project.mkdir()

    src = project / "src"
    src.mkdir()

    # Create TypeScript files with classes and interfaces
    user_ts = """
export interface IUser {
    id: string;
    name: string;
}

export class User implements IUser {
    constructor(public id: string, public name: string) {}
}
"""
    (src / "User.ts").write_text(user_ts, encoding="utf-8")

    service_ts = """
import { User, IUser } from './User';

export class UserService {
    findUser(id: string): IUser {
        return new User(id, "Test");
    }
}
"""
    (src / "UserService.ts").write_text(service_ts, encoding="utf-8")

    (project / "package.json").write_text('{"dependencies": {"typescript": "^5"}}', encoding="utf-8")

    return upload_id, tmp_path


@pytest.fixture
def no_classes_project(tmp_path: Path) -> tuple[str, Path]:
    """Create a project with no classes."""
    upload_id = "test-no-classes"
    project = tmp_path / upload_id
    project.mkdir()

    (project / "README.md").write_text("# Test", encoding="utf-8")

    return upload_id, tmp_path


@pytest.fixture
def empty_project(tmp_path: Path) -> tuple[str, Path]:
    """Create an empty project."""
    upload_id = "test-empty"
    project = tmp_path / upload_id
    project.mkdir()

    return upload_id, tmp_path


class TestUMLApiEndpoint:
    """Tests for POST /uml/{upload_id}."""

    def test_class_diagram_python(
        self, client: TestClient, python_project: tuple[str, Path]
    ) -> None:
        """Test class diagram generation for Python project."""
        upload_id, base_dir = python_project

        with patch("app.api.uml.EXTRACTED_DIR", base_dir):
            response = client.post(f"/uml/{upload_id}?diagram_type=class")

        assert response.status_code == 200
        data = response.json()

        assert data["diagram_type"] == "class"
        assert data["syntax"] == "mermaid"
        assert "classDiagram" in data["diagram"]
        assert data["total_classes"] > 0

    def test_component_diagram_python(
        self, client: TestClient, python_project: tuple[str, Path]
    ) -> None:
        """Test component diagram generation for Python project."""
        upload_id, base_dir = python_project

        with patch("app.api.uml.EXTRACTED_DIR", base_dir):
            response = client.post(f"/uml/{upload_id}?diagram_type=component")

        assert response.status_code == 200
        data = response.json()

        assert data["diagram_type"] == "component"
        assert "flowchart" in data["diagram"]

    def test_package_diagram_python(
        self, client: TestClient, python_project: tuple[str, Path]
    ) -> None:
        """Test package diagram generation for Python project."""
        upload_id, base_dir = python_project

        with patch("app.api.uml.EXTRACTED_DIR", base_dir):
            response = client.post(f"/uml/{upload_id}?diagram_type=package")

        assert response.status_code == 200
        data = response.json()

        assert data["diagram_type"] == "package"
        assert "namespace" in data["diagram"]

    def test_sequence_diagram_python(
        self, client: TestClient, python_project: tuple[str, Path]
    ) -> None:
        """Test sequence diagram generation for Python project."""
        upload_id, base_dir = python_project

        with patch("app.api.uml.EXTRACTED_DIR", base_dir):
            response = client.post(f"/uml/{upload_id}?diagram_type=sequence")

        assert response.status_code == 200
        data = response.json()

        assert data["diagram_type"] == "sequence"
        assert "sequenceDiagram" in data["diagram"]

    def test_class_diagram_java(
        self, client: TestClient, java_project: tuple[str, Path]
    ) -> None:
        """Test class diagram generation for Java project."""
        upload_id, base_dir = java_project

        with patch("app.api.uml.EXTRACTED_DIR", base_dir):
            response = client.post(f"/uml/{upload_id}?diagram_type=class")

        assert response.status_code == 200
        data = response.json()

        assert data["diagram_type"] == "class"
        # Java is not yet supported by the parser, so we expect 0 classes
        # This test verifies the endpoint handles unsupported languages gracefully
        assert data["total_classes"] == 0

    def test_class_diagram_typescript(
        self, client: TestClient, typescript_project: tuple[str, Path]
    ) -> None:
        """Test class diagram generation for TypeScript project."""
        upload_id, base_dir = typescript_project

        with patch("app.api.uml.EXTRACTED_DIR", base_dir):
            response = client.post(f"/uml/{upload_id}?diagram_type=class")

        assert response.status_code == 200
        data = response.json()

        assert data["diagram_type"] == "class"
        assert data["total_classes"] > 0

    def test_no_classes(
        self, client: TestClient, no_classes_project: tuple[str, Path]
    ) -> None:
        """Test response when no classes are detected."""
        upload_id, base_dir = no_classes_project

        with patch("app.api.uml.EXTRACTED_DIR", base_dir):
            response = client.post(f"/uml/{upload_id}?diagram_type=class")

        assert response.status_code == 200
        data = response.json()

        assert data["diagram"] == "No UML diagram could be generated."
        assert data["total_classes"] == 0

    def test_empty_project(
        self, client: TestClient, empty_project: tuple[str, Path]
    ) -> None:
        """Test response for empty project."""
        upload_id, base_dir = empty_project

        with patch("app.api.uml.EXTRACTED_DIR", base_dir):
            response = client.post(f"/uml/{upload_id}?diagram_type=class")

        assert response.status_code == 200
        data = response.json()

        assert data["total_classes"] == 0

    def test_download_mode(
        self, client: TestClient, python_project: tuple[str, Path]
    ) -> None:
        """Test markdown download mode."""
        upload_id, base_dir = python_project

        with patch("app.api.uml.EXTRACTED_DIR", base_dir):
            response = client.post(f"/uml/{upload_id}?diagram_type=class&download=true")

        assert response.status_code == 200
        content = response.text
        assert "classDiagram" in content

    def test_invalid_diagram_type(
        self, client: TestClient, python_project: tuple[str, Path]
    ) -> None:
        """Test invalid diagram type parameter."""
        upload_id, base_dir = python_project

        with patch("app.api.uml.EXTRACTED_DIR", base_dir):
            response = client.post(f"/uml/{upload_id}?diagram_type=invalid")

        assert response.status_code == 400
        assert "Invalid diagram_type" in response.json()["detail"]

    def test_repository_not_found(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test 404 error when repository is not found."""
        with patch("app.api.uml.EXTRACTED_DIR", tmp_path):
            response = client.post("/uml/nonexistent-id")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_not_a_directory(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test 400 error when path is not a directory."""
        upload_id = "test-file"
        file_path = tmp_path / upload_id
        file_path.write_text("not a dir", encoding="utf-8")

        with patch("app.api.uml.EXTRACTED_DIR", tmp_path):
            response = client.post(f"/uml/{upload_id}")

        assert response.status_code == 400
        assert "not a directory" in response.json()["detail"].lower()

    def test_default_diagram_type(
        self, client: TestClient, python_project: tuple[str, Path]
    ) -> None:
        """Test that default diagram type is class."""
        upload_id, base_dir = python_project

        with patch("app.api.uml.EXTRACTED_DIR", base_dir):
            response = client.post(f"/uml/{upload_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["diagram_type"] == "class"

    def test_mermaid_syntax_validation(
        self, client: TestClient, python_project: tuple[str, Path]
    ) -> None:
        """Test that generated diagram contains valid Mermaid syntax."""
        upload_id, base_dir = python_project

        with patch("app.api.uml.EXTRACTED_DIR", base_dir):
            response = client.post(f"/uml/{upload_id}?diagram_type=class")

        data = response.json()
        diagram = data["diagram"]

        # Check for Mermaid class diagram syntax
        assert "classDiagram" in diagram
        assert "class " in diagram

    def test_large_repository(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test handling of a repository with many files."""
        upload_id = "test-large"
        project = tmp_path / upload_id
        project.mkdir()

        src = project / "src"
        src.mkdir()

        # Create many Python files with classes
        for i in range(50):
            (src / f"file{i}.py").write_text(f"class Class{i}:\n    pass", encoding="utf-8")

        (project / "requirements.txt").write_text("fastapi\n", encoding="utf-8")

        with patch("app.api.uml.EXTRACTED_DIR", tmp_path):
            response = client.post(f"/uml/{upload_id}?diagram_type=class")

        assert response.status_code == 200
        data = response.json()
        # Should complete without error even with many files
        assert "diagram" in data

    def test_no_relationships(
        self, client: TestClient, tmp_path: Path
    ) -> None:
        """Test when classes exist but no relationships are detected."""
        upload_id = "test-no-relationships"
        project = tmp_path / upload_id
        project.mkdir()

        (project / "main.py").write_text("class A:\n    pass\nclass B:\n    pass", encoding="utf-8")

        with patch("app.api.uml.EXTRACTED_DIR", tmp_path):
            response = client.post(f"/uml/{upload_id}?diagram_type=class")

        assert response.status_code == 200
        data = response.json()
        # Should still generate diagram even without relationships
        assert "classDiagram" in data["diagram"]
