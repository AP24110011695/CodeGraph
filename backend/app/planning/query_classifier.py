class QueryClassifier:
    """Classifies incoming user queries into distinct execution intents."""
    def classify(self, query: str) -> str:
        query_lower = query.lower()
        if "explain" in query_lower and "architecture" in query_lower:
            return "architecture_explanation"
        if "explain" in query_lower:
            return "concept_explanation"
        if "refactor" in query_lower or "improve" in query_lower or "suggest" in query_lower:
            return "code_modification"
        if "locate" in query_lower or "where" in query_lower or "find" in query_lower:
            return "code_location"
        if "impact" in query_lower or "depend" in query_lower:
            return "impact_analysis"
        return "general_query"
