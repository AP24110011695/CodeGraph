"""Cache metrics shared by all cache backends."""

from dataclasses import dataclass


@dataclass
class CacheMetrics:
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletions: int = 0
    evictions: int = 0
    expirations: int = 0

    def snapshot(self, entries: int, max_entries: int) -> dict[str, int | float]:
        requests = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletions": self.deletions,
            "evictions": self.evictions,
            "expirations": self.expirations,
            "entries": entries,
            "max_entries": max_entries,
            "hit_rate": self.hits / requests if requests else 0.0,
        }
