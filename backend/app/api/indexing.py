"""Thin HTTP API for managing repository indexes."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, status

from app.indexing.index_manager import IndexAlreadyExistsError, IndexManager, IndexNotFoundError
from app.indexing.indexing_models import IndexStatus, RepositoryIndex
from app.indexing.indexing_pipeline import IndexingPipelineError
from app.schemas.indexing import IndexResponse

router = APIRouter(prefix="/index", tags=["indexing"])
EXTRACTED_DIR = Path("storage/extracted")
index_manager = IndexManager()


def _project_path(upload_id: str) -> Path:
    path = EXTRACTED_DIR / upload_id
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Extracted project not found for upload_id: {upload_id}")
    if not path.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory for upload_id: {upload_id}")
    return path


@router.post("/{upload_id}", response_model=IndexResponse, status_code=status.HTTP_201_CREATED)
async def create_index(upload_id: str, rebuild: bool = Query(False)) -> IndexResponse:
    project_path = _project_path(upload_id)
    try:
        return IndexResponse.from_index(index_manager.create_index(project_path, upload_id, rebuild=rebuild))
    except IndexAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except IndexingPipelineError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{upload_id}", response_model=IndexResponse)
async def get_index(upload_id: str) -> IndexResponse:
    _project_path(upload_id)
    index = index_manager.get_index(upload_id) or RepositoryIndex(upload_id=upload_id, status=IndexStatus.NOT_INDEXED)
    return IndexResponse.from_index(index)


@router.delete("/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_index(upload_id: str) -> None:
    try:
        index_manager.delete_index(upload_id)
    except IndexNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
