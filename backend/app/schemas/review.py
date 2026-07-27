"""Schemas for review API responses."""

from typing import Any

from pydantic import BaseModel, Field


class ReviewIssue(BaseModel):
    """A code review issue."""

    title: str
    category: str
    severity: str
    priority: str
    description: str
    evidence: str
    affected_files: list[str] = Field(default_factory=list)
    recommendation: str = ""
    estimated_impact: str = ""
    source: str = ""


class ReviewSummary(BaseModel):
    """Summary of the code review."""

    overall_score: int
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    total_files: int
    total_lines: int | None = None
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    quality_score: int | None = None
    security_score: int | None = None


class ReviewResponse(BaseModel):
    """Complete review response for a repository."""

    project_name: str
    overall_score: int
    summary: ReviewSummary
    issues: list[ReviewIssue] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    recommendations: dict[str, list[str]] = Field(default_factory=dict)
