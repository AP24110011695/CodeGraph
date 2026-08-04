"""Auto memory builder subscriber for repository indexing completion."""

import logging
from app.events.event import Event
from app.events.event_types import EventType
from app.repository_memory.memory_engine import memory_engine

logger = logging.getLogger(__name__)


class AutoMemoryBuilder:
    """Automatically builds repository memory when indexing completes.
    
    Memory building is triggered by REPOSITORY_INDEXED event, which is reliably
    published during the INDEXING state transition. This ensures memory is built
    even if the READY state transition fails or times out.
    """
    
    def __init__(self):
        self._memory_engine = memory_engine
    
    def on_repository_indexed(self, event: Event) -> None:
        """Handle REPOSITORY_INDEXED event by building repository memory."""
        try:
            repository_id = event.repository_id
            
            # Check if memory already exists
            existing_memory = self._memory_engine.get_memory(repository_id)
            if existing_memory:
                return
            
            # Build repository memory
            self._memory_engine.build_memory(repository_id)
            
        except Exception as e:
            logger.error("AUTO_MEMORY_BUILDER: Failed to build memory for repository %s: %s", 
                        event.repository_id, e, exc_info=True)


# Global instance
auto_memory_builder = AutoMemoryBuilder()
