"""Schemas for Jira integration API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class JiraIssueResponse(BaseModel):
    """Jira issue information."""

    key: str = Field(..., description="Issue key")
    summary: str = Field(..., description="Issue summary")
    description: str | None = Field(None, description="Issue description")
    status: str = Field(..., description="Issue status")
    priority: str = Field(..., description="Issue priority")
    issue_type: str = Field(..., description="Issue type")
    assignee: str | None = Field(None, description="Assignee")
    reporter: str | None = Field(None, description="Reporter")
    created_at: str = Field(..., description="Creation date")
    updated_at: str = Field(..., description="Last update date")
    resolved_at: str | None = Field(None, description="Resolution date")
    labels: list[str] = Field(default_factory=list, description="Issue labels")
    components: list[str] = Field(default_factory=list, description="Issue components")
    epic_key: str | None = Field(None, description="Epic key")
    epic_name: str | None = Field(None, description="Epic name")
    story_points: int | None = Field(None, description="Story points")
    repository_links: list[str] = Field(default_factory=list, description="Repository links")
    project_key: str = Field(..., description="Project key")


class JiraProjectResponse(BaseModel):
    """Jira project information."""

    key: str = Field(..., description="Project key")
    name: str = Field(..., description="Project name")
    description: str | None = Field(None, description="Project description")
    project_type: str = Field(..., description="Project type")
    lead: str | None = Field(None, description="Project lead")
    url: str = Field(..., description="Project URL")
    created_at: str = Field(..., description="Creation date")
    updated_at: str = Field(..., description="Last update date")
    issue_count: int = Field(..., description="Total issue count")
    open_issues: int = Field(..., description="Open issue count")
    closed_issues: int = Field(..., description="Closed issue count")


class IssueSummary(BaseModel):
    """Issue summary statistics."""

    total: int = Field(..., description="Total issues")
    open: int = Field(..., description="Open issues")
    closed: int = Field(..., description="Closed issues")
    critical: int = Field(..., description="Critical priority issues")
    high: int = Field(..., description="High priority issues")
    bugs: int = Field(..., description="Bug issues")
    stories: int = Field(..., description="Story issues")
    tasks: int = Field(..., description="Task issues")


class RiskAssessment(BaseModel):
    """Engineering risk assessment."""

    risk_level: str = Field(..., description="Risk level")
    risk_score: int = Field(..., description="Risk score (0-100)")
    critical_issues: int = Field(..., description="Critical issue count")
    high_priority_issues: int = Field(..., description="High priority issue count")
    open_bugs: int = Field(..., description="Open bug count")
    stale_issues: int = Field(..., description="Stale issue count")


class RepositoryMapping(BaseModel):
    """Repository to Jira issue mapping."""

    repository: str = Field(..., description="Repository name")
    linked_issues: int = Field(..., description="Linked issue count")
    unlinked_issues: int = Field(..., description="Unlinked issue count")
    linked_issue_keys: list[str] = Field(default_factory=list, description="Linked issue keys")
    unlinked_issue_keys: list[str] = Field(default_factory=list, description="Unlinked issue keys")
    link_rate: float = Field(..., description="Link rate (0-1)")


class HealthCorrelation(BaseModel):
    """Repository health correlation."""

    repository_health: int = Field(..., description="Repository health score")
    open_issues: int = Field(..., description="Open issue count")
    open_bugs: int = Field(..., description="Open bug count")
    bug_ratio: float = Field(..., description="Bug ratio")
    health_impact: str = Field(..., description="Health impact level")
    recommendation: str = Field(..., description="Health recommendation")


class EpicSummary(BaseModel):
    """Epic summary statistics."""

    total_epics: int = Field(..., description="Total epic count")
    open_epics: int = Field(..., description="Open epic count")
    completed_epics: int = Field(..., description="Completed epic count")
    total_issues: int = Field(..., description="Total issues in epics")
    completed_issues: int = Field(..., description="Completed issues in epics")
    completion_rate: float = Field(..., description="Epic completion rate")


class ConnectJiraRequest(BaseModel):
    """Request to connect a Jira project."""

    project_key: str = Field(..., description="Jira project key")
    repository_id: str | None = Field(None, description="Optional repository ID")
    workspace_id: str | None = Field(None, description="Optional workspace ID")


class JiraResponse(BaseModel):
    """Complete Jira integration response."""

    project: JiraProjectResponse | None = Field(None, description="Project information")
    summary: IssueSummary | None = Field(None, description="Issue summary")
    risk: RiskAssessment | None = Field(None, description="Risk assessment")
    priority_distribution: dict[str, int] = Field(default_factory=dict, description="Priority distribution")
    status_distribution: dict[str, int] = Field(default_factory=dict, description="Status distribution")
    issue_type_distribution: dict[str, int] = Field(default_factory=dict, description="Issue type distribution")
    epic_summary: EpicSummary | None = Field(None, description="Epic summary")
    repository_mapping: RepositoryMapping | None = Field(None, description="Repository mapping")
    health_correlation: HealthCorrelation | None = Field(None, description="Health correlation")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")
    error: str | None = Field(None, description="Error message if failed")


class RepositoryIssuesResponse(BaseModel):
    """Repository issues response."""

    repository: str = Field(..., description="Repository name")
    repository_id: str = Field(..., description="Repository ID")
    project_key: str = Field(..., description="Project key")
    linked_issues: int = Field(..., description="Linked issue count")
    summary: IssueSummary | None = Field(None, description="Issue summary")
    risk: RiskAssessment | None = Field(None, description="Risk assessment")
    issues: list[JiraIssueResponse] = Field(default_factory=list, description="Linked issues")
    repository_mapping: RepositoryMapping | None = Field(None, description="Repository mapping")


class SearchIssuesResponse(BaseModel):
    """Search issues response."""

    project_key: str = Field(..., description="Project key")
    query: str = Field(..., description="Search query")
    total_results: int = Field(..., description="Total results")
    issues: list[JiraIssueResponse] = Field(default_factory=list, description="Matching issues")
