"""Merge a filesystem scan into a repository snapshot without losing identity."""

from datetime import datetime, timezone
import posixpath
from typing import Dict

from app.incremental_indexing.repository_snapshot import RepositorySnapshot
from app.schemas.incremental_indexing import ChangeSet, FileMetadata


class SnapshotMerger:
    def merge(
        self,
        snapshot: RepositorySnapshot,
        changes: ChangeSet,
        current_files: Dict[str, FileMetadata],
    ) -> RepositorySnapshot:
        now = datetime.now(timezone.utc)
        relocations = {**changes.renamed, **changes.moved}

        for old_path, new_path in relocations.items():
            previous = snapshot.get_file(old_path)
            if previous is None:
                continue
            snapshot.remove_file(old_path)
            current = current_files[new_path]
            current.file_uuid = previous.file_uuid
            current.previous_path = old_path
            current.previous_directory = posixpath.dirname(old_path) or None
            current.current_path = new_path
            current.current_directory = posixpath.dirname(new_path) or None
            current.last_seen_timestamp = now
            current.version_counter = previous.version_counter + 1
            snapshot.add_or_update_file(current)

        for path in changes.deleted:
            if path not in relocations:
                snapshot.remove_file(path)

        for path in changes.added + changes.modified:
            if path in relocations.values():
                continue
            current = current_files[path]
            previous = snapshot.get_file(path)
            current.current_path = path
            current.current_directory = posixpath.dirname(path) or None
            current.last_seen_timestamp = now
            if previous:
                current.file_uuid = previous.file_uuid
                current.previous_path = previous.current_path or path
                current.previous_directory = previous.current_directory
                current.version_counter = previous.version_counter + 1
            snapshot.add_or_update_file(current)

        for path in changes.unchanged:
            existing = snapshot.get_file(path)
            if existing:
                existing.current_path = path
                existing.current_directory = posixpath.dirname(path) or None
                existing.last_seen_timestamp = now

        if changes.added or changes.modified or changes.deleted or relocations:
            snapshot.model.repository_version += 1
            snapshot.model.snapshot_version += 1
            snapshot.model.version = snapshot.model.snapshot_version
        snapshot.model.indexed_timestamp = now
        return snapshot
