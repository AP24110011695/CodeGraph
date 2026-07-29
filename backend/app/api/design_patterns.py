"""Design pattern detection API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.design_patterns.pattern_detection_engine import PatternDetectionEngine, pattern_detection_engine
from app.indexing.index_manager import IndexManager, IndexNotFoundError
from app.schemas.design_patterns import PatternDetectionResponse

router = APIRouter(prefix="/design-patterns", tags=["design-patterns"])


@router.post("/{upload_id}", response_model=PatternDetectionResponse)
async def detect_patterns(
    upload_id: str,
    download: bool = Query(False, description="If true, return design_patterns_report.json file")
) -> PatternDetectionResponse | FileResponse:
    """Detect design patterns for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        download: If true, return pattern detection as a downloadable JSON file.

    Returns:
        PatternDetectionResponse with detected patterns,
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

    # Detect patterns
    pattern_detection_engine_with_index = PatternDetectionEngine(index_manager=index_manager)
    result = pattern_detection_engine_with_index.detect(project_path, upload_id)

    # Convert to response format
    response = PatternDetectionResponse(
        patterns=result.patterns,
        anti_patterns=result.anti_patterns,
        architecture_summary=result.architecture_summary,
        improvement_suggestions=result.improvement_suggestions,
    )

    # Handle download mode
    if download:
        # Save pattern detection to JSON file
        report_file = project_path / "design_patterns_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{upload_id}_design_patterns_report.json"
        )

    return response
