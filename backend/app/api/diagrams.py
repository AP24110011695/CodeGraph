"""API route for diagram generation on extracted repositories."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.analyzers.architecture_builder import architecture_builder
from app.parsers.parser_engine import ParserEngine
from app.schemas.diagrams import (
    DiagramResponse,
    DiagramStatistics,
    DiagramSyntax,
    ProjectInfo,
)
from app.services.dependency_graph import graph_builder
from app.services.framework_detector import detector_service
from app.services.scanner_service import scanner_service
from app.visualization.diagram_generator import diagram_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/diagrams", tags=["diagrams"])

EXTRACTED_DIR = Path("storage/extracted")


@router.get("/{upload_id}", response_model=DiagramResponse, status_code=200)
async def generate_diagrams(upload_id: str) -> DiagramResponse:
    """Generate architecture diagrams for an extracted project directory.

    Args:
        upload_id: The UUID of the uploaded and extracted project.

    Returns:
        A DiagramResponse containing Mermaid and PlantUML syntax for all diagram types.
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

    try:
        graph_result = graph_builder.build(project_path, scan_result)
    except Exception as e:
        logger.exception("Error building dependency graph for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during graph building")

    try:
        parsing_result = ParserEngine.parse_project(project_path, scan_result)
    except Exception as e:
        logger.exception("Error parsing project for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during parsing")

    try:
        architecture_result = architecture_builder.build(
            scan_result, detection_result, graph_result, parsing_result
        )
    except Exception as e:
        logger.exception("Error building architecture for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during architecture analysis")

    try:
        diagram_result = diagram_generator.build(architecture_result, graph_result)
    except Exception as e:
        logger.exception("Error generating diagrams for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during diagram generation")

    return DiagramResponse(
        project=ProjectInfo(
            name=diagram_result.project.get("name", ""),
            root_path=diagram_result.project.get("root_path", ""),
        ),
        mermaid=DiagramSyntax(
            system=diagram_result.mermaid.get("system", ""),
            modules=diagram_result.mermaid.get("modules", ""),
            components=diagram_result.mermaid.get("components", ""),
            dependencies=diagram_result.mermaid.get("dependencies", ""),
            layers=diagram_result.mermaid.get("layers", ""),
        ),
        plantuml=DiagramSyntax(
            system=diagram_result.plantuml.get("system", ""),
            modules=diagram_result.plantuml.get("modules", ""),
            components=diagram_result.plantuml.get("components", ""),
            dependencies=diagram_result.plantuml.get("dependencies", ""),
            layers=diagram_result.plantuml.get("layers", ""),
        ),
        statistics=DiagramStatistics(
            nodes=diagram_result.statistics.get("nodes", 0),
            edges=diagram_result.statistics.get("edges", 0),
        ),
    )
