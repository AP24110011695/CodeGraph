"""Schemas for architecture drift API responses."""

from typing import Any

from pydantic import BaseModel, Field


class DriftFinding(BaseModel):
    """An architecture drift finding."""

    title: str
    category: str
    severity: str
    score: int
    reason: str
    evidence: str
    affected_files: list[str] = Field(default_factory=list)
    recommendation: str = ""


class DriftSummary(BaseModel):
    """Summary of architecture drift statistics."""

    violations: int = 0
    layer_violations: int = 0
    cross_layer_dependencies: int = 0
    circular_dependencies: int = 0
    high_coupling: int = 0
    god_modules: int = 0


class ArchitectureDriftResponse(BaseModel):
    """Complete architecture drift response for a repository."""

    project_name: str
    architecture_health_score: int
    architecture_grade: str
    drift_score: int
    stability_score: int
    summary: DriftSummary
    findings: list[DriftFinding] = Field(default_factory=list)
    top_violations: list[DriftFinding] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
