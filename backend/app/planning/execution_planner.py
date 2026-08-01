from typing import List


class ExecutionPlanner:
    """Builds a deterministic execution graph for the required engines."""

    # Maps each intent to the minimal set of tools needed
    _INTENT_MODULES: dict[str, List[str]] = {
        "architecture_explanation": ["RAG Engine", "Architecture Reasoning Engine"],
        "timeline_analysis": ["Timeline Intelligence Engine", "Repository Memory"],
        "concept_explanation": ["RAG Engine"],
        "impact_analysis": ["Impact Analysis Engine", "Knowledge Graph", "Architecture Reasoning Engine"],
        "code_modification": ["Semantic Engine", "Refactoring Engine"],
        "code_location": ["Semantic Engine"],
        "coupling_analysis": ["Knowledge Graph", "RAG Engine"],
        "security_analysis": ["Engineering Reports", "RAG Engine"],
        "tech_stack_query": ["Repository Memory", "RAG Engine"],
        "quality_analysis": ["Engineering Reports", "RAG Engine"],
        "general_query": ["RAG Engine"],
    }

    def plan_modules(self, intent: str) -> List[str]:
        return list(self._INTENT_MODULES.get(intent, self._INTENT_MODULES["general_query"]))

    def order_modules(self, modules: List[str]) -> List[str]:
        order = []
        # Logical layering: Data/Context fetchers go before Reasoners/Generators
        phases = [
            [
                "Knowledge Graph",
                "Semantic Engine",
                "RAG Engine",
                "Repository Memory",
                "Timeline Intelligence Engine",
                "Impact Analysis Engine",
                "Engineering Reports",
            ],
            ["Architecture Reasoning Engine", "Refactoring Engine"],
        ]
        for phase in phases:
            for mod in modules:
                if mod in phase and mod not in order:
                    order.append(mod)
        for mod in modules:
            if mod not in order:
                order.append(mod)
        return order

    def estimate_cost(self, modules: List[str]) -> str:
        if "Architecture Reasoning Engine" in modules or "Refactoring Engine" in modules:
            return "High"
        if (
            "RAG Engine" in modules
            or "Timeline Intelligence Engine" in modules
            or "Impact Analysis Engine" in modules
            or "Engineering Reports" in modules
        ):
            return "Medium"
        return "Low"
