"""Repository metadata store backed by SQLite."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.paths import resolve_repository_path
from app.indexing.indexing_models import IndexStatus, RepositoryIndex
from storage.database import get_session_factory, init_db
from storage.models import RepositoryRow

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RepositoryStore:
    """Source of truth for repository paths, index status, and analysis metadata."""

    def __init__(self, session_factory: sessionmaker[Session] | None = None) -> None:
        # None → resolve lazily via get_session_factory() so reset_engine()/env
        # overrides are picked up (tests and CODEGRAPH_DB_PATH).
        self._session_factory = session_factory
        if session_factory is None:
            init_db()

    def _sessions(self) -> sessionmaker[Session]:
        return self._session_factory or get_session_factory()

    def register_upload(
        self,
        upload_id: str,
        extraction_path: str | Path,
        *,
        repository_id: str | None = None,
        status: str = "UPLOADED",
        name: str | None = None,
        zip_size_bytes: int = 0,
    ) -> None:
        """Create or update a repository row after upload/extract."""
        path = str(Path(extraction_path))
        display_name = (name or "").strip()
        
        # Log registration details
        logger.info("REPOSITORY_STORE: Registering upload - upload_id: %s, repository_id: %s, name: %s, path: %s",
                   upload_id, repository_id or upload_id, display_name or upload_id, path)
        
        with self._sessions()() as session:
            row = session.get(RepositoryRow, upload_id)
            if row is None:
                row = RepositoryRow(
                    upload_id=upload_id,
                    repository_id=repository_id or upload_id,
                    extraction_path=path,
                    status=status,
                    indexing_state=IndexStatus.NOT_INDEXED.value,
                    repository_name=display_name or upload_id,
                    zip_size_bytes=zip_size_bytes,
                    created_at=_utcnow(),
                    updated_at=_utcnow(),
                )
                session.add(row)
                logger.info("REPOSITORY_STORE: Created new repository row for %s", upload_id)
            else:
                row.extraction_path = path
                row.repository_id = repository_id or row.repository_id or upload_id
                row.status = status
                if display_name:
                    row.repository_name = display_name
                row.updated_at = _utcnow()
                logger.info("REPOSITORY_STORE: Updated existing repository row for %s", upload_id)
            session.commit()
            logger.info("REPOSITORY_STORE: Repository registration committed for %s", upload_id)

    def list_repositories(self) -> list[dict[str, Any]]:
        """Return all registered repositories, newest first."""
        with self._sessions()() as session:
            rows = session.scalars(
                select(RepositoryRow).order_by(RepositoryRow.created_at.desc())
            ).all()
            return [self._row_to_summary(row) for row in rows]

    def get_repository(self, upload_id: str) -> dict[str, Any] | None:
        """Return a plain dict of repository metadata, or None."""
        with self._sessions()() as session:
            row = session.get(RepositoryRow, upload_id)
            if row is None:
                return None
            return self._row_to_dict(row)

    def get_repository_summary(self, upload_id: str) -> dict[str, Any] | None:
        """Return public summary fields for a repository, or None."""
        with self._sessions()() as session:
            row = session.get(RepositoryRow, upload_id)
            if row is None:
                return None
            return self._row_to_summary(row)

    def resolve_path(self, upload_id: str) -> Path | None:
        """Resolve extraction path from DB, then filesystem fallbacks."""
        logger.info("=" * 80)
        logger.info("REPOSITORY STORE PATH RESOLUTION")
        logger.info("=" * 80)
        logger.info("Upload ID: %s", upload_id)
        
        with self._sessions()() as session:
            row = session.get(RepositoryRow, upload_id)
            logger.info("Database row found: %s", row is not None)
            
            if row:
                logger.info("Row extraction_path: %s", row.extraction_path)
                logger.info("Row repository_id: %s", row.repository_id)
                logger.info("Row repository_name: %s", row.repository_name)
                logger.info("Row status: %s", row.status)
                logger.info("Row indexing_state: %s", row.indexing_state)
                
                if row.extraction_path:
                    candidate = Path(row.extraction_path)
                    logger.info("Candidate path from DB: %s", candidate)
                    logger.info("Candidate exists: %s", candidate.exists())
                    logger.info("Candidate is_dir: %s", candidate.is_dir())
                    
                    if candidate.is_dir():
                        logger.info("✓ Using DB path: %s", candidate)
                        logger.info("=" * 80)
                        return candidate
                    else:
                        logger.warning("DB path exists but is not directory: %s", candidate)
                else:
                    logger.warning("Row has no extraction_path")
            else:
                logger.warning("No database row found for upload_id: %s", upload_id)
        
        # Fallback to filesystem resolution
        logger.info("Attempting filesystem fallback...")
        fallback_path = resolve_repository_path(upload_id)
        logger.info("Fallback path: %s", fallback_path)
        
        if fallback_path:
            logger.info("Fallback exists: %s", fallback_path.exists())
            logger.info("Fallback is_dir: %s", fallback_path.is_dir())
            if fallback_path.is_dir():
                logger.info("✓ Using fallback path: %s", fallback_path)
            else:
                logger.warning("Fallback path exists but is not directory")
        else:
            logger.warning("Fallback path is None")
        
        logger.info("=" * 80)
        return fallback_path

    def save_index(self, index: RepositoryIndex, extraction_path: str | Path | None = None) -> None:
        """Persist index metadata from a RepositoryIndex domain object."""
        path = str(Path(extraction_path)) if extraction_path else ""
        with self._sessions()() as session:
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

            # Keep upload display name when present; fill from index otherwise.
            if index.repository_name and (
                not (row.repository_name or "").strip()
                or row.repository_name == row.upload_id
            ):
                row.repository_name = index.repository_name
            row.frameworks_json = json.dumps(list(index.frameworks or []))
            row.languages_json = json.dumps(dict(index.languages or {}))
            row.total_files = int(index.total_files or 0)
            row.total_folders = int(index.total_folders or 0)
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
        with self._sessions()() as session:
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
                total_folders=row.total_folders,
                zip_size_bytes=row.zip_size_bytes,
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

    def delete_repository(self, upload_id: str) -> bool:
        """Remove repository metadata. Returns True if a row was deleted."""
        with self._sessions()() as session:
            row = session.get(RepositoryRow, upload_id)
            if row is None:
                return False
            session.delete(row)
            session.commit()
            return True

    def save_analysis(self, upload_id: str, kind: str, payload: dict[str, Any] | list[Any]) -> None:
        """Persist an analysis payload JSON blob for a repository."""
        column = self._analysis_column(kind)
        if column is None:
            return
        with self._sessions()() as session:
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
        with self._sessions()() as session:
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
        with self._sessions()() as session:
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
        with self._sessions()() as session:
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
    def _primary_framework(frameworks: list[Any]) -> str | None:
        for item in frameworks:
            if isinstance(item, str) and item.strip():
                return item.strip()
            if isinstance(item, dict):
                name = item.get("name") or item.get("framework")
                if isinstance(name, str) and name.strip():
                    return name.strip()
        return None

    @staticmethod
    def _primary_language(languages: dict[str, Any] | list[Any]) -> str | None:
        if isinstance(languages, list):
            for item in languages:
                if isinstance(item, str) and item.strip():
                    return item.strip()
            return None
        if not languages:
            return None
        # Prefer highest file count when map is language -> count.
        try:
            ranked = sorted(
                ((str(k), int(v)) for k, v in languages.items() if v is not None),
                key=lambda pair: pair[1],
                reverse=True,
            )
            if ranked:
                return ranked[0][0]
        except (TypeError, ValueError):
            pass
        return next(iter(languages.keys()), None)

    @classmethod
    def _row_to_summary(cls, row: RepositoryRow) -> dict[str, Any]:
        frameworks = json.loads(row.frameworks_json or "[]")
        languages = json.loads(row.languages_json or "{}")
        name = (row.repository_name or "").strip() or row.upload_id
        return {
            "id": row.upload_id,
            "name": name,
            "uploaded_at": row.created_at,
            "status": row.status or row.indexing_state or "UPLOADED",
            "framework": cls._primary_framework(frameworks),
            "language": cls._primary_language(languages),
        }

    @classmethod
    def _row_to_dict(cls, row: RepositoryRow) -> dict[str, Any]:
        summary = cls._row_to_summary(row)
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
            **summary,
        }


# Process-wide default store (auto-initializes SQLite schema).
repository_store = RepositoryStore()
