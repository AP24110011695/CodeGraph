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

    def build_memory(self, repository_id: str) -> RepositoryMemory:
        memory = self._builder.build(repository_id)
        self._store.set(repository_id, memory)
        return memory

    def update_memory(self, repository_id: str, changes: dict) -> RepositoryMemory:
        logger.info(f"MemoryEngine: Updating memory for {repository_id}")
        return self._updater.update_incremental(repository_id, changes)

    def get_memory(self, repository_id: str) -> Optional[RepositoryMemory]:
        return self._retriever.retrieve(repository_id)
        
    def get_memory_summary(self, repository_id: str) -> Optional[MemorySummary]:
        return self._retriever.retrieve_summary(repository_id)

memory_engine = MemoryEngine()
