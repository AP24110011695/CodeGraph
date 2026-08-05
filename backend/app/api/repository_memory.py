from fastapi import APIRouter, HTTPException
from typing import Optional
from app.schemas.repository_memory import RepositoryMemory, MemorySummary
from app.repository_memory.memory_engine import memory_engine
from app.indexing.index_manager import get_shared_index_manager

router = APIRouter(prefix="/repositories", tags=["repository-memory"])
index_manager = get_shared_index_manager()

@router.post("/{repository_id}/memory", response_model=RepositoryMemory)
async def build_repository_memory(repository_id: str):
    """Builds memory for a repository after indexing."""
    # Check if repository is indexed
    index = index_manager.get_index(repository_id)
    if not index or index.status.value != "READY":
        raise HTTPException(status_code=400, detail="Repository must be indexed before building memory")
    
    try:
        memory = memory_engine.build_memory(repository_id)
        return memory
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{repository_id}/memory", response_model=RepositoryMemory)
async def get_repository_memory(repository_id: str):
    """Retrieves the full structured memory for a repository."""
    # Check if repository is indexed
    index = index_manager.get_index(repository_id)
    if not index or index.status.value != "READY":
        raise HTTPException(status_code=400, detail="Repository must be indexed to retrieve memory")
    
    memory = memory_engine.get_memory(repository_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Repository memory not found")
    return memory

@router.get("/{repository_id}/memory/summary", response_model=MemorySummary)
async def get_repository_memory_summary(repository_id: str):
    """Retrieves a lightweight summary of the repository memory."""
    # Check if repository is indexed
    index = index_manager.get_index(repository_id)
    if not index or index.status.value != "READY":
        raise HTTPException(status_code=400, detail="Repository must be indexed to retrieve memory summary")
    
    summary = memory_engine.get_memory_summary(repository_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Repository memory summary not found")
    return summary

@router.get("/{repository_id}/memory/context")
async def get_repository_memory_context(repository_id: str):
    """Retrieves contextual information about the repository for AI assistance."""
    # Check if repository is indexed
    index = index_manager.get_index(repository_id)
    if not index or index.status.value != "READY":
        raise HTTPException(status_code=400, detail="Repository must be indexed to retrieve memory context")
    
    memory = memory_engine.get_memory(repository_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Repository memory not found")
    
    return {
        "repository_id": repository_id,
        "repository_summary": memory.repository_summary,
        "architecture_summary": memory.architecture_summary,
        "framework_summary": memory.framework_summary,
        "service_relationships": memory.service_relationships,
        "entry_points": memory.entry_points,
        "key_modules": list(memory.module_summaries.keys()),
        "api_endpoints": [
            {
                "endpoint_path": endpoint.endpoint_path,
                "http_method": endpoint.http_method,
                "handler": endpoint.handler,
                "purpose": endpoint.purpose
            }
            for endpoint in memory.api_endpoints
        ],
        "module_count": len(memory.module_summaries),
        "file_count": len(memory.file_summaries),
        "symbol_count": len(memory.symbol_summaries),
    }
