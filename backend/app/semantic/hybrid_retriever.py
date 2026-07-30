"""Adapter around the existing repository search intelligence."""

from pathlib import Path
from typing import Any, Literal

from app.search.search_service import SearchService


class HybridRetriever:
    def __init__(self, search_service: SearchService) -> None:
        self._search_service = search_service

    def retrieve(self, repository_id: str, query: str, project_path: Path, mode: Literal["semantic", "hybrid"], limit: int) -> list[dict[str, Any]]:
        return self._search_service.search(
            upload_id=repository_id,
            query=query,
            mode=mode,
            project_path=project_path,
            limit=limit,
        )["results"]
