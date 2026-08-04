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
        self._instance_id = id(self)
        logger.info("=" * 80)
        logger.info("AUTO_MEMORY_BUILDER: __init__() called")
        logger.info("=" * 80)
        logger.info("AutoMemoryBuilder instance ID: %s", self._instance_id)
        logger.info("MemoryEngine instance ID: %s", id(self._memory_engine))
        logger.info("MemoryStore instance ID: %s", id(self._memory_engine._store))
        logger.info("=" * 80)
    
    def on_repository_indexed(self, event: Event) -> None:
        """Handle REPOSITORY_INDEXED event by building repository memory."""
        logger.info("=" * 80)
        logger.info("AUTO_MEMORY_BUILDER: on_repository_indexed() called")
        logger.info("=" * 80)
        logger.info("Event repository_id: %s", event.repository_id)
        logger.info("Event type: %s", event.event_type)
        logger.info("Event payload: %s", event.payload)
        
        try:
            repository_id = event.repository_id
            logger.info("AUTO_MEMORY_BUILDER: Repository indexed event received for %s", repository_id)
            
            # Check if memory already exists
            existing_memory = self._memory_engine.get_memory(repository_id)
            existing_symbol_count = len(existing_memory.symbol_summaries) if existing_memory else 0
            logger.info("AUTO_MEMORY_BUILDER: Existing memory symbol count: %d", existing_symbol_count)
            
            if existing_memory:
                logger.info("AUTO_MEMORY_BUILDER: Memory already exists for %s, skipping", repository_id)
                logger.info("AUTO_MEMORY_BUILDER: MemoryStore.contains(%s): %s", repository_id, self._memory_engine._store.contains(repository_id))
                logger.info("=" * 80)
                return
            
            logger.info("AUTO_MEMORY_BUILDER: Building memory for %s", repository_id)
            
            # Build repository memory
            memory = self._memory_engine.build_memory(repository_id)
            
            # Log memory statistics
            logger.info("AUTO_MEMORY_BUILDER: Memory built successfully for %s", repository_id)
            logger.info("AUTO_MEMORY_BUILDER: Memory statistics:")
            logger.info("  Symbols: %d", len(memory.symbol_summaries))
            logger.info("  Modules: %d", len(memory.module_summaries))
            logger.info("  APIs: %d", len(memory.api_endpoints))
            logger.info("  Workflows: %d", len(memory.workflow_summaries))
            
            # Verify memory is stored
            verification = self._memory_engine._store.get(repository_id)
            if verification:
                logger.info("AUTO_MEMORY_BUILDER: Memory verification successful - stored in MemoryStore")
                logger.info("  MemoryStore.contains(%s): %s", repository_id, self._memory_engine._store.contains(repository_id))
            else:
                logger.error("AUTO_MEMORY_BUILDER: Memory verification FAILED - not in MemoryStore")
                logger.info("  MemoryStore.contains(%s): %s", repository_id, self._memory_engine._store.contains(repository_id))
            
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error("AUTO_MEMORY_BUILDER: Failed to build memory for repository %s: %s", 
                        event.repository_id, e, exc_info=True)
            logger.info("=" * 80)


# Global instance
auto_memory_builder = AutoMemoryBuilder()
