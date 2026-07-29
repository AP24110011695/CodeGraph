"""Schemas for pull request review API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class PRReviewRequest(BaseModel):
    """Request for pull request review."""

    changed_files: list[str] = Field(..., description="List of changed file paths")
    diff: str | None = Field(None, description="Optional diff")
    modified_functions: list[str] = Field(default_factory=list, description="List of modified functions")
    added_files: list[str] = Field(default_factory=list, description="List of added files")
    deleted_files: list[str] = Field(default_factory=list, description="List of deleted files")


class ReviewComment(BaseModel):
    """A review comment for a pull request."""

    title: str
    category: str
    severity: str
    priority: str
    affected_file: str
    affected_function: str | None = None
    evidence: str = ""
    recommendation: str = ""


class PRReviewResponse(BaseModel):
    """Complete pull request review response for a repository."""

    overall_score: int = Field(ge=0, le=100, description="Overall review score (0-100)")
    approval: str = Field(description="Approval recommendation")
    summary: dict[str, int] = Field(default_factory=dict, description="Review summary")
    comments: list[ReviewComment] = Field(default_factory=list, description="Review comments")
    suggested_improvements: list[str] = Field(default_factory=list, description="Suggested improvements")
    risk_assessment: dict[str, Any] = Field(default_factory=dict, description="Risk assessment")
