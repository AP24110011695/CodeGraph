import logging
from typing import Optional, List, Dict
from app.repository_memory.memory_engine import memory_engine

logger = logging.getLogger(__name__)

class ContextSelector:
    """Selects contextual facts from memory, semantic engine, knowledge graph, and timeline."""
    
    def select_memory_context(self, repository_id: str) -> List[Dict]:
        """Fetch high-level facts from the Repository Memory Engine."""
        items = []
        memory = memory_engine.get_memory_summary(repository_id)
        if memory:
            items.append({
                "source_type": "memory",
                "reference": "Repository Overview",
                "content": memory.repository_summary
            })
            items.append({
                "source_type": "memory",
                "reference": "Architecture Overview",
                "content": memory.architecture_summary
            })
        return items

    def select_semantic_context(self, repository_id: str, query: str) -> List[Dict]:
        """Fetch chunks from the standard Semantic Engine / Vector Store."""
        # Simulated retrieval - in a full implementation this queries the semantic engine
        return []

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