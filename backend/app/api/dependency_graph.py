"""API route for building internal dependency graphs."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.schemas.dependency_graph import (
    DependencyGraphResponse,
    GraphEdge,
    GraphNode,
    GraphStatistics,
)
from app.schemas.framework import ProjectInfo
from app.services.dependency_graph import graph_builder
from app.services.scanner_service import scanner_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dependency-graph", tags=["dependency-graph"])

EXTRACTED_DIR = Path("storage/extracted")


@router.get("/{upload_id}", response_model=DependencyGraphResponse, status_code=200)
async def build_dependency_graph(upload_id: str) -> DependencyGraphResponse:
    """Build a deterministic internal dependency graph for an extracted project.

    Args:
        upload_id: The UUID of the uploaded and extracted project.

    Returns:
        A DependencyGraphResponse containing nodes, edges, and statistics.
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
        graph_result = graph_builder.build(project_path, scan_result)
    except Exception as e:
        logger.exception("Error building dependency graph for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error during graph build")

    return DependencyGraphResponse(
        project=ProjectInfo(
            name=scan_result.project_name,
            root_path=scan_result.root_path,
        ),
        summary=scan_result.to_dict()["summary"],
        nodes=[GraphNode(**n) for n in graph_result.nodes],
        edges=[
            GraphEdge(**{"from": e.from_node, "to": e.to_node, "type": e.edge_type})
            for e in graph_result.edges
        ],
        statistics=GraphStatistics(
            nodes=len(graph_result.nodes),
            edges=len(graph_result.edges),
            isolated_files=graph_result.isolated_files,
        ),
    )
