"""Schemas for release notes API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class ReleaseNotesRequest(BaseModel):
    """Request for release notes generation."""

    version: str = Field(..., description="Release version")


class ReleaseSection(BaseModel):
    """Release notes section."""

    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")


class RepositorySummary(BaseModel):
    """Repository summary for release notes."""

    repository_name: str = Field(..., description="Repository name")
    upload_id: str = Field(..., description="Upload ID")
    languages: list[str] = Field(default_factory=list, description="Programming languages")
    architecture_score: int = Field(..., description="Architecture score")
    health_score: int = Field(..., description="Health score")


class EngineeringMetrics(BaseModel):
    """Engineering metrics for release notes."""

    quality_score: int = Field(..., description="Quality score")
    security_score: int = Field(..., description="Security score")
    risk_score: int = Field(..., description="Risk score")


class ChangelogData(BaseModel):
    """Changelog data."""

    version: str = Field(..., description="Version")
    date: str = Field(..., description="Release date")
    changes: list[str] = Field(default_factory=list, description="Changes")
    breaking_changes: list[str] = Field(default_factory=list, description="Breaking changes")
    feature_additions: list[str] = Field(default_factory=list, description="Feature additions")
    bug_fixes: list[str] = Field(default_factory=list, description="Bug fixes")
    improvements: list[str] = Field(default_factory=list, description="Improvements")


class ReleaseNotesResponse(BaseModel):
    """Complete release notes response."""

    version: str = Field(..., description="Release version")
    upload_id: str = Field(..., description="Repository upload ID")
    summary: str = Field(..., description="Executive summary")
    repository_summary: RepositorySummary = Field(..., description="Repository summary")
    sections: list[ReleaseSection] = Field(default_factory=list, description="Release notes sections")
    changelog: ChangelogData | None = Field(None, description="Changelog data")
    engineering_metrics: EngineeringMetrics = Field(..., description="Engineering metrics")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")
    known_issues: list[str] = Field(default_factory=list, description="Known issues")
    error: str | None = Field(None, description="Error message if failed")
