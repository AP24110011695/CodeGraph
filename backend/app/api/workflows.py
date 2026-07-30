from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List, Optional

from app.workflows.workflow_engine import workflow_engine
from app.workflows.workflow_context import WorkflowContext

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/start/{upload_id}", response_model=WorkflowContext)
async def start_workflow(upload_id: str, workflow_name: str = "repository_processing"):
    """Start the standard repository processing workflow for an upload."""
    try:
        return workflow_engine.start_workflow(workflow_name, upload_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("", response_model=List[WorkflowContext])
async def list_workflows():
    """List all workflows (active + completed)."""
    return workflow_engine.list_workflows()


@router.get("/{workflow_id}", response_model=WorkflowContext)
async def get_workflow(workflow_id: str):
    """Get full status and progress of a workflow."""
    ctx = workflow_engine.get_workflow(workflow_id)
    if not ctx:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return ctx


@router.post("/{workflow_id}/pause")
async def pause_workflow(workflow_id: str):
    ok = workflow_engine.pause_workflow(workflow_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Workflow cannot be paused (not running or not found)")
    return {"workflow_id": workflow_id, "status": "paused"}


@router.post("/{workflow_id}/resume")
async def resume_workflow(workflow_id: str):
    ok = workflow_engine.resume_workflow(workflow_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Workflow cannot be resumed (not paused or not found)")
    return {"workflow_id": workflow_id, "status": "resumed"}


@router.post("/{workflow_id}/cancel")
async def cancel_workflow(workflow_id: str):
    ok = workflow_engine.cancel_workflow(workflow_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Workflow cannot be cancelled")
    return {"workflow_id": workflow_id, "status": "cancelled"}


@router.post("/{workflow_id}/checkpoint/save")
async def save_checkpoint(workflow_id: str):
    """Persist the workflow state to disk."""
    path = workflow_engine.save_checkpoint(workflow_id)
    if not path:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"workflow_id": workflow_id, "checkpoint_path": str(path)}


@router.post("/restore")
async def restore_checkpoint(body: Dict[str, Any]):
    """Restore a workflow from a checkpoint payload."""
    workflow_name = body.get("workflow_name", "repository_processing")
    checkpoint_data = body.get("checkpoint_data")
    workflow_id = body.get("workflow_id")
    try:
        ctx = workflow_engine.restore_checkpoint(
            workflow_name=workflow_name,
            checkpoint_data=checkpoint_data,
            workflow_id=workflow_id,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return ctx
