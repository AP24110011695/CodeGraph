"""Pydantic schemas for the framework detection API responses."""

from pydantic import BaseModel, Field

from app.schemas.scanner import FileEntry, ScanSummary


class ProjectInfo(BaseModel):
    """Basic project information."""

    name: str = Field(description="Name of the top-level project directory")
    root_path: str = Field(description="Absolute path to the scanned directory")


class FrameworkMatchSchema(BaseModel):
    """Schema for a detected framework or technology."""

    name: str = Field(description="Name of the detected framework")
    confidence: int = Field(description="Confidence score of the detection (0-100)")


class FrameworkDetectionResponse(BaseModel):
    """Complete response returned by GET /frameworks/{upload_id}."""

    project: ProjectInfo
    summary: ScanSummary
    languages: dict[str, int] = Field(
        description="Language name → file count, sorted by count descending"
    )
    files: list[FileEntry] = Field(description="Per-file metadata entries")
    frameworks: list[FrameworkMatchSchema] = Field(description="Detected frontend frameworks")
    backend: list[FrameworkMatchSchema] = Field(description="Detected backend frameworks")
    package_managers: list[str] = Field(description="Detected package managers")
    containerized: bool = Field(description="Whether Docker containerization is detected")
    parser_targets: list[str] = Field(description="Tree-sitter parser targets based on languages")
