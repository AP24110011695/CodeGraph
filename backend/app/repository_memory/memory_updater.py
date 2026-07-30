import logging
from app.schemas.repository_memory import RepositoryMemory
from .memory_store import MemoryStore

logger = logging.getLogger(__name__)

class MemoryUpdater:
    def __init__(self, store: MemoryStore):
        self._store = store

    def update_incremental(self, repository_id: str, changes: dict) -> RepositoryMemory:
        logger.info(f"Incrementally updating repository memory for {repository_id}")
        
        memory = self._store.get(repository_id)
        if not memory:
            logger.warning(f"No existing memory found for {repository_id}, cannot update incrementally.")
            # Fallback to creating an empty one if not exists for partial updates,
            # though in a real scenario it might trigger a full rebuild.
            memory = RepositoryMemory(repository_id=repository_id)
            
        # Update only affected sections based on `changes` from Incremental Indexing.
        # This ensures we never rebuild the entire memory if only a small portion changes.
        if "affected_files" in changes:
            logger.debug(f"Invalidating memory for {len(changes['affected_files'])} files")
            for file_path in changes["affected_files"]:
                memory.file_summaries.pop(file_path, None)
                
        self._store.set(repository_id, memory)
        return memory
