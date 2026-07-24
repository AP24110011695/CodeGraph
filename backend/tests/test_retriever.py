"""Tests for RAG retriever."""

import pytest
from app.rag.retriever import Retriever, RetrievalError
from app.rag.chunker import Chunk
from app.rag.vector_store import InMemoryVectorStore
from app.rag.embedding_service import EmbeddingService, EmbeddingError
from unittest.mock import Mock, patch


class MockEmbeddingService:
    """Mock embedding service for testing."""

    def __init__(self, dimension: int = 384):
        self._dimension = dimension

    def embed(self, text: str) -> list[float]:
        return [0.1] * self._dimension

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * self._dimension for _ in texts]

    @property
    def dimension(self) -> int:
        return self._dimension


class TestRetriever:
    """Tests for Retriever class."""

    @pytest.fixture
    def retriever(self):
        """Create a retriever instance with mock components."""
        vector_store = InMemoryVectorStore()
        embedding_service = MockEmbeddingService(dimension=384)
        return Retriever(vector_store, embedding_service)

    @pytest.fixture
    def sample_chunks(self):
        """Create sample chunks for testing."""
        return [
            Chunk(
                upload_id="test-upload",
                file_path="test.py",
                language="Python",
                chunk_id="chunk1",
                start_line=1,
                end_line=10,
                content="def hello():\n    print('hello')",
                metadata={},
            ),
            Chunk(
                upload_id="test-upload",
                file_path="test.py",
                language="Python",
                chunk_id="chunk2",
                start_line=11,
                end_line=20,
                content="def world():\n    print('world')",
                metadata={},
            ),
        ]

    def test_retriever_initialization(self, retriever):
        """Test retriever initialization."""
        assert retriever.vector_store is not None
        assert retriever.embedding_service is not None

    def test_retrieve_empty_query(self, retriever):
        """Test retrieve with empty query."""
        with pytest.raises(RetrievalError, match="Query cannot be empty"):
            retriever.retrieve(query="", upload_id="test-upload")

    def test_retrieve_whitespace_query(self, retriever):
        """Test retrieve with whitespace query."""
        with pytest.raises(RetrievalError, match="Query cannot be empty"):
            retriever.retrieve(query="   ", upload_id="test-upload")

    def test_retrieve_with_chunks(self, retriever, sample_chunks):
        """Test retrieve after adding chunks."""
        retriever.add_chunks(sample_chunks)
        results = retriever.retrieve(query="hello", upload_id="test-upload", top_k=2)
        assert len(results) <= 2
        assert all("file" in r for r in results)
        assert all("language" in r for r in results)
        assert all("chunk_id" in r for r in results)
        assert all("score" in r for r in results)
        assert all("content" in r for r in results)

    def test_retrieve_with_filters(self, retriever, sample_chunks):
        """Test retrieve with upload_id filter."""
        retriever.add_chunks(sample_chunks)
        results = retriever.retrieve(
            query="hello",
            upload_id="test-upload",
            top_k=5,
            filters={"upload_id": "test-upload"},
        )
        assert len(results) > 0

    def test_retrieve_no_chunks(self, retriever):
        """Test retrieve with no chunks in store."""
        results = retriever.retrieve(query="hello", upload_id="test-upload", top_k=5)
        assert len(results) == 0

    def test_add_chunks_empty_list(self, retriever):
        """Test adding empty chunk list."""
        retriever.add_chunks([])
        assert retriever.vector_store.count() == 0

    def test_add_chunks_success(self, retriever, sample_chunks):
        """Test adding chunks successfully."""
        retriever.add_chunks(sample_chunks)
        assert retriever.vector_store.count() == len(sample_chunks)

    def test_add_chunks_embedding_failure(self):
        """Test add_chunks when embedding fails."""
        vector_store = InMemoryVectorStore()
        
        # Mock embedding service that raises error
        embedding_service = Mock()
        embedding_service.embed_batch.side_effect = EmbeddingError("Embedding failed")
        
        retriever = Retriever(vector_store, embedding_service)
        
        chunks = [
            Chunk(
                upload_id="test-upload",
                file_path="test.py",
                language="Python",
                chunk_id="chunk1",
                start_line=1,
                end_line=10,
                content="content",
                metadata={},
            ),
        ]
        
        with pytest.raises(RetrievalError, match="Failed to generate embeddings"):
            retriever.add_chunks(chunks)

    def test_add_chunks_embedding_count_mismatch(self):
        """Test add_chunks when embedding count mismatches."""
        vector_store = InMemoryVectorStore()
        
        # Mock embedding service that returns wrong count
        embedding_service = Mock()
        embedding_service.embed_batch.return_value = [[0.1] * 384]  # Only one embedding
        
        retriever = Retriever(vector_store, embedding_service)
        
        chunks = [
            Chunk(
                upload_id="test-upload",
                file_path="test.py",
                language="Python",
                chunk_id="chunk1",
                start_line=1,
                end_line=10,
                content="content1",
                metadata={},
            ),
            Chunk(
                upload_id="test-upload",
                file_path="test.py",
                language="Python",
                chunk_id="chunk2",
                start_line=11,
                end_line=20,
                content="content2",
                metadata={},
            ),
        ]
        
        with pytest.raises(RetrievalError, match="Embedding count mismatch"):
            retriever.add_chunks(chunks)

    def test_retrieve_embedding_failure(self):
        """Test retrieve when embedding fails."""
        vector_store = InMemoryVectorStore()
        
        # Mock embedding service that raises error
        embedding_service = Mock()
        embedding_service.embed.side_effect = EmbeddingError("Embedding failed")
        
        retriever = Retriever(vector_store, embedding_service)
        
        with pytest.raises(RetrievalError, match="Failed to generate query embedding"):
            retriever.retrieve(query="hello", upload_id="test-upload")

    def test_delete_by_upload_id(self, retriever, sample_chunks):
        """Test delete by upload_id."""
        retriever.add_chunks(sample_chunks)
        # Should not raise error (implementation is a no-op for now)
        retriever.delete_by_upload_id("test-upload")
