"""Repository comparison API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.schemas.repository_comparison import (
    RepositoryComparisonRequest,
    RepositoryComparisonResponse,
)
from app.repository_comparison.comparison_engine import ComparisonEngine, comparison_engine

router = APIRouter(prefix="/repository-comparison", tags=["repository-comparison"])


@router.post("", response_model=RepositoryComparisonResponse)
async def compare_repositories(
    request: RepositoryComparisonRequest,
    download: bool = Query(False, description="If true, return repository_comparison_report.json file")
) -> RepositoryComparisonResponse | FileResponse:
    """Compare multiple repositories.

    Args:
        request: Repository comparison request.
        download: If true, return comparison report as a downloadable JSON file.

    Returns:
        RepositoryComparisonResponse with comparison results,
        or FileResponse if download=true.

    Raises:
        HTTPException: If comparison fails.
    """
    result = comparison_engine.compare_repositories(request.repositories)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    response = RepositoryComparisonResponse(
        repository_ids=result.get("repository_ids", []),
        similarity_score=result.get("similarity_score", 0),
        summary=result.get("summary"),
        comparisons=result.get("comparisons", []),
        recommendations=result.get("recommendations", []),
        strengths=result.get("strengths", []),
        weaknesses=result.get("weaknesses", []),
        error=result.get("error"),
    )

    # Handle download mode
    if download:
        # Save comparison report to JSON file
        report_file = Path("repository_comparison_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename="repository_comparison_report.json"
        )

    return response
