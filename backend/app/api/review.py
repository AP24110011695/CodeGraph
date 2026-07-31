"""Review API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.indexing.index_manager import IndexManager, IndexNotFoundError, get_shared_index_manager
from app.review.review_engine import ReviewEngine, review_engine
from app.schemas.review import ReviewResponse

router = APIRouter(prefix="/review", tags=["review"])


@router.post("/{upload_id}", response_model=ReviewResponse)
async def generate_review(
    upload_id: str,
    download: bool = Query(False, description="If true, return code_review.json file")
) -> ReviewResponse | FileResponse:
    """Generate comprehensive code review for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        download: If true, return review as a downloadable JSON file.

    Returns:
        ReviewResponse with comprehensive code review findings,
        or FileResponse if download=true.

    Raises:
        HTTPException: If repository is not found or not indexed.
    """
    # Initialize index manager
    index_manager = get_shared_index_manager()

    # Get the index
    index = index_manager.get_index(upload_id)
    if not index:
        raise HTTPException(status_code=404, detail=f"Repository not found: {upload_id}")

    if index.status.value != "READY":
        raise HTTPException(
            status_code=400,
            detail=f"Repository is not indexed. Current status: {index.status.value}"
        )

    # Determine project path from uploads directory
    project_path = Path("uploads") / upload_id
    if not project_path.exists():
        raise HTTPException(status_code=404, detail=f"Project path not found: {project_path}")

    # Generate review
    review_engine_with_index = ReviewEngine(index_manager=index_manager)
    result = review_engine_with_index.review(project_path, upload_id)

    # Convert to response format
    response = ReviewResponse(
        project_name=result.project_name,
        overall_score=result.overall_score,
        summary=result.summary,
        issues=result.issues,
        strengths=result.strengths,
        recommendations=result.recommendations,
    )

    # Handle download mode
    if download:
        # Save review to JSON file
        review_file = project_path / "code_review.json"
        with open(review_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            review_file,
            media_type="application/json",
            filename=f"{upload_id}_code_review.json"
        )

    return response
