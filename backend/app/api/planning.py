from fastapi import APIRouter, HTTPException
from app.schemas.planning import AIPlanRequest, AIPlanResponse
from app.planning.planning_engine import planning_engine

router = APIRouter(prefix="/planning", tags=["planning"])

@router.post("/plan/{repository_id}", response_model=AIPlanResponse)
async def generate_plan(repository_id: str, request: AIPlanRequest):
    """Analyzes a query and determines the optimal execution strategy and module graph."""
    try:
        return planning_engine.plan(repository_id, request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
