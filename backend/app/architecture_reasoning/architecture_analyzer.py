from typing import List, Dict, Any

class ArchitectureAnalyzer:
    """Analyzes architectural modules based on aggregated RAG context."""
    
    def analyze_modules(self, query: str, rag_context: Dict[str, Any]) -> List[str]:
        modules = set()
        citations = rag_context.get("citations", [])
        for citation in citations:
            reference = citation.get("reference")
            if reference:
                modules.add(reference)
                
        # If no explicit modules found in citations, try to extract from intent
        if not modules:
            intent = rag_context.get("intent", "")
            if intent == "dependency_analysis":
                modules.add("Dependency Subsystem")
            else:
                modules.add("Core System")
                
        return list(modules)
