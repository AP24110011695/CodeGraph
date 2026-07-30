from typing import Dict, Any

class FlowReasoner:
    """Reasons about data and request flows across the architecture."""
    
    def reason(self, query: str, rag_context: Dict[str, Any]) -> str:
        query_lower = query.lower()
        intent = rag_context.get("intent", "")
        
        if "flow" in query_lower or "lifecycle" in query_lower or "sequence" in query_lower:
            return "The request/data flow travels sequentially through the identified architecture components, governed by standard lifecycle hooks."
            
        if intent == "mechanism_explanation":
            return "Execution follows a top-down invocation mechanism."
            
        return "Standard synchronous data flow patterns are applied."
