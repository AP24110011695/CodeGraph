from typing import Optional
from app.schemas.repository_state import RepositoryState, RepositoryStateEnum
from app.repository_state.state_manager import state_manager
from app.repository_state.transition_validator import TransitionValidator

class RepositoryStateMachine:
    """High-level abstraction for repository state lifecycle."""
    
    def __init__(self, repository_id: str):
        self.repository_id = repository_id
        self._manager = state_manager
        
        # Ensure repository is initialized
        if not self._manager.get_state(self.repository_id):
            self._manager.initialize_repository(self.repository_id)

    @property
    def current_state(self) -> RepositoryState:
        state = self._manager.get_state(self.repository_id)
        if not state:
            return self._manager.initialize_repository(self.repository_id)
        return state

    def transition_to(
        self, 
        new_state: RepositoryStateEnum,
        job_id: Optional[str] = None,
        failure_reason: Optional[str] = None,
        progress: Optional[int] = None,
        current_stage: Optional[str] = None
    ) -> RepositoryState:
        """Attempt to transition to a new state."""
        return self._manager.transition_state(
            repository_id=self.repository_id,
            new_state=new_state,
            job_id=job_id,
            failure_reason=failure_reason,
            progress=progress,
            current_stage=current_stage
        )

    def update_progress(self, progress: int, current_stage: Optional[str] = None) -> Optional[RepositoryState]:
        """Update progress for the repository."""
        return self._manager.update_progress(
            repository_id=self.repository_id,
            progress=progress,
            current_stage=current_stage
        )

    def is_ready(self) -> bool:
        """Check if repository is ready for queries/analysis."""
        state = self.current_state
        return state.state == RepositoryStateEnum.READY
