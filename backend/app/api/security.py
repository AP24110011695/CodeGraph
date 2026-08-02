"""API route for security analysis on extracted repositories."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from app.core.paths import get_extracted_dir
from app.schemas.security import SecurityResponse, SecurityIssueSchema, SecuritySummarySchema
from app.security.security_analyzer import security_analyzer
from app.services.scanner_service import scanner_service
from storage.repository_store import repository_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/security", tags=["security"])

# Kept for test monkeypatching and filesystem fallback.
EXTRACTED_DIR = get_extracted_dir()


@router.post("/{upload_id}", response_model=SecurityResponse, status_code=200)
async def analyze_security(upload_id: str) -> SecurityResponse:
    """Analyze security vulnerabilities for an extracted project directory.

    Args:
        upload_id: The UUID of the uploaded and extracted project.

    Returns:
        A SecurityResponse containing detected security issues and summary.

    Raises:
        HTTPException: If the project is not found or an error occurs.
    """
    project_path = repository_store.resolve_path(upload_id) or (EXTRACTED_DIR / upload_id)

    if not project_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Extracted project not found for upload_id: {upload_id}",
        )

    if not project_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"Path is not a directory for upload_id: {upload_id}",
        )

    try:
        scan_result = scanner_service.scan(project_path)
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied when scanning upload_id: {upload_id}",
        )

    try:
        analysis_result = security_analyzer.analyze(project_path, scan_result)
    except FileNotFoundError as e:
        logger.exception("Project not found for upload_id: %s", upload_id)
        raise HTTPException(status_code=404, detail=str(e))
    except NotADirectoryError as e:
        logger.exception("Path is not a directory for upload_id: %s", upload_id)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error analyzing security for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during security analysis")

    # Return JSON response
    return SecurityResponse(
        summary=SecuritySummarySchema(**analysis_result.summary),
        issues=[SecurityIssueSchema(**issue) for issue in analysis_result.issues],
        total_issues=analysis_result.total_issues,
    )
