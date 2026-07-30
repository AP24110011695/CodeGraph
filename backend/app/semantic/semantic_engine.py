"""Primary semantic intelligence facade composed from existing repository modules."""

import hashlib
from pathlib import Path
from typing import Any, Callable, Literal

from app.cache.cache_keys import CacheKeys
from app.cache.cache_interface import CacheInterface
from app.cache.cache_manager import cache_manager
from app.semantic.context_builder import ContextBuilder
from app.semantic.ranking_engine import RankingEngine
from app.semantic.relationship_traverser import RelationshipTraverser
from app.semantic.semantic_search import SemanticSearch
from app.semantic.symbol_resolver import SymbolResolver


class SemanticEngine:
    def __init__(
        self,
        semantic_search: SemanticSearch,
        graph_provider: Callable[[str, Path], Any],
        cache: CacheInterface = cache_manager,
        context_builder: ContextBuilder | None = None,
        ranking_engine: RankingEngine | None = None,
        symbol_resolver: SymbolResolver | None = None,
        relationship_traverser: RelationshipTraverser | None = None,
    ) -> None:
        self._semantic_search = semantic_search
        self._graph_provider = graph_provider
        self._cache = cache
        self._context_builder = context_builder or ContextBuilder()
        self._ranking_engine = ranking_engine or RankingEngine()
        self._symbol_resolver = symbol_resolver or SymbolResolver()
        self._relationship_traverser = relationship_traverser or RelationshipTraverser()

    def search(self, repository_id: str, query: str, project_path: Path, mode: Literal["semantic", "hybrid"] = "hybrid", limit: int = 10) -> dict:
        digest = hashlib.sha256(f"{mode}:{limit}:{query.strip().lower()}".encode()).hexdigest()
        key = CacheKeys.search_results(repository_id, f"semantic:{digest}")
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        results = self._semantic_search.search(repository_id, query, project_path, mode, limit)
        graph = self._graph_provider(repository_id, project_path)
        symbols = self._symbol_resolver.resolve(query, graph)
        relationships = self._relationship_traverser.traverse(graph, [symbol["id"] for symbol in symbols])
        context = self._context_builder.build(results, symbols, relationships)
        ranked = self._ranking_engine.rank(context["results"], context["related_paths"], limit)
        response = {
            "query": query,
            "mode": mode,
            "results": ranked,
            "symbols": symbols,
            "relationships": relationships,
            "total": len(ranked),
        }
        self._cache.set(key, response)
        return response
