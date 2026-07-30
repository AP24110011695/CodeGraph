"""Schemas for repository comparison API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class RepositoryComparisonRequest(BaseModel):
    """Request for repository comparison."""

    repositories: list[str] = Field(..., description="List of repository upload IDs to compare")


class ComparisonCategory(BaseModel):
    """Comparison for a specific category."""

    category: str = Field(..., description="Category name")
    repository_scores: list[dict[str, Any]] = Field(default_factory=list, description="Repository scores")
    highest: dict[str, Any] | None = Field(None, description="Highest scoring repository")
    lowest: dict[str, Any] | None = Field(None, description="Lowest scoring repository")
    average: float = Field(..., description="Average score")
    spread: float = Field(..., description="Score spread")


class ComparisonSummary(BaseModel):
    """Summary of comparison results."""

    repositories: int = Field(..., description="Number of repositories compared")
    average_similarity: float = Field(..., description="Average similarity score")
    most_similar: float | None = Field(None, description="Most similar score")
    least_similar: float | None = Field(None, description="Least similar score")


class ComparisonStrength(BaseModel):
    """Repository strength."""

    repository: str = Field(..., description="Repository ID")
    category: str = Field(..., description="Category")
    score: int = Field(..., description="Score")
    description: str = Field(..., description="Description")


class ComparisonWeakness(BaseModel):
    """Repository weakness."""

    repository: str = Field(..., description="Repository ID")
    category: str = Field(..., description="Category")
    score: int = Field(..., description="Score")
    description: str = Field(..., description="Description")


class RepositoryComparisonResponse(BaseModel):
    """Complete repository comparison response."""

    repository_ids: list[str] = Field(..., description="Repository IDs compared")
    similarity_score: int = Field(..., description="Overall similarity score")
    summary: ComparisonSummary = Field(..., description="Comparison summary")
    comparisons: list[ComparisonCategory] = Field(default_factory=list, description="Category comparisons")
    recommendations: list[str] = Field(default_factory=list, description="Improvement recommendations")
    strengths: list[ComparisonStrength] = Field(default_factory=list, description="Repository strengths")
    weaknesses: list[ComparisonWeakness] = Field(default_factory=list, description="Repository weaknesses")
    error: str | None = Field(None, description="Error message if failed")
