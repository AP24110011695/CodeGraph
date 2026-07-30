import logging
from typing import Optional
from app.schemas.repository_memory import RepositoryMemory, MemorySummary
from .memory_store import MemoryStore

logger = logging.getLogger(__name__)

class MemoryRetriever:
    def __init__(self, store: MemoryStore):
        self._store = store

    def retrieve(self, repository_id: str) -> Optional[RepositoryMemory]:
        logger.debug(f"Retrieving memory for repository {repository_id}")
        return self._store.get(repository_id)
        
    def retrieve_summary(self, repository_id: str) -> Optional[MemorySummary]:
        memory = self.retrieve(repository_id)
        if not memory:
            return None
            
        return MemorySummary(
            repository_id=memory.repository_id,
            repository_summary=memory.repository_summary,
            architecture_summary=memory.architecture_summary,
            module_count=len(memory.module_summaries),
            file_count=len(memory.file_summaries),
            symbol_count=len(memory.symbol_summaries)
        )
