"""Schemas for GitHub integration API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class GitHubCommit(BaseModel):
    """GitHub commit information."""

    sha: str = Field(..., description="Commit SHA")
    message: str = Field(..., description="Commit message")
    author: str = Field(..., description="Commit author")
    date: str = Field(..., description="Commit date")
    url: str = Field(..., description="Commit URL")


class GitHubRepository(BaseModel):
    """GitHub repository information."""

    name: str = Field(..., description="Repository name")
    owner: str = Field(..., description="Repository owner")
    description: str | None = Field(None, description="Repository description")
    default_branch: str = Field(..., description="Default branch")
    language: str | None = Field(None, description="Primary language")
    languages: dict[str, int] = Field(default_factory=dict, description="Language breakdown")
    stars: int = Field(ge=0, description="Star count")
    forks: int = Field(ge=0, description="Fork count")
    topics: list[str] = Field(default_factory=list, description="Repository topics")
    open_issues: int = Field(ge=0, description="Open issues count")
    watchers: int = Field(ge=0, description="Watcher count")
    size: int = Field(ge=0, description="Repository size")
    created_at: str = Field(..., description="Creation date")
    updated_at: str = Field(..., description="Last update date")
    pushed_at: str = Field(..., description="Last push date")
    url: str = Field(..., description="Repository URL")
    clone_url: str = Field(..., description="Clone URL")
    last_commit: GitHubCommit | None = Field(None, description="Last commit")


class ConnectRepositoryRequest(BaseModel):
    """Request to connect a GitHub repository."""

    owner: str = Field(..., description="Repository owner")
    repo: str = Field(..., description="Repository name")
    workspace_id: str | None = Field(None, description="Optional workspace ID")


class GitHubResponse(BaseModel):
    """Complete GitHub integration response."""

    repository: GitHubRepository | None = Field(None, description="Repository information")
    sync_status: str = Field(..., description="Synchronization status")
    workspace_id: str | None = Field(None, description="Associated workspace ID")
    error: str | None = Field(None, description="Error message if failed")
