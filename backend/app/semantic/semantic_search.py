"""Natural-language semantic search use case."""

from pathlib import Path
from typing import Literal

from app.semantic.hybrid_retriever import HybridRetriever


class SemanticSearch:
    def __init__(self, retriever: HybridRetriever) -> None:
        self._retriever = retriever

    def search(self, repository_id: str, query: str, project_path: Path, mode: Literal["semantic", "hybrid"], limit: int) -> list[dict]:
        return self._retriever.retrieve(repository_id, query, project_path, mode, limit)
