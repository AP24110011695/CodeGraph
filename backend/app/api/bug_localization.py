"""Bug localization API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.bug_localization.bug_localization_engine import BugLocalizationEngine, BugLocalizationRequest, bug_localization_engine
from app.indexing.index_manager import IndexManager, IndexNotFoundError
from app.schemas.bug_localization import BugLocalizationResponse

router = APIRouter(prefix="/bug-localization", tags=["bug-localization"])


@router.post("/{upload_id}", response_model=BugLocalizationResponse)
async def localize_bug(
    upload_id: str,
    request: BugLocalizationRequest,
    download: bool = Query(False, description="If true, return bug_localization.json file")
) -> BugLocalizationResponse | FileResponse:
    """Localize bug for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        request: BugLocalizationRequest with bug details.
        download: If true, return bug localization as a downloadable JSON file.

    Returns:
        BugLocalizationResponse with comprehensive bug localization predictions,
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

    # Localize bug
    bug_localization_engine_with_index = BugLocalizationEngine(index_manager=index_manager)
    result = bug_localization_engine_with_index.localize(project_path, request, upload_id)

    # Convert to response format
    response = BugLocalizationResponse(
        likely_root_cause=result.likely_root_cause,
        confidence=result.confidence,
        predictions=result.predictions,
        related_modules=result.related_modules,
        suggested_investigation_order=result.suggested_investigation_order,
    )

    # Handle download mode
    if download:
        # Save bug localization to JSON file
        localization_file = project_path / "bug_localization.json"
        with open(localization_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            localization_file,
            media_type="application/json",
            filename=f"{upload_id}_bug_localization.json"
        )

    return response
