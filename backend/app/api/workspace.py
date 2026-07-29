"""Workspace API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.schemas.workspace import CreateWorkspaceRequest, AddRepositoryRequest, WorkspaceResponse
from app.workspace.workspace_engine import WorkspaceEngine, workspace_engine

router = APIRouter(prefix="/workspace", tags=["workspace"])


@router.post("", response_model=WorkspaceResponse)
async def create_workspace(request: CreateWorkspaceRequest) -> WorkspaceResponse:
    """Create a new workspace.

    Args:
        request: Create workspace request.

    Returns:
        WorkspaceResponse with workspace information.
    """
    result = workspace_engine.create_workspace(request.name)

    return WorkspaceResponse(
        workspace_id=result.workspace_id,
        workspace_name=result.workspace_name,
        repository_count=result.repository_count,
        repositories=result.repositories,
        workspace_score=result.workspace_score,
        combined_statistics=result.combined_statistics,
        architecture_summary=result.architecture_summary,
        technology_summary=result.technology_summary,
    )


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    download: bool = Query(False, description="If true, return workspace_summary.json file")
) -> WorkspaceResponse | FileResponse:
    """Get a workspace.

    Args:
        workspace_id: ID of the workspace.
        download: If true, return workspace summary as a downloadable JSON file.

    Returns:
        WorkspaceResponse with workspace information,
        or FileResponse if download=true.

    Raises:
        HTTPException: If workspace not found.
    """
    try:
        result = workspace_engine.get_workspace(workspace_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    response = WorkspaceResponse(
        workspace_id=result.workspace_id,
        workspace_name=result.workspace_name,
        repository_count=result.repository_count,
        repositories=result.repositories,
        workspace_score=result.workspace_score,
        combined_statistics=result.combined_statistics,
        architecture_summary=result.architecture_summary,
        technology_summary=result.technology_summary,
    )

    # Handle download mode
    if download:
        # Save workspace summary to JSON file
        report_file = Path("workspace_summary.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{workspace_id}_workspace_summary.json"
        )

    return response


@router.post("/{workspace_id}/repositories")
async def add_repository(workspace_id: str, request: AddRepositoryRequest) -> dict[str, str]:
    """Add a repository to a workspace.

    Args:
        workspace_id: ID of the workspace.
        request: Add repository request.

    Returns:
        Success message.

    Raises:
        HTTPException: If workspace or repository not found.
    """
    try:
        success = workspace_engine.add_repository(
            workspace_id=workspace_id,
            repository_name=request.repository_name,
            upload_id=request.upload_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not success:
        raise HTTPException(status_code=400, detail="Failed to add repository to workspace")

    return {"message": "Repository added to workspace successfully"}


@router.delete("/{workspace_id}/repositories/{upload_id}")
async def remove_repository(workspace_id: str, upload_id: str) -> dict[str, str]:
    """Remove a repository from a workspace.

    Args:
        workspace_id: ID of the workspace.
        upload_id: Upload ID of the repository.

    Returns:
        Success message.

    Raises:
        HTTPException: If workspace not found.
    """
    try:
        success = workspace_engine.remove_repository(
            workspace_id=workspace_id,
            upload_id=upload_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not success:
        raise HTTPException(status_code=404, detail="Repository not found in workspace")

    return {"message": "Repository removed from workspace successfully"}
