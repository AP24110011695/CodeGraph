from typing import Dict, Any, Optional
from app.schemas.incremental_indexing import RepositorySnapshotModel, FileMetadata
import json

class RepositorySnapshot:
    def __init__(self, model: RepositorySnapshotModel):
        self.model = model

    def get_file(self, path: str) -> Optional[FileMetadata]:
        return self.model.files.get(path)

    def add_or_update_file(self, file_meta: FileMetadata):
        self.model.files[file_meta.path] = file_meta

    def remove_file(self, path: str):
        if path in self.model.files:
            del self.model.files[path]

    def to_dict(self) -> Dict[str, Any]:
        return self.model.model_dump(mode='json')
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepositorySnapshot":
        return cls(RepositorySnapshotModel(**data))
