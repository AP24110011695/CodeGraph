"""HTTP schemas for repository indexing."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.indexing.indexing_models import IndexStatus, RepositoryIndex


class IndexStatisticsResponse(BaseModel):
    files: int
    chunks: int
    embeddings: int
    added: int
    modified: int
    deleted: int
    unchanged: int


class IndexResponse(BaseModel):
    upload_id: str
    status: IndexStatus
    statistics: IndexStatisticsResponse
    indexed_at: datetime | None = None

    @classmethod
    def from_index(cls, index: RepositoryIndex) -> "IndexResponse":
        stats = index.statistics
        return cls(
            upload_id=index.upload_id,
            status=index.status,
            statistics=IndexStatisticsResponse(
                files=stats.files,
                chunks=stats.chunks,
                embeddings=stats.embeddings,
                added=stats.added,
                modified=stats.modified,
                deleted=stats.deleted,
                unchanged=stats.unchanged,
            ),
            indexed_at=index.indexed_at,
        )
