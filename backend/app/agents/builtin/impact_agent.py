from typing import Any, Dict

from app.impact_analysis.impact_engine import impact_engine

from ..base_agent import BaseAgent


class ImpactAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "ImpactAgent"

    @property
    def description(self) -> str:
        return "Predicts blast radius, propagation paths, and change risk before code changes land."

    @property
    def capabilities(self) -> list[str]:
        return [
            "dependency impact",
            "architecture impact",
            "API impact",
            "change propagation",
            "change risk estimation",
        ]

    def execute(self, repository_id: str, query: str, context: Dict[str, Any]) -> str:
        return impact_engine.answer(repository_id, query)
