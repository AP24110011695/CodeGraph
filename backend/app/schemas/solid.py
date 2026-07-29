"""Schemas for SOLID principle analysis API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class PrincipleResult(BaseModel):
    """Result for a single SOLID principle."""

    principle: str = Field(..., description="Principle name")
    score: int = Field(ge=0, le=100, description="Principle score (0-100)")
    status: str = Field(..., description="Compliance status")
    violations: int = Field(ge=0, description="Number of violations")
    evidence: str = Field(..., description="Evidence for violation")
    affected_files: list[str] = Field(default_factory=list, description="Affected files")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")


class SOLIDResponse(BaseModel):
    """Complete SOLID analysis response for a repository."""

    overall_score: int = Field(ge=0, le=100, description="Overall SOLID score (0-100)")
    overall_rating: str = Field(..., description="Overall rating")
    principles: list[PrincipleResult] = Field(default_factory=list, description="Principle results")
    priority_fixes: list[str] = Field(default_factory=list, description="Priority fixes")
