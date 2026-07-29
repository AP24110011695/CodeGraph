"""Schemas for API dependency flow API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class Endpoint(BaseModel):
    """An API endpoint."""

    method: str = Field(..., description="HTTP method")
    path: str = Field(..., description="Endpoint path")
    controller: str = Field(..., description="Controller name")
    middleware: list[str] = Field(default_factory=list, description="Middleware")
    dependencies: list[str] = Field(default_factory=list, description="Dependencies")
    database_access: list[str] = Field(default_factory=list, description="Database access")
    evidence: str = Field(..., description="Evidence for endpoint detection")


class FlowStep(BaseModel):
    """A step in the API flow."""

    source: str = Field(..., description="Source component")
    destination: str = Field(..., description="Destination component")
    action: str = Field(..., description="Action performed")
    evidence: str = Field(..., description="Evidence for flow detection")


class APIFlowResponse(BaseModel):
    """Complete API flow response for a repository."""

    flow_score: int = Field(ge=0, le=100, description="API flow quality score (0-100)")
    summary: dict[str, int] = Field(default_factory=dict, description="Summary statistics")
    endpoints: list[Endpoint] = Field(default_factory=list, description="Detected endpoints")
    flows: list[FlowStep] = Field(default_factory=list, description="Detected flows")
    sequence_diagram: str = Field(default="", description="Mermaid sequence diagram")
    recommendations: list[str] = Field(default_factory=list, description="Improvement recommendations")
