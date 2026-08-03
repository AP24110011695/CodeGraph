"""HTTP schemas for repository indexing."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.indexing.indexing_models import IndexStatus, RepositoryIndex


class IndexStatisticsResponse(BaseModel):
    files: int
    folders: int = 0
    zip_size_bytes: int = 0
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
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
        # Build language list sorted by file count (most prevalent first)
        languages_map: dict[str, int] = index.languages or {}
        languages_list = [
            lang
            for lang, _ in sorted(languages_map.items(), key=lambda x: x[1], reverse=True)
        ]
        return cls(
            upload_id=index.upload_id,
            status=index.status,
            statistics=IndexStatisticsResponse(
                files=stats.files,
                folders=index.total_folders,
                zip_size_bytes=index.zip_size_bytes,
                languages=languages_list,
                frameworks=list(index.frameworks or []),
                chunks=stats.chunks,
                embeddings=stats.embeddings,
                added=stats.added,
                modified=stats.modified,
                deleted=stats.deleted,
                unchanged=stats.unchanged,
            ),
            indexed_at=index.indexed_at,
        )
