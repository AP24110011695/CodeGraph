"""Checksum-based file rename detection."""

from typing import Dict, Iterable

from app.schemas.incremental_indexing import FileMetadata


class RenameDetector:
    """Pairs removed and added files with the same content deterministically."""

    def detect(
        self,
        deleted: Iterable[str],
        added: Iterable[str],
        previous_files: Dict[str, FileMetadata],
        current_files: Dict[str, FileMetadata],
    ) -> Dict[str, str]:
        by_checksum: Dict[str, list[str]] = {}
        for old_path in sorted(deleted):
            old = previous_files[old_path]
            by_checksum.setdefault(old.checksum, []).append(old_path)

        matches: Dict[str, str] = {}
        for new_path in sorted(added):
            candidates = by_checksum.get(current_files[new_path].checksum, [])
            if candidates:
                matches[candidates.pop(0)] = new_path
        return matches
