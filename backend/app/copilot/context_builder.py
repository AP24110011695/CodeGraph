"""Context builder — assembles engineering + conversational context.

Does not duplicate retrieval: reuses Repository Memory and RAG when available.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.cache.cache_interface import CacheInterface
from app.cache.cache_keys import CacheKeys
from app.cache.cache_manager import cache_manager

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds Copilot context from conversation history and existing intelligence."""

    def __init__(
        self,
        memory_engine=None,
        rag_engine=None,
        cache: Optional[CacheInterface] = None,
    ) -> None:
        self._memory_engine = memory_engine
        self._rag_engine = rag_engine
        self._cache = cache or cache_manager

    def _memory(self):
        if self._memory_engine is None:
            from app.repository_memory.memory_engine import memory_engine

            self._memory_engine = memory_engine
        return self._memory_engine

    def _rag(self):
        if self._rag_engine is None:
            from app.rag.rag_engine import rag_engine

            self._rag_engine = rag_engine
        return self._rag_engine

    def build(
        self,
        repository_id: str,
        query: str,
        conversation_turns: Optional[List[Dict[str, Any]]] = None,
        plan: Optional[Dict[str, Any]] = None,
        shared_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Assemble context for orchestration and prompt construction."""
        modules = list((plan or {}).get("execution_order") or (plan or {}).get("required_modules") or [])
        needs_rag = (not modules) or any(
            m in ("RAG Engine", "rag", "Semantic Engine") for m in modules
        )
        needs_memory = (not modules) or any(
            m in ("Repository Memory", "repository_memory", "Timeline Intelligence Engine")
            for m in modules
        )

        memory_summary = None
        architecture_summary = None
        if needs_memory:
            cache_key = CacheKeys.copilot_context(repository_id, "memory_fragments")
            repo_fragment = self._cache.get(cache_key)
            try:
                if repo_fragment and isinstance(repo_fragment, dict):
                    memory_summary = repo_fragment.get("memory_summary")
                    architecture_summary = repo_fragment.get("architecture_summary")
                else:
                    summary = self._memory().get_memory_summary(repository_id)
                    if summary is None:
                        try:
                            self._memory().build_memory(repository_id)
                            summary = self._memory().get_memory_summary(repository_id)
                        except Exception as exc:  # noqa: BLE001
                            logger.debug("ContextBuilder: memory build skipped: %s", exc)
                    if summary is not None:
                        memory_summary = (
                            summary.model_dump(mode="json")
                            if hasattr(summary, "model_dump")
                            else dict(summary)
                        )
                        architecture_summary = getattr(summary, "architecture_summary", None)
                        self._cache.set(
                            cache_key,
                            {
                                "memory_summary": memory_summary,
                                "architecture_summary": architecture_summary,
                            },
                            ttl_seconds=120,
                        )
            except Exception as exc:  # noqa: BLE001
                logger.debug("ContextBuilder: memory enrichment failed: %s", exc)

        rag_context = None
        rag_citations: List[Any] = []
        if needs_rag:
            try:
                rag = self._rag().generate_context(repository_id, query, max_tokens=2000)
                rag_context = rag.llm_context
                rag_citations = [
                    c.model_dump(mode="json") if hasattr(c, "model_dump") else c
                    for c in (rag.citations or [])
                ]
            except Exception as exc:  # noqa: BLE001
                logger.debug("ContextBuilder: RAG enrichment failed: %s", exc)

        touched = []
        if memory_summary:
            touched.append("Repository Memory")
        if rag_context:
            touched.append("Advanced RAG")

        return {
            "repository_id": repository_id,
            "query": query,
            "plan": plan or {},
            "conversation_turns": conversation_turns or [],
            "shared_context": shared_context or {},
            "memory_summary": memory_summary,
            "architecture_summary": architecture_summary,
            "rag_context": rag_context,
            "rag_citations": rag_citations,
            "modules_touched": touched,
        }


context_builder = ContextBuilder()
