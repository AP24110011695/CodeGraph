"""Schemas for architecture report API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class ReportSection(BaseModel):
    """A section of the architecture report."""

    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    score: int | None = Field(None, description="Section score")


class ArchitectureReportResponse(BaseModel):
    """Complete architecture report response for a repository."""

    overall_score: int = Field(ge=0, le=100, description="Overall architecture score (0-100)")
    engineering_maturity: str = Field(..., description="Engineering maturity level")
    executive_summary: str = Field(..., description="Executive summary")
    strengths: list[str] = Field(default_factory=list, description="Strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Weaknesses")
    high_priority_improvements: list[str] = Field(default_factory=list, description="High priority improvements")
    medium_priority_improvements: list[str] = Field(default_factory=list, description="Medium priority improvements")
    long_term_improvements: list[str] = Field(default_factory=list, description="Long term improvements")
    sections: list[ReportSection] = Field(default_factory=list, description="Report sections")
    markdown: str = Field(default="", description="Full markdown report")
