import logging
from app.schemas.rag import RAGContextResponse
from .query_analyzer import QueryAnalyzer
from .context_selector import ContextSelector
from .context_optimizer import ContextOptimizer
from .citation_builder import CitationBuilder
from .retrieval_statistics import RetrievalStatistics

logger = logging.getLogger(__name__)

class RAGEngine:
    """Advanced RAG Engine for composing structured LLM context from existing intelligence."""
    
    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
        self.context_selector = ContextSelector()
        self.context_optimizer = ContextOptimizer()
        self.citation_builder = CitationBuilder()
        self.retrieval_statistics = RetrievalStatistics()

    def generate_context(self, repository_id: str, query: str, max_tokens: int = 4000) -> RAGContextResponse:
        logger.info(f"RAGEngine: Generating context for {repository_id} with query '{query}'")
        
        # 1. Query Analysis
        analysis = self.query_analyzer.analyze(query)
        
        # 2. Context Selection
        raw_items = []
        raw_items.extend(self.context_selector.select_memory_context(repository_id))
        raw_items.extend(self.context_selector.select_semantic_context(repository_id, query))
        raw_items.extend(self.context_selector.select_graph_context(repository_id, analysis["entities"]))
        
        # 3. Context Optimization
        optimized_items = self.context_optimizer.optimize(raw_items, max_tokens)
        
        # 4. Citation and Stats Generation
        citations = self.citation_builder.build(optimized_items)
        stats = self.retrieval_statistics.generate(len(raw_items), optimized_items)
        
        # 5. LLM Prompt Context Construction
        llm_context = "Repository Context:\n"
        for item in optimized_items:
            llm_context += f"--- {item['source_type'].upper()}: {item['reference']} ---\n{item['content']}\n\n"
            
        return RAGContextResponse(
            query=query,
            intent=analysis["intent"],
            llm_context=llm_context,
            citations=citations,
            statistics=stats
        )

rag_engine = RAGEngine()
