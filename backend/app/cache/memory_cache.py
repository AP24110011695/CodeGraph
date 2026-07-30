"""Thread-safe in-memory implementation of :class:`CacheInterface`."""

from collections import OrderedDict
from dataclasses import dataclass
import threading
import time
from typing import Any, Optional

from app.cache.cache_interface import CacheInterface
from app.cache.cache_metrics import CacheMetrics


@dataclass
class _CacheEntry:
    value: Any
    expires_at: Optional[float]


class MemoryCache(CacheInterface):
    """Bounded LRU cache with lazy TTL expiry; suitable for a single process."""

    def __init__(self, max_entries: int = 1_000) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be at least 1")
        self._max_entries = max_entries
        self._entries: OrderedDict[str, _CacheEntry] = OrderedDict()
        self._metrics = CacheMetrics()
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                self._metrics.misses += 1
                return None
            if entry.expires_at is not None and entry.expires_at <= time.monotonic():
                del self._entries[key]
                self._metrics.misses += 1
                self._metrics.expirations += 1
                return None
            self._entries.move_to_end(key)
            self._metrics.hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        if ttl_seconds is not None and ttl_seconds <= 0:
            self.delete(key)
            return
        expires_at = time.monotonic() + ttl_seconds if ttl_seconds is not None else None
        with self._lock:
            self._entries[key] = _CacheEntry(value=value, expires_at=expires_at)
            self._entries.move_to_end(key)
            self._metrics.sets += 1
            while len(self._entries) > self._max_entries:
                self._entries.popitem(last=False)
                self._metrics.evictions += 1

    def delete(self, key: str) -> bool:
        with self._lock:
            if key not in self._entries:
                return False
            del self._entries[key]
            self._metrics.deletions += 1
            return True

    def clear(self) -> int:
        with self._lock:
            removed = len(self._entries)
            self._entries.clear()
            self._metrics.deletions += removed
            return removed

    def invalidate(self, prefix: str) -> int:
        with self._lock:
            keys = [key for key in self._entries if key.startswith(prefix)]
            for key in keys:
                del self._entries[key]
            self._metrics.deletions += len(keys)
            return len(keys)

    def stats(self) -> dict[str, Any]:
        with self._lock:
            # Remove expired entries before reporting current capacity.
            now = time.monotonic()
            expired = [key for key, entry in self._entries.items()
                       if entry.expires_at is not None and entry.expires_at <= now]
            for key in expired:
                del self._entries[key]
            self._metrics.expirations += len(expired)
            return self._metrics.snapshot(len(self._entries), self._max_entries)
