"""GitHub models for GitHub integration engine.

Data models for GitHub repository and commit information.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class GitHubCommit:
    """GitHub commit information."""

    sha: str
    message: str
    author: str
    date: str
    url: str


@dataclass
class GitHubRepository:
    """GitHub repository information."""

    name: str
    owner: str
    description: str | None
    default_branch: str
    language: str | None
    languages: dict[str, int]
    stars: int
    forks: int
    topics: list[str]
    open_issues: int
    watchers: int
    size: int
    created_at: str
    updated_at: str
    pushed_at: str
    url: str
    clone_url: str
    last_commit: GitHubCommit | None
