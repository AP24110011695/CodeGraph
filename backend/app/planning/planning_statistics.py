from typing import List

class PlanningStatistics:
    """Computes confidence and metadata concerning the generated plan."""
    def calculate_confidence(self, intent: str, modules: List[str]) -> float:
        if intent == "general_query":
            return 0.5
        if modules:
            return 0.95
        return 0.7
