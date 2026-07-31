"""Microservice boundary detection API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.indexing.index_manager import IndexManager, IndexNotFoundError, get_shared_index_manager
from app.schemas.microservices import BoundaryDetectionResponse
from app.microservices.boundary_detection_engine import BoundaryDetectionEngine, boundary_detection_engine

router = APIRouter(prefix="/microservices", tags=["microservices"])


@router.post("/{upload_id}", response_model=BoundaryDetectionResponse)
async def detect_boundaries(
    upload_id: str,
    download: bool = Query(False, description="If true, return microservice_boundary_report.json file")
) -> BoundaryDetectionResponse | FileResponse:
    """Detect microservice boundaries for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        download: If true, return boundary detection as a downloadable JSON file.

    Returns:
        BoundaryDetectionResponse with microservice candidates,
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

    # Detect boundaries
    boundary_detection_engine_with_index = BoundaryDetectionEngine(index_manager=index_manager)
    result = boundary_detection_engine_with_index.detect_boundaries(project_path, upload_id)

    # Convert to response format
    response = BoundaryDetectionResponse(
        overall_score=result.overall_score,
        summary=result.summary,
        candidates=result.candidates,
        communication_recommendations=result.communication_recommendations,
    )

    # Handle download mode
    if download:
        # Save boundary detection to JSON file
        report_file = project_path / "microservice_boundary_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{upload_id}_microservice_boundary_report.json"
        )

    return response
