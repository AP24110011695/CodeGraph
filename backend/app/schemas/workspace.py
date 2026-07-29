"""Schemas for workspace API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class RepositoryInfo(BaseModel):
    """Information about a repository in the workspace."""

    repository: str = Field(..., description="Repository name")
    upload_id: str = Field(..., description="Upload ID")
    languages: list[str] = Field(default_factory=list, description="Languages")
    frameworks: list[str] = Field(default_factory=list, description="Frameworks")
    architecture_score: int = Field(ge=0, le=100, description="Architecture score")
    health_score: int = Field(ge=0, le=100, description="Health score")
    status: str = Field(..., description="Repository status")


class CreateWorkspaceRequest(BaseModel):
    """Request to create a workspace."""

    name: str = Field(..., description="Workspace name")


class AddRepositoryRequest(BaseModel):
    """Request to add a repository to a workspace."""

    repository_name: str = Field(..., description="Repository name")
    upload_id: str = Field(..., description="Upload ID")


class WorkspaceResponse(BaseModel):
    """Complete workspace response."""

    workspace_id: str = Field(..., description="Workspace ID")
    workspace_name: str = Field(..., description="Workspace name")
    repository_count: int = Field(ge=0, description="Number of repositories")
    repositories: list[RepositoryInfo] = Field(default_factory=list, description="Repositories")
    workspace_score: int = Field(ge=0, le=100, description="Workspace score")
    combined_statistics: dict[str, Any] = Field(default_factory=dict, description="Combined statistics")
    architecture_summary: dict[str, Any] = Field(default_factory=dict, description="Architecture summary")
    technology_summary: dict[str, Any] = Field(default_factory=dict, description="Technology summary")
