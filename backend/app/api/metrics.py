"""Metrics API endpoint for CodeGraph."""

import json
from dataclasses import asdict, is_dataclass

from fastapi import APIRouter, Query
from fastapi.responses import FileResponse

from app.indexing.repository_access import require_ready_index
from app.indexing.index_manager import get_shared_index_manager
from app.metrics.metrics_engine import MetricsEngine
from app.schemas.metrics import MetricsResponse
from storage.repository_store import repository_store

router = APIRouter(prefix="/repositories", tags=["metrics"])
index_manager = get_shared_index_manager()


def _to_mapping(value: object) -> dict:
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()  # type: ignore[no-any-return]
    return dict(value)  # type: ignore[arg-type]


@router.post("/{repository_id}/metrics", response_model=MetricsResponse)
async def generate_metrics(
    repository_id: str,
    download: bool = Query(False, description="If true, return metrics.json file"),
) -> MetricsResponse | FileResponse:
    """Generate comprehensive repository metrics."""
    index_manager, _index, project_path = require_ready_index(repository_id)

    metrics_engine_with_index = MetricsEngine(index_manager=index_manager)
    result = metrics_engine_with_index.generate(project_path, repository_id)

    response = MetricsResponse.model_validate(
        {
            "project_name": result.project_name,
            "summary": _to_mapping(result.summary),
            "statistics": _to_mapping(result.statistics),
            "quality": _to_mapping(result.quality),
            "security": _to_mapping(result.security),
            "architecture": _to_mapping(result.architecture),
            "smells": _to_mapping(result.smells),
            "refactoring": _to_mapping(result.refactoring),
        }
    )

    try:
        repository_store.save_analysis(repository_id, "metrics", response.model_dump())
    except Exception:
        # Persistence of analysis artifacts must not break the response.
        pass

    if download:
        metrics_file = project_path / "metrics.json"
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            metrics_file,
            media_type="application/json",
            filename=f"{repository_id}_metrics.json",
        )

    return response
