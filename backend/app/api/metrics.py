"""Metrics API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.indexing.index_manager import IndexManager, IndexNotFoundError
from app.metrics.metrics_engine import MetricsEngine, metrics_engine
from app.schemas.metrics import MetricsResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post("/{upload_id}", response_model=MetricsResponse)
async def generate_metrics(
    upload_id: str,
    download: bool = Query(False, description="If true, return metrics.json file")
) -> MetricsResponse | FileResponse:
    """Generate comprehensive repository metrics.

    Args:
        upload_id: The upload ID of the indexed repository.
        download: If true, return metrics as a downloadable JSON file.

    Returns:
        MetricsResponse with comprehensive repository metrics,
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

    # Generate metrics
    metrics_engine_with_index = MetricsEngine(index_manager=index_manager)
    result = metrics_engine_with_index.generate(project_path, upload_id)

    # Convert to response format
    response = MetricsResponse(
        project_name=result.project_name,
        summary=result.summary,
        statistics=result.statistics,
        quality=result.quality,
        security=result.security,
        architecture=result.architecture,
        smells=result.smells,
        refactoring=result.refactoring,
    )

    # Handle download mode
    if download:
        # Save metrics to JSON file
        metrics_file = project_path / "metrics.json"
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            metrics_file,
            media_type="application/json",
            filename=f"{upload_id}_metrics.json"
        )

    return response
