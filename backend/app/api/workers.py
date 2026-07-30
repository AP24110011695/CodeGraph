from fastapi import APIRouter
from typing import List

from app.workers.worker_manager import worker_manager, WorkerInfo

router = APIRouter(prefix="/workers", tags=["workers"])


@router.get("", response_model=List[WorkerInfo])
async def list_workers():
    """List all registered workers with their status, health, and capabilities."""
    return worker_manager.get_workers()


@router.get("/idle", response_model=List[WorkerInfo])
async def list_idle_workers():
    """List only healthy idle workers."""
    return worker_manager.get_idle_workers()
