"""Dashboard API endpoint for CodeGraph."""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.schemas.dashboard import DashboardResponse
from app.dashboard.dashboard_engine import DashboardEngine, dashboard_engine
from app.indexing.index_manager import get_shared_index_manager
from storage.repository_store import repository_store

router = APIRouter(prefix="/repositories", tags=["dashboard"])
index_manager = get_shared_index_manager()


@router.post("/{workspace_id}", response_model=DashboardResponse)
async def generate_dashboard(
    workspace_id: str,
    download: bool = Query(False, description="If true, return executive_dashboard.json file")
) -> DashboardResponse | FileResponse:
    """Generate executive dashboard for a workspace.

    Args:
        workspace_id: Workspace ID.
        download: If true, return dashboard as a downloadable JSON file.

    Returns:
        DashboardResponse with dashboard data,
        or FileResponse if download=true.

    Raises:
        HTTPException: If workspace not found.
    """
    result = dashboard_engine.generate_dashboard(workspace_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    response = DashboardResponse(
        workspace_id=result.get("workspace_id"),
        workspace_name=result.get("workspace_name"),
        executive_score=result.get("executive_score", 0),
        workspace_health=result.get("workspace_health", 0),
        overall_health=result.get("overall_health"),
        summary=result.get("summary"),
        key_insights=result.get("key_insights", []),
        recommendations=result.get("recommendations", []),
        score_cards=result.get("score_cards", []),
        widgets=result.get("widgets"),
        error=result.get("error"),
    )

    # Handle download mode
    if download:
        # Save dashboard to JSON file
        report_file = Path("executive_dashboard.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, default=str)

        return FileResponse(
            report_file,
            media_type="application/json",
            filename=f"{workspace_id}_executive_dashboard.json"
        )

    return response


@router.get("/{repository_id}/overview")
async def get_repository_overview(repository_id: str):
    """Get repository overview with key metrics."""
    # Check if repository is indexed
    index = index_manager.get_index(repository_id)
    if not index or index.status.value != "READY":
        raise HTTPException(
            status_code=400,
            detail="Repository must be indexed to retrieve overview",
        )

    repository = repository_store.get_repository(repository_id)
    if not repository:
        raise HTTPException(
            status_code=404,
            detail=f"Repository not found: {repository_id}",
        )

    # Compute health score from repository metrics
    total_files = repository.get("total_files", 0)
    languages = repository.get("languages", {})
    frameworks = repository.get("frameworks", [])
    
    # Simple health score based on completeness
    health_score = 50  # Base score
    if total_files > 0:
        health_score += 10
    if len(languages) > 0:
        health_score += 10
    if len(frameworks) > 0:
        health_score += 10
    if repository.get("indexed_at"):
        health_score += 20
    
    # Compute risk level (placeholder for now)
    risk_level = "medium"

    return {
        "repository_id": repository_id,
        "name": repository.get("name", repository.get("repository_name", "")),
        "file_count": total_files,
        "language_count": len(languages),
        "primary_language": max(languages.items(), key=lambda x: x[1])[0] if languages else "Unknown",
        "detected_frameworks": frameworks,
        "health_score": min(health_score, 100),
        "risk_level": risk_level,
        "total_size_bytes": repository.get("zip_size_bytes", 0),
        "indexed_at": repository.get("indexed_at"),
    }


@router.get("/{repository_id}/architecture")
async def get_repository_architecture(repository_id: str):
    """Get repository architecture information."""
    # Check if repository is indexed
    index = index_manager.get_index(repository_id)
    if not index or index.status.value != "READY":
        raise HTTPException(
            status_code=400,
            detail="Repository must be indexed to retrieve architecture",
        )

    repository = repository_store.get_repository(repository_id)
    if not repository:
        raise HTTPException(
            status_code=404,
            detail=f"Repository not found: {repository_id}",
        )

    # Return repository-based architecture info
    return {
        "repository_id": repository_id,
        "frameworks": repository.get("frameworks", []),
        "languages": repository.get("languages", {}),
        "total_files": repository.get("total_files", 0),
        "architecture_type": "monolithic",  # Placeholder - would need full architecture analysis
    }


@router.get("/{repository_id}/dependencies")
async def get_repository_dependencies(repository_id: str):
    """Get repository dependencies."""
    # Check if repository is indexed
    index = index_manager.get_index(repository_id)
    if not index or index.status.value != "READY":
        raise HTTPException(
            status_code=400,
            detail="Repository must be indexed to retrieve dependencies",
        )

    repository = repository_store.get_repository(repository_id)
    if not repository:
        raise HTTPException(
            status_code=404,
            detail=f"Repository not found: {repository_id}",
        )

    # Build actual dependency graph
    from app.services.dependency_graph import graph_builder
    from app.services.scanner_service import scanner_service
    
    project_path = repository_store.resolve_path(repository_id)
    if not project_path:
        raise HTTPException(
            status_code=404,
            detail=f"Extracted project not found: {repository_id}",
        )

    try:
        scan_result = scanner_service.scan(project_path)
        graph_result = graph_builder.build(project_path, scan_result)
        
        # Convert to API response format
        nodes = [
            {
                "id": node.get("id"),
                "path": node.get("path"),
                "language": node.get("language")
            }
            for node in graph_result.nodes
        ]
        
        edges = [
            {
                "from": edge.from_node,
                "to": edge.to_node,
                "type": edge.edge_type
            }
            for edge in graph_result.edges
        ]
        
        return {
            "repository_id": repository_id,
            "nodes": nodes,
            "edges": edges,
            "isolated_files": graph_result.isolated_files,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building dependency graph: {str(e)}")


@router.get("/{repository_id}/risks")
async def get_repository_risks(repository_id: str):
    """Get repository risk assessment."""
    # Check if repository is indexed
    index = index_manager.get_index(repository_id)
    if not index or index.status.value != "READY":
        raise HTTPException(
            status_code=400,
            detail="Repository must be indexed to retrieve risk assessment",
        )

    repository = repository_store.get_repository(repository_id)
    if not repository:
        raise HTTPException(
            status_code=404,
            detail=f"Repository not found: {repository_id}",
        )

    # Return repository-based risk info
    return {
        "repository_id": repository_id,
        "risk_level": "medium",  # Placeholder - would need security analysis
        "risk_factors": [],  # Placeholder - would need security analysis
        "overall_risk_score": 50,  # Placeholder - would need security analysis
    }


@router.get("/{repository_id}/health")
async def get_repository_health(repository_id: str):
    """Get repository health status."""
    # Check if repository is indexed
    index = index_manager.get_index(repository_id)
    if not index or index.status.value != "READY":
        raise HTTPException(
            status_code=400,
            detail="Repository must be indexed to retrieve health status",
        )

    repository = repository_store.get_repository(repository_id)
    if not repository:
        raise HTTPException(
            status_code=404,
            detail=f"Repository not found: {repository_id}",
        )

    # Compute health score from repository metrics
    total_files = repository.get("total_files", 0)
    languages = repository.get("languages", {})
    frameworks = repository.get("frameworks", [])
    
    # Simple health score based on completeness
    health_score = 50  # Base score
    if total_files > 0:
        health_score += 10
    if len(languages) > 0:
        health_score += 10
    if len(frameworks) > 0:
        health_score += 10
    if repository.get("indexed_at"):
        health_score += 20
    
    # Determine overall health
    health_score = min(health_score, 100)
    if health_score >= 80:
        overall_health = "excellent"
    elif health_score >= 60:
        overall_health = "good"
    elif health_score >= 40:
        overall_health = "fair"
    else:
        overall_health = "poor"

    return {
        "repository_id": repository_id,
        "status": index.status.value,
        "health_score": health_score,
        "overall_health": overall_health,
        "last_indexed": repository.get("indexed_at"),
    }
