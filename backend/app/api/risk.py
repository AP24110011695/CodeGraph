"""Risk analysis API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.indexing.index_manager import IndexManager, IndexNotFoundError
from app.risk.risk_engine import RiskEngine, risk_engine
from app.schemas.risk import RiskResponse

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/{upload_id}", response_model=RiskResponse)
async def analyze_risk(
    upload_id: str,
    download: bool = Query(False, description="If true, return risk_report.json file")
) -> RiskResponse | FileResponse:
    """Analyze repository risk for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        download: If true, return risk report as a downloadable JSON file.

    Returns:
        RiskResponse with comprehensive risk analysis findings,
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

    # Analyze risk
    risk_engine_with_index = RiskEngine(index_manager=index_manager)
    result = risk_engine_with_index.analyze(project_path, upload_id)

    # Convert to response format
    response = RiskResponse(
        project_name=result.project_name,
        overall_risk_score=result.overall_risk_score,
        overall_level=result.overall_level,
        summary=result.summary,
        risks=result.risks,
        top_risks=result.top_risks,
        priority_recommendations=result.priority_recommendations,
    )

    # Handle download mode
    if download:
        # Save risk report to JSON file
        risk_file = project_path / "risk_report.json"
        with open(risk_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            risk_file,
            media_type="application/json",
            filename=f"{upload_id}_risk_report.json"
        )

    return response
