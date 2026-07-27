"""API route for generating refactoring suggestions."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.schemas.refactoring import RefactoringResponse
from app.refactoring.refactoring_engine import refactoring_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/refactoring", tags=["refactoring"])

EXTRACTED_DIR = Path("storage/extracted")

@router.post("/{upload_id}", response_model=RefactoringResponse, status_code=200)
async def generate_refactoring_suggestions(upload_id: str) -> RefactoringResponse:
    """Generate refactoring suggestions for an extracted project directory.

    Args:
        upload_id: The UUID of the uploaded and extracted project.

    Returns:
        A RefactoringResponse containing prioritized refactoring suggestions.
    """
    project_path = EXTRACTED_DIR / upload_id

    if not project_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Extracted project not found for upload_id: {upload_id}",
        )

    if not project_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"Path is not a directory for upload_id: {upload_id}",
        )

    try:
        return refactoring_engine.analyze(project_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Error generating refactoring suggestions for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during refactoring analysis")
