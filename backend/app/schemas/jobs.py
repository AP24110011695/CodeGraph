"""Schemas for job API responses."""

from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime


class JobCreateRequest(BaseModel):
    """Request schema for creating a job."""
    
    task_type: str = Field(..., description="Type of analysis task (e.g., 'architecture', 'indexing')")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="Optional metadata for the job")


class JobCreateResponse(BaseModel):
    """Response schema for job creation."""
    
    job_id: str = Field(..., description="Unique job identifier")
    repository_id: str = Field(..., description="Repository identifier")
    task_type: str = Field(..., description="Type of analysis task")
    status: str = Field(..., description="Initial job status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "repository_id": "upload-123",
                "task_type": "architecture",
                "status": "QUEUED"
            }
        }


class JobStatusResponse(BaseModel):
    """Response schema for job status queries."""
    
    job_id: str = Field(..., description="Unique job identifier")
    repository_id: str = Field(..., description="Repository identifier")
    task_type: str = Field(..., description="Type of analysis task")
    status: str = Field(..., description="Current job status")
    current_step: str = Field(default="", description="Current processing step")
    progress: int = Field(default=0, ge=0, le=100, description="Progress percentage")
    start_time: Optional[str] = Field(default=None, description="Job start time (ISO 8601)")
    finish_time: Optional[str] = Field(default=None, description="Job finish time (ISO 8601)")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    result: Optional[dict[str, Any]] = Field(default=None, description="Job result data")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Job metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "repository_id": "upload-123",
                "task_type": "architecture",
                "status": "RUNNING",
                "current_step": "Building architecture model",
                "progress": 75,
                "start_time": "2024-01-15T10:30:00Z",
                "finish_time": None,
                "error_message": None,
                "result": None,
                "metadata": {}
            }
        }


class JobListResponse(BaseModel):
    """Response schema for job list queries."""
    
    jobs: list[JobStatusResponse] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total number of jobs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "jobs": [],
                "total": 0
            }
        }


class JobCancelResponse(BaseModel):
    """Response schema for job cancellation."""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status after cancellation attempt")
    message: str = Field(..., description="Cancellation result message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "CANCELLED",
                "message": "Job cancelled successfully"
            }
        }


class QueueStatusResponse(BaseModel):
    """Response schema for queue status queries."""
    
    queue_size: int = Field(..., description="Current number of jobs in queue")
    queue_capacity: int = Field(..., description="Maximum queue capacity")
    workers: list[dict[str, Any]] = Field(..., description="Worker pool status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "queue_size": 5,
                "queue_capacity": 100,
                "workers": [
                    {
                        "worker_id": 0,
                        "running": True,
                        "current_job": None
                    },
                    {
                        "worker_id": 1,
                        "running": True,
                        "current_job": {
                            "job_id": "550e8400-e29b-41d4-a716-446655440000",
                            "status": "RUNNING",
                            "progress": 50
                        }
                    }
                ]
            }
        }
