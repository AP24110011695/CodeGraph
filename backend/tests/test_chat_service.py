"""Tests for AI-powered chat service."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.chat.chat_service import ChatService, ChatServiceError
from app.chat.conversation_memory import ConversationMemory
from app.chat.prompt_builder import PromptBuilder
from app.indexing.index_manager import IndexManager
from app.indexing.indexing_models import IndexStatus, RepositoryIndex
from app.rag.retriever import Retriever, RetrievalError
from app.rag.embedding_service import EmbeddingError


@pytest.fixture
def mock_index_manager():
    """Mock index manager."""
    manager = MagicMock(spec=IndexManager)
    return manager


@pytest.fixture
def mock_retriever():
    """Mock retriever."""
    retriever = MagicMock(spec=Retriever)
    return retriever


@pytest.fixture
def conversation_memory():
    """Conversation memory instance."""
    return ConversationMemory()


@pytest.fixture
def prompt_builder():
    """Prompt builder instance."""
    return PromptBuilder()


@pytest.fixture
def chat_service(mock_index_manager, mock_retriever, conversation_memory, prompt_builder):
    """Chat service instance."""
    return ChatService(
        index_manager=mock_index_manager,
        retriever=mock_retriever,
        conversation_memory=conversation_memory,
        prompt_builder=prompt_builder,
    )


class TestChatService:
    """Tests for ChatService."""

    def test_repository_not_indexed(self, chat_service, mock_index_manager):
        """Test chat with repository not indexed."""
        mock_index_manager.get_index.return_value = None

        with pytest.raises(ChatServiceError) as exc_info:
            chat_service.chat("test_upload", "Hello")

        assert "not indexed" in str(exc_info.value)

    def test_repository_not_ready(self, chat_service, mock_index_manager):
        """Test chat with repository index not ready."""
        index = RepositoryIndex(upload_id="test_upload", status=IndexStatus.INDEXING)
        mock_index_manager.get_index.return_value = index

        with pytest.raises(ChatServiceError) as exc_info:
            chat_service.chat("test_upload", "Hello")

        assert "not ready" in str(exc_info.value)

    def test_successful_chat_new_conversation(self, chat_service, mock_index_manager, mock_retriever):
        """Test successful chat with new conversation."""
        index = RepositoryIndex(upload_id="test_upload", status=IndexStatus.READY)
        mock_index_manager.get_index.return_value = index

        mock_retriever.retrieve.return_value = [
            {
                "file": "test.py",
                "language": "Python",
                "chunk_id": "chunk1",
                "score": 0.9,
                "content": "def test(): pass",
                "start_line": 1,
                "end_line": 2,
            }
        ]

        result = chat_service.chat("test_upload", "How does this work?")

        assert "conversation_id" in result
        assert "answer" in result
        assert "sources" in result
        assert "confidence" in result
        assert "tokens_used" in result
        assert result["confidence"] > 0
        assert len(result["sources"]) > 0

    def test_successful_chat_existing_conversation(self, chat_service, mock_index_manager, mock_retriever):
        """Test successful chat with existing conversation."""
        index = RepositoryIndex(upload_id="test_upload", status=IndexStatus.READY)
        mock_index_manager.get_index.return_value = index

        mock_retriever.retrieve.return_value = [
            {
                "file": "test.py",
                "language": "Python",
                "chunk_id": "chunk1",
                "score": 0.9,
                "content": "def test(): pass",
                "start_line": 1,
                "end_line": 2,
            }
        ]

        # First message creates conversation
        result1 = chat_service.chat("test_upload", "Hello")
        conversation_id = result1["conversation_id"]

        # Second message continues conversation
        result2 = chat_service.chat("test_upload", "How about this?", conversation_id=conversation_id)

        assert result2["conversation_id"] == conversation_id

    def test_retrieval_returns_empty(self, chat_service, mock_index_manager, mock_retriever):
        """Test chat when retrieval returns no results."""
        index = RepositoryIndex(upload_id="test_upload", status=IndexStatus.READY)
        mock_index_manager.get_index.return_value = index

        mock_retriever.retrieve.return_value = []

        result = chat_service.chat("test_upload", "Hello")

        assert result["answer"] == "I could not find enough evidence in this repository."
        assert result["confidence"] == 0.0
        assert result["sources"] == []

    def test_retrieval_error(self, chat_service, mock_index_manager, mock_retriever):
        """Test chat when retrieval fails."""
        index = RepositoryIndex(upload_id="test_upload", status=IndexStatus.READY)
        mock_index_manager.get_index.return_value = index

        mock_retriever.retrieve.side_effect = RetrievalError("Embedding failed")

        result = chat_service.chat("test_upload", "Hello")

        # Should return insufficient evidence when retrieval fails
        assert result["answer"] == "I could not find enough evidence in this repository."
        assert result["confidence"] == 0.0

    def test_invalid_conversation_id(self, chat_service, mock_index_manager, mock_retriever):
        """Test chat with invalid conversation ID."""
        index = RepositoryIndex(upload_id="test_upload", status=IndexStatus.READY)
        mock_index_manager.get_index.return_value = index

        with pytest.raises(ChatServiceError) as exc_info:
            chat_service.chat("test_upload", "Hello", conversation_id="invalid_id")

        assert "not found" in str(exc_info.value)

    def test_conversation_id_wrong_upload(self, chat_service, mock_index_manager, mock_retriever):
        """Test chat with conversation ID from different upload."""
        index = RepositoryIndex(upload_id="test_upload", status=IndexStatus.READY)
        mock_index_manager.get_index.return_value = index

        # Create conversation for upload1
        mock_retriever.retrieve.return_value = []
        result1 = chat_service.chat("upload1", "Hello")
        conversation_id = result1["conversation_id"]

        # Try to use it for upload2
        with pytest.raises(ChatServiceError) as exc_info:
            chat_service.chat("upload2", "Hello", conversation_id=conversation_id)

        assert "does not belong" in str(exc_info.value)

    def test_get_conversation(self, chat_service, mock_index_manager, mock_retriever):
        """Test getting a conversation."""
        index = RepositoryIndex(upload_id="test_upload", status=IndexStatus.READY)
        mock_index_manager.get_index.return_value = index

        mock_retriever.retrieve.return_value = []

        result1 = chat_service.chat("test_upload", "Hello")
        conversation_id = result1["conversation_id"]

        conversation = chat_service.get_conversation(conversation_id)

        assert conversation is not None
        assert conversation["conversation_id"] == conversation_id
        assert len(conversation["messages"]) == 2  # user + assistant

    def test_get_nonexistent_conversation(self, chat_service):
        """Test getting a non-existent conversation."""
        conversation = chat_service.get_conversation("nonexistent")
        assert conversation is None

    def test_delete_conversation(self, chat_service, mock_index_manager, mock_retriever):
        """Test deleting a conversation."""
        index = RepositoryIndex(upload_id="test_upload", status=IndexStatus.READY)
        mock_index_manager.get_index.return_value = index

        mock_retriever.retrieve.return_value = []

        result1 = chat_service.chat("test_upload", "Hello")
        conversation_id = result1["conversation_id"]

        chat_service.delete_conversation(conversation_id)

        conversation = chat_service.get_conversation(conversation_id)
        assert conversation is None

    def test_get_conversations_for_upload(self, chat_service, mock_index_manager, mock_retriever):
        """Test getting all conversations for an upload."""
        index = RepositoryIndex(upload_id="test_upload", status=IndexStatus.READY)
        mock_index_manager.get_index.return_value = index

        mock_retriever.retrieve.return_value = []

        # Create multiple conversations
        chat_service.chat("test_upload", "Hello 1")
        chat_service.chat("test_upload", "Hello 2")

        conversations = chat_service.get_conversations_for_upload("test_upload")

        assert len(conversations) == 2

    def test_with_project_context(self, chat_service, mock_index_manager, mock_retriever, tmp_path):
        """Test chat with project path for context gathering."""
        index = RepositoryIndex(upload_id="test_upload", status=IndexStatus.READY)
        mock_index_manager.get_index.return_value = index

        mock_retriever.retrieve.return_value = [
            {
                "file": "test.py",
                "language": "Python",
                "chunk_id": "chunk1",
                "score": 0.9,
                "content": "def test(): pass",
                "start_line": 1,
                "end_line": 2,
            }
        ]

        # Create a mock project directory
        project_path = tmp_path / "test_upload"
        project_path.mkdir()
        (project_path / "test.py").write_text("def test(): pass")

        result = chat_service.chat("test_upload", "Hello", project_path=project_path)

        assert "conversation_id" in result
        # Context gathering is optional, so chat should still succeed even if it fails


class TestConversationMemory:
    """Tests for ConversationMemory."""

    def test_create_conversation(self, conversation_memory):
        """Test creating a conversation."""
        conversation_id = conversation_memory.create_conversation("upload1")

        assert conversation_id is not None
        conversation = conversation_memory.get_conversation(conversation_id)
        assert conversation is not None
        assert conversation.upload_id == "upload1"

    def test_get_conversation_not_found(self, conversation_memory):
        """Test getting non-existent conversation."""
        conversation = conversation_memory.get_conversation("nonexistent")
        assert conversation is None

    def test_get_or_create_new(self, conversation_memory):
        """Test get_or_create with new conversation."""
        conversation = conversation_memory.get_or_create_conversation("upload1")

        assert conversation is not None
        assert conversation.upload_id == "upload1"

    def test_get_or_create_existing(self, conversation_memory):
        """Test get_or_create with existing conversation."""
        conv1 = conversation_memory.get_or_create_conversation("upload1")
        conv2 = conversation_memory.get_or_create_conversation("upload1", conv1.conversation_id)

        assert conv1.conversation_id == conv2.conversation_id

    def test_get_or_create_invalid_id(self, conversation_memory):
        """Test get_or_create with invalid conversation ID."""
        with pytest.raises(ValueError) as exc_info:
            conversation_memory.get_or_create_conversation("upload1", "invalid_id")

        assert "not found" in str(exc_info.value)

    def test_add_message(self, conversation_memory):
        """Test adding a message."""
        conversation_id = conversation_memory.create_conversation("upload1")
        conversation_memory.add_message(conversation_id, "user", "Hello")

        conversation = conversation_memory.get_conversation(conversation_id)
        messages = conversation.get_messages()

        assert len(messages) == 1
        assert messages[0].role == "user"
        assert messages[0].content == "Hello"

    def test_add_message_invalid_conversation(self, conversation_memory):
        """Test adding message to invalid conversation."""
        with pytest.raises(ValueError) as exc_info:
            conversation_memory.add_message("invalid", "user", "Hello")

        assert "not found" in str(exc_info.value)

    def test_message_limit(self, conversation_memory):
        """Test that conversation respects message limit (20 messages)."""
        conversation_id = conversation_memory.create_conversation("upload1")

        # Add 25 messages
        for i in range(25):
            conversation_memory.add_message(conversation_id, "user", f"Message {i}")

        conversation = conversation_memory.get_conversation(conversation_id)
        messages = conversation.get_messages()

        # Should only keep last 20
        assert len(messages) == 20

    def test_update_context(self, conversation_memory):
        """Test updating conversation context."""
        conversation_id = conversation_memory.create_conversation("upload1")
        context = {"key": "value"}

        conversation_memory.update_context(conversation_id, context)

        conversation = conversation_memory.get_conversation(conversation_id)
        assert conversation.last_context == context

    def test_delete_conversation(self, conversation_memory):
        """Test deleting a conversation."""
        conversation_id = conversation_memory.create_conversation("upload1")
        conversation_memory.delete_conversation(conversation_id)

        conversation = conversation_memory.get_conversation(conversation_id)
        assert conversation is None

    def test_get_conversations_for_upload(self, conversation_memory):
        """Test getting conversations for an upload."""
        conv1 = conversation_memory.create_conversation("upload1")
        conv2 = conversation_memory.create_conversation("upload1")
        conversation_memory.create_conversation("upload2")

        conversations = conversation_memory.get_conversations_for_upload("upload1")

        assert len(conversations) == 2
        conversation_ids = {c.conversation_id for c in conversations}
        assert conv1 in conversation_ids
        assert conv2 in conversation_ids

    def test_clear_upload(self, conversation_memory):
        """Test clearing all conversations for an upload."""
        conv1 = conversation_memory.create_conversation("upload1")
        conv2 = conversation_memory.create_conversation("upload1")
        conv3 = conversation_memory.create_conversation("upload2")

        conversation_memory.clear_upload("upload1")

        assert conversation_memory.get_conversation(conv1) is None
        assert conversation_memory.get_conversation(conv2) is None
        assert conversation_memory.get_conversation(conv3) is not None


class TestPromptBuilder:
    """Tests for PromptBuilder."""

    def test_build_prompt_basic(self, prompt_builder):
        """Test basic prompt building."""
        prompt = prompt_builder.build_prompt(
            user_question="How does this work?",
            retrieved_chunks=[],
            architecture_summary={},
            framework_summary=[],
            dependency_summary={},
        )

        assert "How does this work?" in prompt
        assert "AI software architect assistant" in prompt

    def test_build_prompt_with_chunks(self, prompt_builder):
        """Test prompt building with retrieved chunks."""
        chunks = [
            {
                "file": "test.py",
                "language": "Python",
                "chunk_id": "chunk1",
                "score": 0.9,
                "content": "def test(): pass",
                "start_line": 1,
                "end_line": 2,
            }
        ]

        prompt = prompt_builder.build_prompt(
            user_question="How does this work?",
            retrieved_chunks=chunks,
            architecture_summary={},
            framework_summary=[],
            dependency_summary={},
        )

        assert "test.py" in prompt
        assert "def test(): pass" in prompt

    def test_build_prompt_with_architecture(self, prompt_builder):
        """Test prompt building with architecture summary."""
        architecture_summary = {
            "project": {"name": "TestProject"},
            "modules": [{"name": "auth", "type": "module"}],
            "layers": ["controller", "service"],
        }

        prompt = prompt_builder.build_prompt(
            user_question="How does this work?",
            retrieved_chunks=[],
            architecture_summary=architecture_summary,
            framework_summary=[],
            dependency_summary={},
        )

        assert "TestProject" in prompt
        assert "auth" in prompt

    def test_build_prompt_with_frameworks(self, prompt_builder):
        """Test prompt building with framework summary."""
        framework_summary = ["Django", "React"]

        prompt = prompt_builder.build_prompt(
            user_question="How does this work?",
            retrieved_chunks=[],
            architecture_summary={},
            framework_summary=framework_summary,
            dependency_summary={},
        )

        assert "Django" in prompt
        assert "React" in prompt

    def test_build_prompt_with_conversation_history(self, prompt_builder):
        """Test prompt building with conversation history."""
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]

        prompt = prompt_builder.build_prompt(
            user_question="How does this work?",
            retrieved_chunks=[],
            architecture_summary={},
            framework_summary=[],
            dependency_summary={},
            conversation_history=history,
        )

        assert "Conversation History" in prompt
        assert "Hello" in prompt

    def test_prompt_truncation(self, prompt_builder):
        """Test prompt truncation when too long."""
        # Create a very long prompt
        chunks = [{"file": f"file{i}.py", "language": "Python", "chunk_id": f"chunk{i}", "score": 0.9, "content": "x" * 1000, "start_line": 1, "end_line": 2} for i in range(100)]

        prompt = prompt_builder.build_prompt(
            user_question="How does this work?",
            retrieved_chunks=chunks,
            architecture_summary={},
            framework_summary=[],
            dependency_summary={},
        )

        # Should be truncated
        assert len(prompt) <= prompt_builder.max_context_length + 100  # Allow some margin

    def test_system_instruction_content(self, prompt_builder):
        """Test that system instruction contains required rules."""
        prompt = prompt_builder.build_prompt(
            user_question="How does this work?",
            retrieved_chunks=[],
            architecture_summary={},
            framework_summary=[],
            dependency_summary={},
        )

        assert "ONLY the information" in prompt
        assert "insufficient evidence" in prompt
        assert "Never hallucinate" in prompt
