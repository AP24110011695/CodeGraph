import logging
from app.schemas.architecture_reasoning import ArchitectureExplanationResponse
from .architecture_analyzer import ArchitectureAnalyzer
from .dependency_reasoner import DependencyReasoner
from .flow_reasoner import FlowReasoner
from .explanation_builder import ExplanationBuilder
from .reasoning_statistics import ReasoningStatistics
from app.rag.rag_engine import rag_engine

logger = logging.getLogger(__name__)

class ReasoningPipeline:
    """Pipeline coordinating the reasoning process over RAG context."""
    
    def __init__(self):
        self.architecture_analyzer = ArchitectureAnalyzer()
        self.dependency_reasoner = DependencyReasoner()
        self.flow_reasoner = FlowReasoner()
        self.explanation_builder = ExplanationBuilder()
        self.statistics = ReasoningStatistics()

    def run(self, repository_id: str, query: str) -> ArchitectureExplanationResponse:
        logger.info(f"ReasoningPipeline: Processing query '{query}' for {repository_id}")
        
        # 1. Fetch LLM Context from Advanced RAG Engine
        rag_response = rag_engine.generate_context(repository_id, query)
        rag_context = rag_response.model_dump()
        
        # 2. Analyze Architecture Modules
        modules = self.architecture_analyzer.analyze_modules(query, rag_context)
        
        # 3. Reason over dependencies
        dep_insight = self.dependency_reasoner.reason(modules)
        
        # 4. Reason over flow
        flow_insight = self.flow_reasoner.reason(query, rag_context)
        
        # 5. Build Final Explanation
        explanation = self.explanation_builder.build(
            query=query,
            dependency_insight=dep_insight,
            flow_insight=flow_insight,
            modules=modules,
            rag_context=rag_context
        )
        
        # Optional: Log statistics
        stats = self.statistics.collect(explanation)
        logger.debug(f"Reasoning stats: {stats}")
        
        return explanation
