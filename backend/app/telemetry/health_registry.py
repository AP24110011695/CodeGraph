"""Registry for component health probes."""

import threading
from typing import Callable


class HealthRegistry:
    def __init__(self) -> None:
        self._checks: dict[str, Callable[[], dict]] = {}
        self._lock = threading.RLock()

    def register(self, component: str, check: Callable[[], dict]) -> None:
        with self._lock:
            self._checks[component] = check

    def checks(self) -> dict[str, Callable[[], dict]]:
        with self._lock:
            return dict(self._checks)
