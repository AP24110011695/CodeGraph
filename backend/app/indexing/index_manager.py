"""Stateful manager for per-repository vector indexes."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from app.indexing.indexing_models import IndexStatus, RepositoryIndex
from app.indexing.indexing_pipeline import IndexingPipeline, IndexingPipelineError
from app.rag.chunker import Chunker
from app.rag.embedding_service import EmbeddingService
from app.rag.vector_store import InMemoryVectorStore, VectorStore
from app.services.framework_detector import detector_service
from app.services.scanner_service import scanner_service

if TYPE_CHECKING:
    from storage.repository_store import RepositoryStore


class IndexAlreadyExistsError(Exception):
    """Raised when creating an already-ready index without rebuild permission."""


class IndexNotFoundError(Exception):
    """Raised when an operation requires an existing index."""


class IndexManager:
    """Creates, rebuilds, deletes, and reports repository indexes.

    Memory cache is used for hot access; when a ``RepositoryStore`` is attached,
    index metadata survives process restarts via SQLite.
    """

    def __init__(
        self,
        vector_store: VectorStore | None = None,
        pipeline: IndexingPipeline | None = None,
        repository_store: RepositoryStore | None = None,
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
        self._store = repository_store

    def get_index(self, upload_id: str) -> RepositoryIndex | None:
        """Return an index record if it exists (memory first, then SQLite)."""
        cached = self._indexes.get(upload_id)
        if cached is not None:
            return cached
        if self._store is not None:
            loaded = self._store.load_index(upload_id)
            if loaded is not None and loaded.status != IndexStatus.NOT_INDEXED:
                self._indexes[upload_id] = loaded
                return loaded
        return None

    def create_index(self, project_path: Path, upload_id: str, force: bool = False) -> RepositoryIndex:
        """Create an index, or replace its vectors when force is requested."""
        existing = self.get_index(upload_id)
        if existing and existing.status == IndexStatus.INDEXING:
            raise IndexAlreadyExistsError("Repository indexing is already in progress")

        index = existing or RepositoryIndex(upload_id=upload_id)
        index.status = IndexStatus.INDEXING
        index.error = None
        index.indexed_at = None
        if force or not existing:
            index.total_chunks = 0
            index.total_embeddings = 0
        self._indexes[upload_id] = index
        self._persist(index, project_path)

        before_ids = self._store_document_ids()
        try:
            from app.indexing.incremental_indexer import IncrementalIndexer

            indexer = IncrementalIndexer(self)
            result = indexer.index(project_path, upload_id, force=force)

            index.repository_name = str(result.repository_name)
            index.frameworks = list(result.frameworks)
            index.languages = dict(result.languages)
            index.total_files = int(result.total_files)

            if force:
                index.total_chunks = int(result.total_chunks)
                index.total_embeddings = int(result.total_embeddings)
            else:
                index.total_chunks += int(result.total_chunks)
                index.total_embeddings += int(result.total_embeddings)

            index.added = int(result.added)
            index.modified = int(result.modified)
            index.deleted = int(result.deleted)
            index.unchanged = int(result.unchanged)

            index.indexed_at = datetime.now(timezone.utc)
            index.status = IndexStatus.READY

            new_ids = self._store_document_ids() - before_ids
            if upload_id not in self._document_ids:
                self._document_ids[upload_id] = set()
            self._document_ids[upload_id].update(new_ids)

            self._persist(index, project_path)
            return index
        except Exception as exc:
            if force or not existing:
                self._delete_documents(upload_id)
            index.status = IndexStatus.FAILED
            index.error = str(exc)
            self._persist(index, project_path)
            if isinstance(exc, IndexingPipelineError):
                raise
            raise IndexingPipelineError(f"Indexing failed: {exc}") from exc

    def delete_index(self, upload_id: str, keep_record: bool = False) -> None:
        """Remove an index record and only its vectors."""
        if self.get_index(upload_id) is None and upload_id not in self._indexes:
            raise IndexNotFoundError(f"Repository index not found: {upload_id}")
        self._delete_documents(upload_id)

        if not keep_record:
            self._indexes.pop(upload_id, None)
            if self._store is not None:
                self._store.delete_repository(upload_id)

    def delete_file_vectors(self, upload_id: str, file_paths: list[str]) -> None:
        """Delete vectors corresponding to specific file paths."""
        if upload_id not in self._document_ids:
            return

        ids_to_delete = []
        for file_path in file_paths:
            prefix = f"{upload_id}:{file_path}:"
            for doc_id in self._document_ids[upload_id]:
                if doc_id.startswith(prefix):
                    ids_to_delete.append(doc_id)

        if ids_to_delete:
            self.vector_store.delete(ids_to_delete)
            self._document_ids[upload_id].difference_update(ids_to_delete)

            index = self._indexes.get(upload_id)
            if index:
                removed_count = len(ids_to_delete)
                index.total_chunks = max(0, index.total_chunks - removed_count)
                index.total_embeddings = max(0, index.total_embeddings - removed_count)
                self._persist(index)

    def _persist(self, index: RepositoryIndex, project_path: Path | None = None) -> None:
        if self._store is None:
            return
        self._store.save_index(index, extraction_path=project_path)

    def _delete_documents(self, upload_id: str) -> None:
        ids = self._document_ids.pop(upload_id, set())
        if ids:
            self.vector_store.delete(list(ids))

    def _store_document_ids(self) -> set[str]:
        """Obtain IDs for the built-in store; other stores track IDs on successful runs."""
        documents = getattr(self.vector_store, "_documents", None)
        return set(documents) if isinstance(documents, dict) else set()


_shared_index_manager: IndexManager | None = None


def get_shared_index_manager() -> IndexManager:
    """Return the process-wide IndexManager backed by SQLite repository store."""
    global _shared_index_manager
    if _shared_index_manager is None:
        from storage.repository_store import repository_store

        _shared_index_manager = IndexManager(repository_store=repository_store)
    return _shared_index_manager


def reset_shared_index_manager() -> None:
    """Clear the shared singleton (tests only)."""
    global _shared_index_manager
    _shared_index_manager = None
