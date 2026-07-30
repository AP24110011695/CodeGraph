"""Structured log event collector with standard-library logging output."""

from collections import deque
from datetime import datetime, timezone
import logging
import threading
from typing import Any, Optional


class LoggerManager:
    def __init__(self, history_size: int = 200) -> None:
        self._records: deque[dict] = deque(maxlen=history_size)
        self._lock = threading.Lock()

    def log(self, component: str, message: str, level: str = "INFO", correlation_id: Optional[str] = None, **fields: Any) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level.upper(),
            "component": component,
            "message": message,
            "correlation_id": correlation_id,
            "fields": fields,
        }
        with self._lock:
            self._records.append(record)
        getattr(logging.getLogger(component), level.lower(), logging.getLogger(component).info)(message)

    def recent(self) -> list[dict]:
        with self._lock:
            return list(self._records)
