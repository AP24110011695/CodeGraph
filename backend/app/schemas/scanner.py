"""Pydantic schemas for the repository scanner API responses."""

from pydantic import BaseModel, Field


class FileEntry(BaseModel):
    """Schema for a single file in the scan results."""

    name: str = Field(description="Filename including extension")
    path: str = Field(description="Relative path from project root (POSIX-style)")
    extension: str = Field(description="Lowercase file extension including the dot")
    language: str = Field(description="Detected programming language or 'Unknown'")
    size: int = Field(ge=0, description="File size in bytes")
    folder: str = Field(description="Parent folder relative path (POSIX-style)")


class ScanSummary(BaseModel):
    """High-level counts for the scanned project."""

    files: int = Field(ge=0, description="Total number of files found")
    folders: int = Field(ge=0, description="Total number of folders found")


class ScanResponse(BaseModel):
    """Complete scan response returned by POST /scan/{upload_id}."""

    project_name: str = Field(description="Name of the top-level project directory")
    root_path: str = Field(description="Absolute path to the scanned directory")
    summary: ScanSummary
    languages: dict[str, int] = Field(
        description="Language name → file count, sorted by count descending"
    )
    files: list[FileEntry] = Field(description="Per-file metadata entries")
