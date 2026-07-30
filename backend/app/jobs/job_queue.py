"""Thread-safe job queue for async analysis pipeline."""

import queue
import threading
from typing import Any
from collections.abc import Iterator
import logging

logger = logging.getLogger(__name__)


class JobQueue:
    """Thread-safe queue for managing analysis jobs."""
    
    def __init__(self, max_size: int = 100) -> None:
        """Initialize job queue with optional size limit."""
        self._queue: queue.Queue[dict[str, Any]] = queue.Queue(maxsize=max_size)
        self._lock = threading.Lock()
        self._size = 0
    
    def enqueue(self, job: dict[str, Any]) -> bool:
        """Add a job to the queue.
        
        Returns:
            True if job was enqueued, False if queue is full.
        """
        try:
            self._queue.put(job, block=False)
            with self._lock:
                self._size += 1
            logger.info(f"Job {job.get('job_id')} enqueued")
            return True
        except queue.Full:
            logger.warning("Job queue is full, cannot enqueue job")
            return False
    
    def dequeue(self, timeout: float | None = None) -> dict[str, Any] | None:
        """Remove and return a job from the queue.
        
        Args:
            timeout: Maximum time to wait for a job. None means wait indefinitely.
        
        Returns:
            Job dict or None if timeout expires.
        """
        try:
            job = self._queue.get(block=True, timeout=timeout)
            with self._lock:
                self._size -= 1
            logger.info(f"Job {job.get('job_id')} dequeued")
            return job
        except queue.Empty:
            return None
    
    def peek(self) -> dict[str, Any] | None:
        """Look at the next job without removing it.
        
        Returns:
            Next job dict or None if queue is empty.
        """
        try:
            return self._queue.queue[0] if self._queue.queue else None
        except (IndexError, AttributeError):
            return None
    
    def size(self) -> int:
        """Get current queue size."""
        with self._lock:
            return self._size
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return self._queue.empty()
    
    def is_full(self) -> bool:
        """Check if queue is full."""
        return self._queue.full()
    
    def clear(self) -> None:
        """Clear all jobs from the queue."""
        with self._lock:
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    break
            self._size = 0
        logger.info("Job queue cleared")
    
    def iterate(self) -> Iterator[dict[str, Any]]:
        """Iterate over queued jobs without removing them."""
        with self._lock:
            for job in list(self._queue.queue):
                yield job
