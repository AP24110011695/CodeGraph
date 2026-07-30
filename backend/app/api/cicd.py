"""CI/CD integration API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.schemas.cicd import CICDResponse, ConnectCICDRequest
from app.cicd.cicd_engine import CICDEngine, cicd_engine

router = APIRouter(prefix="/cicd", tags=["cicd"])


@router.post("/connect", response_model=CICDResponse)
async def connect_repository(
    request: ConnectCICDRequest,
    download: bool = Query(False, description="If true, return cicd_summary.json file")
) -> CICDResponse | FileResponse:
    """Connect a repository and analyze its CI/CD pipeline.

    Args:
        request: Connect repository request.
        download: If true, return CI/CD summary as a downloadable JSON file.

    Returns:
        CICDResponse with pipeline analysis results,
        or FileResponse if download=true.
    """
    result = cicd_engine.connect_repository(
        owner=request.owner,
        repo=request.repo,
        workspace_id=request.workspace_id,
    )

    response = CICDResponse(
        provider=result.get("provider"),
        pipeline_health=result.get("pipeline_health", 0),
        summary=result.get("summary"),
        workflow_inventory=result.get("workflow_inventory", []),
        job_statistics=result.get("job_statistics"),
        execution_summary=result.get("execution_summary"),
        readiness=result.get("readiness"),
        recommendations=result.get("recommendations", []),
        repository=result.get("repository"),
        error=result.get("error"),
    )

    # Handle download mode
    if download and result.get("provider") != "none":
        # Save CI/CD summary to JSON file
        report_file = Path("cicd_summary.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{request.owner}_{request.repo}_cicd_summary.json"
        )

    return response


@router.get("/{repository_id}", response_model=CICDResponse)
async def get_repository_cicd(
    repository_id: str,
    download: bool = Query(False, description="If true, return cicd_summary.json file")
) -> CICDResponse | FileResponse:
    """Get CI/CD information for a repository by ID.

    Args:
        repository_id: Repository ID (upload_id).
        download: If true, return CI/CD summary as a downloadable JSON file.

    Returns:
        CICDResponse with pipeline analysis results,
        or FileResponse if download=true.

    Raises:
        HTTPException: If repository not found.
    """
    cicd_data = cicd_engine.get_repository_cicd(repository_id)

    if not cicd_data:
        raise HTTPException(status_code=404, detail=f"Repository not found: {repository_id}")

    response = CICDResponse(
        provider=cicd_data.get("provider"),
        pipeline_health=cicd_data.get("pipeline_health", 0),
        summary=cicd_data.get("summary"),
        workflow_inventory=cicd_data.get("workflow_inventory", []),
        job_statistics=cicd_data.get("job_statistics"),
        execution_summary=cicd_data.get("execution_summary"),
        readiness=cicd_data.get("readiness"),
        recommendations=cicd_data.get("recommendations", []),
        repository=cicd_data.get("repository"),
        error=cicd_data.get("error"),
    )

    # Handle download mode
    if download:
        # Save CI/CD summary to JSON file
        report_file = Path("cicd_summary.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{repository_id}_cicd_summary.json"
        )

    return response


@router.get("/repository/{owner}/{repo}", response_model=CICDResponse)
async def get_repository_cicd_by_owner_repo(
    owner: str,
    repo: str,
    download: bool = Query(False, description="If true, return cicd_summary.json file")
) -> CICDResponse | FileResponse:
    """Get CI/CD information for a repository by owner and repo name.

    Args:
        owner: Repository owner.
        repo: Repository name.
        download: If true, return CI/CD summary as a downloadable JSON file.

    Returns:
        CICDResponse with pipeline analysis results,
        or FileResponse if download=true.

    Raises:
        HTTPException: If repository not found.
    """
    repository_id = f"{owner}/{repo}"
    cicd_data = cicd_engine.get_repository_cicd(repository_id)

    if not cicd_data:
        raise HTTPException(status_code=404, detail=f"Repository not found: {repository_id}")

    response = CICDResponse(
        provider=cicd_data.get("provider"),
        pipeline_health=cicd_data.get("pipeline_health", 0),
        summary=cicd_data.get("summary"),
        workflow_inventory=cicd_data.get("workflow_inventory", []),
        job_statistics=cicd_data.get("job_statistics"),
        execution_summary=cicd_data.get("execution_summary"),
        readiness=cicd_data.get("readiness"),
        recommendations=cicd_data.get("recommendations", []),
        repository=cicd_data.get("repository"),
        error=cicd_data.get("error"),
    )

    # Handle download mode
    if download:
        # Save CI/CD summary to JSON file
        report_file = Path("cicd_summary.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{owner}_{repo}_cicd_summary.json"
        )

    return response
