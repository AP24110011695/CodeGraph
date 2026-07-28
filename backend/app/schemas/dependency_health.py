"""Schemas for dependency health API responses."""

from typing import Any

from pydantic import BaseModel, Field


class DependencyFinding(BaseModel):
    """A dependency health finding."""

    title: str
    category: str
    severity: str
    score: int
    evidence: str
    affected_files: list[str] = Field(default_factory=list)
    recommendation: str = ""


class DependencyHealthSummary(BaseModel):
    """Summary of dependency health statistics."""

    internal_dependencies: int = 0
    external_dependencies: int = 0
    cycles: int = 0
    critical_modules: int = 0
    high_risk_modules: int = 0
    coupling_density: float = 0.0
    fan_out_max: int = 0
    fan_in_max: int = 0
    isolated_modules: int = 0


class DependencyHealthResponse(BaseModel):
    """Complete dependency health response for a repository."""

    project_name: str
    overall_health_score: int
    health_grade: str
    summary: DependencyHealthSummary
    findings: list[DependencyFinding] = Field(default_factory=list)
    critical_modules: list[str] = Field(default_factory=list)
    high_risk_modules: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
