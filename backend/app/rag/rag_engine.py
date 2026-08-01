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
        logger.info("RAGEngine: Generating context for %s with query '%s'", repository_id, query)
        logger.info("QUERY: %s", query)

        # 1. Query Analysis
        analysis = self.query_analyzer.analyze(query)
        intent = analysis["intent"]

        # 2. Context Selection — intent-driven, not hardcoded
        raw_items: list = []

        # Generic memory context only for broad/architectural queries
        raw_items.extend(self.context_selector.select_memory_context(repository_id, intent))

        # Semantic vector search — always uses the current query
        raw_items.extend(self.context_selector.select_semantic_context(repository_id, query))

        # Graph context for dependency / coupling queries
        if intent in ("dependency_analysis", "coupling_analysis"):
            raw_items.extend(self.context_selector.select_graph_context(repository_id, analysis["entities"]))

        # Timeline context only when explicitly about history / evolution
        if intent == "timeline_analysis":
            raw_items.extend(self.context_selector.select_timeline_context(repository_id, query))

        # 3. Context Optimization
        optimized_items = self.context_optimizer.optimize(raw_items, max_tokens)

        # 4. Citation and Stats Generation
        citations = self.citation_builder.build(optimized_items)
        stats = self.retrieval_statistics.generate(len(raw_items), optimized_items)

        # 5. LLM Prompt Context Construction
        llm_context = "Repository Context:\n"
        for item in optimized_items:
            llm_context += f"--- {item['source_type'].upper()}: {item['reference']} ---\n{item['content']}\n\n"

        retrieved_sources = [f"{i['source_type']}:{i['reference']}" for i in optimized_items]
        logger.info("RETRIEVED SOURCES: %s", retrieved_sources)
        logger.info("FINAL CONTEXT (%d items, intent=%s): %s", len(optimized_items), intent, retrieved_sources)

        return RAGContextResponse(
            query=query,
            intent=intent,
            llm_context=llm_context,
            citations=citations,
            statistics=stats,
        )


rag_engine = RAGEngine()
