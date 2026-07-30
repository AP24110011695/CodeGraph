class RetrievalStrategy:
    """Selects the optimal data retrieval pattern before execution begins."""
    def determine(self, intent: str) -> str:
        if intent == "architecture_explanation":
            return "RAG Engine (Memory + Semantic + Graph)"
        elif intent == "code_location":
            return "Semantic Search Only"
        elif intent == "impact_analysis":
            return "Knowledge Graph Only"
        else:
            return "Hybrid (Semantic + Memory)"
