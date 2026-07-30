"""Repository Timeline Intelligence API (CG-067)."""

from fastapi import APIRouter, HTTPException, Query

from app.schemas.timeline import EvolutionResponse, HotspotsResponse, RepositoryTimelineResponse
from app.timeline.timeline_engine import timeline_engine

router = APIRouter(prefix="/timeline", tags=["timeline"])


@router.get("/evolution/{repository_id}", response_model=EvolutionResponse)
async def get_repository_evolution(repository_id: str):
    """Return module/file evolution and co-evolution analysis."""
    try:
        return timeline_engine.get_evolution(repository_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/hotspots/{repository_id}", response_model=HotspotsResponse)
async def get_repository_hotspots(repository_id: str):
    """Return hotspot / instability analysis for the repository."""
    try:
        return timeline_engine.get_hotspots(repository_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{repository_id}", response_model=RepositoryTimelineResponse)
async def get_repository_timeline(
    repository_id: str,
    limit: int = Query(100, ge=1, le=500, description="Max commits to analyze"),
):
    """Return the full repository timeline intelligence payload."""
    try:
        return timeline_engine.get_timeline(repository_id, limit=limit)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
