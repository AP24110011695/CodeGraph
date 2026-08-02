"""Architecture drift API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.architecture_drift.architecture_drift_engine import ArchitectureDriftEngine, architecture_drift_engine
from app.indexing.index_manager import IndexManager, IndexNotFoundError, get_shared_index_manager
from app.schemas.architecture_drift import ArchitectureDriftResponse

router = APIRouter(prefix="/architecture-drift", tags=["architecture-drift"])


@router.post("/{upload_id}", response_model=ArchitectureDriftResponse)
async def analyze_architecture_drift(
    upload_id: str,
    download: bool = Query(False, description="If true, return architecture_drift_report.json file")
) -> ArchitectureDriftResponse | FileResponse:
    """Analyze architecture drift for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        download: If true, return architecture drift report as a downloadable JSON file.

    Returns:
        ArchitectureDriftResponse with comprehensive architecture drift findings,
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

    # Analyze architecture drift
    architecture_drift_engine_with_index = ArchitectureDriftEngine(index_manager=index_manager)
    result = architecture_drift_engine_with_index.analyze(project_path, upload_id)

    # Convert to response format
    response = ArchitectureDriftResponse(
        project_name=result.project_name,
        architecture_health_score=result.architecture_health_score,
        architecture_grade=result.architecture_grade,
        drift_score=result.drift_score,
        stability_score=result.stability_score,
        summary=result.summary,
        findings=result.findings,
        top_violations=result.top_violations,
        recommendations=result.recommendations,
    )

    # Handle download mode
    if download:
        # Save architecture drift report to JSON file
        drift_file = project_path / "architecture_drift_report.json"
        with open(drift_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            drift_file,
            media_type="application/json",
            filename=f"{upload_id}_architecture_drift_report.json"
        )

    return response
