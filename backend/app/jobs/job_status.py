"""Job status models and state tracking for async analysis pipeline."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import uuid


class JobStatus(str, Enum):
    """Lifecycle states for analysis jobs."""
    
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class Job:
    """Represents an analysis job with state tracking."""
    
    job_id: str
    repository_id: str
    task_type: str
    status: JobStatus = JobStatus.QUEUED
    current_step: str = ""
    progress: int = 0
    start_time: datetime | None = None
    finish_time: datetime | None = None
    error_message: str | None = None
    result: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create(cls, repository_id: str, task_type: str) -> "Job":
        """Create a new job with generated ID."""
        return cls(
            job_id=str(uuid.uuid4()),
            repository_id=repository_id,
            task_type=task_type,
            start_time=datetime.now(timezone.utc),
        )
    
    def update_progress(self, step: str, progress_percent: int) -> None:
        """Update job progress."""
        self.current_step = step
        self.progress = min(100, max(0, progress_percent))
    
    def mark_running(self) -> None:
        """Mark job as running."""
        self.status = JobStatus.RUNNING
        if not self.start_time:
            self.start_time = datetime.now(timezone.utc)
    
    def mark_completed(self, result: dict[str, Any] | None = None) -> None:
        """Mark job as completed."""
        self.status = JobStatus.COMPLETED
        self.finish_time = datetime.now(timezone.utc)
        self.progress = 100
        if result:
            self.result = result
    
    def mark_failed(self, error: str) -> None:
        """Mark job as failed."""
        self.status = JobStatus.FAILED
        self.finish_time = datetime.now(timezone.utc)
        self.error_message = error
    
    def mark_cancelled(self) -> None:
        """Mark job as cancelled."""
        self.status = JobStatus.CANCELLED
        self.finish_time = datetime.now(timezone.utc)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert job to dictionary for API responses."""
        return {
            "job_id": self.job_id,
            "repository_id": self.repository_id,
            "task_type": self.task_type,
            "status": self.status.value,
            "current_step": self.current_step,
            "progress": self.progress,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "finish_time": self.finish_time.isoformat() if self.finish_time else None,
            "error_message": self.error_message,
            "result": self.result,
            "metadata": self.metadata,
        }
