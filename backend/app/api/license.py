"""License compliance API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.indexing.index_manager import IndexManager, IndexNotFoundError
from app.license.license_engine import LicenseEngine, license_engine
from app.schemas.license import LicenseResponse

router = APIRouter(prefix="/license", tags=["license"])


@router.post("/{upload_id}", response_model=LicenseResponse)
async def analyze_license(
    upload_id: str,
    download: bool = Query(False, description="If true, return license_report.json file")
) -> LicenseResponse | FileResponse:
    """Analyze license compliance for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        download: If true, return license report as a downloadable JSON file.

    Returns:
        LicenseResponse with comprehensive license compliance findings,
        or FileResponse if download=true.

    Raises:
        HTTPException: If repository is not found or not indexed.
    """
    # Initialize index manager
    index_manager = IndexManager()

    # Get the index
    index = index_manager.get_index(upload_id)
    if not index:
        raise HTTPException(status_code=404, detail=f"Repository not found: {upload_id}")

    if index.status.value != "READY":
        raise HTTPException(
            status_code=400,
            detail=f"Repository is not indexed. Current status: {index.status.value}"
        )

    # Determine project path from uploads directory
    project_path = Path("uploads") / upload_id
    if not project_path.exists():
        raise HTTPException(status_code=404, detail=f"Project path not found: {project_path}")

    # Analyze license compliance
    license_engine_with_index = LicenseEngine(index_manager=index_manager)
    result = license_engine_with_index.analyze(project_path, upload_id)

    # Convert to response format
    response = LicenseResponse(
        project_name=result.project_name,
        repository_license=result.repository_license,
        compliance_status=result.compliance_status,
        summary=result.summary,
        findings=result.findings,
        dependency_licenses=result.dependency_licenses,
        recommendations=result.recommendations,
    )

    # Handle download mode
    if download:
        # Save license report to JSON file
        license_file = project_path / "license_report.json"
        with open(license_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            license_file,
            media_type="application/json",
            filename=f"{upload_id}_license_report.json"
        )

    return response
