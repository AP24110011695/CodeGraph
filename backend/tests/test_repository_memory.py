import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.repository_memory import RepositoryMemory, MemorySummary
from app.repository_memory.memory_engine import memory_engine

client = TestClient(app)

def test_repository_memory_build():
    repo_id = "test-repo-123"
    response = client.post(f"/repository-memory/build/{repo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["repository_id"] == repo_id
    assert "repository_summary" in data

def test_repository_memory_get():
    repo_id = "test-repo-123"
    # Ensure it's built first
    client.post(f"/repository-memory/build/{repo_id}")
    
    response = client.get(f"/repository-memory/{repo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["repository_id"] == repo_id

def test_repository_memory_summary():
    repo_id = "test-repo-123"
    client.post(f"/repository-memory/build/{repo_id}")
    
    response = client.get(f"/repository-memory/{repo_id}/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["repository_id"] == repo_id
    assert "module_count" in data

def test_repository_memory_incremental_update():
    repo_id = "test-repo-123"
    memory = memory_engine.build_memory(repo_id)
    memory.file_summaries["test_file.py"] = {"file_path": "test_file.py", "summary": "test", "important_symbols": []}
    memory_engine._store.set(repo_id, memory)
    
    # Update
    memory_engine.update_memory(repo_id, {"affected_files": ["test_file.py"]})
    
    updated = memory_engine.get_memory(repo_id)
    assert "test_file.py" not in updated.file_summaries

def test_repository_memory_serialization():
    from app.repository_memory.memory_serializer import MemorySerializer
    serializer = MemorySerializer()
    repo_id = "test-repo-456"
    memory = memory_engine.build_memory(repo_id)
    
    serialized = serializer.serialize(memory)
    assert isinstance(serialized, str)
    
    deserialized = serializer.deserialize(serialized)
    assert deserialized.repository_id == repo_id
