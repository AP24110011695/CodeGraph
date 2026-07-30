import threading
import time
import logging
import uuid
from typing import List, Optional

from app.workers.worker_manager import worker_manager, WorkerManager, WorkerStatus
from app.workers.task_router import task_router
from app.workers.task_executor import task_executor
from app.events.event_bus import event_bus
from app.events.event_types import EventType

logger = logging.getLogger(__name__)


class WorkerThread(threading.Thread):
    """A single concurrent worker — polls the task router and executes tasks.

    * Heartbeats the WorkerManager every poll cycle so health checks work.
    * Publishes JOB_COMPLETED / JOB_FAILED via EventBus for WorkflowExecutor.
    * Never contains business logic — delegates all execution to TaskExecutor.
    """

    def __init__(self, manager: WorkerManager, capabilities: List[str]) -> None:
        super().__init__(daemon=True)
        self.worker_id = f"worker-{uuid.uuid4().hex[:8]}"
        self.name = self.worker_id
        self.capabilities = capabilities
        self._manager = manager
        self._running = False

        # Register immediately so the API can see this worker before start()
        self._manager.register_worker(self.worker_id, self.capabilities)

    def stop(self) -> None:
        """Signal graceful shutdown."""
        self._running = False
        self._manager.heartbeat(self.worker_id, WorkerStatus.STOPPING)

    def run(self) -> None:
        self._running = True
        logger.info(f"[{self.worker_id}] Started")

        while self._running:
            # Heartbeat idle before blocking on the queue
            self._manager.heartbeat(self.worker_id, WorkerStatus.IDLE)

            task = task_router.get_next_task(timeout=2.0)
            if task is None:
                continue

            task_type: str = task["task_type"]
            repository_id: str = task["repository_id"]
            context_data: dict = task.get("context", {})

            self._manager.heartbeat(
                self.worker_id, WorkerStatus.BUSY, current_task=task_type
            )
            logger.info(f"[{self.worker_id}] Executing '{task_type}' for '{repository_id}'")

            try:
                result = task_executor.execute(
                    task_type=task_type,
                    repository_id=repository_id,
                    context=context_data,
                )
                event_bus.publish(
                    event_type=EventType.JOB_COMPLETED,
                    repository_id=repository_id,
                    payload={
                        "task_type": task_type,
                        "result": result,
                        "context": context_data,
                    },
                    correlation_id=context_data.get("correlation_id"),
                )

            except Exception as exc:
                logger.error(
                    f"[{self.worker_id}] Failed '{task_type}': {exc}", exc_info=True
                )
                event_bus.publish(
                    event_type=EventType.JOB_FAILED,
                    repository_id=repository_id,
                    payload={
                        "task_type": task_type,
                        "error": str(exc),
                        "context": context_data,
                    },
                    correlation_id=context_data.get("correlation_id"),
                )

        self._manager.heartbeat(self.worker_id, WorkerStatus.OFFLINE)
        self._manager.deregister_worker(self.worker_id)
        logger.info(f"[{self.worker_id}] Stopped")


class WorkerPool:
    """Manages a pool of WorkerThreads with health monitoring.

    Uses the shared global `worker_manager` singleton so the API layer
    always sees the same worker registry.
    """

    def __init__(self, num_workers: int = 3) -> None:
        self.num_workers = num_workers
        self._workers: List[WorkerThread] = []
        self._health_thread: Optional[threading.Thread] = None
        self._started = False

    # ------------------------------------------------------------------ #
    # Lifecycle                                                             #
    # ------------------------------------------------------------------ #

    def start(self) -> None:
        if self._started:
            return
        self._started = True

        for _ in range(self.num_workers):
            w = WorkerThread(worker_manager, capabilities=["all"])
            w.start()
            self._workers.append(w)
            logger.info(f"[WorkerPool] Spawned {w.worker_id}")

        self._health_thread = threading.Thread(
            target=self._health_loop, daemon=True, name="worker-health-monitor"
        )
        self._health_thread.start()
        logger.info(f"[WorkerPool] Ready — {self.num_workers} workers active")

    def stop(self) -> None:
        """Graceful shutdown: signal workers then wait."""
        logger.info("[WorkerPool] Initiating graceful shutdown…")
        for w in self._workers:
            w.stop()
        for w in self._workers:
            w.join(timeout=10.0)
            if w.is_alive():
                logger.warning(f"[WorkerPool] {w.worker_id} did not exit in time")
        self._workers.clear()
        self._started = False
        logger.info("[WorkerPool] All workers stopped")

    # ------------------------------------------------------------------ #
    # Introspection                                                         #
    # ------------------------------------------------------------------ #

    def active_count(self) -> int:
        return sum(1 for w in self._workers if w.is_alive())

    # ------------------------------------------------------------------ #
    # Health loop                                                           #
    # ------------------------------------------------------------------ #

    def _health_loop(self) -> None:
        while True:
            time.sleep(15)
            worker_manager.check_health()


# Global singleton
worker_pool = WorkerPool()
