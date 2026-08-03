"""Auto-indexing subscriber for repository uploads."""

import logging
import threading
from pathlib import Path

from app.events.event import Event
from app.events.event_types import EventType
from app.indexing.index_manager import get_shared_index_manager

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
            
            logger.info("AUTO_INDEXER: Starting auto-index for %s (%s) at %s", 
                       repository_name, repository_id, project_path)
            
            project_path = Path(project_path)
            if not project_path.exists():
                logger.warning("AUTO_INDEXER: Project path does not exist: %s", project_path)
                return
            
            # Start indexing in background thread to avoid blocking
            def index_repository():
                try:
                    logger.info("AUTO_INDEXER: Background thread started for %s", repository_id)
                    logger.info("AUTO_INDEXER: Calling create_index for %s", repository_id)
                    # Trigger indexing
                    index = self.index_manager.create_index(project_path, repository_id, force=False)
                    
                    logger.info("AUTO_INDEXER: Successfully indexed %s - chunks: %d, embeddings: %d",
                               repository_id, index.total_chunks, index.total_embeddings)
                except Exception as e:
                    logger.error("AUTO_INDEXER: Failed to auto-index repository %s: %s", 
                                repository_id, e, exc_info=True)
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
