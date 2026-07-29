"""Schemas for bug localization API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class BugLocalizationRequest(BaseModel):
    """Request for bug localization."""

    bug_description: str = Field(..., description="Description of the bug")
    stack_trace: str | None = Field(None, description="Optional stack trace")
    file_name: str | None = Field(None, description="Optional file name")
    function_name: str | None = Field(None, description="Optional function name")


class BugPrediction(BaseModel):
    """A bug location prediction."""

    file: str
    function: str | None = None
    module: str | None = None
    confidence: int = Field(ge=0, le=100, description="Confidence score (0-100)")
    priority: int = Field(ge=1, description="Investigation priority (lower is higher priority)")
    reason: str = ""
    evidence: str = ""


class BugLocalizationResponse(BaseModel):
    """Complete bug localization response for a repository."""

    likely_root_cause: str
    confidence: int = Field(ge=0, le=100, description="Overall confidence score (0-100)")
    predictions: list[BugPrediction] = Field(default_factory=list)
    related_modules: list[str] = Field(default_factory=list)
    suggested_investigation_order: list[str] = Field(default_factory=list)
