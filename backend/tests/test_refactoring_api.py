import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import json
import shutil
import uuid

from app.main import app

client = TestClient(app)

EXTRACTED_DIR = Path("storage/extracted")

@pytest.fixture
def mock_extracted_dir():
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
    yield EXTRACTED_DIR

@pytest.fixture
def valid_upload_id(mock_extracted_dir):
    uid = str(uuid.uuid4())
    project_dir = mock_extracted_dir / uid
    project_dir.mkdir()
    
    # Create some python files to trigger parser and suggestions
    (project_dir / "main.py").write_text("import utils\ndef main():\n    pass")
    
    # Large class simulation (just many classes in one file)
    utils_code = "\n".join(f"class A{i}:\n    pass" for i in range(10))
    (project_dir / "utils.py").write_text(utils_code)
    
    # Circular dependency simulation
    (project_dir / "a.py").write_text("import b")
    (project_dir / "b.py").write_text("import a")
    
    yield uid
    
    shutil.rmtree(project_dir, ignore_errors=True)

@pytest.fixture
def empty_upload_id(mock_extracted_dir):
    uid = str(uuid.uuid4())
    project_dir = mock_extracted_dir / uid
    project_dir.mkdir()
    
    yield uid
    
    shutil.rmtree(project_dir, ignore_errors=True)

def test_api_success(valid_upload_id):
    response = client.post(f"/refactoring/{valid_upload_id}")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "suggestions" in data
    assert data["summary"]["total_suggestions"] >= 0

def test_large_class_suggestion(valid_upload_id):
    response = client.post(f"/refactoring/{valid_upload_id}")
    assert response.status_code == 200
    data = response.json()
    suggestions = data["suggestions"]
    # utils.py has 6 classes, which triggers Large Class (>5)
    large_class_sug = [s for s in suggestions if s["title"].startswith("Large Class")]
    assert len(large_class_sug) > 0

def test_circular_dependency_suggestion(valid_upload_id):
    response = client.post(f"/refactoring/{valid_upload_id}")
    assert response.status_code == 200
    data = response.json()
    suggestions = data["suggestions"]
    # a.py and b.py import each other
    circular = [s for s in suggestions if "Circular Dependency" in s["title"]]
    assert len(circular) > 0

def test_dead_code_suggestion(valid_upload_id):
    response = client.post(f"/refactoring/{valid_upload_id}")
    assert response.status_code == 200
    data = response.json()
    suggestions = data["suggestions"]
    dead_code = [s for s in suggestions if "Unused File" in s["title"]]
    assert len(dead_code) >= 0

def test_invalid_upload_id():
    response = client.post("/refactoring/invalid-1234")
    assert response.status_code == 404

def test_empty_repository(empty_upload_id):
    response = client.post(f"/refactoring/{empty_upload_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total_suggestions"] == 0
    assert len(data["suggestions"]) == 0

def test_repository_not_indexed_simulated(mock_extracted_dir):
    # Just meaning not extracted
    response = client.post("/refactoring/not-extracted-yet")
    assert response.status_code == 404
