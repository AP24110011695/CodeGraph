"""Repository metadata store backed by SQLite."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from app.core.paths import resolve_repository_path
from app.indexing.indexing_models import IndexStatus, RepositoryIndex
from storage.database import get_session_factory, init_db
from storage.models import RepositoryRow


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RepositoryStore:
    """Source of truth for repository paths, index status, and analysis metadata."""

    def __init__(self, session_factory: sessionmaker[Session] | None = None) -> None:
        if session_factory is None:
            init_db()
        self._session_factory = session_factory or get_session_factory()

    def register_upload(
        self,
        upload_id: str,
        extraction_path: str | Path,
        *,
        repository_id: str | None = None,
        status: str = "UPLOADED",
    ) -> None:
        """Create or update a repository row after upload/extract."""
        path = str(Path(extraction_path))
        with self._session_factory() as session:
            row = session.get(RepositoryRow, upload_id)
            if row is None:
                row = RepositoryRow(
                    upload_id=upload_id,
                    repository_id=repository_id or upload_id,
                    extraction_path=path,
                    status=status,
                    indexing_state=IndexStatus.NOT_INDEXED.value,
                    created_at=_utcnow(),
                    updated_at=_utcnow(),
                )
                session.add(row)
            else:
                row.extraction_path = path
                row.repository_id = repository_id or row.repository_id or upload_id
                row.status = status
                row.updated_at = _utcnow()
            session.commit()

    def get_repository(self, upload_id: str) -> dict[str, Any] | None:
        """Return a plain dict of repository metadata, or None."""
        with self._session_factory() as session:
            row = session.get(RepositoryRow, upload_id)
            if row is None:
                return None
            return self._row_to_dict(row)

    def resolve_path(self, upload_id: str) -> Path | None:
        """Resolve extraction path from DB, then filesystem fallbacks."""
        with self._session_factory() as session:
            row = session.get(RepositoryRow, upload_id)
            if row and row.extraction_path:
                candidate = Path(row.extraction_path)
                if candidate.is_dir():
                    return candidate
        return resolve_repository_path(upload_id)

    def save_index(self, index: RepositoryIndex, extraction_path: str | Path | None = None) -> None:
        """Persist index metadata from a RepositoryIndex domain object."""
        path = str(Path(extraction_path)) if extraction_path else ""
        with self._session_factory() as session:
            row = session.get(RepositoryRow, index.upload_id)
            if row is None:
                resolved = path or str(resolve_repository_path(index.upload_id) or "")
                row = RepositoryRow(
                    upload_id=index.upload_id,
                    repository_id=index.upload_id,
                    extraction_path=resolved,
                    created_at=_utcnow(),
                )
                session.add(row)
            elif path:
                row.extraction_path = path

            row.repository_name = index.repository_name or ""
            row.frameworks_json = json.dumps(list(index.frameworks or []))
            row.languages_json = json.dumps(dict(index.languages or {}))
            row.total_files = int(index.total_files or 0)
            row.total_chunks = int(index.total_chunks or 0)
            row.total_embeddings = int(index.total_embeddings or 0)
            row.added = int(index.added or 0)
            row.modified = int(index.modified or 0)
            row.deleted = int(index.deleted or 0)
            row.unchanged = int(index.unchanged or 0)
            row.indexing_state = index.status.value
            if index.status == IndexStatus.READY:
                row.status = "READY"
            elif index.status == IndexStatus.FAILED:
                row.status = "FAILED"
            elif index.status == IndexStatus.INDEXING:
                row.status = "INDEXING"
            row.error = index.error
            row.indexed_at = index.indexed_at
            row.updated_at = _utcnow()
            session.commit()

    def load_index(self, upload_id: str) -> RepositoryIndex | None:
        """Load a RepositoryIndex from SQLite, or None if unknown."""
        with self._session_factory() as session:
            row = session.get(RepositoryRow, upload_id)
            if row is None:
                return None
            try:
                status = IndexStatus(row.indexing_state)
            except ValueError:
                status = IndexStatus.NOT_INDEXED
            return RepositoryIndex(
                upload_id=row.upload_id,
                repository_name=row.repository_name or "",
                frameworks=json.loads(row.frameworks_json or "[]"),
                languages=json.loads(row.languages_json or "{}"),
                total_files=row.total_files,
                total_chunks=row.total_chunks,
                total_embeddings=row.total_embeddings,
                added=row.added,
                modified=row.modified,
                deleted=row.deleted,
                unchanged=row.unchanged,
                indexed_at=row.indexed_at,
                status=status,
                error=row.error,
            )

    def delete_repository(self, upload_id: str) -> None:
        """Remove repository metadata."""
        with self._session_factory() as session:
            row = session.get(RepositoryRow, upload_id)
            if row is not None:
                session.delete(row)
                session.commit()

    def save_analysis(self, upload_id: str, kind: str, payload: dict[str, Any] | list[Any]) -> None:
        """Persist an analysis payload JSON blob for a repository."""
        column = self._analysis_column(kind)
        if column is None:
            return
        with self._session_factory() as session:
            row = session.get(RepositoryRow, upload_id)
            if row is None:
                path = self.resolve_path(upload_id)
                row = RepositoryRow(
                    upload_id=upload_id,
                    repository_id=upload_id,
                    extraction_path=str(path or ""),
                    created_at=_utcnow(),
                )
                session.add(row)
            setattr(row, column, json.dumps(payload, default=str))
            row.updated_at = _utcnow()
            session.commit()

    def get_analysis(self, upload_id: str, kind: str) -> Any | None:
        """Load a previously saved analysis payload."""
        column = self._analysis_column(kind)
        if column is None:
            return None
        with self._session_factory() as session:
            row = session.get(RepositoryRow, upload_id)
            if row is None:
                return None
            raw = getattr(row, column, None)
            if not raw:
                return None
            return json.loads(raw)

    def save_workflow_state(self, upload_id: str, state_payload: dict[str, Any]) -> None:
        """Persist workflow state for registered repositories only.

        Does not create orphan rows for ephemeral IDs (e.g. unit-test job
        fixtures) so workflow recovery stays tied to real uploads.
        """
        with self._session_factory() as session:
            row = session.get(RepositoryRow, upload_id)
            if row is None:
                return
            row.workflow_state_json = json.dumps(state_payload, default=str)
            if "state" in state_payload:
                row.status = str(state_payload["state"])
            row.updated_at = _utcnow()
            session.commit()

    def load_workflow_state(self, upload_id: str) -> dict[str, Any] | None:
        """Load persisted workflow state for a registered repository, if any."""
        with self._session_factory() as session:
            row = session.get(RepositoryRow, upload_id)
            if row is None or not row.workflow_state_json:
                return None
            # Skip rows never associated with an extraction (orphans / junk).
            if not (row.extraction_path or "").strip():
                return None
            return json.loads(row.workflow_state_json)

    @staticmethod
    def _analysis_column(kind: str) -> str | None:
        mapping = {
            "frameworks": "frameworks_result_json",
            "dependency_graph": "dependency_graph_meta_json",
            "knowledge_graph": "knowledge_graph_meta_json",
            "architecture": "architecture_result_json",
            "metrics": "metrics_result_json",
        }
        return mapping.get(kind)

    @staticmethod
    def _row_to_dict(row: RepositoryRow) -> dict[str, Any]:
        return {
            "upload_id": row.upload_id,
            "repository_id": row.repository_id,
            "extraction_path": row.extraction_path,
            "status": row.status,
            "indexing_state": row.indexing_state,
            "repository_name": row.repository_name,
            "frameworks": json.loads(row.frameworks_json or "[]"),
            "languages": json.loads(row.languages_json or "{}"),
            "total_files": row.total_files,
            "total_chunks": row.total_chunks,
            "total_embeddings": row.total_embeddings,
            "created_at": row.created_at,
            "indexed_at": row.indexed_at,
            "error": row.error,
        }


# Process-wide default store (auto-initializes SQLite schema).
repository_store = RepositoryStore()
