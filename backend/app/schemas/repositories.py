"""Schemas for repository management APIs."""

from datetime import datetime

from pydantic import BaseModel, Field


class RepositorySummary(BaseModel):
    """Public repository metadata for list/detail views."""

    id: str = Field(..., description="Repository / upload identifier")
    name: str
    uploaded_at: datetime
    status: str
    framework: str | None = None
    language: str | None = None


class RepositoryListResponse(BaseModel):
    """List of known repositories."""

    repositories: list[RepositorySummary] = Field(default_factory=list)
    total: int = 0
