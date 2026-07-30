"""API route for quality analysis on extracted repositories."""

import logging

from fastapi import APIRouter, HTTPException

from app.core.paths import resolve_repository_path
from app.quality.quality_analyzer import quality_analyzer
from app.schemas.quality import (
    QualityMetadata,
    QualityRecommendationsSchema,
    QualityResponse,
    QualityScoresSchema,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quality", tags=["quality"])


@router.post("/{upload_id}", response_model=QualityResponse, status_code=200)
async def analyze_quality(upload_id: str) -> QualityResponse:
    """Analyze the code quality of an extracted project directory.

    Args:
        upload_id: The UUID of the uploaded and extracted project.

    Returns:
        A QualityResponse containing quality scores, recommendations, and metadata.
    """
    project_path = resolve_repository_path(upload_id)

    if project_path is None:
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
        result = quality_analyzer.analyze(project_path)
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied when analyzing upload_id: {upload_id}",
        )
    except Exception:
        logger.exception("Error analyzing quality for upload_id: %s", upload_id)
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
