from fastapi import APIRouter, HTTPException
from app.schemas.repository_state import RepositoryState
from app.repository_state.state_machine import RepositoryStateMachine
from app.repository_state.state_manager import state_manager

router = APIRouter(prefix="/repository-state", tags=["repository-state"])

@router.get("/{upload_id}", response_model=RepositoryState)
async def get_repository_state(upload_id: str) -> RepositoryState:
    """Get the current state of a repository."""
    state = state_manager.get_state(upload_id)
    if not state:
        raise HTTPException(status_code=404, detail="Repository state not found")
    return state
