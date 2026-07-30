from fastapi import APIRouter, HTTPException
import os
from typing import Dict, Any
from app.schemas.incremental_indexing import IncrementalResponse, RepositorySnapshotModel
from app.incremental_indexing.snapshot_manager import snapshot_manager
from app.incremental_indexing.incremental_indexer import IncrementalIndexer

router = APIRouter(tags=["incremental_indexing"])

@router.post("/incremental-index/{repository_id}", response_model=IncrementalResponse)
def run_incremental_index(repository_id: str):
    root_dir = os.path.join("uploads", repository_id)
    if not os.path.exists(root_dir):
        # Even if not found, we can return empty or simulate
        # Let's create it for simulation if it doesn't exist
        os.makedirs(root_dir, exist_ok=True)
        
    indexer = IncrementalIndexer(root_dir=root_dir, repository_id=repository_id)
    try:
        response = indexer.run_indexing()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/repository-snapshot/{repository_id}", response_model=RepositorySnapshotModel)
def get_snapshot(repository_id: str):
    snapshot = snapshot_manager.get_snapshot(repository_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snapshot.model
