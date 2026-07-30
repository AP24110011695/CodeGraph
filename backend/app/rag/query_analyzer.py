class QueryAnalyzer:
    """Analyzes user queries to determine retrieval intent and extract entities."""
    
    def analyze(self, query: str) -> dict:
        query_lower = query.lower()
        intent = "general_explanation"
        
        if any(
            phrase in query_lower
            for phrase in (
                "timeline",
                "what changed",
                "hotspot",
                "unstable",
                "evolve",
                "ownership",
            )
        ):
            intent = "timeline_analysis"
        elif "where" in query_lower or "find" in query_lower:
            intent = "location_search"
        elif "how" in query_lower or "explain" in query_lower:
            intent = "mechanism_explanation"
        elif "depend" in query_lower or "call" in query_lower or "use" in query_lower:
            intent = "dependency_analysis"
        elif "first" in query_lower or "start" in query_lower:
            intent = "entry_point_discovery"
            
        return {
            "intent": intent,
            "entities": self._extract_entities(query)
        }
        
    def _extract_entities(self, query: str) -> list:
        # A full implementation would use NER models to detect file names and symbols.
        # For this architecture, we return an empty list as placeholder.
        return []
