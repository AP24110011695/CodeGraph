"""Knowledge graph API endpoint for CodeGraph."""

import json

from fastapi import APIRouter, Query
from fastapi.responses import FileResponse

from app.indexing.repository_access import require_ready_index
from app.knowledge_graph.graph_builder import KnowledgeGraphBuilder
from app.knowledge_graph.graph_serializer import graph_serializer
from app.schemas.knowledge_graph import KnowledgeGraphResponse
from storage.repository_store import repository_store

router = APIRouter(prefix="/knowledge-graph", tags=["knowledge-graph"])


@router.post("/{upload_id}", response_model=KnowledgeGraphResponse)
async def generate_knowledge_graph(
    upload_id: str,
    download: bool = Query(False, description="If true, return knowledge_graph.json file"),
) -> KnowledgeGraphResponse | FileResponse:
    """Generate comprehensive knowledge graph for a repository."""
    index_manager, _index, project_path = require_ready_index(upload_id)

    graph_builder_with_index = KnowledgeGraphBuilder(index_manager=index_manager)
    graph = graph_builder_with_index.build(project_path, upload_id)

    response = KnowledgeGraphResponse.model_validate(graph_serializer.to_dict(graph))

    try:
        repository_store.save_analysis(
            upload_id,
            "knowledge_graph",
            {
                "node_count": len(graph.nodes),
                "edge_count": len(graph.edges),
                "statistics": graph.statistics,
            },
        )
    except Exception:
        pass

    if download:
        graph_file = project_path / "knowledge_graph.json"
        with open(graph_file, "w", encoding="utf-8") as f:
            json.dump(graph_serializer.to_dict(graph), f, indent=2, default=str)

        return FileResponse(
            graph_file,
            media_type="application/json",
            filename=f"{upload_id}_knowledge_graph.json",
        )

    return response
