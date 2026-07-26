"""Pydantic schemas for the UML diagram API responses."""

from pydantic import BaseModel, Field


class UMLResponse(BaseModel):
    """Complete response returned by POST /uml/{upload_id}."""

    diagram_type: str = Field(description="Type of diagram generated")
    syntax: str = Field(description="Diagram syntax format (mermaid)")
    diagram: str = Field(description="Mermaid diagram syntax")
    total_classes: int = Field(description="Total number of classes detected")
    total_relationships: int = Field(description="Total number of relationships detected")
