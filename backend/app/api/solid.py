"""SOLID principle analysis API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.indexing.index_manager import IndexManager, IndexNotFoundError, get_shared_index_manager
from app.schemas.solid import SOLIDResponse
from app.solid.solid_engine import SOLIDEngine, solid_engine

router = APIRouter(prefix="/solid", tags=["solid"])


@router.post("/{upload_id}", response_model=SOLIDResponse)
async def analyze_solid(
    upload_id: str,
    download: bool = Query(False, description="If true, return solid_analysis.json file")
) -> SOLIDResponse | FileResponse:
    """Analyze SOLID principles for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        download: If true, return SOLID analysis as a downloadable JSON file.

    Returns:
        SOLIDResponse with SOLID analysis,
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
    from app.core.paths import get_project_path
    project_path = get_project_path(upload_id)
    if not project_path.exists():
        raise HTTPException(status_code=404, detail=f"Project path not found: {project_path}")

    # Analyze SOLID principles
    solid_engine_with_index = SOLIDEngine(index_manager=index_manager)
    result = solid_engine_with_index.analyze(project_path, upload_id)

    # Convert to response format
    response = SOLIDResponse(
        overall_score=result.overall_score,
        overall_rating=result.overall_rating,
        principles=result.principles,
        priority_fixes=result.priority_fixes,
    )

    # Handle download mode
    if download:
        # Save SOLID analysis to JSON file
        analysis_file = project_path / "solid_analysis.json"
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            analysis_file,
            media_type="application/json",
            filename=f"{upload_id}_solid_analysis.json"
        )

    return response
