import logging
from typing import Optional
from app.schemas.repository_memory import RepositoryMemory, MemorySummary
from .memory_store import memory_store, MemoryStore
from .memory_builder import MemoryBuilder
from .memory_updater import MemoryUpdater
from .memory_retriever import MemoryRetriever

logger = logging.getLogger(__name__)

class MemoryEngine:
    """
    Facade for the Repository Memory subsystem.
    Coordinates memory building, updating, and retrieval.
    """
    def __init__(
        self,
        store: MemoryStore = memory_store,
        builder: Optional[MemoryBuilder] = None,
        updater: Optional[MemoryUpdater] = None,
        retriever: Optional[MemoryRetriever] = None,
    ):
        self._store = store
        self._builder = builder or MemoryBuilder()
        self._updater = updater or MemoryUpdater(store)
        self._retriever = retriever or MemoryRetriever(store)
        self._instance_id = id(self)
        logger.info("=" * 80)
        logger.info("MEMORY_ENGINE: __init__() called")
        logger.info("=" * 80)
        logger.info("MemoryEngine instance ID: %s", self._instance_id)
        logger.info("MemoryStore instance ID: %s", id(self._store))
        logger.info("=" * 80)

    def build_memory(self, repository_id: str) -> RepositoryMemory:
        logger.info("=" * 80)
        logger.info("MEMORY_ENGINE: build_memory() called")
        logger.info("=" * 80)
        logger.info("MemoryEngine instance ID: %s", self._instance_id)
        logger.info("MemoryStore instance ID: %s", id(self._store))
        logger.info("Repository ID: %s", repository_id)
        logger.info("MemoryEngine: Building memory for %s", repository_id)
        memory = self._builder.build(repository_id)
        logger.info("MEMORY_ENGINE: Memory built by builder")
        logger.info("  Symbol summaries: %d", len(memory.symbol_summaries))
        logger.info("  Module summaries: %d", len(memory.module_summaries))
        logger.info("MEMORY_ENGINE: Storing memory in store")
        self._store.set(repository_id, memory)
        logger.info("MEMORY_ENGINE: Memory stored successfully")
        logger.info("=" * 80)
        return memory

    def update_memory(self, repository_id: str, changes: dict) -> RepositoryMemory:
        logger.info(f"MemoryEngine: Updating memory for {repository_id}")
        return self._updater.update_incremental(repository_id, changes)

    def get_memory(self, repository_id: str) -> Optional[RepositoryMemory]:
        logger.info("=" * 80)
        logger.info("MEMORY_ENGINE: get_memory() called")
        logger.info("=" * 80)
        logger.info("MemoryEngine instance ID: %s", self._instance_id)
        logger.info("MemoryStore instance ID: %s", id(self._store))
        logger.info("Repository ID: %s", repository_id)
        result = self._retriever.retrieve(repository_id)
        logger.info("MEMORY_ENGINE: Result from retriever: %s", "found" if result else "not found")
        logger.info("=" * 80)
        return result
        
    def get_memory_summary(self, repository_id: str) -> Optional[MemorySummary]:
        return self._retriever.retrieve_summary(repository_id)

memory_engine = MemoryEngine()
