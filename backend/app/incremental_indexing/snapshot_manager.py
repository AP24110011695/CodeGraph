import threading
import json
import os
from typing import Optional, Dict
from app.schemas.incremental_indexing import RepositorySnapshotModel
from app.schemas.incremental_indexing import ChangeSet, FileMetadata
from app.incremental_indexing.repository_snapshot import RepositorySnapshot

class SnapshotManager:
    """
    Manages loading and saving of RepositorySnapshots.
    Currently uses local storage, designed to be swapped for Redis/S3.
    """
    def __init__(self, storage_dir: str = None):
        self.storage_dir = storage_dir or os.path.join("uploads", ".snapshots")
        os.makedirs(self.storage_dir, exist_ok=True)
        self._lock = threading.Lock()
        
    def _get_snapshot_path(self, repository_id: str) -> str:
        return os.path.join(self.storage_dir, f"{repository_id}_snapshot.json")

    def get_snapshot(self, repository_id: str) -> Optional[RepositorySnapshot]:
        path = self._get_snapshot_path(repository_id)
        with self._lock:
            if not os.path.exists(path):
                return None
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return RepositorySnapshot.from_dict(data)
            except Exception:
                return None

    def save_snapshot(self, snapshot: RepositorySnapshot) -> None:
        path = self._get_snapshot_path(snapshot.model.repository_id)
        with self._lock:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(snapshot.to_dict(), f)

    def create_empty_snapshot(self, repository_id: str) -> RepositorySnapshot:
        model = RepositorySnapshotModel(repository_id=repository_id)
        return RepositorySnapshot(model)

    def merge_snapshot(
        self,
        snapshot: RepositorySnapshot,
        changes: ChangeSet,
        current_files: Dict[str, FileMetadata],
    ) -> RepositorySnapshot:
        """Storage-neutral snapshot evolution entry point."""
        return snapshot.evolve(changes, current_files)

# Global instance
snapshot_manager = SnapshotManager()
