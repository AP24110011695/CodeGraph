import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

# Intents for which broad memory context (repo overview, architecture) is useful
_BROAD_MEMORY_INTENTS = {
    "architecture_explanation",
    "tech_stack_query",
    "general_explanation",
    "mechanism_explanation",
}


class ContextSelector:
    """Selects contextual facts from memory, semantic engine, knowledge graph, and timeline."""

    def select_memory_context(self, repository_id: str, intent: str = "general_explanation") -> List[Dict]:
        """Fetch high-level facts from the Repository Memory Engine.

        Only returns generic repository/architecture overview for intents where it is
        broadly useful.  Targeted intents (security, coupling, etc.) should use
        dedicated tools instead, so memory noise is avoided.
        """
        if intent not in _BROAD_MEMORY_INTENTS:
            return []

        items = []
        try:
            from app.repository_memory.memory_engine import memory_engine
            memory = memory_engine.get_memory_summary(repository_id)
            if memory:
                if memory.repository_summary:
                    items.append({
                        "source_type": "memory",
                        "reference": "Repository Overview",
                        "content": memory.repository_summary,
                    })
                if memory.architecture_summary:
                    items.append({
                        "source_type": "memory",
                        "reference": "Architecture Overview",
                        "content": memory.architecture_summary,
                    })
        except Exception as exc:  # noqa: BLE001
            logger.debug("Memory context unavailable: %s", exc)
        return items

    def select_semantic_context(self, repository_id: str, query: str) -> List[Dict]:
        """Fetch chunks from the Semantic Engine / Vector Store using the current query."""
        items = []
        try:
            from app.api.semantic import semantic_engine
            from app.api.search import _project_path
            path = _project_path(repository_id)
            if path and path.exists():
                res = semantic_engine.search(repository_id, query, path, mode="semantic", limit=5)
                for rank_item in res.get("results", []):
                    snippet = rank_item.get("snippet", "").strip()
                    if not snippet:
                        continue
                    items.append({
                        "source_type": "semantic",
                        "reference": rank_item.get("path", "unknown"),
                        "content": snippet,
                        "score": rank_item.get("context_score", 0.0),
                    })
        except Exception as exc:
            logger.debug("Semantic context unavailable: %s", exc)
        return items

    def select_graph_context(self, repository_id: str, entities: List[str]) -> List[Dict]:
        """Fetch dependencies from Knowledge Graph for specific entities."""
        return []

    def select_timeline_context(self, repository_id: str, query: str = "") -> List[Dict]:
        """Fetch evolution / hotspot facts from Timeline Intelligence."""
        items: List[Dict] = []
        try:
            from app.timeline.timeline_engine import timeline_engine

            if query:
                answer = timeline_engine.answer(repository_id, query)
                items.append({
                    "source_type": "timeline",
                    "reference": "Timeline Answer",
                    "content": answer,
                })
            else:
                summary = timeline_engine.get_timeline(repository_id).historical_summary
                items.append({
                    "source_type": "timeline",
                    "reference": "Historical Summary",
                    "content": summary.narrative,
                })
        except Exception as exc:  # noqa: BLE001
            logger.debug("Timeline context unavailable: %s", exc)
        return items