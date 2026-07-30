"""Reusable duration tracking context manager."""

from contextlib import contextmanager
import time
from typing import Iterator

from app.telemetry.metrics_collector import MetricsCollector


class PerformanceTracker:
    def __init__(self, metrics: MetricsCollector) -> None:
        self._metrics = metrics

    @contextmanager
    def track(self, operation: str) -> Iterator[None]:
        started = time.perf_counter()
        try:
            yield
        finally:
            self._metrics.timing(operation, (time.perf_counter() - started) * 1000)

    def summary(self) -> dict:
        return self._metrics.snapshot()["timings"]
