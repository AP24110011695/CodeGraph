"""Shared helpers for index-gated analysis endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException

from app.indexing.index_manager import IndexManager, get_shared_index_manager
from app.indexing.indexing_models import IndexStatus, RepositoryIndex
from storage.repository_store import RepositoryStore, repository_store


def require_ready_index(
    upload_id: str,
    *,
    index_manager: IndexManager | None = None,
) -> tuple[IndexManager, RepositoryIndex, Path]:
    """Resolve shared index manager, READY index, and project path.

    Raises HTTPException with the same status codes previously used by
    metrics / knowledge-graph / risk routers.
    """
    manager = index_manager or get_shared_index_manager()
    index = manager.get_index(upload_id)
    if not index:
        raise HTTPException(status_code=404, detail=f"Repository not found: {upload_id}")

    if index.status != IndexStatus.READY:
        raise HTTPException(
            status_code=400,
            detail=f"Repository is not indexed. Current status: {index.status.value}",
        )

    project_path = resolve_indexed_project_path(upload_id, store=repository_store)
    return manager, index, project_path


def resolve_indexed_project_path(
    upload_id: str,
    *,
    store: RepositoryStore | None = None,
) -> Path:
    """Resolve extracted project directory for an upload_id."""
    active_store = store or repository_store
    project_path = active_store.resolve_path(upload_id)
    if project_path is None or not project_path.is_dir():
        raise HTTPException(status_code=404, detail=f"Project path not found: {upload_id}")
    return project_path
