from typing import Optional
from app.schemas.repository_memory import RepositoryMemory

class MemoryStore:
    def __init__(self):
        # In-memory storage designed to be easily replaced by Redis, PostgreSQL, or VectorDB
        self._storage: dict[str, RepositoryMemory] = {}

    def get(self, repository_id: str) -> Optional[RepositoryMemory]:
        return self._storage.get(repository_id)

    def set(self, repository_id: str, memory: RepositoryMemory) -> None:
        self._storage[repository_id] = memory

    def delete(self, repository_id: str) -> None:
        self._storage.pop(repository_id, None)

memory_store = MemoryStore()
