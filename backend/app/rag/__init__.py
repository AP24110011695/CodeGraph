"""RAG (Retrieval-Augmented Generation) module for CodeGraph."""

from app.rag.chunker import Chunker, Chunk
from app.rag.embedding_service import EmbeddingService, EmbeddingProvider
from app.rag.vector_store import VectorStore, InMemoryVectorStore
from app.rag.retriever import Retriever
from app.rag.rag_pipeline import RAGPipeline

__all__ = [
    "Chunker",
    "Chunk",
    "EmbeddingService",
    "EmbeddingError",
    "Retriever",
    "RetrievalError",
    "VectorStore",
    "InMemoryVectorStore",
    "RAGPipeline",
    "RAGPipelineError",
    "rag_engine",
    "RAGEngine",
    "QueryAnalyzer",
    "ContextSelector",
    "ContextOptimizer",
    "CitationBuilder",
    "RetrievalStatistics"
]
