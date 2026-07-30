"""Backend-independent contract for CodeGraph's distributed cache."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class CacheInterface(ABC):
    """Synchronous cache contract implemented by memory and future Redis stores."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Return a cached value, or ``None`` on a miss."""

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        """Store a value with an optional time-to-live."""

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Remove one value and return whether it existed."""

    @abstractmethod
    def clear(self) -> int:
        """Remove all values and return the number removed."""

    @abstractmethod
    def invalidate(self, prefix: str) -> int:
        """Remove values whose keys begin with the supplied namespace prefix."""

    @abstractmethod
    def stats(self) -> dict[str, Any]:
        """Return backend-neutral cache statistics."""
