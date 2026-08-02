"""Vector store with abstract interface for RAG."""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import numpy as np
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class VectorDocument:
    """A document with its embedding vector."""

    id: str
    embedding: list[float]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "embedding": self.embedding,
            "metadata": self.metadata,
        }


class VectorStoreError(Exception):
    """Exception raised when vector store operations fail."""

    pass


class VectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    def add(self, documents: list[VectorDocument]) -> None:
        """Add documents to the vector store.

        Args:
            documents: List of documents to add

        Raises:
            VectorStoreError: If addition fails
        """
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[VectorDocument, float]]:
        """Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of (document, score) tuples sorted by score (descending)

        Raises:
            VectorStoreError: If search fails
        """
        pass

    @abstractmethod
    def delete(self, document_ids: list[str]) -> None:
        """Delete documents from the vector store.

        Args:
            document_ids: List of document IDs to delete

        Raises:
            VectorStoreError: If deletion fails
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all documents from the vector store.

        Raises:
            VectorStoreError: If clearing fails
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """Return the number of documents in the store.

        Returns:
            Number of documents
        """
        pass


class InMemoryVectorStore(VectorStore):
    """In-memory vector store using numpy for similarity search."""

    def __init__(self, dimension: int | None = None) -> None:
        """Initialize in-memory vector store.

        Args:
            dimension: Embedding dimension (auto-detected if None)
        """
        self._documents: dict[str, VectorDocument] = {}
        self._embeddings: list[list[float]] = []
        self._dimension = dimension

    def add(self, documents: list[VectorDocument]) -> None:
        """Add documents to the vector store."""
        for doc in documents:
            if doc.id in self._documents:
                logger.warning(f"Document {doc.id} already exists, overwriting")
                self._embeddings = [
                    emb for i, emb in enumerate(self._embeddings)
                    if list(self._documents.keys())[i] != doc.id
                ]

            self._documents[doc.id] = doc
            self._embeddings.append(doc.embedding)

            if self._dimension is None:
                self._dimension = len(doc.embedding)
            elif len(doc.embedding) != self._dimension:
                raise VectorStoreError(
                    f"Embedding dimension mismatch: expected {self._dimension}, got {len(doc.embedding)}"
                )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[VectorDocument, float]]:
        """Search for similar documents using cosine similarity."""
        if not self._documents:
            return []

        if self._dimension is not None and len(query_embedding) != self._dimension:
            raise VectorStoreError(
                f"Query embedding dimension mismatch: expected {self._dimension}, got {len(query_embedding)}"
            )

        # Apply filters if provided
        candidate_docs = []
        candidate_embeddings = []

        for doc_id, doc in self._documents.items():
            if filters is None or self._matches_filters(doc.metadata, filters):
                candidate_docs.append(doc)
                candidate_embeddings.append(doc.embedding)

        if not candidate_docs:
            return []

        # Calculate cosine similarity
        query_vec = np.array(query_embedding)
        doc_matrix = np.array(candidate_embeddings)

        # Normalize vectors
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            raise VectorStoreError("Query embedding is zero vector")

        query_vec = query_vec / query_norm

        doc_norms = np.linalg.norm(doc_matrix, axis=1)
        doc_norms[doc_norms == 0] = 1  # Avoid division by zero
        doc_matrix = doc_matrix / doc_norms[:, np.newaxis]

        # Compute similarities
        similarities = np.dot(doc_matrix, query_vec)

        # Get top-k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            doc = candidate_docs[idx]
            score = float(similarities[idx])
            results.append((doc, score))

        return results

    def _matches_filters(self, metadata: dict[str, Any], filters: dict[str, Any]) -> bool:
        """Check if metadata matches all filters.

        Args:
            metadata: Document metadata
            filters: Filter criteria

        Returns:
            True if all filters match
        """
        for key, value in filters.items():
            if key not in metadata:
                return False
            if metadata[key] != value:
                return False
        return True

    def delete(self, document_ids: list[str]) -> None:
        """Delete documents from the vector store."""
        for doc_id in document_ids:
            if doc_id in self._documents:
                del self._documents[doc_id]
                # Rebuild embeddings list
                self._embeddings = [doc.embedding for doc in self._documents.values()]
            else:
                logger.warning(f"Document {doc_id} not found for deletion")

    def clear(self) -> None:
        """Clear all documents from the vector store."""
        self._documents.clear()
        self._embeddings.clear()

    def count(self) -> int:
        """Return the number of documents in the store."""
        return len(self._documents)

    @property
    def dimension(self) -> int | None:
        """Return the embedding dimension."""
        return self._dimension


class PersistentVectorStore(VectorStore):
    """Persistent vector store using disk-based JSON storage."""

    def __init__(self, storage_path: Path | None = None, dimension: int | None = None) -> None:
        """Initialize persistent vector store.
        
        Args:
            storage_path: Path to storage directory (defaults to backend/storage/vectors)
            dimension: Embedding dimension (auto-detected if None)
        """
        if storage_path is None:
            storage_path = Path(settings.VECTOR_STORAGE_PATH) if settings.VECTOR_STORAGE_PATH else Path("storage/vectors")
        
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self._documents: dict[str, VectorDocument] = {}
        self._embeddings: list[list[float]] = []
        self._dimension = dimension
        self._dirty = False  # Track if changes need to be saved
        
        # Load existing data on initialization
        self._load()
    
    def _load(self) -> None:
        """Load documents from disk."""
        metadata_file = self.storage_path / "metadata.json"
        if not metadata_file.exists():
            logger.info("PersistentVectorStore: No existing data found, starting fresh")
            return
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._dimension = data.get("dimension")
            documents_data = data.get("documents", {})
            
            for doc_id, doc_data in documents_data.items():
                self._documents[doc_id] = VectorDocument(
                    id=doc_data["id"],
                    embedding=doc_data["embedding"],
                    metadata=doc_data["metadata"]
                )
                self._embeddings.append(doc_data["embedding"])
            
            logger.info("PersistentVectorStore: Loaded %d documents from disk", len(self._documents))
            
        except Exception as e:
            logger.warning("PersistentVectorStore: Failed to load data from disk: %s", e)
            self._documents.clear()
            self._embeddings.clear()
    
    def _save(self) -> None:
        """Save documents to disk."""
        if not self._dirty:
            return
        
        try:
            documents_data = {}
            for doc_id, doc in self._documents.items():
                documents_data[doc_id] = {
                    "id": doc.id,
                    "embedding": doc.embedding,
                    "metadata": doc.metadata
                }
            
            data = {
                "dimension": self._dimension,
                "documents": documents_data
            }
            
            metadata_file = self.storage_path / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            self._dirty = False
            logger.info("PersistentVectorStore: Saved %d documents to disk", len(self._documents))
            
        except Exception as e:
            logger.error("PersistentVectorStore: Failed to save data to disk: %s", e)
            # Don't raise exception - allow in-memory operation to continue
    
    def add(self, documents: list[VectorDocument]) -> None:
        """Add documents to the vector store."""
        for doc in documents:
            if doc.id in self._documents:
                logger.warning(f"Document {doc.id} already exists, overwriting")
                self._embeddings = [
                    emb for i, emb in enumerate(self._embeddings)
                    if list(self._documents.keys())[i] != doc.id
                ]

            self._documents[doc.id] = doc
            self._embeddings.append(doc.embedding)

            if self._dimension is None:
                self._dimension = len(doc.embedding)
            elif len(doc.embedding) != self._dimension:
                raise VectorStoreError(
                    f"Embedding dimension mismatch: expected {self._dimension}, got {len(doc.embedding)}"
                )
        
        self._dirty = True
    
    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[tuple[VectorDocument, float]]:
        """Search for similar documents using cosine similarity."""
        if not self._documents:
            return []

        if self._dimension is not None and len(query_embedding) != self._dimension:
            raise VectorStoreError(
                f"Query embedding dimension mismatch: expected {self._dimension}, got {len(query_embedding)}"
            )

        # Apply filters if provided
        candidate_docs = []
        candidate_embeddings = []

        for doc_id, doc in self._documents.items():
            if filters is None or self._matches_filters(doc.metadata, filters):
                candidate_docs.append(doc)
                candidate_embeddings.append(doc.embedding)

        if not candidate_docs:
            return []

        # Calculate cosine similarity
        query_vec = np.array(query_embedding)
        doc_matrix = np.array(candidate_embeddings)

        # Normalize vectors
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            raise VectorStoreError("Query embedding is zero vector")

        query_vec = query_vec / query_norm

        doc_norms = np.linalg.norm(doc_matrix, axis=1)
        doc_norms[doc_norms == 0] = 1  # Avoid division by zero
        doc_matrix = doc_matrix / doc_norms[:, np.newaxis]

        # Compute similarities
        similarities = np.dot(doc_matrix, query_vec)

        # Get top-k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            doc = candidate_docs[idx]
            score = float(similarities[idx])
            results.append((doc, score))

        return results
    
    def _matches_filters(self, metadata: dict[str, Any], filters: dict[str, Any]) -> bool:
        """Check if metadata matches all filters.

        Args:
            metadata: Document metadata
            filters: Filter criteria

        Returns:
            True if all filters match
        """
        for key, value in filters.items():
            if key not in metadata:
                return False
            if metadata[key] != value:
                return False
        return True

    def delete(self, document_ids: list[str]) -> None:
        """Delete documents from the vector store."""
        for doc_id in document_ids:
            if doc_id in self._documents:
                del self._documents[doc_id]
                # Rebuild embeddings list
                self._embeddings = [doc.embedding for doc in self._documents.values()]
            else:
                logger.warning(f"Document {doc_id} not found for deletion")
        
        self._dirty = True
        self._save()

    def clear(self) -> None:
        """Clear all documents from the vector store."""
        self._documents.clear()
        self._embeddings.clear()
        self._dirty = True
        self._save()

    def save(self) -> None:
        """Explicitly save to disk (useful after batch operations)."""
        self._save()

    def count(self) -> int:
        """Return the number of documents in the store."""
        return len(self._documents)

    @property
    def dimension(self) -> int | None:
        """Return the embedding dimension."""
        return self._dimension
