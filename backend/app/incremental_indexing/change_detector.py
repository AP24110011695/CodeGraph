import os
import hashlib
from typing import Dict, List, Tuple
from app.schemas.incremental_indexing import ChangeSet, FileMetadata
from app.incremental_indexing.repository_snapshot import RepositorySnapshot

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

    def detect_changes(self, snapshot: RepositorySnapshot) -> Tuple[ChangeSet, Dict[str, FileMetadata]]:
        """
        Scans the root_dir and compares with snapshot.
        Returns the ChangeSet and a dict of the new FileMetadata for all current files.
        """
        changes = ChangeSet()
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
                        last_modified=mtime
                    )
                    
                    if not old_meta:
                        changes.added.append(rel_path)
                    elif old_meta.checksum != checksum:
                        changes.modified.append(rel_path)
                        
                except Exception as e:
                    # Skip files we can't read
                    pass

        # Detect deleted files
        for old_path in snapshot.model.files.keys():
            if old_path not in current_files:
                changes.deleted.append(old_path)
                
        # Future enhancement: Detect renamed/moved files based on identical checksums between deleted and added

        return changes, current_files
