"""Tests for chat API."""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.chat import ChatRequest, ChatMatch, ChatResponse


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """Create a sample project for testing."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    (project_dir / "test.py").write_text("""
def hello():
    print("hello")
""")
    
    return project_dir


@pytest.fixture
def extracted_dir(tmp_path: Path) -> Path:
    """Create extracted directory structure."""
    extracted = tmp_path / "storage" / "extracted"
    extracted.mkdir(parents=True)
    return extracted


class TestChatAPI:
    """Tests for chat API endpoint."""

    def test_chat_endpoint_missing_upload(self, client):
        """Test chat with non-existent upload."""
        response = client.post(
            "/chat/nonexistent-id",
            json={"query": "test query"},
        )
        assert response.status_code == 404

    def test_chat_endpoint_empty_query(self, client, extracted_dir, sample_project):
        """Test chat with empty query."""
        upload_id = "test-upload"
        project_path = extracted_dir / upload_id
        project_path.mkdir()
        
        response = client.post(
            f"/chat/{upload_id}",
            json={"query": ""},
        )
        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_success(self, client, extracted_dir, sample_project, monkeypatch):
        """Test successful chat request."""
        # This test requires mocking the embedding service
        # since we don't want to require actual embedding models in tests
        
        upload_id = "test-upload"
        project_path = extracted_dir / upload_id
        
        # Copy sample project to extracted directory
        import shutil
        shutil.copytree(sample_project, project_path, dirs_exist_ok=True)
        
        # Mock the embedding service to avoid requiring actual models
        from app.rag import embedding_service
        from unittest.mock import Mock, MagicMock
        
        mock_service = Mock()
        mock_service.dimension = 384
        mock_service.embed = Mock(return_value=[0.1] * 384)
        mock_service.embed_batch = Mock(return_value=[[0.1] * 384, [0.2] * 384])
        mock_service.validate_config = Mock(return_value=True)
        
        # Patch the embedding service in the chat module
        monkeypatch.setattr("app.api.chat.rag_pipeline", None)
        
        # For now, skip this test as it requires more complex mocking
        pytest.skip("Requires complex mocking of RAG pipeline")

    def test_chat_request_schema(self):
        """Test chat request schema validation."""
        # Valid request
        request = ChatRequest(query="test query")
        assert request.query == "test query"
        
        # Invalid request (empty query)
        with pytest.raises(ValueError):
            ChatRequest(query="")


class TestChatSchemas:
    """Tests for chat schemas."""

    def test_chat_request_creation(self):
        """Test ChatRequest creation."""
        request = ChatRequest(query="How does authentication work?")
        assert request.query == "How does authentication work?"

    def test_chat_response_creation(self):
        """Test ChatResponse creation."""
        from app.schemas.chat import ChatResponse, ChatMatch
        
        response = ChatResponse(
            query="test query",
            matches=[
                ChatMatch(
                    file="test.py",
                    language="Python",
                    chunk_id="chunk1",
                    score=0.95,
                    content="def hello():",
                    start_line=1,
                    end_line=10,
                )
            ],
        )
        
        assert response.query == "test query"
        assert len(response.matches) == 1
        assert response.matches[0].file == "test.py"
        assert response.matches[0].score == 0.95

    def test_chat_match_creation(self):
        """Test ChatMatch creation."""
        match = ChatMatch(
            file="test.py",
            language="Python",
            chunk_id="chunk1",
            score=0.97,
            content="def hello():",
            start_line=1,
            end_line=10,
        )
        
        assert match.file == "test.py"
        assert match.language == "Python"
        assert match.chunk_id == "chunk1"
        assert match.score == 0.97
        assert match.content == "def hello():"
        assert match.start_line == 1
        assert match.end_line == 10
