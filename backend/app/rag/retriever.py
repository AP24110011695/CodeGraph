"""Retriever for top-K similarity search in RAG."""

import logging
from typing import Any, List, Dict

from app.rag.chunker import Chunk
from app.rag.embedding_service import EmbeddingService, EmbeddingError
from app.rag.vector_store import VectorStore, VectorDocument, VectorStoreError
from app.rag.keyword_retriever import KeywordRetriever
from app.rag.hybrid_ranker import HybridRanker
from app.rag.query_analyzer import QueryAnalyzer

logger = logging.getLogger(__name__)


class RetrievalError(Exception):
    """Exception raised when retrieval operations fail."""

    pass


class Retriever:
    """Retriever for top-K similarity search."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_service: EmbeddingService,
    ) -> None:
        """Initialize the retriever.

        Args:
            vector_store: Vector store instance
            embedding_service: Embedding service instance
        """
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.keyword_retriever = KeywordRetriever()
        self.hybrid_ranker = HybridRanker()
        self.query_analyzer = QueryAnalyzer()

    def retrieve(
        self,
        query: str,
        upload_id: str | None = None,
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
        intent: str = "general_explanation",
        memory_context: List[Dict] = None,
    ) -> list[dict[str, Any]]:
        """Retrieve top-K relevant chunks for a query.

        Args:
            query: User query
            upload_id: Optional upload identifier
            top_k: Number of results to return
            filters: Optional metadata filters (e.g., {"upload_id": "xxx"})
            intent: The parsed intent of the query.
            memory_context: Optional context from repository memory.

        Returns:
            List of retrieved chunks with scores

        Raises:
            RetrievalError: If retrieval fails
        """
        if not query or not query.strip():
            raise RetrievalError("Query cannot be empty")
            
        if upload_id:
            filters = filters or {}
            filters["upload_id"] = upload_id

        # 1. Expand Query
        expanded_terms = self.query_analyzer.expand_query(query.lower())
        expanded_query = query + " " + " ".join(expanded_terms)

        try:
            # Generate query embedding
            query_embedding = self.embedding_service.embed(expanded_query)
        except EmbeddingError as e:
            logger.exception("Failed to generate query embedding")
            raise RetrievalError(f"Failed to generate query embedding: {str(e)}")

        try:
            # Search vector store (fetch more candidates to rank)
            semantic_results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k * 2,
                filters=filters,
            )
        except VectorStoreError as e:
            logger.exception("Vector store search failed")
            raise RetrievalError(f"Vector store search failed: {str(e)}")

        try:
            # Search keyword store
            keyword_results = self.keyword_retriever.search(
                query=expanded_query,
                top_k=top_k * 2,
                filters=filters,
            )
        except Exception as e:
            logger.exception("Keyword store search failed")
            keyword_results = []

        # Hybrid Ranking
        ranked_results = self.hybrid_ranker.rank(
            semantic_results=semantic_results,
            keyword_results=keyword_results,
            intent=intent,
            memory_context=memory_context,
            top_k=top_k
        )

        # Format results
        formatted_results = []
        for doc, score in ranked_results:
            formatted_results.append({
                "file": doc.metadata.get("file_path", ""),
                "language": doc.metadata.get("language", ""),
                "chunk_id": doc.metadata.get("chunk_id", doc.id),
                "score": score,
                "content": doc.metadata.get("content", ""),
                "start_line": doc.metadata.get("start_line", 0),
                "end_line": doc.metadata.get("end_line", 0),
                "role": doc.metadata.get("role", ""),
                "symbol_kind": doc.metadata.get("symbol_kind", ""),
            })

        return formatted_results

    def add_chunks(self, chunks: list[Chunk]) -> None:
        """Add chunks to the vector store with embeddings.

        Args:
            chunks: List of chunks to add

        Raises:
            RetrievalError: If addition fails
        """
        if not chunks:
            logger.warning("No chunks to add")
            return

        # Generate embeddings for all chunks
        texts = [chunk.content for chunk in chunks]
        try:
            embeddings = self.embedding_service.embed_batch(texts)
        except EmbeddingError as e:
            logger.exception("Failed to generate embeddings for chunks")
            raise RetrievalError(f"Failed to generate embeddings: {str(e)}")

        if len(embeddings) != len(chunks):
            raise RetrievalError(
                f"Embedding count mismatch: expected {len(chunks)}, got {len(embeddings)}"
            )

        # Create vector documents
        documents = []
        for chunk, embedding in zip(chunks, embeddings):
            doc = VectorDocument(
                id=chunk.chunk_id,
                embedding=embedding,
                metadata={
                    "upload_id": chunk.upload_id,
                    "file_path": chunk.file_path,
                    "language": chunk.language,
                    "chunk_id": chunk.chunk_id,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "content": chunk.content,
                    **chunk.metadata,
                },
            )
            documents.append(doc)

        # Add to vector store
        try:
            self.vector_store.add(documents)
            self.keyword_retriever.add(documents)
        except VectorStoreError as e:
            logger.exception("Failed to add documents to vector store")
            raise RetrievalError(f"Failed to add documents: {str(e)}")

        logger.info(f"Added {len(documents)} chunks to vector store and keyword index")

    def delete_by_upload_id(self, upload_id: str) -> None:
        """Delete all chunks for a specific upload.

        Args:
            upload_id: Upload identifier

        Raises:
            RetrievalError: If deletion fails
        """
        logger.warning(f"Deletion by upload_id not fully implemented for {upload_id}")
        self.keyword_retriever.clear()  # Since it's in-memory, clearing is simple if single upload, but should ideally filter by upload_id.
