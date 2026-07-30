class QueryClassifier:
    """Classifies incoming user queries into distinct execution intents."""
    def classify(self, query: str) -> str:
        query_lower = query.lower()
        if any(
            phrase in query_lower
            for phrase in (
                "timeline",
                "what changed",
                "changed the most",
                "evolve together",
                "unstable",
                "hotspot",
                "ownership",
                "how has the architecture",
                "tightly coupled",
                "change frequently",
                "repository history",
            )
        ):
            return "timeline_analysis"
        if "explain" in query_lower and "architecture" in query_lower:
            return "architecture_explanation"
        if "explain" in query_lower:
            return "concept_explanation"
        if "refactor" in query_lower or "improve" in query_lower or "suggest" in query_lower:
            return "code_modification"
        if "locate" in query_lower or "where" in query_lower or "find" in query_lower:
            return "code_location"
        if any(
            phrase in query_lower
            for phrase in (
                "impact",
                "depend",
                "what breaks",
                "blast radius",
                "propagation",
                "if i modify",
                "change risk",
                "will be affected",
            )
        ):
            return "impact_analysis"
        return "general_query"
