"""Tests for RAG vector store."""

import pytest
import numpy as np
from app.rag.vector_store import (
    VectorStore,
    InMemoryVectorStore,
    VectorDocument,
    VectorStoreError,
)


class TestVectorDocument:
    """Tests for VectorDocument dataclass."""

    def test_document_creation(self):
        """Test document creation."""
        doc = VectorDocument(
            id="test-id",
            embedding=[0.1, 0.2, 0.3],
            metadata={"file": "test.py"},
        )
        assert doc.id == "test-id"
        assert doc.embedding == [0.1, 0.2, 0.3]
        assert doc.metadata == {"file": "test.py"}

    def test_document_to_dict(self):
        """Test document to_dict method."""
        doc = VectorDocument(
            id="test-id",
            embedding=[0.1, 0.2, 0.3],
            metadata={"file": "test.py"},
        )
        doc_dict = doc.to_dict()
        assert doc_dict["id"] == "test-id"
        assert doc_dict["embedding"] == [0.1, 0.2, 0.3]
        assert doc_dict["metadata"] == {"file": "test.py"}


class TestInMemoryVectorStore:
    """Tests for InMemoryVectorStore."""

    def test_store_initialization(self):
        """Test store initialization."""
        store = InMemoryVectorStore()
        assert store.count() == 0
        assert store.dimension is None

    def test_store_with_dimension(self):
        """Test store with predefined dimension."""
        store = InMemoryVectorStore(dimension=384)
        assert store.dimension == 384

    def test_add_documents(self):
        """Test adding documents."""
        store = InMemoryVectorStore()
        docs = [
            VectorDocument(
                id="doc1",
                embedding=[0.1, 0.2, 0.3],
                metadata={"file": "test1.py"},
            ),
            VectorDocument(
                id="doc2",
                embedding=[0.4, 0.5, 0.6],
                metadata={"file": "test2.py"},
            ),
        ]
        store.add(docs)
        assert store.count() == 2
        assert store.dimension == 3

    def test_add_empty_list(self):
        """Test adding empty document list."""
        store = InMemoryVectorStore()
        store.add([])
        assert store.count() == 0

    def test_add_duplicate_document(self):
        """Test adding duplicate document (should overwrite)."""
        store = InMemoryVectorStore()
        doc1 = VectorDocument(
            id="doc1",
            embedding=[0.1, 0.2, 0.3],
            metadata={"file": "test1.py"},
        )
        doc2 = VectorDocument(
            id="doc1",
            embedding=[0.7, 0.8, 0.9],
            metadata={"file": "test2.py"},
        )
        store.add([doc1])
        store.add([doc2])
        assert store.count() == 1

    def test_add_mismatched_dimensions(self):
        """Test adding documents with mismatched dimensions."""
        store = InMemoryVectorStore(dimension=3)
        docs = [
            VectorDocument(
                id="doc1",
                embedding=[0.1, 0.2, 0.3],
                metadata={"file": "test1.py"},
            ),
            VectorDocument(
                id="doc2",
                embedding=[0.4, 0.5, 0.6, 0.7],  # Wrong dimension
                metadata={"file": "test2.py"},
            ),
        ]
        with pytest.raises(VectorStoreError):
            store.add(docs)

    def test_search_empty_store(self):
        """Test searching empty store."""
        store = InMemoryVectorStore()
        results = store.search(query_embedding=[0.1, 0.2, 0.3], top_k=5)
        assert results == []

    def test_search_with_results(self):
        """Test search with results."""
        store = InMemoryVectorStore()
        docs = [
            VectorDocument(
                id="doc1",
                embedding=[1.0, 0.0, 0.0],
                metadata={"file": "test1.py"},
            ),
            VectorDocument(
                id="doc2",
                embedding=[0.0, 1.0, 0.0],
                metadata={"file": "test2.py"},
            ),
        ]
        store.add(docs)

        # Query similar to doc1
        results = store.search(query_embedding=[1.0, 0.1, 0.0], top_k=2)
        assert len(results) == 2
        assert results[0][0].id == "doc1"  # Most similar
        assert results[0][1] > results[1][1]  # Score sorted descending

    def test_search_with_filters(self):
        """Test search with metadata filters."""
        store = InMemoryVectorStore()
        docs = [
            VectorDocument(
                id="doc1",
                embedding=[1.0, 0.0, 0.0],
                metadata={"file": "test1.py", "language": "Python"},
            ),
            VectorDocument(
                id="doc2",
                embedding=[0.0, 1.0, 0.0],
                metadata={"file": "test2.js", "language": "JavaScript"},
            ),
        ]
        store.add(docs)

        results = store.search(
            query_embedding=[1.0, 0.0, 0.0],
            top_k=5,
            filters={"language": "Python"},
        )
        assert len(results) == 1
        assert results[0][0].id == "doc1"

    def test_search_with_no_filter_matches(self):
        """Test search with filters that match nothing."""
        store = InMemoryVectorStore()
        docs = [
            VectorDocument(
                id="doc1",
                embedding=[1.0, 0.0, 0.0],
                metadata={"file": "test1.py", "language": "Python"},
            ),
        ]
        store.add(docs)

        results = store.search(
            query_embedding=[1.0, 0.0, 0.0],
            top_k=5,
            filters={"language": "JavaScript"},
        )
        assert len(results) == 0

    def test_search_mismatched_query_dimension(self):
        """Test search with mismatched query dimension."""
        store = InMemoryVectorStore(dimension=3)
        docs = [
            VectorDocument(
                id="doc1",
                embedding=[0.1, 0.2, 0.3],
                metadata={"file": "test1.py"},
            ),
        ]
        store.add(docs)

        with pytest.raises(VectorStoreError):
            store.search(query_embedding=[0.1, 0.2], top_k=5)

    def test_search_zero_query_vector(self):
        """Test search with zero query vector."""
        store = InMemoryVectorStore()
        docs = [
            VectorDocument(
                id="doc1",
                embedding=[0.1, 0.2, 0.3],
                metadata={"file": "test1.py"},
            ),
        ]
        store.add(docs)

        with pytest.raises(VectorStoreError):
            store.search(query_embedding=[0.0, 0.0, 0.0], top_k=5)

    def test_delete_documents(self):
        """Test deleting documents."""
        store = InMemoryVectorStore()
        docs = [
            VectorDocument(
                id="doc1",
                embedding=[0.1, 0.2, 0.3],
                metadata={"file": "test1.py"},
            ),
            VectorDocument(
                id="doc2",
                embedding=[0.4, 0.5, 0.6],
                metadata={"file": "test2.py"},
            ),
        ]
        store.add(docs)
        assert store.count() == 2

        store.delete(["doc1"])
        assert store.count() == 1

    def test_delete_nonexistent_document(self):
        """Test deleting non-existent document."""
        store = InMemoryVectorStore()
        docs = [
            VectorDocument(
                id="doc1",
                embedding=[0.1, 0.2, 0.3],
                metadata={"file": "test1.py"},
            ),
        ]
        store.add(docs)

        # Should not raise error
        store.delete(["nonexistent"])
        assert store.count() == 1

    def test_clear_store(self):
        """Test clearing the store."""
        store = InMemoryVectorStore()
        docs = [
            VectorDocument(
                id="doc1",
                embedding=[0.1, 0.2, 0.3],
                metadata={"file": "test1.py"},
            ),
        ]
        store.add(docs)
        assert store.count() == 1

        store.clear()
        assert store.count() == 0

    def test_count(self):
        """Test count method."""
        store = InMemoryVectorStore()
        assert store.count() == 0

        docs = [
            VectorDocument(
                id=f"doc{i}",
                embedding=[0.1, 0.2, 0.3],
                metadata={"file": f"test{i}.py"},
            )
            for i in range(5)
        ]
        store.add(docs)
        assert store.count() == 5
