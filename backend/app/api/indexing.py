"""Thin HTTP API for managing repository indexes."""

from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, status

from app.indexing.index_manager import (
    IndexAlreadyExistsError,
    IndexNotFoundError,
    get_shared_index_manager,
)
from app.indexing.indexing_models import IndexStatus, RepositoryIndex
from app.indexing.indexing_pipeline import IndexingPipelineError
from app.schemas.indexing import IndexResponse
from storage.repository_store import repository_store

router = APIRouter(prefix="/repositories", tags=["indexing"])
from app.core.paths import get_extracted_dir
EXTRACTED_DIR = get_extracted_dir()
# Shared process-wide manager (SQLite-backed metadata).
index_manager = get_shared_index_manager()


def _project_path(repository_id: str) -> Path:
    path = repository_store.resolve_path(repository_id) or (EXTRACTED_DIR / repository_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Extracted project not found for repository_id: {repository_id}")
    if not path.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory for repository_id: {repository_id}")
    return path


@router.post("/{repository_id}/index", response_model=IndexResponse, status_code=status.HTTP_201_CREATED)
async def create_index(repository_id: str, force: bool = Query(False)) -> IndexResponse:
    project_path = _project_path(repository_id)
    try:
        return IndexResponse.from_index(index_manager.create_index(project_path, repository_id, force=force))
    except IndexAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except IndexingPipelineError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{repository_id}/index", response_model=IndexResponse)
async def get_index(repository_id: str) -> IndexResponse:
    _project_path(repository_id)
    index = index_manager.get_index(repository_id) or RepositoryIndex(
        upload_id=repository_id, status=IndexStatus.NOT_INDEXED
    )
    return IndexResponse.from_index(index)


@router.get("/{repository_id}/index/status")
async def get_index_status(repository_id: str):
    """Get the current indexing status and progress for a repository."""
    _project_path(repository_id)
    
    # Try to get real-time progress from repository state machine
    try:
        from app.repository_state.state_machine import RepositoryStateMachine
        sm = RepositoryStateMachine(repository_id)
        state = sm.current_state
        
        # Map repository state to indexing status
        from app.schemas.repository_state import RepositoryStateEnum
        
        status_map = {
            RepositoryStateEnum.UPLOADED: "NOT_INDEXED",
            RepositoryStateEnum.SCAN: "INDEXING",
            RepositoryStateEnum.PARSING: "INDEXING",
            RepositoryStateEnum.INDEXING: "INDEXING",
            RepositoryStateEnum.EMBEDDING: "INDEXING",
            RepositoryStateEnum.ANALYZING: "INDEXING",
            RepositoryStateEnum.READY: "READY",
            RepositoryStateEnum.FAILED: "FAILED",
        }
        
        progress_map = {
            RepositoryStateEnum.UPLOADED: 0,
            RepositoryStateEnum.SCAN: 15,
            RepositoryStateEnum.PARSING: 35,
            RepositoryStateEnum.INDEXING: 55,
            RepositoryStateEnum.EMBEDDING: 75,
            RepositoryStateEnum.ANALYZING: 90,
            RepositoryStateEnum.READY: 100,
            RepositoryStateEnum.FAILED: 0,
        }
        
        stage_map = {
            RepositoryStateEnum.UPLOADED: "Not started",
            RepositoryStateEnum.SCAN: "Scanning files",
            RepositoryStateEnum.PARSING: "Parsing code",
            RepositoryStateEnum.INDEXING: "Building dependency graph",
            RepositoryStateEnum.EMBEDDING: "Generating embeddings",
            RepositoryStateEnum.ANALYZING: "Saving vector index",
            RepositoryStateEnum.READY: "Complete",
            RepositoryStateEnum.FAILED: "Failed",
        }
        
        # Determine stages based on current state
        if state.state == RepositoryStateEnum.READY:
            stages_complete = ["scan", "parse", "chunk", "embed", "store"]
            stages_remaining = []
        elif state.state == RepositoryStateEnum.FAILED:
            stages_complete = []
            stages_remaining = ["scan", "parse", "chunk", "embed", "store"]
        elif state.state == RepositoryStateEnum.EMBEDDING:
            stages_complete = ["scan", "parse", "chunk"]
            stages_remaining = ["embed", "store"]
        elif state.state == RepositoryStateEnum.INDEXING:
            stages_complete = ["scan", "parse"]
            stages_remaining = ["chunk", "embed", "store"]
        elif state.state == RepositoryStateEnum.PARSING:
            stages_complete = ["scan"]
            stages_remaining = ["parse", "chunk", "embed", "store"]
        elif state.state == RepositoryStateEnum.SCAN:
            stages_complete = []
            stages_remaining = ["scan", "parse", "chunk", "embed", "store"]
        else:
            stages_complete = []
            stages_remaining = ["scan", "parse", "chunk", "embed", "store"]
        
        return {
            "repository_id": repository_id,
            "status": status_map.get(state.state, "NOT_INDEXED"),
            "progress_percent": state.progress if state.progress is not None else progress_map.get(state.state, 0),
            "current_stage": state.current_stage if state.current_stage else stage_map.get(state.state, "Unknown"),
            "stages_complete": stages_complete,
            "stages_remaining": stages_remaining,
            "started_at": None,
            "estimated_completion": None,
        }
    except Exception as e:
        # Fallback to index manager if state machine fails
        index = index_manager.get_index(repository_id)
        
        if not index:
            return {
                "repository_id": repository_id,
                "status": "NOT_INDEXED",
                "progress_percent": 0,
                "current_stage": "Not started",
                "stages_complete": [],
                "stages_remaining": ["scan", "parse", "chunk", "embed", "store"],
                "started_at": None,
                "estimated_completion": None,
            }
        
        progress_map = {
            IndexStatus.NOT_INDEXED: 0,
            IndexStatus.INDEXING: 50,
            IndexStatus.READY: 100,
            IndexStatus.FAILED: 0,
        }
        
        progress = progress_map.get(index.status, 0)
        
        stage_map = {
            IndexStatus.NOT_INDEXED: "Not started",
            IndexStatus.INDEXING: "Processing",
            IndexStatus.READY: "Complete",
            IndexStatus.FAILED: "Failed",
        }
        
        current_stage = stage_map.get(index.status, "Unknown")
        
        if index.status == IndexStatus.READY:
            stages_complete = ["scan", "parse", "chunk", "embed", "store"]
            stages_remaining = []
        elif index.status == IndexStatus.INDEXING:
            stages_complete = ["scan", "parse"]
            stages_remaining = ["chunk", "embed", "store"]
        elif index.status == IndexStatus.FAILED:
            stages_complete = []
            stages_remaining = ["scan", "parse", "chunk", "embed", "store"]
        else:
            stages_complete = []
            stages_remaining = ["scan", "parse", "chunk", "embed", "store"]
        
        return {
            "repository_id": repository_id,
            "status": index.status.value,
            "progress_percent": progress,
            "current_stage": current_stage,
            "stages_complete": stages_complete,
            "stages_remaining": stages_remaining,
            "started_at": index.indexed_at.isoformat() if index.indexed_at else None,
            "estimated_completion": None,
        }


@router.get("/{repository_id}/index/progress")
async def get_index_progress(repository_id: str):
    """Get detailed indexing progress information."""
    _project_path(repository_id)
    
    # Try to get real-time progress from repository state machine
    try:
        from app.repository_state.state_machine import RepositoryStateMachine
        sm = RepositoryStateMachine(repository_id)
        state = sm.current_state
        
        # Map repository state to indexing status
        from app.schemas.repository_state import RepositoryStateEnum
        
        status_map = {
            RepositoryStateEnum.UPLOADED: "NOT_INDEXED",
            RepositoryStateEnum.SCAN: "INDEXING",
            RepositoryStateEnum.PARSING: "INDEXING",
            RepositoryStateEnum.INDEXING: "INDEXING",
            RepositoryStateEnum.EMBEDDING: "INDEXING",
            RepositoryStateEnum.ANALYZING: "INDEXING",
            RepositoryStateEnum.READY: "READY",
            RepositoryStateEnum.FAILED: "FAILED",
        }
        
        progress_map = {
            RepositoryStateEnum.UPLOADED: 0,
            RepositoryStateEnum.SCAN: 15,
            RepositoryStateEnum.PARSING: 35,
            RepositoryStateEnum.INDEXING: 55,
            RepositoryStateEnum.EMBEDDING: 75,
            RepositoryStateEnum.ANALYZING: 90,
            RepositoryStateEnum.READY: 100,
            RepositoryStateEnum.FAILED: 0,
        }
        
        stage_map = {
            RepositoryStateEnum.UPLOADED: "Not started",
            RepositoryStateEnum.SCAN: "Scanning files",
            RepositoryStateEnum.PARSING: "Parsing code",
            RepositoryStateEnum.INDEXING: "Building dependency graph",
            RepositoryStateEnum.EMBEDDING: "Generating embeddings",
            RepositoryStateEnum.ANALYZING: "Saving vector index",
            RepositoryStateEnum.READY: "Complete",
            RepositoryStateEnum.FAILED: "Failed",
        }
        
        # Determine stages based on current state
        if state.state == RepositoryStateEnum.READY:
            stages_complete = ["scan", "parse", "chunk", "embed", "store"]
            stages_remaining = []
        elif state.state == RepositoryStateEnum.FAILED:
            stages_complete = []
            stages_remaining = ["scan", "parse", "chunk", "embed", "store"]
        elif state.state == RepositoryStateEnum.EMBEDDING:
            stages_complete = ["scan", "parse", "chunk"]
            stages_remaining = ["embed", "store"]
        elif state.state == RepositoryStateEnum.INDEXING:
            stages_complete = ["scan", "parse"]
            stages_remaining = ["chunk", "embed", "store"]
        elif state.state == RepositoryStateEnum.PARSING:
            stages_complete = ["scan"]
            stages_remaining = ["parse", "chunk", "embed", "store"]
        elif state.state == RepositoryStateEnum.SCAN:
            stages_complete = []
            stages_remaining = ["scan", "parse", "chunk", "embed", "store"]
        else:
            stages_complete = []
            stages_remaining = ["scan", "parse", "chunk", "embed", "store"]
        
        # Get index for statistics
        index = index_manager.get_index(repository_id)
        
        return {
            "repository_id": repository_id,
            "status": status_map.get(state.state, "NOT_INDEXED"),
            "progress_percent": state.progress if state.progress is not None else progress_map.get(state.state, 0),
            "current_stage": state.current_stage if state.current_stage else stage_map.get(state.state, "Unknown"),
            "stages_complete": stages_complete,
            "stages_remaining": stages_remaining,
            "started_at": index.indexed_at.isoformat() if index and index.indexed_at else None,
            "estimated_completion": None,
            "details": {
                "total_files": index.total_files if index else 0,
                "total_chunks": index.total_chunks if index else 0,
                "total_embeddings": index.total_embeddings if index else 0,
                "added": index.added if index else 0,
                "modified": index.modified if index else 0,
                "deleted": index.deleted if index else 0,
                "unchanged": index.unchanged if index else 0,
            },
        }
    except Exception as e:
        # Fallback to index manager if state machine fails
        index = index_manager.get_index(repository_id)
        
        if not index:
            return {
                "repository_id": repository_id,
                "status": "NOT_INDEXED",
                "progress_percent": 0,
                "current_stage": "Not started",
                "stages_complete": [],
                "stages_remaining": ["scan", "parse", "chunk", "embed", "store"],
                "started_at": None,
                "estimated_completion": None,
                "details": {
                    "total_files": 0,
                    "total_chunks": 0,
                    "total_embeddings": 0,
                    "added": 0,
                    "modified": 0,
                    "deleted": 0,
                    "unchanged": 0,
                },
            }
        
        progress_map = {
            IndexStatus.NOT_INDEXED: 0,
            IndexStatus.INDEXING: 50,
            IndexStatus.READY: 100,
            IndexStatus.FAILED: 0,
        }
        
        progress = progress_map.get(index.status, 0)
        
        stage_map = {
            IndexStatus.NOT_INDEXED: "Not started",
            IndexStatus.INDEXING: "Processing",
            IndexStatus.READY: "Complete",
            IndexStatus.FAILED: "Failed",
        }
        
        current_stage = stage_map.get(index.status, "Unknown")
        
        if index.status == IndexStatus.READY:
            stages_complete = ["scan", "parse", "chunk", "embed", "store"]
            stages_remaining = []
        elif index.status == IndexStatus.INDEXING:
            stages_complete = ["scan", "parse"]
            stages_remaining = ["chunk", "embed", "store"]
        elif index.status == IndexStatus.FAILED:
            stages_complete = []
            stages_remaining = ["scan", "parse", "chunk", "embed", "store"]
        else:
            stages_complete = []
            stages_remaining = ["scan", "parse", "chunk", "embed", "store"]
        
        return {
            "repository_id": repository_id,
            "status": index.status.value,
            "progress_percent": progress,
            "current_stage": current_stage,
            "stages_complete": stages_complete,
            "stages_remaining": stages_remaining,
            "started_at": index.indexed_at.isoformat() if index.indexed_at else None,
            "estimated_completion": None,
            "details": {
                "total_files": index.total_files,
                "total_chunks": index.total_chunks,
                "total_embeddings": index.total_embeddings,
                "added": index.added,
                "modified": index.modified,
                "deleted": index.deleted,
                "unchanged": index.unchanged,
            },
        }


@router.delete("/{repository_id}/index", status_code=status.HTTP_204_NO_CONTENT)
async def delete_index(repository_id: str) -> None:
    try:
        index_manager.delete_index(repository_id)
    except IndexNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
