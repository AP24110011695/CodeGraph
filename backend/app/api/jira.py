"""Jira integration API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.schemas.jira import (
    ConnectJiraRequest,
    JiraResponse,
    RepositoryIssuesResponse,
    SearchIssuesResponse,
)
from app.jira.jira_engine import JiraEngine, jira_engine

router = APIRouter(prefix="/jira", tags=["jira"])


@router.post("/connect", response_model=JiraResponse)
async def connect_project(
    request: ConnectJiraRequest,
    download: bool = Query(False, description="If true, return jira_project_summary.json file")
) -> JiraResponse | FileResponse:
    """Connect a Jira project and analyze its issues.

    Args:
        request: Connect project request.
        download: If true, return project summary as a downloadable JSON file.

    Returns:
        JiraResponse with project analysis results,
        or FileResponse if download=true.
    """
    result = jira_engine.connect_project(
        project_key=request.project_key,
        repository_id=request.repository_id,
        workspace_id=request.workspace_id,
    )

    response = JiraResponse(
        project=result.get("project"),
        summary=result.get("summary"),
        risk=result.get("risk"),
        priority_distribution=result.get("priority_distribution", {}),
        status_distribution=result.get("status_distribution", {}),
        issue_type_distribution=result.get("issue_type_distribution", {}),
        epic_summary=result.get("epic_summary"),
        repository_mapping=result.get("repository_mapping"),
        health_correlation=result.get("health_correlation"),
        recommendations=result.get("recommendations", []),
        error=result.get("error"),
    )

    # Handle download mode
    if download and result.get("project"):
        # Save project summary to JSON file
        report_file = Path("jira_project_summary.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{request.project_key}_summary.json"
        )

    return response


@router.get("/project/{project_key}", response_model=JiraResponse)
async def get_project(
    project_key: str,
    download: bool = Query(False, description="If true, return jira_project_summary.json file")
) -> JiraResponse | FileResponse:
    """Get Jira project information.

    Args:
        project_key: Jira project key.
        download: If true, return project summary as a downloadable JSON file.

    Returns:
        JiraResponse with project information,
        or FileResponse if download=true.

    Raises:
        HTTPException: If project not found.
    """
    project_data = jira_engine.get_project(project_key)

    if not project_data:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_key}")

    response = JiraResponse(
        project=project_data.get("project"),
        summary=project_data.get("summary"),
        risk=project_data.get("risk"),
        priority_distribution={},
        status_distribution={},
        issue_type_distribution={},
        epic_summary=None,
        repository_mapping=None,
        health_correlation=None,
        recommendations=[],
        error=None,
    )

    # Handle download mode
    if download:
        # Save project summary to JSON file
        report_file = Path("jira_project_summary.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{project_key}_summary.json"
        )

    return response


@router.get("/issues/{repository_id}", response_model=RepositoryIssuesResponse)
async def get_repository_issues(
    repository_id: str,
    download: bool = Query(False, description="If true, return jira_issues_summary.json file")
) -> RepositoryIssuesResponse | FileResponse:
    """Get Jira issues for a repository.

    Args:
        repository_id: Repository ID.
        download: If true, return issues summary as a downloadable JSON file.

    Returns:
        RepositoryIssuesResponse with repository issues,
        or FileResponse if download=true.

    Raises:
        HTTPException: If repository not found.
    """
    issues_data = jira_engine.get_repository_issues(repository_id)

    if not issues_data:
        raise HTTPException(status_code=404, detail=f"Repository not found: {repository_id}")

    response = RepositoryIssuesResponse(
        repository=issues_data.get("repository"),
        repository_id=issues_data.get("repository_id"),
        project_key=issues_data.get("project_key"),
        linked_issues=issues_data.get("linked_issues"),
        summary=issues_data.get("summary"),
        risk=issues_data.get("risk"),
        issues=issues_data.get("issues", []),
        repository_mapping=issues_data.get("repository_mapping"),
    )

    # Handle download mode
    if download:
        # Save issues summary to JSON file
        report_file = Path("jira_issues_summary.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{repository_id}_jira_issues.json"
        )

    return response


@router.get("/search/{project_key}", response_model=SearchIssuesResponse)
async def search_issues(
    project_key: str,
    query: str = Query(..., description="Search query"),
) -> SearchIssuesResponse:
    """Search issues in Jira project.

    Args:
        project_key: Jira project key.
        query: Search query.

    Returns:
        SearchIssuesResponse with matching issues.
    """
    search_results = jira_engine.search_issues(project_key, query)

    return SearchIssuesResponse(
        project_key=search_results.get("project_key"),
        query=search_results.get("query"),
        total_results=search_results.get("total_results"),
        issues=search_results.get("issues", []),
    )
