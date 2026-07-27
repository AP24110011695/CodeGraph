"""Knowledge graph API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.indexing.index_manager import IndexManager, IndexNotFoundError
from app.knowledge_graph.graph_builder import KnowledgeGraphBuilder, knowledge_graph_builder
from app.knowledge_graph.graph_serializer import graph_serializer
from app.schemas.knowledge_graph import KnowledgeGraphResponse

router = APIRouter(prefix="/knowledge-graph", tags=["knowledge-graph"])


@router.post("/{upload_id}", response_model=KnowledgeGraphResponse)
async def generate_knowledge_graph(
    upload_id: str,
    download: bool = Query(False, description="If true, return knowledge_graph.json file")
) -> KnowledgeGraphResponse | FileResponse:
    """Generate comprehensive knowledge graph for a repository.

    Args:
        upload_id: The upload ID of the indexed repository.
        download: If true, return graph as a downloadable JSON file.

    Returns:
        KnowledgeGraphResponse with comprehensive repository knowledge graph,
        or FileResponse if download=true.

    Raises:
        HTTPException: If repository is not found or not indexed.
    """
    # Initialize index manager
    index_manager = IndexManager()

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
    project_path = Path("uploads") / upload_id
    if not project_path.exists():
        raise HTTPException(status_code=404, detail=f"Project path not found: {project_path}")

    # Generate knowledge graph
    graph_builder_with_index = KnowledgeGraphBuilder(index_manager=index_manager)
    graph = graph_builder_with_index.build(project_path, upload_id)

    # Convert to response format
    response = KnowledgeGraphResponse(
        nodes=graph.nodes,
        edges=graph.edges,
        statistics=graph.statistics,
    )

    # Handle download mode
    if download:
        # Save graph to JSON file
        graph_file = project_path / "knowledge_graph.json"
        with open(graph_file, "w", encoding="utf-8") as f:
            json.dump(graph_serializer.to_dict(graph), f, indent=2, default=str)

        return FileResponse(
            graph_file,
            media_type="application/json",
            filename=f"{upload_id}_knowledge_graph.json"
        )

    return response
