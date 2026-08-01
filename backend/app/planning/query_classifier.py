class QueryClassifier:
    """Classifies incoming user queries into distinct execution intents."""

    def classify(self, query: str) -> str:
        query_lower = query.lower()

        # --- Timeline / history ---
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

        # --- Architecture ---
        if "explain" in query_lower and "architecture" in query_lower:
            return "architecture_explanation"
        if any(phrase in query_lower for phrase in ("architecture", "summarize", "overview", "structure")):
            return "architecture_explanation"

        # --- Impact (before coupling so 'impact of changing ... dependencies' isn't hijacked) ---
        if any(
            phrase in query_lower
            for phrase in (
                "impact",
                "what breaks",
                "blast radius",
                "propagation",
                "if i modify",
                "change risk",
                "will be affected",
            )
        ):
            return "impact_analysis"

        # --- Coupling / dependencies ---
        if any(
            phrase in query_lower
            for phrase in ("coupled", "coupling", "depend", "dependencies", "dependency", "call", "import")
        ):
            return "coupling_analysis"

        # --- Security ---
        if any(
            phrase in query_lower
            for phrase in ("security", "vulnerability", "vulnerabilities", "risk", "risks", "threat", "exploit", "cve")
        ):
            return "security_analysis"

        # --- Code location (before tech_stack to avoid 'loc' matching 'locate') ---
        if any(phrase in query_lower for phrase in ("locate", "where", "find")):
            return "code_location"

        # --- Language / tech stack ---
        if any(
            phrase in query_lower
            for phrase in ("language", "languages", "tech stack", "framework", "frameworks", "technology", "metrics", "lines of code", "loc ")
        ):
            return "tech_stack_query"

        # --- Code explanation ---
        if "explain" in query_lower:
            return "concept_explanation"

        # --- Code modification ---
        if any(phrase in query_lower for phrase in ("refactor", "improve", "suggest", "fix")):
            return "code_modification"


        # --- Quality / maintainability ---
        if any(phrase in query_lower for phrase in ("quality", "maintainability", "technical debt", "code smell")):
            return "quality_analysis"

        return "general_query"
