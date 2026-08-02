"""API route for architecture analysis on extracted repositories."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.analyzers.architecture_builder import architecture_builder
from app.parsers.parser_engine import ParserEngine
from app.schemas.architecture import (
    ArchitectureModuleSchema,
    ArchitectureRelationship,
    ArchitectureResponse,
    ArchitectureStatistics,
    ArchitectureComponent,
    ProjectInfo,
)
from app.services.dependency_graph import graph_builder
from app.services.framework_detector import detector_service
from app.services.scanner_service import scanner_service
from storage.repository_store import repository_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/architecture", tags=["architecture"])

# Filesystem fallback / test monkeypatch compatibility.
EXTRACTED_DIR = Path(settings.STORAGE_DIR) / "extracted"


@router.get("/{upload_id}", response_model=ArchitectureResponse, status_code=200)
async def analyze_architecture(upload_id: str) -> ArchitectureResponse:
    """Analyze the software architecture of an extracted project directory.

    Args:
        upload_id: The UUID of the uploaded and extracted project.

    Returns:
        An ArchitectureResponse containing detected layers, modules, components, and relationships.
    """
    project_path = repository_store.resolve_path(upload_id) or (EXTRACTED_DIR / upload_id)

    if project_path is None or not project_path.exists():
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

    return ArchitectureResponse(
        project=ProjectInfo(
            name=architecture_result.project.get("name", ""),
            root_path=architecture_result.project.get("root_path", ""),
        ),
        layers=architecture_result.layers,
        modules=[
            ArchitectureModuleSchema(
                name=m.name,
                type=m.type,
                files=m.files,
                components=[
                    ArchitectureComponent(
                        name=c.name,
                        type=c.type,
                        file_path=c.file_path,
                        language=c.language,
                    )
                    for c in m.components
                ],
                layer=m.layer,
            )
            for m in architecture_result.modules
        ],
        relationships=[
            ArchitectureRelationship(
                source=r.source, target=r.target, type=r.type
            )
            for r in architecture_result.relationships
        ],
        statistics=ArchitectureStatistics(
            modules=architecture_result.statistics.get("modules", 0),
            components=architecture_result.statistics.get("components", 0),
            relationships=architecture_result.statistics.get("relationships", 0),
        ),
    )
    try:
        repository_store.save_analysis(
            upload_id,
            "architecture",
            {
                "layers": response.layers,
                "statistics": response.statistics.model_dump(),
                "module_count": len(response.modules),
            },
        )
    except Exception:
        pass
    return response
