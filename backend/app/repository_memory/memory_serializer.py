import json
from app.schemas.repository_memory import RepositoryMemory

class MemorySerializer:
    def serialize(self, memory: RepositoryMemory) -> str:
        return memory.model_dump_json()

    def deserialize(self, data: str) -> RepositoryMemory:
        return RepositoryMemory.model_validate_json(data)
