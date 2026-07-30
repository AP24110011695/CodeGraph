import logging
from typing import Dict, Any, Optional
from app.reliability.idempotency_manager import idempotency_manager
import queue

logger = logging.getLogger(__name__)

class TaskRouter:
    """Routes tasks to workers independent of underlying queue implementation."""
    
    def __init__(self):
        # Fallback in-memory queue for tasks
        self._queue = queue.Queue()
        
    def route_task(self, task_type: str, repository_id: str, context_data: Dict[str, Any]) -> None:
        """Route task to appropriate worker queue."""
        fingerprint = idempotency_manager.generate_fingerprint(task_type, repository_id, context_data)
        if not idempotency_manager.mark_execution_started("queued", fingerprint):
            logger.info(f"Duplicate task ignored: {task_type} for {repository_id}")
            return

        # For in-memory implementation, we just queue it locally
        task_data = {
            "task_type": task_type,
            "repository_id": repository_id,
            "context": context_data
        }
        self._queue.put(task_data)
        logger.info(f"Routed task {task_type} for {repository_id}")
        
    def get_next_task(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """Get next available task from queue."""
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

# Global router
task_router = TaskRouter()
