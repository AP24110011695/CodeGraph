"""Schemas for database schema visualization API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class Entity(BaseModel):
    """A database entity (table/model)."""

    name: str = Field(..., description="Entity name")
    columns: list[str] = Field(default_factory=list, description="Column names")
    primary_key: str | None = Field(None, description="Primary key")
    foreign_keys: list[str] = Field(default_factory=list, description="Foreign keys")
    indexes: list[str] = Field(default_factory=list, description="Indexes")
    relationships: list[str] = Field(default_factory=list, description="Relationships")
    evidence: str = Field(..., description="Evidence for entity detection")


class Relationship(BaseModel):
    """A relationship between entities."""

    source: str = Field(..., description="Source entity")
    target: str = Field(..., description="Target entity")
    type: str = Field(..., description="Relationship type")
    evidence: str = Field(..., description="Evidence for relationship detection")


class SchemaResponse(BaseModel):
    """Complete schema visualization response for a repository."""

    schema_score: int = Field(ge=0, le=100, description="Schema quality score (0-100)")
    summary: dict[str, int] = Field(default_factory=dict, description="Summary statistics")
    entities: list[Entity] = Field(default_factory=list, description="Detected entities")
    relationships: list[Relationship] = Field(default_factory=list, description="Detected relationships")
    mermaid: str = Field(default="", description="Mermaid ERD diagram")
    recommendations: list[str] = Field(default_factory=list, description="Improvement recommendations")
