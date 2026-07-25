"""Pipeline that converts an extracted repository into vector documents."""

import logging
from collections.abc import Callable
from pathlib import Path

from app.parsers.parser_engine import ParserEngine
from app.rag.chunker import Chunk, Chunker
from app.rag.embedding_service import EmbeddingService
from app.rag.vector_store import VectorDocument, VectorStore
from app.services.framework_detector import FrameworkDetector
from app.services.scanner_service import RepositoryScanner

logger = logging.getLogger(__name__)


class IndexingPipelineError(Exception):
    """Raised when a repository cannot produce a usable index."""


class IndexingPipeline:
    """Coordinates existing scanner, detector, parser, chunker and RAG services."""

    def __init__(
        self,
        scanner: RepositoryScanner,
        detector: FrameworkDetector,
        chunker: Chunker,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ) -> None:
        self.scanner = scanner
        self.detector = detector
        self.chunker = chunker
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def index(self, project_path: Path, upload_id: str) -> dict[str, object]:
        """Index supported readable files, preserving progress through local failures."""
        scan_result = self.scanner.scan(project_path)
        if not scan_result.files:
            raise IndexingPipelineError("Repository is empty")

        detection = self.detector.detect(project_path, scan_result)
        parsing = ParserEngine.parse_project(project_path, scan_result)
        parsed_by_path = {result.path: result for result in parsing.files}

        chunks: list[Chunk] = []
        seen_chunk_ids: set[str] = set()
        for file_info in scan_result.files:
            if file_info.language == "Unknown":
                continue
            try:
                file_chunks = self.chunker.chunk_file(
                    project_path / file_info.path,
                    file_info.path,
                    file_info.language,
                    upload_id,
                    parsed_by_path.get(file_info.path),
                )
                for chunk in file_chunks:
                    if chunk.chunk_id not in seen_chunk_ids and chunk.content.strip():
                        seen_chunk_ids.add(chunk.chunk_id)
                        chunks.append(chunk)
            except Exception:
                logger.warning("Skipping file that could not be chunked: %s", file_info.path, exc_info=True)

        if not chunks:
            raise IndexingPipelineError("Repository contains no supported indexable files")

        documents = self._embed_documents(chunks)
        if not documents:
            raise IndexingPipelineError("No embeddings could be generated for repository")

        self.vector_store.add(documents)
        frameworks = [match.name for match in detection.frameworks + detection.backend]
        return {
            "repository_name": scan_result.project_name,
            "frameworks": list(dict.fromkeys(frameworks)),
            "languages": dict(scan_result.languages),
            "files": scan_result.total_files,
            "chunks": len(documents),
            "embeddings": len(documents),
        }

    def _embed_documents(self, chunks: list[Chunk]) -> list[VectorDocument]:
        """Embed in a batch; fall back per chunk so one bad input does not stop a run."""
        try:
            embeddings = self.embedding_service.embed_batch([chunk.content for chunk in chunks])
            if len(embeddings) != len(chunks):
                raise ValueError("Embedding provider returned an unexpected number of vectors")
            pairs = zip(chunks, embeddings)
            return [self._document(chunk, embedding) for chunk, embedding in pairs]
        except Exception:
            logger.warning("Batch embedding failed; falling back to individual chunks", exc_info=True)

        documents: list[VectorDocument] = []
        for chunk in chunks:
            try:
                documents.append(self._document(chunk, self.embedding_service.embed(chunk.content)))
            except Exception:
                logger.warning("Skipping chunk with failed embedding: %s", chunk.chunk_id, exc_info=True)
        return documents

    @staticmethod
    def _document(chunk: Chunk, embedding: list[float]) -> VectorDocument:
        return VectorDocument(
            id=f"{chunk.upload_id}:{chunk.chunk_id}",
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
