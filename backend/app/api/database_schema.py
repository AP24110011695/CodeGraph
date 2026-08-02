"""Database schema visualization API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.indexing.index_manager import IndexManager, IndexNotFoundError, get_shared_index_manager
from app.schemas.database_schema import SchemaResponse
from app.database_schema.schema_engine import SchemaEngine, schema_engine

router = APIRouter(prefix="/database-schema", tags=["database-schema"])


@router.post("/{upload_id}", response_model=SchemaResponse)
async def visualize_schema(
    upload_id: str,
    download: bool = Query(False, description="If true, return database_schema_report.json file")
) -> SchemaResponse | FileResponse:
    """Visualize database schema for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        download: If true, return schema visualization as a downloadable JSON file.

    Returns:
        SchemaResponse with database schema visualization,
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

    # Visualize schema
    schema_engine_with_index = SchemaEngine()
    result = schema_engine_with_index.visualize_schema(project_path, upload_id)

    # Convert to response format
    response = SchemaResponse(
        schema_score=result.schema_score,
        summary=result.summary,
        entities=result.entities,
        relationships=result.relationships,
        mermaid=result.mermaid,
        recommendations=result.recommendations,
    )

    # Handle download mode
    if download:
        # Save schema visualization to JSON file
        report_file = project_path / "database_schema_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{upload_id}_database_schema_report.json"
        )

    return response
