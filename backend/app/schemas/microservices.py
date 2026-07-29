"""Schemas for microservice boundary detection API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class ServiceCandidate(BaseModel):
    """A potential microservice candidate."""

    service_name: str = Field(..., description="Service name")
    confidence: int = Field(ge=0, le=100, description="Confidence score (0-100)")
    boundary_score: int = Field(ge=0, le=100, description="Boundary score (0-100)")
    reason: str = Field(..., description="Reason for candidate selection")
    evidence: str = Field(..., description="Evidence for candidate selection")
    included_modules: list[str] = Field(default_factory=list, description="Included modules")
    dependencies: list[str] = Field(default_factory=list, description="Dependencies")
    migration_difficulty: str = Field(..., description="Migration difficulty")
    recommendation: str = Field(..., description="Extraction recommendation")


class BoundaryDetectionResponse(BaseModel):
    """Complete boundary detection response for a repository."""

    overall_score: int = Field(ge=0, le=100, description="Overall boundary detection score (0-100)")
    summary: dict[str, int] = Field(default_factory=dict, description="Summary statistics")
    candidates: list[ServiceCandidate] = Field(default_factory=list, description="Service candidates")
    communication_recommendations: list[str] = Field(default_factory=list, description="Communication recommendations")
