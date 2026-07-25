"""Domain models for repository indexing."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class IndexStatus(str, Enum):
    """Lifecycle state of a repository index."""

    NOT_INDEXED = "NOT_INDEXED"
    INDEXING = "INDEXING"
    READY = "READY"
    FAILED = "FAILED"


@dataclass
class IndexStatistics:
    """Counts produced by a repository indexing run."""

    files: int = 0
    chunks: int = 0
    embeddings: int = 0


@dataclass
class RepositoryIndex:
    """Stored metadata and lifecycle state for one uploaded repository."""

    upload_id: str
    repository_name: str = ""
    frameworks: list[str] = field(default_factory=list)
    languages: dict[str, int] = field(default_factory=dict)
    total_files: int = 0
    total_chunks: int = 0
    total_embeddings: int = 0
    indexed_at: datetime | None = None
    status: IndexStatus = IndexStatus.NOT_INDEXED
    error: str | None = None

    @property
    def statistics(self) -> IndexStatistics:
        """Return public indexing counters."""
        return IndexStatistics(
            files=self.total_files,
            chunks=self.total_chunks,
            embeddings=self.total_embeddings,
        )
