from typing import List

class ExecutionPlanner:
    """Builds a deterministic execution graph for the required engines."""
    def plan_modules(self, intent: str) -> List[str]:
        if intent == "architecture_explanation":
            return ["RAG Engine", "Architecture Reasoning Engine"]
        elif intent == "concept_explanation":
            return ["RAG Engine"]
        elif intent == "impact_analysis":
            return ["Knowledge Graph", "Architecture Reasoning Engine"]
        elif intent == "code_modification":
            return ["Semantic Engine", "Refactoring Engine"]
        elif intent == "code_location":
            return ["Semantic Engine"]
        return ["RAG Engine"]

    def order_modules(self, modules: List[str]) -> List[str]:
        order = []
        # Logical layering: Data/Context fetchers go before Reasoners/Generators
        phases = [
            ["Knowledge Graph", "Semantic Engine", "RAG Engine"], 
            ["Architecture Reasoning Engine", "Refactoring Engine"]
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
        if "RAG Engine" in modules:
            return "Medium"
        return "Low"
