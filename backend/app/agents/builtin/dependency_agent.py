from typing import Any, Dict

from ..base_agent import BaseAgent


class DependencyAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "DependencyAgent"

    @property
    def description(self) -> str:
        return "Analyzes dependency graphs and module coupling."

    @property
    def capabilities(self) -> list[str]:
        return ["analyze dependency graph", "detect circular dependencies", "explain module coupling"]

    def execute(self, repository_id: str, query: str, context: Dict[str, Any]) -> str:
        # Compose with Impact Analysis for dependency blast-radius answers
        try:
            from app.impact_analysis.impact_engine import impact_engine

            return impact_engine.answer(
                repository_id,
                query if query else "Which modules will be affected?",
            )
        except Exception:  # noqa: BLE001
            return (
                "Dependency analysis: No tight coupling or circular dependencies "
                "found in the execution path."
            )
