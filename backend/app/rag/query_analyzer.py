import re


class QueryAnalyzer:
    """Analyzes user queries to determine retrieval intent and extract entities."""

    def analyze(self, query: str) -> dict:
        query_lower = query.lower()
        intent = self._classify_intent(query_lower)
        return {
            "intent": intent,
            "entities": self._extract_entities(query),
        }

    def _classify_intent(self, query_lower: str) -> str:
        # Timeline / history
        if any(
            phrase in query_lower
            for phrase in (
                "timeline", "what changed", "hotspot", "unstable", "evolve",
                "ownership", "tightly coupled", "change frequently", "history",
            )
        ):
            return "timeline_analysis"

        # Architecture / summarize
        if any(phrase in query_lower for phrase in ("architecture", "summarize", "overview", "structure")):
            return "architecture_explanation"

        # Coupling / dependencies
        if any(
            phrase in query_lower
            for phrase in ("coupled", "coupling", "depend", "dependencies", "dependency", "call", "import")
        ):
            return "dependency_analysis"

        # Security / vulnerabilities
        if any(
            phrase in query_lower
            for phrase in ("security", "vulnerability", "vulnerabilities", "risk", "risks", "threat", "exploit")
        ):
            return "security_analysis"

        # Code location (before tech_stack to avoid 'loc' in 'locate')
        if "where" in query_lower or "find" in query_lower or "locate" in query_lower:
            return "location_search"

        # Language / tech stack
        if any(
            phrase in query_lower
            for phrase in ("language", "languages", "tech stack", "framework", "frameworks", "technology", "metrics", "lines of code", "loc ")
        ):
            return "tech_stack_query"

        # Code explanation / how/explain
        if "how" in query_lower or "explain" in query_lower:
            return "mechanism_explanation"

        # Quality / debt
        if any(phrase in query_lower for phrase in ("quality", "maintainability", "technical debt", "code smell")):
            return "quality_analysis"

        # Entry point
        if "first" in query_lower or "start" in query_lower or "entry" in query_lower:
            return "entry_point_discovery"

        return "general_explanation"

    def _extract_entities(self, query: str) -> list:
        """Extract file names, module names, and symbol identifiers from query."""
        entities = []
        # Match identifiers like foo.py, bar/baz, CamelCase
        for match in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*(?:[./][A-Za-z0-9_.]+)*)\b", query):
            if len(match) > 2 and match not in (
                "the", "and", "that", "what", "which", "are", "is", "how", "does", "most", "all"
            ):
                entities.append(match)
        return list(dict.fromkeys(entities))  # deduplicate preserving order
