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
        logger.info("INDEXING_PIPELINE: Starting indexing for %s at %s", upload_id, project_path)
        
        scan_result = self.scanner.scan(project_path)
        if not scan_result.files:
            raise IndexingPipelineError("Repository is empty")

        logger.info("INDEXING_PIPELINE: Scanned %d files", scan_result.total_files)
        logger.info("INDEXING_PIPELINE: Languages detected: %s", dict(scan_result.languages))

        detection = self.detector.detect(project_path, scan_result)
        parsing = ParserEngine.parse_project(project_path, scan_result)
        parsed_by_path = {result.path: result for result in parsing.files}

        logger.info("INDEXING_PIPELINE: Parsed %d files successfully", len(parsed_by_path))

        chunks: list[Chunk] = []
        seen_chunk_ids: set[str] = set()
        indexed_files = 0
        skipped_files = 0
        
        for file_info in scan_result.files:
            if file_info.language == "Unknown":
                skipped_files += 1
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
                indexed_files += 1
            except Exception:
                logger.warning("Skipping file that could not be chunked: %s", file_info.path, exc_info=True)
                skipped_files += 1

        logger.info("INDEXING_PIPELINE: Generated %d chunks from %d files (skipped %d)", len(chunks), indexed_files, skipped_files)

        if not chunks:
            raise IndexingPipelineError("Repository contains no supported indexable files")

        documents = self._embed_documents(chunks)
        logger.info("INDEXING_PIPELINE: Generated %d embeddings from %d chunks", len(documents), len(chunks))
        
        if not documents:
            raise IndexingPipelineError("No embeddings could be generated for repository")

        self.vector_store.add(documents)
        logger.info("INDEXING_PIPELINE: Stored %d vectors in vector store", len(documents))
        
        # Trigger save for persistent vector stores
        if hasattr(self.vector_store, 'save'):
            self.vector_store.save()
        
        # Trigger save for persistent vector stores
        if hasattr(self.vector_store, '_save'):
            self.vector_store._save()
        
        frameworks = [match.name for match in detection.frameworks + detection.backend]
        logger.info("INDEXING_PIPELINE: Frameworks detected: %s", frameworks)
        
        result = {
            "repository_name": scan_result.project_name,
            "frameworks": list(dict.fromkeys(frameworks)),
            "languages": dict(scan_result.languages),
            "files": scan_result.total_files,
            "chunks": len(documents),
            "embeddings": len(documents),
        }
        
        logger.info("INDEXING_PIPELINE: Indexing complete for %s - chunks: %d, embeddings: %d", 
                   upload_id, result["chunks"], result["embeddings"])
        
        return result

    def index_files(self, project_path: Path, upload_id: str, original_scan: object, files_to_index: list) -> dict[str, object]:
        logger.info("INDEXING_PIPELINE: Indexing %d files for %s", len(files_to_index), upload_id)
        
        try:
            import copy
            subset_scan = copy.copy(original_scan)
            subset_scan.files = files_to_index
            
            logger.info("INDEXING_PIPELINE: Step 1 - Detecting frameworks")
            detection = self.detector.detect(project_path, original_scan)
            logger.info("INDEXING_PIPELINE: Step 1 complete - Frameworks detected")
            
            logger.info("INDEXING_PIPELINE: Step 2 - Parsing %d files", len(files_to_index))
            parsing = ParserEngine.parse_project(project_path, subset_scan)
            parsed_by_path = {result.path: result for result in parsing.files}
            logger.info("INDEXING_PIPELINE: Step 2 complete - Parsed %d files", len(parsed_by_path))
            
            logger.info("INDEXING_PIPELINE: Step 3 - Chunking files")
            chunks: list[Chunk] = []
            seen_chunk_ids: set[str] = set()
            indexed_files = 0
            
            for file_info in files_to_index:
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
                    indexed_files += 1
                except Exception:
                    logger.warning("Skipping file that could not be chunked: %s", file_info.path, exc_info=True)
                    
            logger.info("INDEXING_PIPELINE: Step 3 complete - Generated %d chunks from %d files", len(chunks), indexed_files)
                
            if not chunks:
                frameworks = [match.name for match in detection.frameworks + detection.backend]
                logger.info("INDEXING_PIPELINE: No chunks generated, returning empty result")
                return {
                    "repository_name": original_scan.project_name,
                    "frameworks": list(dict.fromkeys(frameworks)),
                    "languages": dict(original_scan.languages),
                    "files": len(files_to_index),
                    "chunks": 0,
                    "embeddings": 0,
                }

            logger.info("INDEXING_PIPELINE: Step 4 - Generating embeddings for %d chunks", len(chunks))
            documents = self._embed_documents(chunks)
            logger.info("INDEXING_PIPELINE: Step 4 complete - Generated %d embeddings from %d chunks", len(documents), len(chunks))
            
            if documents:
                logger.info("INDEXING_PIPELINE: Step 5 - Storing %d vectors in vector store", len(documents))
                self.vector_store.add(documents)
                logger.info("INDEXING_PIPELINE: Step 5 complete - Vectors stored")
                
                # Trigger save for persistent vector stores
                if hasattr(self.vector_store, 'save'):
                    logger.info("INDEXING_PIPELINE: Step 6 - Saving vector store")
                    self.vector_store.save()
                    logger.info("INDEXING_PIPELINE: Step 6 complete - Vector store saved")

            frameworks = [match.name for match in detection.frameworks + detection.backend]
            result = {
                "repository_name": original_scan.project_name,
                "frameworks": list(dict.fromkeys(frameworks)),
                "languages": dict(original_scan.languages),
                "files": len(files_to_index),
                "chunks": len(documents),
                "embeddings": len(documents),
            }
            
            logger.info("INDEXING_PIPELINE: File indexing complete for %s - chunks: %d, embeddings: %d", 
                       upload_id, result["chunks"], result["embeddings"])
            
            return result
        except Exception as e:
            logger.error("INDEXING_PIPELINE: File indexing failed for %s: %s", upload_id, e, exc_info=True)
            raise

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
