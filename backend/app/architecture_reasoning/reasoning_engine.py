import logging
from app.schemas.architecture_reasoning import ArchitectureExplanationResponse, ArchitectureSummaryResponse
from .reasoning_pipeline import ReasoningPipeline
from app.repository_memory.memory_engine import memory_engine

logger = logging.getLogger(__name__)

class ReasoningEngine:
    """Facade for the Architecture Reasoning subsystem."""
    
    def __init__(self):
        self.pipeline = ReasoningPipeline()

    def explain(self, repository_id: str, query: str) -> ArchitectureExplanationResponse:
        return self.pipeline.run(repository_id, query)
        
    def summary(self, repository_id: str) -> ArchitectureSummaryResponse:
        # Reuses Repository Memory directly to fetch a quick summary without deep reasoning
        mem_summary = memory_engine.get_memory_summary(repository_id)
        if not mem_summary:
            return ArchitectureSummaryResponse(
                repository_id=repository_id,
                overall_architecture="No architecture summary available yet. Please index the repository first."
            )
            
        return ArchitectureSummaryResponse(
            repository_id=repository_id,
            overall_architecture=mem_summary.architecture_summary or "Architecture summary is empty."
        )

reasoning_engine = ReasoningEngine()
