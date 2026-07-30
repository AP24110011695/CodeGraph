class ReasoningStrategy:
    """Determines which higher-level engine to route context to for LLM generation."""
    def determine(self, intent: str) -> str:
        if intent in ["architecture_explanation", "impact_analysis"]:
            if intent == "impact_analysis":
                return "Impact Analysis Engine"
            return "Architecture Reasoning Engine"
        elif intent == "timeline_analysis":
            return "Timeline Intelligence Engine"
        elif intent == "code_modification":
            return "Code Generation / Refactoring Agent"
        else:
            return "Standard LLM Generation"
