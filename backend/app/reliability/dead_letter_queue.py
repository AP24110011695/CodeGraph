import logging
from typing import Dict, List, Optional
from app.schemas.reliability import DeadLetterJob
import uuid

logger = logging.getLogger(__name__)

class DeadLetterQueue:
    def __init__(self):
        # In-memory store for demonstration; in production, this would be a DB or persistent queue
        self._queue: Dict[str, DeadLetterJob] = {}

    def add_job(self, job_id: str, task_type: str, repository_id: str, payload: dict, failure_reason: str, retry_history: list = None) -> DeadLetterJob:
        dlq_job = DeadLetterJob(
            original_job_id=job_id,
            task_type=task_type,
            repository_id=repository_id,
            payload=payload,
            failure_reason=failure_reason,
            retry_history=retry_history or []
        )
        self._queue[dlq_job.id] = dlq_job
        logger.error(f"Job {job_id} ({task_type}) moved to DLQ. Reason: {failure_reason}")
        return dlq_job

    def get_jobs(self, limit: int = 100, offset: int = 0) -> List[DeadLetterJob]:
        return list(self._queue.values())[offset:offset+limit]

    def get_job(self, dlq_id: str) -> Optional[DeadLetterJob]:
        return self._queue.get(dlq_id)

    def remove_job(self, dlq_id: str) -> bool:
        if dlq_id in self._queue:
            del self._queue[dlq_id]
            return True
        return False

    def purge(self) -> int:
        count = len(self._queue)
        self._queue.clear()
        return count

# Global instance
dead_letter_queue = DeadLetterQueue()
