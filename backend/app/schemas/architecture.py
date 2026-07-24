"""Pydantic schemas for the architecture analysis API responses."""

from pydantic import BaseModel, Field

from app.schemas.framework import ProjectInfo
from app.schemas.scanner import ScanSummary


class ArchitectureComponent(BaseModel):
    """A detected architectural component."""

    name: str = Field(description="Name of the component (class, function, etc.)")
    type: str = Field(description="Type of component (Controller, Service, Repository, etc.)")
    file_path: str = Field(description="Relative path of the file containing the component")
    language: str = Field(description="Programming language of the component")


class ArchitectureModuleSchema(BaseModel):
    """A logical module grouping related files and components."""

    name: str = Field(description="Name of the module")
    type: str = Field(description="Type of module (Backend Module, Frontend Module, etc.)")
    files: list[str] = Field(description="List of file paths in this module")
    components: list[ArchitectureComponent] = Field(
        description="List of components in this module"
    )
    layer: str = Field(description="Application layer this module belongs to")


class ArchitectureRelationship(BaseModel):
    """A relationship between architectural elements."""

    source: str = Field(description="Source module or component name")
    target: str = Field(description="Target module or component name")
    type: str = Field(description="Type of relationship (depends_on, inherits, etc.)")


class ArchitectureStatistics(BaseModel):
    """Summary statistics for the architecture analysis."""

    modules: int = Field(ge=0, description="Total number of detected modules")
    components: int = Field(ge=0, description="Total number of detected components")
    relationships: int = Field(ge=0, description="Total number of detected relationships")


class ArchitectureResponse(BaseModel):
    """Complete response returned by GET /architecture/{upload_id}."""

    project: ProjectInfo = Field(description="Project metadata")
    layers: list[str] = Field(description="Detected application layers")
    modules: list[ArchitectureModuleSchema] = Field(description="Detected architecture modules")
    relationships: list[ArchitectureRelationship] = Field(
        description="Detected relationships between modules"
    )
    statistics: ArchitectureStatistics = Field(description="Architecture analysis statistics")
