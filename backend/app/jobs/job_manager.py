"""Job manager - orchestrator for async analysis pipeline."""

import logging
from typing import Any
from pathlib import Path

from app.jobs.job_queue import JobQueue
from app.jobs.job_status import Job, JobStatus
from app.jobs.job_worker import WorkerPool
from app.jobs.job_worker import WorkerPool
from app.jobs.task_registry import task_registry
from app.repository_state.state_machine import RepositoryStateMachine
from app.schemas.repository_state import RepositoryStateEnum
from app.events.event_bus import event_bus
from app.events.event_types import EventType

logger = logging.getLogger(__name__)


class JobManager:
    """Central orchestrator for job management and execution."""
    
    def __init__(
        self,
        max_queue_size: int = 100,
        num_workers: int = 2
    ) -> None:
        """Initialize job manager.
        
        Args:
            max_queue_size: Maximum number of jobs in queue.
            num_workers: Number of worker threads.
        """
        self._queue = JobQueue(max_size=max_queue_size)
        self._jobs: dict[str, Job] = {}
        self._worker_pool = WorkerPool(
            self._queue,
            self._on_job_update,
            num_workers=num_workers
        )
        self._worker_pool.start()
        logger.info("Job manager initialized")
    
    def create_job(
        self,
        repository_id: str,
        task_type: str,
        metadata: dict[str, Any] | None = None
    ) -> Job:
        """Create and enqueue a new analysis job.
        
        Args:
            repository_id: ID of the repository to analyze.
            task_type: Type of analysis task (e.g., 'architecture', 'indexing').
            metadata: Optional metadata for the job.
        
        Returns:
            Created Job object.
        
        Raises:
            ValueError: If task type is not registered.
        """
        if not task_registry.has_task(task_type):
            raise ValueError(f"Unknown task type: {task_type}")
        
        # Validate repository exists
        self._validate_repository(repository_id)
        
        # Create job
        job = Job.create(repository_id, task_type)
        if metadata:
            job.metadata = metadata
        
        # Store job
        self._jobs[job.job_id] = job
        
        # Enqueue job
        job_data = job.to_dict()
        if not self._queue.enqueue(job_data):
            job.mark_failed("Job queue is full")
            event_bus.publish(
                event_type=EventType.JOB_FAILED,
                repository_id=repository_id,
                payload={"job_id": job.job_id, "task_type": task_type, "error": "Job queue is full"}
            )
            raise RuntimeError("Job queue is full")
            
        try:
            state_machine = RepositoryStateMachine(repository_id)
            state_machine.transition_to(
                new_state=RepositoryStateEnum.QUEUED,
                job_id=job.job_id
            )
        except Exception as e:
            logger.error(f"Failed to update repository state to QUEUED: {e}")
        
        event_bus.publish(
            event_type=EventType.JOB_QUEUED,
            repository_id=repository_id,
            payload={"job_id": job.job_id, "task_type": task_type}
        )
        
        logger.info(f"Created job {job.job_id} for repository {repository_id}")
        return job
    
    def get_job(self, job_id: str) -> Job | None:
        """Get job by ID.
        
        Args:
            job_id: Job identifier.
        
        Returns:
            Job object or None if not found.
        """
        return self._jobs.get(job_id)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job.
        
        Args:
            job_id: Job identifier.
        
        Returns:
            True if job was cancelled, False if not found or already completed.
        """
        job = self._jobs.get(job_id)
        if not job:
            return False
        
        if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            return False
        
        # If job is still queued, remove from queue
        if job.status == JobStatus.QUEUED:
            # Try to remove from queue (this is tricky with queue.Queue)
            # For now, we'll mark it as cancelled and let worker skip it
            job.mark_cancelled()
            
            try:
                state_machine = RepositoryStateMachine(job.repository_id)
                state_machine.transition_to(RepositoryStateEnum.CANCELLED)
            except Exception as e:
                logger.error(f"Failed to transition state to CANCELLED: {e}")
                
            logger.info(f"Cancelled queued job {job_id}")
            return True
        
        # If job is running, we can't easily stop it mid-execution
        # Mark as cancelled but worker will finish current task
        if job.status == JobStatus.RUNNING:
            job.mark_cancelled()
            try:
                state_machine = RepositoryStateMachine(job.repository_id)
                state_machine.transition_to(RepositoryStateEnum.CANCELLED)
            except Exception as e:
                logger.error(f"Failed to transition state to CANCELLED: {e}")
                
            logger.info(f"Marked running job {job_id} as cancelled")
            return True
        
        return False
    
    def list_jobs(
        self,
        repository_id: str | None = None,
        status: JobStatus | None = None
    ) -> list[Job]:
        """List jobs with optional filters.
        
        Args:
            repository_id: Filter by repository ID.
            status: Filter by job status.
        
        Returns:
            List of matching jobs.
        """
        jobs = list(self._jobs.values())
        
        if repository_id:
            jobs = [j for j in jobs if j.repository_id == repository_id]
        
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        return jobs
    
    def get_queue_status(self) -> dict[str, Any]:
        """Get queue and worker pool status.
        
        Returns:
            Dictionary with queue and worker status.
        """
        return {
            "queue_size": self._queue.size(),
            "queue_capacity": self._queue.maxsize if hasattr(self._queue, 'maxsize') else 100,
            "workers": self._worker_pool.get_status(),
        }
    
    def cleanup_old_jobs(self, max_age_hours: int = 24) -> int:
        """Remove old completed/failed jobs from memory.
        
        Args:
            max_age_hours: Maximum age in hours to keep jobs.
        
        Returns:
            Number of jobs removed.
        """
        from datetime import datetime, timedelta, timezone
        
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        to_remove = []
        
        for job_id, job in self._jobs.items():
            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                if job.finish_time and job.finish_time < cutoff:
                    to_remove.append(job_id)
        
        for job_id in to_remove:
            del self._jobs[job_id]
        
        logger.info(f"Cleaned up {len(to_remove)} old jobs")
        return len(to_remove)
    
    def shutdown(self) -> None:
        """Shutdown job manager gracefully."""
        logger.info("Shutting down job manager")
        self._worker_pool.stop()
        self._queue.clear()
        logger.info("Job manager shutdown complete")
    
    def _validate_repository(self, repository_id: str) -> None:
        """Validate that repository exists and is accessible.
        
        Args:
            repository_id: Repository identifier.
        
        Raises:
            ValueError: If repository is not found.
        """
        # Check both possible locations
        from app.core.paths import get_extracted_dir, get_upload_dir
        extracted_path = get_extracted_dir() / repository_id
        uploads_path = get_upload_dir() / repository_id
        
        if not extracted_path.exists() and not uploads_path.exists():
            raise ValueError(f"Repository not found: {repository_id}")
        
        if extracted_path.exists() and not extracted_path.is_dir():
            raise ValueError(f"Repository path is not a directory: {repository_id}")
        
        if uploads_path.exists() and not uploads_path.is_dir():
            raise ValueError(f"Repository path is not a directory: {repository_id}")
    
    def _on_job_update(self, job_id: str, job_data: dict[str, Any]) -> None:
        """Handle job status updates from workers.
        
        Args:
            job_id: Job identifier.
            job_data: Updated job data.
        """
        job = self._jobs.get(job_id)
        if job:
            # Update job in memory
            job.status = JobStatus(job_data["status"])
            job.current_step = job_data.get("current_step", "")
            job.progress = job_data.get("progress", 0)
            job.error_message = job_data.get("error_message")
            job.result = job_data.get("result")
            
            if job_data.get("finish_time"):
                from datetime import datetime
                finish_time = job_data["finish_time"]
                if isinstance(finish_time, str):
                    job.finish_time = datetime.fromisoformat(finish_time)
                else:
                    job.finish_time = finish_time
            
            logger.debug(f"Job {job_id} updated: {job.status} ({job.progress}%)")


# Global job manager instance
job_manager = JobManager()
