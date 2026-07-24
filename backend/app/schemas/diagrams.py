"""Pydantic schemas for the diagram generation API responses."""

from pydantic import BaseModel, Field

from app.schemas.framework import ProjectInfo


class DiagramSyntax(BaseModel):
    """Diagram syntax in a specific format."""

    system: str = Field(description="System architecture diagram syntax")
    modules: str = Field(description="Module diagram syntax")
    components: str = Field(description="Component diagram syntax")
    dependencies: str = Field(description="Dependency diagram syntax")
    layers: str = Field(description="Layer diagram syntax")


class DiagramStatistics(BaseModel):
    """Summary statistics for the diagram generation."""

    nodes: int = Field(ge=0, description="Total number of nodes in the graph")
    edges: int = Field(ge=0, description="Total number of edges in the graph")


class DiagramResponse(BaseModel):
    """Complete response returned by GET /diagrams/{upload_id}."""

    project: ProjectInfo = Field(description="Project metadata")
    mermaid: DiagramSyntax = Field(description="Mermaid diagram syntax for all diagram types")
    plantuml: DiagramSyntax = Field(description="PlantUML diagram syntax for all diagram types")
    statistics: DiagramStatistics = Field(description="Diagram generation statistics")
