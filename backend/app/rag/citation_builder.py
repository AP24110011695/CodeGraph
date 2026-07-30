from typing import List, Dict
from app.schemas.rag import Citation

class CitationBuilder:
    """Builds formal citations from context items to present to the LLM and User."""
    
    def build(self, optimized_context: List[Dict]) -> List[Citation]:
        citations = []
        for item in optimized_context:
            snippet = item.get("content", "")
            if len(snippet) > 100:
                snippet = snippet[:97] + "..."
                
            citations.append(Citation(
                source_type=item.get("source_type", "unknown"),
                reference=item.get("reference", "unknown"),
                snippet=snippet
            ))
        return citations
