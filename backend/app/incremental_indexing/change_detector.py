import os
import hashlib
from typing import Dict, List, Tuple
from app.schemas.incremental_indexing import FileMetadata
from app.incremental_indexing.repository_snapshot import RepositorySnapshot
from app.incremental_indexing.rename_detector import RenameDetector
from app.incremental_indexing.move_detector import MoveDetector
from app.incremental_indexing.snapshot_diff import SnapshotDiff

class ChangeDetector:
    """Detects changes between the filesystem and the last snapshot."""
    
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def _compute_checksum(self, filepath: str) -> str:
        """Compute SHA256 checksum of a file."""
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def detect_changes(self, snapshot: RepositorySnapshot) -> Tuple[SnapshotDiff, Dict[str, FileMetadata]]:
        """
        Scans the root_dir and compares with snapshot.
        Returns the ChangeSet and a dict of the new FileMetadata for all current files.
        """
        changes = SnapshotDiff()
        current_files: Dict[str, FileMetadata] = {}
        
        # Scan filesystem
        for root, _, files in os.walk(self.root_dir):
            if ".git" in root or ".snapshots" in root:
                continue
                
            for filename in files:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, self.root_dir).replace('\\', '/')
                
                try:
                    stat = os.stat(filepath)
                    size = stat.st_size
                    mtime = stat.st_mtime
                    
                    old_meta = snapshot.get_file(rel_path)
                    
                    # Quick optimization: check mtime and size first
                    if old_meta and old_meta.size == size and old_meta.last_modified == mtime:
                        checksum = old_meta.checksum
                    else:
                        checksum = self._compute_checksum(filepath)
                        
                    current_files[rel_path] = FileMetadata(
                        path=rel_path,
                        checksum=checksum,
                        size=size,
                        last_modified=mtime,
                        current_path=rel_path,
                    )
                    
                    if not old_meta:
                        changes.added.append(rel_path)
                    elif old_meta.checksum != checksum:
                        changes.modified.append(rel_path)
                    else:
                        changes.unchanged.append(rel_path)
                        
                except Exception as e:
                    # Skip files we can't read
                    pass

        # Detect deleted files
        for old_path in snapshot.model.files.keys():
            if old_path not in current_files:
                changes.deleted.append(old_path)
                
        # A checksum match preserves identity.  Remove the paired entries from
        # add/delete so invalidators never treat a location-only change as content.
        relocations = RenameDetector().detect(
            changes.deleted, changes.added, snapshot.model.files, current_files
        )
        changes.moved = MoveDetector.detect(relocations)
        changes.renamed = {
            old_path: new_path
            for old_path, new_path in relocations.items()
            if old_path not in changes.moved
        }
        relocated_old = set(relocations)
        relocated_new = set(relocations.values())
        changes.deleted = [path for path in changes.deleted if path not in relocated_old]
        changes.added = [path for path in changes.added if path not in relocated_new]

        return changes, current_files
