"""API route for AI architecture explanation on extracted repositories."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.ai.architecture_explainer import ArchitectureExplainer
from app.ai.llm_client import LLMError
from app.analyzers.architecture_builder import architecture_builder
from app.parsers.parser_engine import ParserEngine
from app.schemas.explain import ExplanationResponse, ProjectInfo
from app.services.dependency_graph import graph_builder
from app.services.framework_detector import detector_service
from app.services.scanner_service import scanner_service
from app.visualization.diagram_generator import diagram_generator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/explain", tags=["explain"])

EXTRACTED_DIR = Path("storage/extracted")


@router.post("/{upload_id}", response_model=ExplanationResponse, status_code=200)
async def explain_architecture(upload_id: str) -> ExplanationResponse:
    """Generate an AI-powered architecture explanation for an extracted project directory.

    Args:
        upload_id: The UUID of the uploaded and extracted project.

    Returns:
        An ExplanationResponse containing the AI-generated architecture explanation.

    Raises:
        HTTPException: If the project is not found, permission is denied, or LLM generation fails.
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

    try:
        explainer = ArchitectureExplainer()
        explanation = explainer.explain(
            scan_result,
            detection_result,
            graph_result,
            parsing_result,
            architecture_result,
            diagram_result,
        )
    except LLMError as e:
        logger.exception("LLM generation error for upload_id: %s", upload_id)
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {str(e)}")
    except Exception as e:
        logger.exception("Error generating explanation for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during explanation generation")

    return ExplanationResponse(
        project=ProjectInfo(
            name=explanation["project"]["name"],
            root_path=explanation["project"]["root_path"],
        ),
        overview=explanation["overview"],
        architecture_style=explanation.get("architecture_style", ""),
        technology_stack=explanation.get("technology_stack", []),
        major_modules=explanation.get("major_modules", []),
        data_flow=explanation.get("data_flow", ""),
        design_patterns=explanation.get("design_patterns", []),
        strengths=explanation.get("strengths", []),
        improvements=explanation.get("improvements", []),
        scalability=explanation.get("scalability", ""),
        maintainability=explanation.get("maintainability", ""),
    )
