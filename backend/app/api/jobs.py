"""API endpoints for async job management."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.jobs.job_manager import job_manager
from app.jobs.job_status import JobStatus
from app.schemas.jobs import (
    JobCreateRequest,
    JobCreateResponse,
    JobStatusResponse,
    JobListResponse,
    JobCancelResponse,
    QueueStatusResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/analyze/{upload_id}", response_model=JobCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis_job(upload_id: str, request: JobCreateRequest) -> JobCreateResponse:
    """Create and enqueue an analysis job for a repository.
    
    Args:
        upload_id: The UUID of the uploaded repository.
        request: Job creation request with task type and optional metadata.
    
    Returns:
        JobCreateResponse with job ID and initial status.
    
    Raises:
        HTTPException: If repository not found or task type invalid.
    """
    try:
        job = job_manager.create_job(
            repository_id=upload_id,
            task_type=request.task_type,
            metadata=request.metadata
        )
        
        return JobCreateResponse(
            job_id=job.job_id,
            repository_id=job.repository_id,
            task_type=job.task_type,
            status=job.status.value
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        logger.exception("Error creating job for upload_id: %s", upload_id)
        raise HTTPException(status_code=500, detail="Internal server error creating job") from e


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """Get the current status of a job.
    
    Args:
        job_id: The UUID of the job.
    
    Returns:
        JobStatusResponse with current job status and progress.
    
    Raises:
        HTTPException: If job not found.
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    job_dict = job.to_dict()
    return JobStatusResponse(**job_dict)


@router.post("/{job_id}/cancel", response_model=JobCancelResponse)
async def cancel_job(job_id: str) -> JobCancelResponse:
    """Cancel a running or queued job.
    
    Args:
        job_id: The UUID of the job.
    
    Returns:
        JobCancelResponse with cancellation result.
    
    Raises:
        HTTPException: If job not found.
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    success = job_manager.cancel_job(job_id)
    
    if success:
        return JobCancelResponse(
            job_id=job_id,
            status=job.status.value,
            message="Job cancelled successfully"
        )
    else:
        return JobCancelResponse(
            job_id=job_id,
            status=job.status.value,
            message="Job could not be cancelled (already completed or not cancellable)"
        )


@router.get("", response_model=JobListResponse)
async def list_jobs(
    repository_id: Optional[str] = Query(None, description="Filter by repository ID"),
    status: Optional[str] = Query(None, description="Filter by job status")
) -> JobListResponse:
    """List jobs with optional filters.
    
    Args:
        repository_id: Optional filter by repository ID.
        status: Optional filter by job status.
    
    Returns:
        JobListResponse with matching jobs.
    """
    try:
        status_filter = JobStatus(status) if status else None
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    jobs = job_manager.list_jobs(repository_id=repository_id, status=status_filter)
    
    return JobListResponse(
        jobs=[JobStatusResponse(**job.to_dict()) for job in jobs],
        total=len(jobs)
    )


@router.get("/queue/status", response_model=QueueStatusResponse)
async def get_queue_status() -> QueueStatusResponse:
    """Get the current status of the job queue and worker pool.
    
    Returns:
        QueueStatusResponse with queue and worker status.
    """
    status = job_manager.get_queue_status()
    return QueueStatusResponse(**status)


@router.delete("/cleanup", status_code=status.HTTP_204_NO_CONTENT)
async def cleanup_old_jobs(
    max_age_hours: int = Query(24, ge=1, description="Maximum job age in hours to keep")
) -> None:
    """Remove old completed/failed jobs from memory.
    
    Args:
        max_age_hours: Maximum age in hours to keep jobs.
    """
    job_manager.cleanup_old_jobs(max_age_hours=max_age_hours)
