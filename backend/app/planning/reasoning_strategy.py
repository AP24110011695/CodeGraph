class ReasoningStrategy:
    """Determines which higher-level engine to route context to for LLM generation."""
    def determine(self, intent: str) -> str:
        if intent in ["architecture_explanation", "impact_analysis"]:
            return "Architecture Reasoning Engine"
        elif intent == "code_modification":
            return "Code Generation / Refactoring Agent"
        else:
            return "Standard LLM Generation"
