"""Schemas for knowledge graph API responses."""

from typing import Any

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    """A node in the knowledge graph."""

    id: str
    type: str
    name: str
    properties: dict[str, Any] = Field(default_factory=dict)
    labels: list[str] = Field(default_factory=list)


class GraphEdge(BaseModel):
    """An edge in the knowledge graph."""

    source: str
    target: str
    type: str
    properties: dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraphResponse(BaseModel):
    """Complete knowledge graph response for a repository."""

    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    statistics: dict[str, int | dict[str, int]] = Field(default_factory=dict)
