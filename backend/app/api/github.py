"""GitHub integration API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.schemas.github import ConnectRepositoryRequest, GitHubResponse
from app.github.github_engine import GitHubEngine, github_engine

router = APIRouter(prefix="/github", tags=["github"])


@router.post("/connect", response_model=GitHubResponse)
async def connect_repository(
    request: ConnectRepositoryRequest,
    download: bool = Query(False, description="If true, return github_repository_summary.json file")
) -> GitHubResponse | FileResponse:
    """Connect a GitHub repository to CodeGraph.

    Args:
        request: Connect repository request.
        download: If true, return repository summary as a downloadable JSON file.

    Returns:
        GitHubResponse with repository information and sync status,
        or FileResponse if download=true.
    """
    result = github_engine.connect_repository(
        owner=request.owner,
        repo=request.repo,
        workspace_id=request.workspace_id,
    )

    response = GitHubResponse(
        repository=result.get("repository"),
        sync_status=result.get("sync_status"),
        workspace_id=result.get("workspace_id"),
        error=result.get("error"),
    )

    # Handle download mode
    if download and result.get("repository"):
        # Save repository summary to JSON file
        report_file = Path("github_repository_summary.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{request.owner}_{request.repo}_summary.json"
        )

    return response


@router.get("/repository/{owner}/{repo}", response_model=GitHubResponse)
async def get_repository(
    owner: str,
    repo: str,
    download: bool = Query(False, description="If true, return github_repository_summary.json file")
) -> GitHubResponse | FileResponse:
    """Get GitHub repository information.

    Args:
        owner: Repository owner.
        repo: Repository name.
        download: If true, return repository summary as a downloadable JSON file.

    Returns:
        GitHubResponse with repository information,
        or FileResponse if download=true.

    Raises:
        HTTPException: If repository not found.
    """
    repository = github_engine.get_repository(owner, repo)

    if not repository:
        raise HTTPException(status_code=404, detail=f"Repository not found: {owner}/{repo}")

    response = GitHubResponse(
        repository=repository,
        sync_status="SUCCESS",
        workspace_id=None,
    )

    # Handle download mode
    if download:
        # Save repository summary to JSON file
        report_file = Path("github_repository_summary.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{owner}_{repo}_summary.json"
        )

    return response


@router.post("/workspace/{workspace_id}")
async def associate_with_workspace(
    workspace_id: str,
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
) -> dict[str, str]:
    """Associate a GitHub repository with a workspace.

    Args:
        workspace_id: Workspace ID.
        owner: Repository owner.
        repo: Repository name.

    Returns:
        Success message.

    Raises:
        HTTPException: If workspace or repository not found.
    """
    try:
        result = github_engine.associate_with_workspace(
            owner=owner,
            repo=repo,
            workspace_id=workspace_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return result
