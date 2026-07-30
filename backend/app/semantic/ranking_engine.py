"""Context-aware ranking for results supplied by the existing search service."""

from typing import Any


class RankingEngine:
    def rank(self, results: list[dict[str, Any]], related_paths: set[str], limit: int) -> list[dict[str, Any]]:
        ranked = []
        for result in results:
            item = dict(result)
            graph_bonus = 0.1 if item.get("path") in related_paths else 0.0
            item["context_score"] = round(min(1.0, float(item.get("score", 0)) + graph_bonus), 4)
            ranked.append(item)
        return sorted(ranked, key=lambda item: (-item["context_score"], item.get("path", "")))[:limit]
