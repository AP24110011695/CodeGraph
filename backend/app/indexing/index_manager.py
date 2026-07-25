"""Stateful manager for per-repository vector indexes."""

from datetime import datetime, timezone
from pathlib import Path

from app.indexing.indexing_models import IndexStatus, RepositoryIndex
from app.indexing.indexing_pipeline import IndexingPipeline, IndexingPipelineError
from app.rag.chunker import Chunker
from app.rag.embedding_service import EmbeddingService
from app.rag.vector_store import InMemoryVectorStore, VectorStore
from app.services.framework_detector import detector_service
from app.services.scanner_service import scanner_service


class IndexAlreadyExistsError(Exception):
    """Raised when creating an already-ready index without rebuild permission."""


class IndexNotFoundError(Exception):
    """Raised when an operation requires an existing index."""


class IndexManager:
    """Creates, rebuilds, deletes, and reports repository indexes."""

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        pipeline: IndexingPipeline | None = None,
    ) -> None:
        self.vector_store = vector_store or InMemoryVectorStore()
        self.pipeline = pipeline or IndexingPipeline(
            scanner=scanner_service,
            detector=detector_service,
            chunker=Chunker(),
            embedding_service=EmbeddingService(),
            vector_store=self.vector_store,
        )
        self._indexes: dict[str, RepositoryIndex] = {}
        self._document_ids: dict[str, set[str]] = {}

    def get_index(self, upload_id: str) -> RepositoryIndex | None:
        """Return an index record if it exists."""
        return self._indexes.get(upload_id)

    def create_index(self, project_path: Path, upload_id: str, rebuild: bool = False) -> RepositoryIndex:
        """Create an index, or replace its vectors when rebuild is requested."""
        existing = self._indexes.get(upload_id)
        if existing and existing.status == IndexStatus.INDEXING:
            raise IndexAlreadyExistsError("Repository indexing is already in progress")
        if existing and existing.status == IndexStatus.READY and not rebuild:
            raise IndexAlreadyExistsError("Repository index already exists")
        if existing and rebuild:
            self._delete_documents(upload_id)

        index = existing or RepositoryIndex(upload_id=upload_id)
        index.status = IndexStatus.INDEXING
        index.error = None
        index.indexed_at = None
        index.total_chunks = index.total_embeddings = 0
        self._indexes[upload_id] = index
        before_ids = self._store_document_ids()
        try:
            result = self.pipeline.index(project_path, upload_id)
            index.repository_name = str(result["repository_name"])
            index.frameworks = list(result["frameworks"])
            index.languages = dict(result["languages"])
            index.total_files = int(result["files"])
            index.total_chunks = int(result["chunks"])
            index.total_embeddings = int(result["embeddings"])
            index.indexed_at = datetime.now(timezone.utc)
            index.status = IndexStatus.READY
            self._document_ids[upload_id] = self._store_document_ids() - before_ids
            return index
        except Exception as exc:
            self._delete_documents(upload_id)
            index.status = IndexStatus.FAILED
            index.error = str(exc)
            if isinstance(exc, IndexingPipelineError):
                raise
            raise IndexingPipelineError(f"Indexing failed: {exc}") from exc

    def delete_index(self, upload_id: str) -> None:
        """Remove an index record and only its vectors."""
        if upload_id not in self._indexes:
            raise IndexNotFoundError(f"Repository index not found: {upload_id}")
        self._delete_documents(upload_id)
        del self._indexes[upload_id]

    def _delete_documents(self, upload_id: str) -> None:
        ids = self._document_ids.pop(upload_id, set())
        if ids:
            self.vector_store.delete(list(ids))

    def _store_document_ids(self) -> set[str]:
        """Obtain IDs for the built-in store; other stores track IDs on successful runs."""
        documents = getattr(self.vector_store, "_documents", None)
        return set(documents) if isinstance(documents, dict) else set()
