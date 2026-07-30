"""Schemas for copilot API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class CopilotRequest(BaseModel):
    """Request for copilot query."""

    query: str = Field(..., description="User query about the repository")


class CopilotResponse(BaseModel):
    """Complete copilot response."""

    upload_id: str = Field(..., description="Repository upload ID")
    query: str = Field(..., description="User query")
    intent: str = Field(..., description="Detected intent")
    module: str = Field(..., description="Module used to answer")
    confidence: int = Field(..., description="Confidence score (0-100)")
    answer: str = Field(..., description="Answer to the query")
    sources: list[str] = Field(default_factory=list, description="Sources of the answer")
    evidence: list[str] = Field(default_factory=list, description="Evidence supporting the answer")
    related_modules: list[str] = Field(default_factory=list, description="Related modules")
    error: str | None = Field(None, description="Error message if failed")
