from typing import Any, Dict

from app.timeline.timeline_engine import timeline_engine

from ..base_agent import BaseAgent


class TimelineAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "TimelineAgent"

    @property
    def description(self) -> str:
        return "Analyzes repository evolution, hotspots, ownership, and architecture drift over time."

    @property
    def capabilities(self) -> list[str]:
        return [
            "repository timeline",
            "evolution tracking",
            "hotspot detection",
            "ownership analysis",
            "architecture drift over time",
        ]

    def execute(self, repository_id: str, query: str, context: Dict[str, Any]) -> str:
        return timeline_engine.answer(repository_id, query)
