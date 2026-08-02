"""Thin HTTP API for repository README generation."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.ai.llm_client import LLMError
from app.indexing.index_manager import IndexManager, get_shared_index_manager
from app.readme.readme_generator import (
    EmptyRepositoryError,
    ReadmeGenerationError,
    ReadmeTimeoutError,
    RepositoryNotIndexedError,
    readme_generator,
)
from app.schemas.readme import ReadmeResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/readme", tags=["readme"])
from app.core.paths import get_extracted_dir
EXTRACTED_DIR = get_extracted_dir()
index_manager = get_shared_index_manager()


def _project_path(upload_id: str) -> Path:
    path = EXTRACTED_DIR / upload_id
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Extracted project not found for upload_id: {upload_id}")
    if not path.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory for upload_id: {upload_id}")
    return path


@router.post("/{upload_id}", response_model=ReadmeResponse, status_code=200)
async def generate_readme(upload_id: str, download: bool = Query(False)) -> ReadmeResponse | Response:
    """Generate a repository README from extracted and indexed repository facts only."""
    project_path = _project_path(upload_id)
    index = index_manager.get_index(upload_id)
    if index is None:
        raise HTTPException(status_code=409, detail="Repository is not indexed.")

    try:
        markdown = readme_generator.generate(project_path=project_path, upload_id=upload_id, index=index)
    except RepositoryNotIndexedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except EmptyRepositoryError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ReadmeTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except LLMError as exc:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {str(exc)}") from exc
    except ReadmeGenerationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected README generation failure for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during README generation") from exc

    if download:
        return Response(
            content=markdown,
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="README.md"'},
        )

    return ReadmeResponse(markdown=markdown)
