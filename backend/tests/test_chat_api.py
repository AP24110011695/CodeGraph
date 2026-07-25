"""Tests for chat API."""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.chat import ChatRequest, ChatMatch, ChatResponse
from app.schemas.conversation import ConversationRequest, ChatAnswerResponse


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
            json={"message": "test query"},
        )
        assert response.status_code == 404

    def test_chat_endpoint_empty_message(self, client, extracted_dir, sample_project):
        """Test chat with empty message."""
        upload_id = "test-upload"
        project_path = extracted_dir / upload_id
        project_path.mkdir()

        response = client.post(
            f"/chat/{upload_id}",
            json={"message": ""},
        )
        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_repository_not_indexed(self, client, extracted_dir, sample_project):
        """Test chat with repository not indexed."""
        # This test requires the actual storage/extracted directory setup
        # Skip for now as it requires more complex fixture setup
        pytest.skip("Requires actual storage directory setup")

    def test_chat_request_schema(self):
        """Test chat request schema validation."""
        # Valid request
        request = ConversationRequest(message="test query")
        assert request.message == "test query"

        # Invalid request (empty message)
        with pytest.raises(ValueError):
            ConversationRequest(message="")


class TestChatSchemas:
    """Tests for chat schemas."""

    def test_conversation_request_creation(self):
        """Test ConversationRequest creation."""
        request = ConversationRequest(message="How does authentication work?")
        assert request.message == "How does authentication work?"

    def test_conversation_request_with_conversation_id(self):
        """Test ConversationRequest with conversation_id."""
        request = ConversationRequest(
            conversation_id="conv-123",
            message="How does authentication work?"
        )
        assert request.conversation_id == "conv-123"
        assert request.message == "How does authentication work?"

    def test_chat_answer_response_creation(self):
        """Test ChatAnswerResponse creation."""
        response = ChatAnswerResponse(
            conversation_id="conv-123",
            answer="Authentication works by validating tokens",
            sources=["src/auth/login.py", "src/routes/auth.py"],
            confidence=0.94,
            tokens_used=150,
        )

        assert response.conversation_id == "conv-123"
        assert response.answer == "Authentication works by validating tokens"
        assert len(response.sources) == 2
        assert response.confidence == 0.94
        assert response.tokens_used == 150
