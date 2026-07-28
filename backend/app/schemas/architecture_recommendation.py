"""Schemas for architecture recommendation API responses."""

from typing import Any

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    """An architecture recommendation."""

    title: str
    category: str
    priority: str
    impact: str
    confidence: int
    reason: str
    evidence: str
    affected_files: list[str] = Field(default_factory=list)
    recommendation: str = ""
    expected_benefit: str = ""


class RecommendationSummary(BaseModel):
    """Summary of recommendation statistics."""

    recommendations: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class ArchitectureRecommendationResponse(BaseModel):
    """Complete architecture recommendation response for a repository."""

    project_name: str
    overall_architecture_score: int
    summary: RecommendationSummary
    recommendations: list[Recommendation] = Field(default_factory=list)
