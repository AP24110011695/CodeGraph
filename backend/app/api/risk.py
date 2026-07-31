"""Risk analysis API endpoint for CodeGraph."""

import json

from fastapi import APIRouter, Query
from fastapi.responses import FileResponse

from app.indexing.repository_access import require_ready_index
from app.risk.risk_engine import RiskEngine
from app.schemas.risk import RiskResponse

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/{upload_id}", response_model=RiskResponse)
async def analyze_risk(
    upload_id: str,
    download: bool = Query(False, description="If true, return risk_report.json file"),
) -> RiskResponse | FileResponse:
    """Analyze repository risk for a repository."""
    index_manager, _index, project_path = require_ready_index(upload_id)

    risk_engine_with_index = RiskEngine(index_manager=index_manager)
    result = risk_engine_with_index.analyze(project_path, upload_id)

    response = RiskResponse(
        project_name=result.project_name,
        overall_risk_score=result.overall_risk_score,
        overall_level=result.overall_level,
        summary=result.summary,
        risks=result.risks,
        top_risks=result.top_risks,
        priority_recommendations=result.priority_recommendations,
    )

    if download:
        risk_file = project_path / "risk_report.json"
        with open(risk_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            risk_file,
            media_type="application/json",
            filename=f"{upload_id}_risk_report.json",
        )

    return response
