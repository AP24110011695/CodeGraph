from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.api.search import _project_path, search_service
from app.indexing.index_manager import IndexManager
from app.knowledge_graph.graph_builder import KnowledgeGraphBuilder
from app.schemas.semantic import SemanticSearchRequest, SemanticSearchResponse
from app.semantic.hybrid_retriever import HybridRetriever
from app.semantic.semantic_engine import SemanticEngine
from app.semantic.semantic_search import SemanticSearch
from app.search.search_service import SearchServiceError

router = APIRouter(prefix="/semantic", tags=["semantic"])


def _graph_provider(repository_id: str, project_path: Path):
    return KnowledgeGraphBuilder(index_manager=IndexManager()).build(project_path, repository_id)


semantic_engine = SemanticEngine(SemanticSearch(HybridRetriever(search_service)), _graph_provider)


@router.post("/{upload_id}", response_model=SemanticSearchResponse)
async def semantic_search(upload_id: str, request: SemanticSearchRequest) -> dict:
    try:
        return semantic_engine.search(upload_id, request.query, _project_path(upload_id), request.mode, request.limit)
    except SearchServiceError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
