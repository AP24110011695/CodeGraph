from fastapi import APIRouter, HTTPException

from app.architecture_reasoning.reasoning_engine import reasoning_engine
from app.core.config import settings
from app.schemas.architecture_reasoning import (
    ArchitectureExplanationRequest,
    ArchitectureExplanationResponse,
    ArchitectureSummaryResponse,
)

router = APIRouter(prefix="/architecture", tags=["architecture-reasoning"])


def _server_error(exc: Exception) -> HTTPException:
    detail = str(exc) if settings.EXPOSE_ERROR_DETAILS else "Internal server error"
    return HTTPException(status_code=500, detail=detail)


@router.post("/explain/{repository_id}", response_model=ArchitectureExplanationResponse)
async def explain_architecture(repository_id: str, request: ArchitectureExplanationRequest):
    """Explains an architectural aspect based on existing repository context."""
    try:
        return reasoning_engine.explain(repository_id, request.query)
    except Exception as e:
        raise _server_error(e) from e


@router.get("/summary/{repository_id}", response_model=ArchitectureSummaryResponse)
async def get_architecture_summary(repository_id: str):
    """Retrieves a high-level architectural summary of the repository."""
    try:
        return reasoning_engine.summary(repository_id)
    except Exception as e:
        raise _server_error(e) from e
