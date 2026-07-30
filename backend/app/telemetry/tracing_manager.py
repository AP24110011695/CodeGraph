"""In-process tracing abstraction ready for OpenTelemetry exporters."""

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import threading
import time
import uuid
from collections import deque
from typing import Iterator, Optional

_correlation_id: ContextVar[Optional[str]] = ContextVar("telemetry_correlation_id", default=None)


@dataclass
class TraceRecord:
    trace_id: str
    operation: str
    component: str
    correlation_id: str
    started_at: datetime
    duration_ms: Optional[float] = None
    status: str = "running"


class TracingManager:
    def __init__(self, history_size: int = 200) -> None:
        self._traces: deque[TraceRecord] = deque(maxlen=history_size)
        self._lock = threading.Lock()

    def current_correlation_id(self) -> Optional[str]:
        return _correlation_id.get()

    @contextmanager
    def trace(self, operation: str, component: str, correlation_id: Optional[str] = None) -> Iterator[TraceRecord]:
        correlation = correlation_id or self.current_correlation_id() or str(uuid.uuid4())
        token = _correlation_id.set(correlation)
        record = TraceRecord(str(uuid.uuid4()), operation, component, correlation, datetime.now(timezone.utc))
        started = time.perf_counter()
        try:
            yield record
        except Exception:
            record.status = "error"
            raise
        else:
            record.status = "ok"
        finally:
            record.duration_ms = round((time.perf_counter() - started) * 1000, 3)
            with self._lock:
                self._traces.append(record)
            _correlation_id.reset(token)

    def recent(self) -> list[dict]:
        with self._lock:
            return [asdict(trace) for trace in reversed(self._traces)]
