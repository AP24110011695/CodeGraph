"""Auto-indexing subscriber for repository uploads."""

import logging
import threading
from pathlib import Path

from app.events.event import Event
from app.events.event_types import EventType
from app.events.event_bus import event_bus
from app.indexing.index_manager import get_shared_index_manager
from app.repository_state.state_machine import RepositoryStateMachine
from app.schemas.repository_state import RepositoryStateEnum

logger = logging.getLogger(__name__)


class AutoIndexer:
    """Automatically indexes repositories when they are uploaded."""
    
    def __init__(self):
        self.index_manager = get_shared_index_manager()
        self._indexing_threads: dict[str, threading.Thread] = {}
    
    def on_repository_uploaded(self, event: Event) -> None:
        """Handle REPOSITORY_UPLOADED event by triggering indexing in background thread."""
        try:
            repository_id = event.repository_id
            payload = event.payload or {}
            project_path = payload.get("project_path")
            repository_name = payload.get("name", repository_id)
            
            logger.info("AUTO_INDEXER: Repository uploaded event received for %s (%s)", repository_name, repository_id)
            
            if not project_path:
                logger.warning("AUTO_INDEXER: No project_path in event payload for %s", repository_id)
                return
            
            # Check if already indexing
            if repository_id in self._indexing_threads and self._indexing_threads[repository_id].is_alive():
                logger.warning("AUTO_INDEXER: Indexing already in progress for %s", repository_id)
                return
            
            # Check if repository is already indexed
            existing_index = self.index_manager.get_index(repository_id)
            if existing_index and existing_index.status == "READY":
                logger.info("AUTO_INDEXER: Repository %s is already indexed, skipping", repository_id)
                # Ensure state is set to READY
                try:
                    state_machine = RepositoryStateMachine(repository_id)
                    if state_machine.current_state.state != RepositoryStateEnum.READY:
                        state_machine.transition_to(RepositoryStateEnum.READY, progress=100, current_stage="Already indexed")
                        logger.info("AUTO_INDEXER: Updated state to READY for already-indexed repository %s", repository_id)
                except Exception as e:
                    logger.warning("AUTO_INDEXER: Failed to update state for already-indexed repository %s: %s", repository_id, e)
                return
            
            logger.info("AUTO_INDEXER: Starting auto-index for %s (%s) at %s", 
                       repository_name, repository_id, project_path)
            
            project_path = Path(project_path)
            if not project_path.exists():
                logger.warning("AUTO_INDEXER: Project path does not exist: %s", project_path)
                return
            
            # Start indexing in background thread to avoid blocking
            def index_repository():
                state_machine = None
                try:
                    logger.info("AUTO_INDEXER: Background thread started for %s", repository_id)
                    
                    # Initialize state machine but don't manually set states
                    # Let the actual indexing process handle state transitions
                    state_machine = RepositoryStateMachine(repository_id)
                    
                    logger.info("AUTO_INDEXER: Calling create_index for %s", repository_id)
                    # Trigger indexing - let the indexing process handle state transitions
                    index = self.index_manager.create_index(project_path, repository_id, force=False)
                    
                    logger.info("AUTO_INDEXER: Successfully indexed %s - chunks: %d, embeddings: %d",
                               repository_id, index.total_chunks, index.total_embeddings)
                    
                    # Note: Memory building is triggered by REPOSITORY_INDEXED event
                    # which is published by StateManager.transition_state() during INDEXING transition
                    # No need to manually trigger memory building here
                    
                except Exception as e:
                    logger.error("AUTO_INDEXER: Failed to auto-index repository %s: %s", 
                                repository_id, e, exc_info=True)
                    # Transition to FAILED on error
                    if state_machine:
                        try:
                            state_machine.transition_to(RepositoryStateEnum.FAILED, failure_reason=str(e))
                            logger.info("AUTO_INDEXER: State transitioned to FAILED for %s", repository_id)
                        except Exception as e2:
                            logger.error("AUTO_INDEXER: Failed to transition to FAILED for %s: %s", repository_id, e2)
                finally:
                    # Clean up thread reference
                    self._indexing_threads.pop(repository_id, None)
            
            thread = threading.Thread(target=index_repository, daemon=True, name=f"Indexing-{repository_id}")
            self._indexing_threads[repository_id] = thread
            thread.start()
            logger.info("AUTO_INDEXER: Started background indexing thread for %s", repository_id)
            
        except Exception as e:
            logger.error("AUTO_INDEXER: Failed to start indexing for repository %s: %s", 
                        event.repository_id, e, exc_info=True)


# Global instance
auto_indexer = AutoIndexer()
