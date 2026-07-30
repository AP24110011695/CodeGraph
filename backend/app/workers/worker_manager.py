import logging
import threading
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta

from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class WorkerStatus(str, Enum):
    IDLE = "IDLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"
    STARTING = "STARTING"
    STOPPING = "STOPPING"


class WorkerHealth(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"


class WorkerInfo(BaseModel):
    """Serialisable snapshot of a worker's status."""

    worker_id: str
    status: WorkerStatus = WorkerStatus.STARTING
    health: WorkerHealth = WorkerHealth.HEALTHY
    current_task: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkerManager:
    """Thread-safe registry for worker registration, heartbeats, and health checks."""

    HEARTBEAT_TIMEOUT_SECS: int = 30

    def __init__(self) -> None:
        self._workers: Dict[str, WorkerInfo] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # Registration                                                          #
    # ------------------------------------------------------------------ #

    def register_worker(self, worker_id: str, capabilities: List[str]) -> WorkerInfo:
        with self._lock:
            info = WorkerInfo(
                worker_id=worker_id,
                capabilities=capabilities,
                status=WorkerStatus.IDLE,
            )
            self._workers[worker_id] = info
            logger.info(f"[WorkerManager] Registered {worker_id} capabilities={capabilities}")
            return info

    def deregister_worker(self, worker_id: str) -> None:
        with self._lock:
            self._workers.pop(worker_id, None)
            logger.info(f"[WorkerManager] Deregistered {worker_id}")

    # ------------------------------------------------------------------ #
    # Heartbeat                                                             #
    # ------------------------------------------------------------------ #

    def heartbeat(
        self,
        worker_id: str,
        status: Optional[WorkerStatus] = None,
        current_task: Optional[str] = None,
    ) -> None:
        with self._lock:
            w = self._workers.get(worker_id)
            if not w:
                return
            w.last_heartbeat = datetime.now(timezone.utc)
            w.health = WorkerHealth.HEALTHY
            if status is not None:
                w.status = status
            if current_task is not None:
                w.current_task = current_task
            elif status in (WorkerStatus.IDLE, WorkerStatus.STOPPING, WorkerStatus.OFFLINE):
                w.current_task = None

    # ------------------------------------------------------------------ #
    # Health check                                                          #
    # ------------------------------------------------------------------ #

    def check_health(self) -> None:
        """Mark stale workers DEGRADED or OFFLINE based on heartbeat age."""
        now = datetime.now(timezone.utc)
        with self._lock:
            for w in self._workers.values():
                if w.status == WorkerStatus.OFFLINE:
                    continue
                age = (now - w.last_heartbeat).total_seconds()
                if age > self.HEARTBEAT_TIMEOUT_SECS * 2:
                    w.status = WorkerStatus.OFFLINE
                    w.health = WorkerHealth.UNHEALTHY
                    logger.warning(f"[WorkerManager] {w.worker_id} OFFLINE (heartbeat age {age:.0f}s)")
                elif age > self.HEARTBEAT_TIMEOUT_SECS:
                    w.health = WorkerHealth.DEGRADED
                    logger.warning(f"[WorkerManager] {w.worker_id} DEGRADED")

    # ------------------------------------------------------------------ #
    # Queries                                                               #
    # ------------------------------------------------------------------ #

    def get_workers(self) -> List[WorkerInfo]:
        with self._lock:
            return list(self._workers.values())

    def get_idle_workers(self, required_capability: Optional[str] = None) -> List[WorkerInfo]:
        with self._lock:
            return [
                w for w in self._workers.values()
                if w.status == WorkerStatus.IDLE
                and w.health == WorkerHealth.HEALTHY
                and (not required_capability or required_capability in w.capabilities)
            ]

    def get_worker(self, worker_id: str) -> Optional[WorkerInfo]:
        with self._lock:
            return self._workers.get(worker_id)


# Global singleton — shared across WorkerPool and the API layer
worker_manager = WorkerManager()
