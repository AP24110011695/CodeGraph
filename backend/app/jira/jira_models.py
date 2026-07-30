"""Jira models for Jira integration engine.

Data models for Jira projects, issues, and related entities.
"""

from dataclasses import dataclass
from typing import Any
from datetime import datetime


@dataclass
class JiraIssue:
    """Represents a Jira issue."""

    key: str
    summary: str
    description: str | None
    status: str
    priority: str
    issue_type: str  # Bug, Story, Task, Epic, etc.
    assignee: str | None
    reporter: str | None
    created_at: str
    updated_at: str
    resolved_at: str | None
    labels: list[str]
    components: list[str]
    epic_key: str | None
    epic_name: str | None
    story_points: int | None
    repository_links: list[str]  # Linked repository URLs/branches
    project_key: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "key": self.key,
            "summary": self.summary,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "issue_type": self.issue_type,
            "assignee": self.assignee,
            "reporter": self.reporter,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "resolved_at": self.resolved_at,
            "labels": self.labels,
            "components": self.components,
            "epic_key": self.epic_key,
            "epic_name": self.epic_name,
            "story_points": self.story_points,
            "repository_links": self.repository_links,
            "project_key": self.project_key,
        }


@dataclass
class JiraEpic:
    """Represents a Jira epic."""

    key: str
    name: str
    summary: str
    status: str
    issue_count: int
    completed_issues: int
    project_key: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "key": self.key,
            "name": self.name,
            "summary": self.summary,
            "status": self.status,
            "issue_count": self.issue_count,
            "completed_issues": self.completed_issues,
            "project_key": self.project_key,
        }


@dataclass
class JiraProject:
    """Represents a Jira project."""

    key: str
    name: str
    description: str | None
    project_type: str  # Software, Business, etc.
    lead: str | None
    url: str
    created_at: str
    updated_at: str
    issue_count: int
    open_issues: int
    closed_issues: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "project_type": self.project_type,
            "lead": self.lead,
            "url": self.url,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "issue_count": self.issue_count,
            "open_issues": self.open_issues,
            "closed_issues": self.closed_issues,
        }
