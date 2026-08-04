import logging
from typing import Dict, Optional, Any
from datetime import datetime, timezone
import threading

from app.schemas.repository_state import RepositoryState, RepositoryStateEnum
from app.repository_state.transition_validator import TransitionValidator
from app.events.event_bus import event_bus
from app.events.event_types import EventType

logger = logging.getLogger(__name__)

class StateManager:
    """Manages repository states with validation."""
    
    def __init__(self):
        self._states: Dict[str, RepositoryState] = {}
        self._lock = threading.Lock()
    
    def initialize_repository(self, repository_id: str) -> RepositoryState:
        """Initializes a new repository to UPLOADED state."""
        with self._lock:
            if repository_id in self._states:
                logger.warning(f"Repository {repository_id} already initialized")
                return self._states[repository_id]
            
            state = RepositoryState(
                repository=repository_id,
                state=RepositoryStateEnum.UPLOADED,
                state_timestamp=datetime.now(timezone.utc),
                progress=0
            )
            self._states[repository_id] = state
            logger.info(f"Initialized repository {repository_id} state to UPLOADED")
            try:
                from storage.repository_store import repository_store

                repository_store.save_workflow_state(
                    repository_id, state.model_dump(mode="json")
                )
            except Exception:
                logger.debug("Failed to persist initial workflow state for %s", repository_id, exc_info=True)
            return state

    def get_state(self, repository_id: str) -> Optional[RepositoryState]:
        """Gets the current state of a repository."""
        with self._lock:
            # Return a copy to avoid external mutations
            state = self._states.get(repository_id)
            if state:
                return state.model_copy()

        # Fallback to SQLite for process-restart survival
        try:
            from storage.repository_store import repository_store

            payload = repository_store.load_workflow_state(repository_id)
            if payload:
                restored = RepositoryState.model_validate(payload)
                with self._lock:
                    self._states[repository_id] = restored
                return restored.model_copy()
        except Exception:
            logger.debug("No persisted workflow state for %s", repository_id, exc_info=True)
        return None

    def transition_state(
        self, 
        repository_id: str, 
        new_state: RepositoryStateEnum,
        job_id: Optional[str] = None,
        failure_reason: Optional[str] = None,
        progress: Optional[int] = None,
        current_stage: Optional[str] = None
    ) -> RepositoryState:
        """Transitions repository to a new state if valid."""
        with self._lock:
            current = self._states.get(repository_id)
            if not current:
                # If it doesn't exist, allow creating it if it's a valid starting point
                # For simplicity, we initialize it to UPLOADED and then transition if needed
                current = RepositoryState(
                    repository=repository_id,
                    state=RepositoryStateEnum.UPLOADED,
                    state_timestamp=datetime.now(timezone.utc),
                    progress=0
                )
                self._states[repository_id] = current
            
            if not TransitionValidator.is_valid_transition(current.state, new_state):
                error_msg = f"Invalid state transition for {repository_id}: {current.state} -> {new_state}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            current.previous_state = current.state
            current.state = new_state
            current.state_timestamp = datetime.now(timezone.utc)
            
            if job_id is not None:
                current.job_id = job_id
            if failure_reason is not None:
                current.failure_reason = failure_reason
            if progress is not None:
                current.progress = progress
            if current_stage is not None:
                current.current_stage = current_stage
                
            # Publish event based on new state
            state_to_event = {
                RepositoryStateEnum.QUEUED: EventType.REPOSITORY_QUEUED,
                RepositoryStateEnum.SCANNING: EventType.REPOSITORY_SCANNING,
                RepositoryStateEnum.INDEXING: EventType.REPOSITORY_INDEXED,
                RepositoryStateEnum.READY: EventType.REPOSITORY_READY,
                RepositoryStateEnum.FAILED: EventType.REPOSITORY_FAILED,
            }
            if new_state in state_to_event:
                logger.info("=" * 80)
                logger.info("STATE_MANAGER: Publishing event for state transition")
                logger.info("=" * 80)
                logger.info("Repository ID: %s", repository_id)
                logger.info("New state: %s", new_state)
                logger.info("Event type: %s", state_to_event[new_state])
                event_bus.publish(
                    event_type=state_to_event[new_state],
                    repository_id=repository_id,
                    payload={"new_state": new_state, "previous_state": current.previous_state, "job_id": job_id}
                )
                logger.info("STATE_MANAGER: Event published successfully")
                logger.info("=" * 80)
            
            logger.info(f"Repository {repository_id} transitioned to {new_state}")
            snapshot = current.model_copy()
            try:
                from storage.repository_store import repository_store

                repository_store.save_workflow_state(
                    repository_id, snapshot.model_dump(mode="json")
                )
            except Exception:
                logger.debug("Failed to persist workflow state for %s", repository_id, exc_info=True)
            return snapshot
    
    def update_progress(self, repository_id: str, progress: int, current_stage: Optional[str] = None) -> Optional[RepositoryState]:
        """Updates progress and stage without changing state."""
        with self._lock:
            current = self._states.get(repository_id)
            if not current:
                return None
            
            current.progress = progress
            if current_stage is not None:
                current.current_stage = current_stage
            
            snapshot = current.model_copy()
            try:
                from storage.repository_store import repository_store
                repository_store.save_workflow_state(
                    repository_id, snapshot.model_dump(mode="json")
                )
            except Exception:
                logger.debug("Failed to persist updated workflow state for %s", repository_id, exc_info=True)
            return snapshot

state_manager = StateManager()
