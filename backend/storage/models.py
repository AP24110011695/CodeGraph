"""SQLAlchemy models for persistent repository metadata."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Declarative base for storage models."""


class RepositoryRow(Base):
    """Canonical repository / index metadata row."""

    __tablename__ = "repositories"

    upload_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    repository_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    extraction_path: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="UPLOADED", index=True)
    indexing_state: Mapped[str] = mapped_column(String(32), nullable=False, default="NOT_INDEXED")
    repository_name: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    frameworks_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    languages_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    total_files: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_folders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    zip_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_chunks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_embeddings: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    added: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    modified: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    deleted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unchanged: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

    # Optional analysis payloads (JSON text)
    frameworks_result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    dependency_graph_meta_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    knowledge_graph_meta_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    architecture_result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    metrics_result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    workflow_state_json: Mapped[str | None] = mapped_column(Text, nullable=True)
