"""Hybrid ranking utilities for repository search results."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SearchCandidate:
    """Internal candidate used for semantic, keyword, and hybrid ranking."""

    path: str
    score: float
    snippet: str
    language: str
    line_start: int
    line_end: int
    semantic_score: float = 0.0
    keyword_score: float = 0.0
    file_relevance: float = 0.0


class HybridRanker:
    """Combine semantic and keyword signals into final ranked results."""

    def rank(
        self,
        semantic: list[SearchCandidate],
        keyword: list[SearchCandidate],
        limit: int = 10,
    ) -> list[SearchCandidate]:
        merged: dict[tuple[str, int, int, str], SearchCandidate] = {}

        for candidate in semantic:
            key = self._key(candidate)
            current = merged.get(key)
            if current is None:
                merged[key] = candidate
            else:
                current.semantic_score = max(current.semantic_score, candidate.semantic_score)
                current.score = max(current.score, candidate.score)

        for candidate in keyword:
            key = self._key(candidate)
            current = merged.get(key)
            if current is None:
                merged[key] = candidate
            else:
                current.keyword_score = max(current.keyword_score, candidate.keyword_score)
                current.file_relevance = max(current.file_relevance, candidate.file_relevance)
                if len(candidate.snippet) > len(current.snippet):
                    current.snippet = candidate.snippet
                current.score = max(current.score, candidate.score)

        ranked: list[SearchCandidate] = []
        for candidate in merged.values():
            candidate.score = self._combined_score(candidate)
            ranked.append(candidate)

        ranked.sort(key=lambda item: (-item.score, item.path, item.line_start, item.line_end))
        return ranked[:limit]

    def deduplicate(self, candidates: list[SearchCandidate], limit: int = 10) -> list[SearchCandidate]:
        unique: dict[tuple[str, int, int, str], SearchCandidate] = {}
        for candidate in candidates:
            key = self._key(candidate)
            existing = unique.get(key)
            if existing is None or candidate.score > existing.score:
                unique[key] = candidate
        ranked = sorted(unique.values(), key=lambda item: (-item.score, item.path, item.line_start, item.line_end))
        return ranked[:limit]

    def _combined_score(self, candidate: SearchCandidate) -> float:
        score = (
            candidate.semantic_score * 0.55
            + candidate.keyword_score * 0.35
            + candidate.file_relevance * 0.10
        )
        return max(0.0, min(1.0, score))

    def _key(self, candidate: SearchCandidate) -> tuple[str, int, int, str]:
        return (candidate.path, candidate.line_start, candidate.line_end, candidate.snippet)


hybrid_ranker = HybridRanker()
