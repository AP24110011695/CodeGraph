"""Schemas for license compliance API responses."""

from typing import Any

from pydantic import BaseModel, Field


class LicenseFinding(BaseModel):
    """A license compliance finding."""

    title: str
    category: str
    severity: str
    compliance_status: str
    evidence: str
    affected_files: list[str] = Field(default_factory=list)
    recommendation: str = ""


class LicenseSummary(BaseModel):
    """Summary of license compliance statistics."""

    dependencies: int = 0
    licensed: int = 0
    unknown: int = 0
    conflicts: int = 0


class LicenseResponse(BaseModel):
    """Complete license compliance response for a repository."""

    project_name: str
    repository_license: str
    compliance_status: str
    summary: LicenseSummary
    findings: list[LicenseFinding] = Field(default_factory=list)
    dependency_licenses: dict[str, str] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)
