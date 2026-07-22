"""Pydantic schemas for the dependency graph API responses."""

from pydantic import BaseModel, Field

from app.schemas.framework import ProjectInfo
from app.schemas.scanner import ScanSummary


class GraphNode(BaseModel):
    """A node representing a file in the dependency graph."""

    id: str = Field(description="Unique identifier (usually the relative path)")
    path: str = Field(description="Relative path of the file")
    language: str = Field(description="Detected programming language")


class GraphEdge(BaseModel):
    """A directed edge representing a dependency between two files."""

    from_: str = Field(alias="from", description="Source node ID (file making the import)")
    to: str = Field(description="Target node ID (file being imported)")
    type: str = Field(default="import", description="Type of relationship")


class GraphStatistics(BaseModel):
    """Summary statistics for the dependency graph."""

    nodes: int = Field(ge=0, description="Total number of nodes")
    edges: int = Field(ge=0, description="Total number of edges")
    isolated_files: int = Field(ge=0, description="Nodes with zero in-degree and zero out-degree")


class DependencyGraphResponse(BaseModel):
    """Complete response returned by GET /dependency-graph/{upload_id}."""

    project: ProjectInfo
    summary: ScanSummary
    nodes: list[GraphNode] = Field(description="List of all file nodes in the graph")
    edges: list[GraphEdge] = Field(description="List of all internal dependencies")
    statistics: GraphStatistics = Field(description="Graph topology statistics")
