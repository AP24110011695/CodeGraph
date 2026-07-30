"""Worker for executing analysis jobs asynchronously."""

import threading
import time
import logging
from typing import Any, Callable

from app.jobs.job_queue import JobQueue
from app.jobs.job_status import Job, JobStatus
from app.jobs.job_queue import JobQueue
from app.jobs.job_status import Job, JobStatus
from app.jobs.task_registry import task_registry
from app.repository_state.state_machine import RepositoryStateMachine
from app.schemas.repository_state import RepositoryStateEnum
from app.events.event_bus import event_bus
from app.events.event_types import EventType

logger = logging.getLogger(__name__)


class JobWorker:
    """Worker thread that processes jobs from the queue."""
    
    def __init__(
        self,
        queue: JobQueue,
        job_update_callback: Callable[[str, dict], None],
        worker_id: int = 0
    ) -> None:
        """Initialize job worker.
        
        Args:
            queue: Job queue to pull jobs from.
            job_update_callback: Callback to notify job status updates.
            worker_id: Unique identifier for this worker.
        """
        self._queue = queue
        self._job_update_callback = job_update_callback
        self._worker_id = worker_id
        self._running = False
        self._thread: threading.Thread | None = None
        self._current_job: Job | None = None
    
    def start(self) -> None:
        """Start the worker thread."""
        if self._running:
            logger.warning(f"Worker {self._worker_id} is already running")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info(f"Worker {self._worker_id} started")
    
    def stop(self) -> None:
        """Stop the worker thread gracefully."""
        if not self._running:
            return
        
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
            if self._thread.is_alive():
                logger.warning(f"Worker {self._worker_id} did not stop gracefully")
            else:
                logger.info(f"Worker {self._worker_id} stopped")
    
    def is_running(self) -> bool:
        """Check if worker is running."""
        return self._running
    
    def get_current_job(self) -> Job | None:
        """Get the job currently being processed."""
        return self._current_job
    
    def _run_loop(self) -> None:
        """Main worker loop."""
        while self._running:
            try:
                # Wait for job with timeout to allow periodic stop checks
                job_data = self._queue.dequeue(timeout=1.0)
                
                if job_data is None:
                    continue
                
                # Reconstruct Job object
                start_time = job_data.get("start_time")
                if isinstance(start_time, str):
                    from datetime import datetime
                    start_time = datetime.fromisoformat(start_time)
                
                finish_time = job_data.get("finish_time")
                if isinstance(finish_time, str):
                    from datetime import datetime
                    finish_time = datetime.fromisoformat(finish_time)
                
                job = Job(
                    job_id=job_data["job_id"],
                    repository_id=job_data["repository_id"],
                    task_type=job_data["task_type"],
                    status=JobStatus(job_data["status"]),
                    current_step=job_data.get("current_step", ""),
                    progress=job_data.get("progress", 0),
                    start_time=start_time,
                    finish_time=finish_time,
                    error_message=job_data.get("error_message"),
                    result=job_data.get("result"),
                    metadata=job_data.get("metadata", {}),
                )
                
                self._current_job = job
                self._process_job(job)
                self._current_job = None
                
            except Exception as e:
                logger.exception(f"Worker {self._worker_id} encountered error: {e}")
                time.sleep(1.0)  # Prevent tight error loop
    
    def _process_job(self, job: Job) -> None:
        """Process a single job."""
        logger.info(f"Worker {self._worker_id} processing job {job.job_id}")
        
        # Mark job as running
        job.mark_running()
        
        try:
            state_machine = RepositoryStateMachine(job.repository_id)
            # Transition to initial active state
            initial_state = RepositoryStateEnum.SCANNING if job.task_type == "indexing" else RepositoryStateEnum.ANALYZING
            try:
                state_machine.transition_to(initial_state, job_id=job.job_id)
            except ValueError:
                pass # Transition might be invalid if retrying, etc.
        except Exception as e:
            logger.error(f"Failed to set initial active state for {job.job_id}: {e}")
            
        event_bus.publish(
            event_type=EventType.JOB_STARTED,
            repository_id=job.repository_id,
            payload={"job_id": job.job_id, "task_type": job.task_type}
        )
            
        self._notify_update(job)
        
        try:
            # Get task handler
            handler = task_registry.get_handler(job.task_type)
            if handler is None:
                raise ValueError(f"No handler registered for task type: {job.task_type}")
            
            # Progress callback
            def progress_callback(step: str, progress_percent: int) -> None:
                job.update_progress(step, progress_percent)
                
                try:
                    sm = RepositoryStateMachine(job.repository_id)
                    step_lower = step.lower()
                    new_state = None
                    if "scan" in step_lower:
                        new_state = RepositoryStateEnum.SCANNING
                    elif "pars" in step_lower:
                        new_state = RepositoryStateEnum.PARSING
                    elif "index" in step_lower:
                        new_state = RepositoryStateEnum.INDEXING
                    elif "embed" in step_lower:
                        new_state = RepositoryStateEnum.EMBEDDING
                    elif any(k in step_lower for k in ["analyz", "detect", "build", "generat"]):
                        new_state = RepositoryStateEnum.ANALYZING
                        
                    if new_state and new_state != sm.current_state.state:
                        try:
                            sm.transition_to(new_state, progress=progress_percent, current_stage=step)
                        except ValueError:
                            sm.update_progress(progress=progress_percent, current_stage=step)
                    else:
                        sm.update_progress(progress=progress_percent, current_stage=step)
                except Exception as e:
                    logger.error(f"Failed to update state for {job.job_id} at {step}: {e}")
                    
                event_bus.publish(
                    event_type=EventType.JOB_PROGRESS_UPDATED,
                    repository_id=job.repository_id,
                    payload={"job_id": job.job_id, "step": step, "progress": progress_percent}
                )
                    
                self._notify_update(job)
            
            # Execute task
            result = handler(job.repository_id, progress_callback)
            
            # Mark job as completed
            job.mark_completed(result)
            try:
                sm = RepositoryStateMachine(job.repository_id)
                sm.transition_to(RepositoryStateEnum.READY, progress=100, current_stage="Complete")
            except Exception as e:
                logger.error(f"Failed to transition to READY for {job.job_id}: {e}")
            
            event_bus.publish(
                event_type=EventType.JOB_COMPLETED,
                repository_id=job.repository_id,
                payload={"job_id": job.job_id, "task_type": job.task_type}
            )
            
            # Map task types to analysis completion events
            task_to_event = {
                "architecture": EventType.ARCHITECTURE_GENERATED,
                "quality": EventType.QUALITY_COMPLETED,
                "security": EventType.SECURITY_COMPLETED,
                "metrics": EventType.METRICS_GENERATED,
                "risk": EventType.RISK_COMPLETED,
            }
            if job.task_type in task_to_event:
                event_bus.publish(
                    event_type=task_to_event[job.task_type],
                    repository_id=job.repository_id,
                    payload={"job_id": job.job_id, "task_type": job.task_type}
                )
            
            logger.info(f"Job {job.job_id} completed successfully")
            
        except Exception as e:
            # Mark job as failed
            error_msg = str(e)
            job.mark_failed(error_msg)
            try:
                sm = RepositoryStateMachine(job.repository_id)
                sm.transition_to(RepositoryStateEnum.FAILED, failure_reason=error_msg)
            except Exception as e2:
                logger.error(f"Failed to transition to FAILED for {job.job_id}: {e2}")
                
            event_bus.publish(
                event_type=EventType.JOB_FAILED,
                repository_id=job.repository_id,
                payload={"job_id": job.job_id, "task_type": job.task_type, "error": error_msg}
            )
            
            logger.error(f"Job {job.job_id} failed: {error_msg}")
        
        finally:
            self._notify_update(job)
    
    def _notify_update(self, job: Job) -> None:
        """Notify job manager of status update."""
        try:
            self._job_update_callback(job.job_id, job.to_dict())
        except Exception as e:
            logger.error(f"Failed to notify job update for {job.job_id}: {e}")


class WorkerPool:
    """Pool of worker threads for parallel job processing."""
    
    def __init__(
        self,
        queue: JobQueue,
        job_update_callback: Callable[[str, dict], None],
        num_workers: int = 2
    ) -> None:
        """Initialize worker pool.
        
        Args:
            queue: Job queue to pull jobs from.
            job_update_callback: Callback to notify job status updates.
            num_workers: Number of worker threads to create.
        """
        self._queue = queue
        self._job_update_callback = job_update_callback
        self._num_workers = num_workers
        self._workers: list[JobWorker] = []
    
    def start(self) -> None:
        """Start all workers in the pool."""
        self._workers = [
            JobWorker(self._queue, self._job_update_callback, worker_id=i)
            for i in range(self._num_workers)
        ]
        
        for worker in self._workers:
            worker.start()
        
        logger.info(f"Worker pool started with {self._num_workers} workers")
    
    def stop(self) -> None:
        """Stop all workers in the pool."""
        for worker in self._workers:
            worker.stop()
        
        self._workers.clear()
        logger.info("Worker pool stopped")
    
    def get_status(self) -> list[dict[str, Any]]:
        """Get status of all workers."""
        return [
            {
                "worker_id": worker._worker_id,
                "running": worker.is_running(),
                "current_job": worker.get_current_job().to_dict() if worker.get_current_job() else None,
            }
            for worker in self._workers
        ]
