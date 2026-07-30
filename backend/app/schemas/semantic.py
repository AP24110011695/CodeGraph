from typing import Any, Literal

from pydantic import BaseModel, Field


class SemanticSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    mode: Literal["semantic", "hybrid"] = "hybrid"
    limit: int = Field(default=10, ge=1, le=20)


class SemanticResult(BaseModel):
    path: str
    score: float
    context_score: float
    snippet: str
    language: str
    line_start: int
    line_end: int


class SemanticSearchResponse(BaseModel):
    query: str
    mode: str
    results: list[SemanticResult]
    symbols: list[dict[str, Any]]
    relationships: list[dict[str, Any]]
    total: int
