"""Pydantic schemas for the quality analysis API responses."""

from pydantic import BaseModel, Field


class QualityScoresSchema(BaseModel):
    """Individual quality scores."""

    architecture: int = Field(ge=0, le=100, description="Architecture quality score (0-100)")
    security: int = Field(ge=0, le=100, description="Security quality score (0-100)")
    documentation: int = Field(ge=0, le=100, description="Documentation quality score (0-100)")
    maintainability: int = Field(ge=0, le=100, description="Maintainability quality score (0-100)")
    testing: int = Field(ge=0, le=100, description="Testing quality score (0-100)")
    complexity: int = Field(ge=0, le=100, description="Complexity quality score (0-100)")
    readability: int = Field(ge=0, le=100, description="Readability quality score (0-100)")
    scalability: int = Field(ge=0, le=100, description="Scalability quality score (0-100)")


class QualityRecommendationsSchema(BaseModel):
    """Complete recommendations output."""

    strengths: list[str] = Field(description="List of detected strengths")
    weaknesses: list[str] = Field(description="List of detected weaknesses")
    recommendations: list[str] = Field(description="List of actionable recommendations")


class QualityMetadata(BaseModel):
    """Metadata about the analyzed project."""

    total_files: int = Field(ge=0, description="Total number of files")
    total_folders: int = Field(ge=0, description="Total number of folders")
    languages: dict[str, int] = Field(description="Detected languages and file counts")
    containerized: bool = Field(description="Whether the project is containerized")
    package_managers: list[str] = Field(description="Detected package managers")
    backend_frameworks: list[str] = Field(description="Detected backend frameworks")
    frontend_frameworks: list[str] = Field(description="Detected frontend frameworks")


class QualityResponse(BaseModel):
    """Complete response returned by POST /quality/{upload_id}."""

    project_name: str = Field(description="Name of the analyzed project")
    scores: QualityScoresSchema = Field(description="Quality scores for each metric")
    recommendations: QualityRecommendationsSchema = Field(
        description="Strengths, weaknesses, and recommendations"
    )
    metadata: QualityMetadata = Field(description="Project metadata")
