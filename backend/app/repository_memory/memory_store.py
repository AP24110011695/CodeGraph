from typing import Optional
from app.schemas.repository_memory import RepositoryMemory
import logging

logger = logging.getLogger(__name__)

class MemoryStore:
    def __init__(self):
        # In-memory storage designed to be easily replaced by Redis, PostgreSQL, or VectorDB
        self._storage: dict[str, RepositoryMemory] = {}
        self._instance_id = id(self)
        logger.info("=" * 80)
        logger.info("MEMORY_STORE: __init__() called")
        logger.info("=" * 80)
        logger.info("MemoryStore instance ID: %s", self._instance_id)
        logger.info("=" * 80)

    def get(self, repository_id: str) -> Optional[RepositoryMemory]:
        logger.info("=" * 80)
        logger.info("MEMORY_STORE: get() called")
        logger.info("=" * 80)
        logger.info("MemoryStore instance ID: %s", self._instance_id)
        logger.info("Repository ID: %s", repository_id)
        logger.info("Storage keys: %s", list(self._storage.keys()))
        result = self._storage.get(repository_id)
        if result:
            logger.info("MEMORY_STORE: Memory found")
            logger.info("  Symbol summaries: %d", len(result.symbol_summaries))
        else:
            logger.info("MEMORY_STORE: Memory NOT found")
        logger.info("=" * 80)
        return result

    def set(self, repository_id: str, memory: RepositoryMemory) -> None:
        logger.info("=" * 80)
        logger.info("MEMORY_STORE: set() called")
        logger.info("=" * 80)
        logger.info("MemoryStore instance ID: %s", self._instance_id)
        logger.info("Repository ID: %s", repository_id)
        logger.info("Memory symbol_summaries: %d", len(memory.symbol_summaries))
        logger.info("Memory module_summaries: %d", len(memory.module_summaries))
        self._storage[repository_id] = memory
        logger.info("MEMORY_STORE: Memory stored successfully")
        logger.info("Storage keys after set: %s", list(self._storage.keys()))
        
        # Verify storage
        verification = self._storage.get(repository_id)
        if verification:
            logger.info("MEMORY_STORE: Verification successful - memory retrievable")
            logger.info("  Verified symbol_summaries: %d", len(verification.symbol_summaries))
        else:
            logger.error("MEMORY_STORE: Verification FAILED - memory not retrievable")
        logger.info("=" * 80)

    def delete(self, repository_id: str) -> None:
        logger.info("MEMORY_STORE: delete() called for %s", repository_id)
        logger.info("MemoryStore instance ID: %s", self._instance_id)
        self._storage.pop(repository_id, None)
    
    def contains(self, repository_id: str) -> bool:
        """Check if repository_id exists in storage."""
        return repository_id in self._storage

memory_store = MemoryStore()
