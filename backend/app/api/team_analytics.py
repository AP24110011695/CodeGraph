"""Team analytics API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.schemas.team_analytics import TeamAnalyticsResponse
from app.team_analytics.analytics_engine import AnalyticsEngine, analytics_engine

router = APIRouter(prefix="/team-analytics", tags=["team-analytics"])


@router.post("/{workspace_id}", response_model=TeamAnalyticsResponse)
async def generate_workspace_analytics(
    workspace_id: str,
    download: bool = Query(False, description="If true, return team_analytics_report.json file")
) -> TeamAnalyticsResponse | FileResponse:
    """Generate comprehensive team analytics for a workspace.

    Args:
        workspace_id: Workspace ID.
        download: If true, return analytics report as a downloadable JSON file.

    Returns:
        TeamAnalyticsResponse with workspace analytics,
        or FileResponse if download=true.

    Raises:
        HTTPException: If workspace not found.
    """
    result = analytics_engine.generate_workspace_analytics(workspace_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    response = TeamAnalyticsResponse(
        workspace_id=result.get("workspace_id"),
        workspace_name=result.get("workspace_name"),
        engineering_score=result.get("engineering_score", 0),
        workspace_health=result.get("workspace_health", 0),
        summary=result.get("summary"),
        quality_metrics=result.get("quality_metrics"),
        risk_metrics=result.get("risk_metrics"),
        security_metrics=result.get("security_metrics"),
        technology_distribution=result.get("technology_distribution"),
        cicd_health=result.get("cicd_health"),
        quality_trend=result.get("quality_trend"),
        risk_trend=result.get("risk_trend"),
        security_trend=result.get("security_trend"),
        engineering_trend=result.get("engineering_trend"),
        repository_rankings=result.get("repository_rankings", []),
        top_improvements=result.get("top_improvements", []),
        repository_summaries=result.get("repository_summaries", []),
        error=result.get("error"),
    )

    # Handle download mode
    if download:
        # Save analytics report to JSON file
        report_file = Path("team_analytics_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{workspace_id}_team_analytics.json"
        )

    return response
