"""API dependency flow API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.indexing.index_manager import IndexManager, IndexNotFoundError, get_shared_index_manager
from app.schemas.api_flow import APIFlowResponse
from app.api_flow.api_flow_engine import APIFlowEngine, api_flow_engine

router = APIRouter(prefix="/api-flow", tags=["api-flow"])


@router.post("/{upload_id}", response_model=APIFlowResponse)
async def analyze_flow(
    upload_id: str,
    download: bool = Query(False, description="If true, return api_flow_report.json file")
) -> APIFlowResponse | FileResponse:
    """Analyze API dependency flow for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        download: If true, return API flow analysis as a downloadable JSON file.

    Returns:
        APIFlowResponse with API dependency flow visualization,
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

    # Analyze API flow
    api_flow_engine_with_index = APIFlowEngine()
    result = api_flow_engine_with_index.analyze_flow(project_path, upload_id)

    # Convert to response format
    response = APIFlowResponse(
        flow_score=result.flow_score,
        summary=result.summary,
        endpoints=result.endpoints,
        flows=result.flows,
        sequence_diagram=result.sequence_diagram,
        recommendations=result.recommendations,
    )

    # Handle download mode
    if download:
        # Save API flow analysis to JSON file
        report_file = project_path / "api_flow_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{upload_id}_api_flow_report.json"
        )

    return response
