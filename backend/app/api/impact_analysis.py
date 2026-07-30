"""Intelligent Code Impact Analysis API (CG-068)."""

from fastapi import APIRouter, HTTPException

from app.schemas.impact_analysis import (
    ImpactAnalyzeRequest,
    ImpactAnalyzeResponse,
    ImpactSummaryResponse,
)
from app.impact_analysis.impact_engine import impact_engine

router = APIRouter(prefix="/impact", tags=["impact-analysis"])


@router.post("/analyze/{repository_id}", response_model=ImpactAnalyzeResponse)
async def analyze_impact(repository_id: str, request: ImpactAnalyzeRequest):
    """Predict the effect of a proposed code change before it happens."""
    try:
        return impact_engine.analyze(repository_id, request)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/summary/{repository_id}", response_model=ImpactSummaryResponse)
async def impact_summary(repository_id: str):
    """Return a repository-level impact summary."""
    try:
        return impact_engine.get_summary(repository_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
