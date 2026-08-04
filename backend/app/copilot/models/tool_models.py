"""Tool models for the Copilot tool execution layer."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ToolDefinition(BaseModel):
    """Defines a specialized tool's metadata and capabilities."""
    name: str = Field(..., description="Unique identifier for the tool")
    description: str = Field(..., description="Description of what the tool does")
    capabilities: List[str] = Field(..., description="Capabilities this tool provides (e.g. 'architecture', 'workflow')")
    input_schema: Dict[str, Any] = Field(default_factory=dict, description="Expected input JSON schema")
    output_schema: Dict[str, Any] = Field(default_factory=dict, description="Expected output JSON schema")


class ToolResult(BaseModel):
    """Standardized output schema for every tool execution."""
    tool: str = Field(..., description="Name of the tool that generated this result")
    summary: str = Field(..., description="Human-readable summary of the tool's findings")
    evidence: List[Dict[str, Any]] = Field(default_factory=list, description="Structured evidence or findings")
    related_files: List[str] = Field(default_factory=list, description="Files related to the findings")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context or metadata")
