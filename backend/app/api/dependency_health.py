"""Dependency health API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.dependency_health.dependency_health_engine import DependencyHealthEngine, dependency_health_engine
from app.indexing.index_manager import IndexManager, IndexNotFoundError
from app.schemas.dependency_health import DependencyHealthResponse

router = APIRouter(prefix="/dependency-health", tags=["dependency-health"])


@router.post("/{upload_id}", response_model=DependencyHealthResponse)
async def analyze_dependency_health(
    upload_id: str,
    download: bool = Query(False, description="If true, return dependency_health.json file")
) -> DependencyHealthResponse | FileResponse:
    """Analyze dependency health for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        download: If true, return dependency health report as a downloadable JSON file.

    Returns:
        DependencyHealthResponse with comprehensive dependency health findings,
        or FileResponse if download=true.

    Raises:
        HTTPException: If repository is not found or not indexed.
    """
    # Initialize index manager
    index_manager = IndexManager()

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

    # Analyze dependency health
    dependency_health_engine_with_index = DependencyHealthEngine(index_manager=index_manager)
    result = dependency_health_engine_with_index.analyze(project_path, upload_id)

    # Convert to response format
    response = DependencyHealthResponse(
        project_name=result.project_name,
        overall_health_score=result.overall_health_score,
        health_grade=result.health_grade,
        summary=result.summary,
        findings=result.findings,
        critical_modules=result.critical_modules,
        high_risk_modules=result.high_risk_modules,
        recommendations=result.recommendations,
    )

    # Handle download mode
    if download:
        # Save dependency health report to JSON file
        health_file = project_path / "dependency_health.json"
        with open(health_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            health_file,
            media_type="application/json",
            filename=f"{upload_id}_dependency_health.json"
        )

    return response
