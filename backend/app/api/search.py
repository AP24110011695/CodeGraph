"""Thin HTTP API for repository search."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.indexing.index_manager import get_shared_index_manager
from app.rag.embedding_service import EmbeddingService
from app.rag.retriever import Retriever
from app.schemas.search import SearchRequest, SearchResponse
from app.search.search_service import (
    EmptyQueryError,
    EmptyRepositoryError,
    RepositoryNotIndexedError,
    SearchService,
    SearchServiceError,
)
from storage.repository_store import repository_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/repositories", tags=["search"])
from app.core.paths import get_extracted_dir
EXTRACTED_DIR = get_extracted_dir()

index_manager = get_shared_index_manager()
embedding_service = EmbeddingService()
retriever = Retriever(vector_store=index_manager.vector_store, embedding_service=embedding_service)
search_service = SearchService(index_manager=index_manager, retriever=retriever)


def _project_path(repository_id: str) -> Path:
    path = repository_store.resolve_path(repository_id) or (EXTRACTED_DIR / repository_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Extracted project not found for repository_id: {repository_id}")
    if not path.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory for repository_id: {repository_id}")
    return path


@router.post("/{repository_id}/search", response_model=SearchResponse, status_code=200)
async def search_repository(repository_id: str, request: SearchRequest) -> SearchResponse:
    """Search an indexed repository using semantic, keyword, or hybrid mode."""
    project_path = _project_path(repository_id)

    try:
        result = search_service.search(
            upload_id=repository_id,
            query=request.query,
            mode=request.mode,
            project_path=project_path,
        )
        return SearchResponse(**result)
    except EmptyQueryError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RepositoryNotIndexedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except EmptyRepositoryError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except SearchServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected repository search failure for repository_id: %s", repository_id)
        raise HTTPException(status_code=500, detail="Internal server error during repository search") from exc
