"""Pydantic schemas for the repository scanner API responses."""

from datetime import datetime
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
    total_size_bytes: int = Field(ge=0, description="Total size of all files in bytes")


class ScanResponse(BaseModel):
    """Complete scan response returned by POST /scan/{upload_id}."""

    project_name: str = Field(description="Name of the top-level project directory")
    root_path: str = Field(description="Absolute path to the scanned directory")
    summary: ScanSummary
    languages: dict[str, int] = Field(
        description="Language name → file count, sorted by count descending"
    )
    files: list[FileEntry] = Field(description="Per-file metadata entries")


class ScanResultResponse(BaseModel):
    """Response format matching Phase 9 requirements."""

    repository_id: str = Field(description="Repository UUID")
    status: str = Field(description="Scan status")
    file_count: int = Field(ge=0, description="Total number of files")
    directory_count: int = Field(ge=0, description="Total number of directories")
    languages: dict[str, int] = Field(description="Language distribution")
    total_size_bytes: int = Field(ge=0, description="Total size in bytes")
    scanned_at: datetime = Field(description="Timestamp when scan was completed")
