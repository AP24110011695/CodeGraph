"""Schemas for design pattern detection API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class PatternDetection(BaseModel):
    """A detected design pattern."""

    name: str = Field(..., description="Pattern name")
    category: str = Field(..., description="Pattern category")
    confidence: int = Field(ge=0, le=100, description="Confidence score (0-100)")
    evidence: str = Field(..., description="Evidence for pattern detection")
    affected_files: list[str] = Field(default_factory=list, description="Affected files")
    reason: str = Field(..., description="Reason for pattern detection")


class AntiPatternDetection(BaseModel):
    """A detected anti-pattern."""

    name: str = Field(..., description="Anti-pattern name")
    severity: str = Field(..., description="Severity level")
    evidence: str = Field(..., description="Evidence for anti-pattern detection")
    affected_files: list[str] = Field(default_factory=list, description="Affected files")
    recommendation: str = Field(..., description="Recommendation for improvement")


class PatternDetectionResponse(BaseModel):
    """Complete pattern detection response for a repository."""

    patterns: list[PatternDetection] = Field(default_factory=list, description="Detected patterns")
    anti_patterns: list[AntiPatternDetection] = Field(default_factory=list, description="Detected anti-patterns")
    architecture_summary: dict[str, Any] = Field(default_factory=dict, description="Architecture summary")
    improvement_suggestions: list[str] = Field(default_factory=list, description="Improvement suggestions")
