from typing import List, Dict, Any
from app.schemas.architecture_reasoning import ArchitectureExplanationResponse, ReasoningTraceStep

class ExplanationBuilder:
    """Assembles reasoned insights into a structured enterprise explanation format."""
    
    def build(self, query: str, dependency_insight: str, flow_insight: str, modules: List[str], rag_context: Dict[str, Any]) -> ArchitectureExplanationResponse:
        evidence = []
        citations = rag_context.get("citations", [])
        for citation in citations:
            snippet = citation.get("snippet", "")
            if snippet:
                evidence.append(snippet)
                
        trace = [
            ReasoningTraceStep(step="RAG Context Composition", description=f"Composed multi-source knowledge for '{query}'"),
            ReasoningTraceStep(step="Architecture Module Analysis", description=f"Extracted {len(modules)} primary modules from context"),
            ReasoningTraceStep(step="Dependency Reasoning", description=dependency_insight),
            ReasoningTraceStep(step="Flow Reasoning", description=flow_insight)
        ]
        
        summary = f"Based on composed repository intelligence: {dependency_insight} {flow_insight}"
        confidence = 0.9 if evidence else 0.5
        
        return ArchitectureExplanationResponse(
            summary=summary,
            evidence=evidence,
            referenced_modules=modules,
            confidence_score=confidence,
            reasoning_trace=trace
        )
