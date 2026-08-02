"""Architecture recommendation API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.architecture_recommendation.recommendation_engine import RecommendationEngine, recommendation_engine
from app.indexing.index_manager import IndexManager, IndexNotFoundError, get_shared_index_manager
from app.schemas.architecture_recommendation import ArchitectureRecommendationResponse

router = APIRouter(prefix="/architecture-recommendation", tags=["architecture-recommendation"])


@router.post("/{upload_id}", response_model=ArchitectureRecommendationResponse)
async def analyze_architecture_recommendation(
    upload_id: str,
    download: bool = Query(False, description="If true, return architecture_recommendations.json file")
) -> ArchitectureRecommendationResponse | FileResponse:
    """Analyze architecture recommendations for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        download: If true, return architecture recommendations as a downloadable JSON file.

    Returns:
        ArchitectureRecommendationResponse with comprehensive architecture recommendations,
        or FileResponse if download=true.

    Raises:
        HTTPException: If repository is not found or not indexed.
    """
    # Initialize index manager
    index_manager = get_shared_index_manager()

    # Get the index
    index = index_manager.get_index(upload_id)
    if not index:
        raise HTTPException(status_code=404, detail=f"Repository not found: {upload_id}")

    if index.status.value != "READY":
        raise HTTPException(
            status_code=400,
            detail=f"Repository is not indexed. Current status: {index.status.value}"
        )

    # Determine project path from uploads directory
    from app.core.paths import get_project_path
    project_path = get_project_path(upload_id)
    if not project_path.exists():
        raise HTTPException(status_code=404, detail=f"Project path not found: {project_path}")

    # Analyze architecture recommendations
    recommendation_engine_with_index = RecommendationEngine(index_manager=index_manager)
    result = recommendation_engine_with_index.analyze(project_path, upload_id)

    # Convert to response format
    response = ArchitectureRecommendationResponse(
        project_name=result.project_name,
        overall_architecture_score=result.overall_architecture_score,
        summary=result.summary,
        recommendations=result.recommendations,
    )

    # Handle download mode
    if download:
        # Save architecture recommendations to JSON file
        recommendation_file = project_path / "architecture_recommendations.json"
        with open(recommendation_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            recommendation_file,
            media_type="application/json",
            filename=f"{upload_id}_architecture_recommendations.json"
        )

    return response
