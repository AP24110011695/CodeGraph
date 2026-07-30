"""Thread-safe, exporter-neutral metric collection."""

import threading
from collections import defaultdict
from typing import Dict


class MetricsCollector:
    def __init__(self) -> None:
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._timings: Dict[str, list[float]] = defaultdict(list)
        self._lock = threading.RLock()

    def increment(self, name: str, value: float = 1) -> None:
        with self._lock:
            self._counters[name] += value

    def gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = value

    def timing(self, name: str, duration_ms: float) -> None:
        with self._lock:
            self._timings[name].append(duration_ms)

    def snapshot(self) -> dict:
        with self._lock:
            timings = {
                name: {
                    "count": len(values),
                    "total_ms": round(sum(values), 3),
                    "average_ms": round(sum(values) / len(values), 3) if values else 0.0,
                    "max_ms": round(max(values), 3) if values else 0.0,
                }
                for name, values in self._timings.items()
            }
            return {"counters": dict(self._counters), "gauges": dict(self._gauges), "timings": timings}
