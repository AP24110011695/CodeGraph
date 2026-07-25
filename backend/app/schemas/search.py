"""HTTP schemas for repository search."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Search request payload."""

    query: str = Field(description="Search query string")
    mode: Literal["semantic", "keyword", "hybrid"] = Field(default="hybrid")


class SearchResultSchema(BaseModel):
    """Single ranked search result."""

    path: str
    score: float
    snippet: str
    language: str
    line_start: int
    line_end: int


class SearchResponse(BaseModel):
    """Repository search response payload."""

    results: list[SearchResultSchema]
    total: int
