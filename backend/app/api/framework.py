"""API route for framework detection on extracted repositories."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.schemas.framework import (
    FrameworkDetectionResponse,
    FrameworkMatchSchema,
    ProjectInfo,
)
from app.services.framework_detector import detector_service
from app.services.scanner_service import scanner_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/frameworks", tags=["frameworks"])

EXTRACTED_DIR = Path("storage/extracted")


@router.get("/{upload_id}", response_model=FrameworkDetectionResponse, status_code=200)
async def detect_frameworks(upload_id: str) -> FrameworkDetectionResponse:
    """Detect the technology stack of an extracted project directory.

    Args:
        upload_id: The UUID of the uploaded and extracted project.

    Returns:
        A FrameworkDetectionResponse containing project metadata and detected technologies.
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
        scan_result = scanner_service.scan(project_path)
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied when scanning upload_id: {upload_id}",
        )

    try:
        detection_result = detector_service.detect(project_path, scan_result)
    except Exception as e:
        logger.exception("Error detecting frameworks for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during detection")

    return FrameworkDetectionResponse(
        project=ProjectInfo(
            name=scan_result.project_name,
            root_path=scan_result.root_path,
        ),
        summary=scan_result.to_dict()["summary"],
        languages=scan_result.to_dict()["languages"],
        files=scan_result.to_dict()["files"],
        frameworks=[
            FrameworkMatchSchema(name=m.name, confidence=m.confidence)
            for m in detection_result.frameworks
        ],
        backend=[
            FrameworkMatchSchema(name=m.name, confidence=m.confidence)
            for m in detection_result.backend
        ],
        package_managers=detection_result.package_managers,
        containerized=detection_result.containerized,
        parser_targets=detection_result.parser_targets,
    )
