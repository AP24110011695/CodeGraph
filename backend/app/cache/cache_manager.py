"""Cache facade used by business modules through the CacheInterface contract."""

from typing import Any, Optional

from app.cache.cache_interface import CacheInterface
from app.cache.memory_cache import MemoryCache


class CacheManager(CacheInterface):
    def __init__(self, backend: Optional[CacheInterface] = None, default_ttl_seconds: Optional[float] = 300) -> None:
        self._backend: CacheInterface = backend or MemoryCache()
        self._default_ttl_seconds = default_ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        return self._backend.get(key)

    def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        self._backend.set(
            key, value,
            self._default_ttl_seconds if ttl_seconds is None else ttl_seconds,
        )

    def delete(self, key: str) -> bool:
        return self._backend.delete(key)

    def clear(self) -> int:
        return self._backend.clear()

    def invalidate(self, namespace: str) -> int:
        return self._backend.invalidate(namespace if namespace.endswith(":") else f"{namespace}:")

    def stats(self) -> dict[str, Any]:
        return self._backend.stats()


cache_manager = CacheManager()


def get_cache() -> CacheInterface:
    """Dependency-injection provider for business modules and future backends."""
    return cache_manager
