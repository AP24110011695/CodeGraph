"""Repository management API — list, detail, and delete uploaded repositories."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, Response, status

from app.indexing.index_manager import (
    IndexNotFoundError,
    get_shared_index_manager,
)
from app.schemas.repositories import RepositoryListResponse, RepositorySummary
from storage.repository_store import repository_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/repositories", tags=["repositories"])


def _cleanup_repository_files(upload_id: str, extraction_path: str | None) -> None:
    """Best-effort removal of extracted tree and uploaded zip."""
    from app.core.paths import get_extracted_dir, get_upload_dir
    
    if extraction_path:
        path = Path(extraction_path)
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)

    for root in (get_extracted_dir(), get_upload_dir()):
        candidate = root / upload_id
        if candidate.is_dir():
            shutil.rmtree(candidate, ignore_errors=True)

    for zip_root in (get_upload_dir(), Path("storage/uploads")):
        zip_path = zip_root / f"{upload_id}.zip"
        if zip_path.is_file():
            try:
                zip_path.unlink()
            except OSError:
                logger.debug("Could not delete zip %s", zip_path, exc_info=True)


@router.get("", response_model=RepositoryListResponse)
async def list_repositories() -> RepositoryListResponse:
    """Return all uploaded repositories (newest first)."""
    repositories = [
        RepositorySummary.model_validate(item) for item in repository_store.list_repositories()
    ]
    return RepositoryListResponse(repositories=repositories, total=len(repositories))


@router.get("/{repository_id}", response_model=RepositorySummary)
async def get_repository(repository_id: str) -> RepositorySummary:
    """Return metadata for a single repository."""
    summary = repository_store.get_repository_summary(repository_id)
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository not found: {repository_id}",
        )
    return RepositorySummary.model_validate(summary)


@router.delete("/{repository_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_repository(repository_id: str) -> Response:
    """Delete repository metadata, index vectors, and on-disk artifacts."""
    existing = repository_store.get_repository(repository_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository not found: {repository_id}",
        )

    index_manager = get_shared_index_manager()
    try:
        index_manager.delete_index(repository_id)
    except IndexNotFoundError:
        # Metadata-only or never-indexed repository — still remove the store row.
        repository_store.delete_repository(repository_id)
    except Exception:
        logger.exception("Index cleanup failed for %s; continuing with file/store delete", repository_id)
        repository_store.delete_repository(repository_id)

    _cleanup_repository_files(repository_id, existing.get("extraction_path"))
    return Response(status_code=status.HTTP_204_NO_CONTENT)