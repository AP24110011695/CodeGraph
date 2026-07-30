from fastapi import APIRouter, HTTPException
from typing import Optional
from app.schemas.repository_memory import RepositoryMemory, MemorySummary
from app.repository_memory.memory_engine import memory_engine

router = APIRouter(prefix="/repository-memory", tags=["repository-memory"])

@router.post("/build/{repository_id}", response_model=RepositoryMemory)
async def build_repository_memory(repository_id: str):
    """Builds memory for a repository after indexing."""
    try:
        memory = memory_engine.build_memory(repository_id)
        return memory
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{repository_id}", response_model=RepositoryMemory)
async def get_repository_memory(repository_id: str):
    """Retrieves the full structured memory for a repository."""
    memory = memory_engine.get_memory(repository_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Repository memory not found")
    return memory

@router.get("/{repository_id}/summary", response_model=MemorySummary)
async def get_repository_memory_summary(repository_id: str):
    """Retrieves a lightweight summary of the repository memory."""
    summary = memory_engine.get_memory_summary(repository_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Repository memory summary not found")
    return summary
