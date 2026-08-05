"""API route for quality analysis on extracted repositories."""

import logging
import asyncio

from fastapi import APIRouter, HTTPException

from app.core.paths import resolve_repository_path
from app.quality.quality_analyzer import quality_analyzer
from app.schemas.quality import (
    QualityMetadata,
    QualityRecommendationsSchema,
    QualityResponse,
    QualityScoresSchema,
)
from storage.repository_store import repository_store
from app.indexing.index_manager import get_shared_index_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/repositories", tags=["quality"])
index_manager = get_shared_index_manager()


@router.post("/{repository_id}/quality", response_model=QualityResponse, status_code=200)
async def analyze_quality(repository_id: str) -> QualityResponse:
    """Analyze the code quality of an extracted project directory.

    Args:
        repository_id: The UUID of the uploaded and extracted project.

    Returns:
        A QualityResponse containing quality scores, recommendations, and metadata.
    """
    # Check if repository is indexed
    index = index_manager.get_index(repository_id)
    if not index or index.status.value != "READY":
        raise HTTPException(
            status_code=400,
            detail="Repository must be indexed before quality analysis",
        )

    project_path = repository_store.resolve_path(repository_id) or resolve_repository_path(repository_id)

    if project_path is None:
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
        result = await asyncio.to_thread(quality_analyzer.analyze, project_path)
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied when analyzing repository_id: {repository_id}",
        )
    except Exception:
        logger.exception("Error analyzing quality for repository_id: %s", repository_id)
        raise HTTPException(status_code=500, detail="Internal server error during quality analysis")

    return QualityResponse(
        project_name=result.project_name,
        scores=QualityScoresSchema(
            architecture=result.scores.architecture,
            security=result.scores.security,
            documentation=result.scores.documentation,
            maintainability=result.scores.maintainability,
            testing=result.scores.testing,
            complexity=result.scores.complexity,
            readability=result.scores.readability,
            scalability=result.scores.scalability,
        ),
        recommendations=QualityRecommendationsSchema(
            strengths=result.recommendations.strengths,
            weaknesses=result.recommendations.weaknesses,
            recommendations=result.recommendations.recommendations,
        ),
        metadata=QualityMetadata(
            total_files=result.metadata.get("total_files", 0),
            total_folders=result.metadata.get("total_folders", 0),
            languages=result.metadata.get("languages", {}),
            containerized=result.metadata.get("containerized", False),
            package_managers=result.metadata.get("package_managers", []),
            backend_frameworks=result.metadata.get("backend_frameworks", []),
            frontend_frameworks=result.metadata.get("frontend_frameworks", []),
        ),
    )
