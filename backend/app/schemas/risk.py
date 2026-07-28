"""Schemas for risk analysis API responses."""

from typing import Any

from pydantic import BaseModel, Field


class RiskItem(BaseModel):
    """A single risk item."""

    title: str
    category: str
    risk_level: str
    score: int
    reason: str
    evidence: str
    affected_files: list[str] = Field(default_factory=list)
    recommendation: str = ""
    potential_impact: str = ""
    source: str = ""


class RiskSummary(BaseModel):
    """Summary of risks by level."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class RiskResponse(BaseModel):
    """Complete risk analysis response for a repository."""

    project_name: str
    overall_risk_score: int
    overall_level: str
    summary: RiskSummary
    risks: list[RiskItem] = Field(default_factory=list)
    top_risks: list[RiskItem] = Field(default_factory=list)
    priority_recommendations: list[str] = Field(default_factory=list)
