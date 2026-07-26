"""API route for code smell detection on extracted repositories."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.analyzers.architecture_builder import architecture_builder
from app.parsers.parser_engine import ParserEngine
from app.schemas.smells import CodeSmellSchema, DebtEstimateSchema, SmellSummary, SmellsResponse
from app.services.dependency_graph import graph_builder
from app.services.framework_detector import detector_service
from app.services.scanner_service import scanner_service
from app.smells.smell_detector import smell_detector

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/smells", tags=["smells"])

EXTRACTED_DIR = Path("storage/extracted")


@router.post("/{upload_id}", response_model=SmellsResponse, status_code=200)
async def detect_smells(upload_id: str) -> SmellsResponse:
    """Detect code smells and estimate technical debt for an extracted project directory.

    Args:
        upload_id: The UUID of the uploaded and extracted project.

    Returns:
        A SmellsResponse containing detected smells and technical debt estimate.
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
        # Scan the repository
        scan_result = scanner_service.scan(project_path)
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied when scanning upload_id: {upload_id}",
        )

    try:
        # Detect frameworks
        detection_result = detector_service.detect(project_path, scan_result)
    except Exception as e:
        logger.exception("Error detecting frameworks for upload_id: %s", upload_id)
        detection_result = None

    try:
        # Build dependency graph
        graph_result = graph_builder.build(project_path, scan_result)
    except Exception as e:
        logger.exception("Error building dependency graph for upload_id: %s", upload_id)
        graph_result = None

    try:
        # Parse the project (optional)
        parsing_result = ParserEngine.parse_project(project_path, scan_result)
    except Exception as e:
        logger.warning("Failed to parse project for upload_id: %s", upload_id)
        parsing_result = None

    try:
        # Build architecture (optional)
        if detection_result and graph_result:
            architecture_result = architecture_builder.build(
                scan_result, detection_result, graph_result, parsing_result
            )
        else:
            architecture_result = None
    except Exception as e:
        logger.warning("Failed to build architecture for upload_id: %s", upload_id)
        architecture_result = None

    try:
        # Detect smells
        result = smell_detector.detect(
            project_path,
            scan_result=scan_result,
            parsing_result=parsing_result,
            graph_result=graph_result,
            architecture_result=architecture_result,
        )
    except Exception as e:
        logger.exception("Error detecting smells for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during smell detection")

    return SmellsResponse(
        technical_debt=result.debt_estimate.level,
        estimated_effort=result.debt_estimate.estimated_effort,
        summary=SmellSummary(
            total_smells=result.summary["total_smells"],
            critical=result.summary["critical"],
            major=result.summary["major"],
            minor=result.summary["minor"],
        ),
        smells=[
            CodeSmellSchema(
                type=smell.type,
                severity=smell.severity,
                file=smell.file,
                line=smell.line,
                description=smell.description,
            )
            for smell in result.smells
        ],
    )
