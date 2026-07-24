"""RAG pipeline orchestrating chunking, embedding, and retrieval."""

import logging
from pathlib import Path
from typing import Any

from app.parsers.ast_models import FileParsingResult, ProjectParsingResult
from app.parsers.parser_engine import ParserEngine
from app.rag.chunker import Chunker, Chunk
from app.rag.embedding_service import EmbeddingService, EmbeddingError
from app.rag.retriever import Retriever, RetrievalError
from app.rag.vector_store import VectorStore, InMemoryVectorStore
from app.services.scanner_service import ScanResult, scanner_service

logger = logging.getLogger(__name__)


class RAGPipelineError(Exception):
    """Exception raised when RAG pipeline operations fail."""

    pass


class RAGPipeline:
    """RAG pipeline for indexing and retrieving code context."""

    def __init__(
        self,
        chunker: Chunker | None = None,
        embedding_service: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        """Initialize the RAG pipeline.

        Args:
            chunker: Chunker instance (defaults to new instance)
            embedding_service: Embedding service instance (defaults to new instance)
            vector_store: Vector store instance (defaults to new InMemoryVectorStore)
        """
        self.chunker = chunker or Chunker()
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = vector_store or InMemoryVectorStore()
        self.retriever = Retriever(self.vector_store, self.embedding_service)

    def index_repository(
        self,
        project_path: Path,
        upload_id: str,
        scan_result: ScanResult | None = None,
        parsing_result: ProjectParsingResult | None = None,
    ) -> dict[str, Any]:
        """Index a repository for RAG retrieval.

        Args:
            project_path: Path to the extracted repository
            upload_id: Upload identifier
            scan_result: Optional scan result (will scan if not provided)
            parsing_result: Optional parsing result (will parse if not provided)

        Returns:
            Dictionary with indexing statistics

        Raises:
            RAGPipelineError: If indexing fails
        """
        if not project_path.exists():
            raise RAGPipelineError(f"Project path does not exist: {project_path}")

        # Scan if not provided
        if scan_result is None:
            try:
                scan_result = scanner_service.scan(project_path)
            except Exception as e:
                raise RAGPipelineError(f"Failed to scan repository: {str(e)}")

        # Parse if not provided
        if parsing_result is None:
            try:
                parsing_result = ParserEngine.parse_project(project_path, scan_result)
            except Exception as e:
                raise RAGPipelineError(f"Failed to parse repository: {str(e)}")

        # Create a lookup for parsing results
        parsing_lookup = {f.path: f for f in parsing_result.files}

        # Chunk all files
        all_chunks = []
        for file_info in scan_result.files:
            file_path = project_path / file_info.path
            parsing_result_for_file = parsing_lookup.get(file_info.path)

            try:
                chunks = self.chunker.chunk_file(
                    file_path=file_path,
                    rel_path=file_info.path,
                    language=file_info.language,
                    upload_id=upload_id,
                    parsing_result=parsing_result_for_file,
                )
                all_chunks.extend(chunks)
            except Exception as e:
                logger.warning(f"Failed to chunk file {file_info.path}: {e}")
                continue

        if not all_chunks:
            raise RAGPipelineError("No chunks generated from repository")

        # Add chunks to vector store
        try:
            self.retriever.add_chunks(all_chunks)
        except RetrievalError as e:
            raise RAGPipelineError(f"Failed to add chunks to vector store: {str(e)}")

        return {
            "upload_id": upload_id,
            "files_indexed": len(scan_result.files),
            "chunks_created": len(all_chunks),
            "vector_store_count": self.vector_store.count(),
        }

    def retrieve(
        self,
        query: str,
        upload_id: str,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Retrieve relevant chunks for a query.

        Args:
            query: User query
            upload_id: Upload identifier to filter results
            top_k: Number of results to return

        Returns:
            Dictionary with query and retrieved matches

        Raises:
            RAGPipelineError: If retrieval fails
        """
        if not query or not query.strip():
            raise RAGPipelineError("Query cannot be empty")
            
        if self.vector_store.count() == 0:
            raise RAGPipelineError("Vector store is empty. Must index repository first.")

        try:
            matches = self.retriever.retrieve(
                query=query,
                top_k=top_k,
                filters={"upload_id": upload_id},
            )
        except RetrievalError as e:
            raise RAGPipelineError(f"Retrieval failed: {str(e)}")

        return {
            "query": query,
            "matches": matches,
        }

    def clear_upload(self, upload_id: str) -> None:
        """Clear indexed data for a specific upload.

        Args:
            upload_id: Upload identifier

        Raises:
            RAGPipelineError: If clearing fails
        """
        try:
            self.retriever.delete_by_upload_id(upload_id)
        except RetrievalError as e:
            raise RAGPipelineError(f"Failed to clear upload: {str(e)}")

    def get_stats(self) -> dict[str, Any]:
        """Get pipeline statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "vector_store_count": self.vector_store.count(),
            "embedding_dimension": self.embedding_service.dimension,
        }
