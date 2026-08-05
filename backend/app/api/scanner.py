"""API route for scanning extracted repositories."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.schemas.scanner import ScanResponse, ScanResultResponse
from app.services.scanner_service import scanner_service
from storage.repository_store import RepositoryStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/repositories", tags=["scan"])

from app.core.paths import get_extracted_dir
EXTRACTED_DIR = get_extracted_dir()

repository_store = RepositoryStore()


@router.post("/{repository_id}/scan", response_model=ScanResultResponse, status_code=200)
async def scan_repository(repository_id: str) -> ScanResultResponse:
    """Scan an extracted project directory and return its metadata inventory.

    Args:
        repository_id: The UUID of the uploaded and extracted project.

    Returns:
        A ScanResultResponse containing project summary and language breakdown.
    """
    project_path = EXTRACTED_DIR / repository_id

    if not project_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Extracted project not found for repository_id: {repository_id}",
        )

    if not project_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"Path is not a directory for repository_id: {repository_id}",
        )

    try:
        result = scanner_service.scan(project_path)
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied when scanning repository_id: {repository_id}",
        )

    # Persist scan result to database
    scan_data = {
        "repository_id": repository_id,
        "status": "scanned",
        "file_count": result.total_files,
        "directory_count": result.total_folders,
        "languages": result.languages,
        "total_size_bytes": result.total_size_bytes,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "files": [f.__dict__ for f in result.files],
    }
    
    repository_store.save_scan_result(repository_id, json.dumps(scan_data))

    return ScanResultResponse(
        repository_id=repository_id,
        status="scanned",
        file_count=result.total_files,
        directory_count=result.total_folders,
        languages=result.languages,
        total_size_bytes=result.total_size_bytes,
        scanned_at=datetime.now(timezone.utc),
    )


@router.get("/{repository_id}/scan", response_model=ScanResultResponse, status_code=200)
async def get_scan_result(repository_id: str) -> ScanResultResponse:
    """Retrieve the scan result for a repository.

    Args:
        repository_id: The UUID of the repository.

    Returns:
        A ScanResultResponse containing the previously saved scan result.
    """
    scan_result = repository_store.load_scan_result(repository_id)
    
    if not scan_result:
        raise HTTPException(
            status_code=404,
            detail=f"Scan result not found for repository_id: {repository_id}",
        )
    
    scan_data = json.loads(scan_result)
    
    return ScanResultResponse(
        repository_id=scan_data["repository_id"],
        status=scan_data["status"],
        file_count=scan_data["file_count"],
        directory_count=scan_data["directory_count"],
        languages=scan_data["languages"],
        total_size_bytes=scan_data["total_size_bytes"],
        scanned_at=datetime.fromisoformat(scan_data["scanned_at"]),
    )
