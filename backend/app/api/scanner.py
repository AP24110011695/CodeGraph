"""API route for scanning extracted repositories."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.schemas.scanner import ScanResponse
from app.services.scanner_service import scanner_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scan", tags=["scan"])

EXTRACTED_DIR = Path("storage/extracted")


@router.post("/{upload_id}", response_model=ScanResponse, status_code=200)
async def scan_repository(upload_id: str) -> ScanResponse:
    """Scan an extracted project directory and return its metadata inventory.

    Args:
        upload_id: The UUID of the uploaded and extracted project.

    Returns:
        A ScanResponse containing project summary, language breakdown, and file list.
    """
    project_path = EXTRACTED_DIR / upload_id

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
        result = scanner_service.scan(project_path)
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied when scanning upload_id: {upload_id}",
        )

    return ScanResponse(**result.to_dict())
