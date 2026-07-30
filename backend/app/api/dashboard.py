"""Dashboard API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.schemas.dashboard import DashboardResponse
from app.dashboard.dashboard_engine import DashboardEngine, dashboard_engine

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.post("/{workspace_id}", response_model=DashboardResponse)
async def generate_dashboard(
    workspace_id: str,
    download: bool = Query(False, description="If true, return executive_dashboard.json file")
) -> DashboardResponse | FileResponse:
    """Generate executive dashboard for a workspace.

    Args:
        workspace_id: Workspace ID.
        download: If true, return dashboard as a downloadable JSON file.

    Returns:
        DashboardResponse with dashboard data,
        or FileResponse if download=true.

    Raises:
        HTTPException: If workspace not found.
    """
    result = dashboard_engine.generate_dashboard(workspace_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    response = DashboardResponse(
        workspace_id=result.get("workspace_id"),
        workspace_name=result.get("workspace_name"),
        executive_score=result.get("executive_score", 0),
        workspace_health=result.get("workspace_health", 0),
        overall_health=result.get("overall_health"),
        summary=result.get("summary"),
        key_insights=result.get("key_insights", []),
        recommendations=result.get("recommendations", []),
        score_cards=result.get("score_cards", []),
        widgets=result.get("widgets"),
        error=result.get("error"),
    )

    # Handle download mode
    if download:
        # Save dashboard to JSON file
        report_file = Path("executive_dashboard.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{workspace_id}_executive_dashboard.json"
        )

    return response
