"""Snapshot tracking for incremental repository indexing."""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.services.scanner_service import ScanResult

logger = logging.getLogger(__name__)


@dataclass
class FileSnapshot:
    """Snapshot metadata for a single file."""

    relative_path: str
    sha256_hash: str
    size: int
    modified_time: float
    language: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "relative_path": self.relative_path,
            "sha256_hash": self.sha256_hash,
            "size": self.size,
            "modified_time": self.modified_time,
            "language": self.language,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FileSnapshot":
        """Create from dictionary."""
        return cls(
            relative_path=data["relative_path"],
            sha256_hash=data["sha256_hash"],
            size=data["size"],
            modified_time=data["modified_time"],
            language=data["language"],
        )


@dataclass
class RepositorySnapshot:
    """Snapshot tracking state of an entire repository."""

    upload_id: str
    files: dict[str, FileSnapshot] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "upload_id": self.upload_id,
            "files": {path: file.to_dict() for path, file in self.files.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RepositorySnapshot":
        """Create from dictionary."""
        snapshot = cls(upload_id=data["upload_id"])
        if "files" in data:
            snapshot.files = {
                path: FileSnapshot.from_dict(file_data)
                for path, file_data in data["files"].items()
            }
        return snapshot

    def save(self, project_path: Path) -> None:
        """Save snapshot to a JSON file in the project directory."""
        snapshot_path = project_path / ".codegraph_snapshot.json"
        try:
            with open(snapshot_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save snapshot for {self.upload_id}: {e}")

    @classmethod
    def load(cls, project_path: Path, upload_id: str) -> "RepositorySnapshot | None":
        """Load snapshot from a JSON file in the project directory."""
        snapshot_path = project_path / ".codegraph_snapshot.json"
        if not snapshot_path.exists():
            return None
        try:
            with open(snapshot_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            logger.warning(f"Failed to load snapshot for {upload_id}, assuming corrupted: {e}")
            return None

    def delete(self, project_path: Path) -> None:
        """Delete the snapshot file from the project directory."""
        snapshot_path = project_path / ".codegraph_snapshot.json"
        if snapshot_path.exists():
            try:
                snapshot_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete snapshot for {self.upload_id}: {e}")

    @classmethod
    def compute(cls, project_path: Path, upload_id: str, scan_result: ScanResult) -> "RepositorySnapshot":
        """Compute a fresh snapshot from a ScanResult."""
        snapshot = cls(upload_id=upload_id)
        
        for file_info in scan_result.files:
            if file_info.language == "Unknown":
                continue

            file_path = project_path / file_info.path
            if not file_path.exists():
                continue

            try:
                # Calculate sha256
                sha256 = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256.update(chunk)
                
                stat = file_path.stat()
                snapshot.files[file_info.path] = FileSnapshot(
                    relative_path=file_info.path,
                    sha256_hash=sha256.hexdigest(),
                    size=stat.st_size,
                    modified_time=stat.st_mtime,
                    language=file_info.language,
                )
            except Exception as e:
                logger.warning(f"Could not compute snapshot for {file_info.path}: {e}")
                
        return snapshot
