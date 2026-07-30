from typing import Dict, Any
from app.schemas.architecture_reasoning import ArchitectureExplanationResponse

class ReasoningStatistics:
    """Collects metadata on the reasoning process."""
    
    def collect(self, response: ArchitectureExplanationResponse) -> Dict[str, Any]:
        return {
            "evidence_count": len(response.evidence),
            "module_count": len(response.referenced_modules),
            "confidence_score": response.confidence_score,
            "reasoning_depth": len(response.reasoning_trace)
        }
