"""Pull request review API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.indexing.index_manager import IndexManager, IndexNotFoundError, get_shared_index_manager
from app.pull_request_review.pr_review_engine import PRReviewEngine, PRReviewRequest, pr_review_engine
from app.schemas.pull_request_review import PRReviewResponse

router = APIRouter(prefix="/pull-request-review", tags=["pull-request-review"])


@router.post("/{upload_id}", response_model=PRReviewResponse)
async def review_pull_request(
    upload_id: str,
    request: PRReviewRequest,
    download: bool = Query(False, description="If true, return pull_request_review.json file")
) -> PRReviewResponse | FileResponse:
    """Review a pull request for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        request: PRReviewRequest with PR details.
        download: If true, return PR review as a downloadable JSON file.

    Returns:
        PRReviewResponse with comprehensive PR review,
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

    # Review pull request
    pr_review_engine_with_index = PRReviewEngine(index_manager=index_manager)
    result = pr_review_engine_with_index.review(project_path, request, upload_id)

    # Convert to response format
    response = PRReviewResponse(
        overall_score=result.overall_score,
        approval=result.approval,
        summary=result.summary,
        comments=result.comments,
        suggested_improvements=result.suggested_improvements,
        risk_assessment=result.risk_assessment,
    )

    # Handle download mode
    if download:
        # Save PR review to JSON file
        review_file = project_path / "pull_request_review.json"
        with open(review_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            review_file,
            media_type="application/json",
            filename=f"{upload_id}_pull_request_review.json"
        )

    return response
