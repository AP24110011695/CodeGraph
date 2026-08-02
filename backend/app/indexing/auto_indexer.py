"""Auto-indexing subscriber for repository uploads."""

import logging
from pathlib import Path

from app.events.event import Event
from app.events.event_types import EventType
from app.indexing.index_manager import get_shared_index_manager

logger = logging.getLogger(__name__)


class AutoIndexer:
    """Automatically indexes repositories when they are uploaded."""
    
    def __init__(self):
        self.index_manager = get_shared_index_manager()
    
    def on_repository_uploaded(self, event: Event) -> None:
        """Handle REPOSITORY_UPLOADED event by triggering indexing."""
        try:
            repository_id = event.repository_id
            payload = event.payload or {}
            project_path = payload.get("project_path")
            repository_name = payload.get("name", repository_id)
            
            if not project_path:
                logger.warning("AUTO_INDEXER: No project_path in event payload for %s", repository_id)
                return
            
            logger.info("AUTO_INDEXER: Starting auto-index for %s (%s) at %s", 
                       repository_name, repository_id, project_path)
            
            project_path = Path(project_path)
            if not project_path.exists():
                logger.warning("AUTO_INDEXER: Project path does not exist: %s", project_path)
                return
            
            # Trigger indexing
            index = self.index_manager.create_index(project_path, repository_id, force=False)
            
            logger.info("AUTO_INDEXER: Successfully indexed %s - chunks: %d, embeddings: %d",
                       repository_id, index.total_chunks, index.total_embeddings)
            
        except Exception as e:
            logger.error("AUTO_INDEXER: Failed to auto-index repository %s: %s", 
                        event.repository_id, e, exc_info=True)


# Global instance
auto_indexer = AutoIndexer()
