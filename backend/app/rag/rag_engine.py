import logging
import os
from app.schemas.rag import RAGContextResponse
from .query_analyzer import QueryAnalyzer
from .context_selector import ContextSelector
from .context_optimizer import ContextOptimizer
from .citation_builder import CitationBuilder
from .retrieval_statistics import RetrievalStatistics

logger = logging.getLogger(__name__)

# Phase 1 intents that benefit from memory (architecture/workflow)
_BROAD_MEMORY_INTENTS = {
    "architecture",
    "workflow",
    "architecture_explanation",
    "tech_stack_query",
    "general_explanation",
    "mechanism_explanation",
}


def _format_context_item(item: dict) -> str:
    """Format a single retrieved context item into a structured block.

    Every chunk is formatted as:
        FILE: <path>
        SYMBOL: <function/class if available, or source type>
        REASON: <why this chunk was selected>
        CODE:
        <content>

    This ensures the LLM receives grounded, attributed context rather than
    an unstructured text blob.
    """
    reference = item.get("reference", "unknown")
    source_type = item.get("source_type", "code")
    content = (item.get("content") or "").strip()
    symbol = item.get("symbol") or item.get("function") or item.get("class_name")
    score = item.get("score")

    # Derive a human-readable reason from source_type + score
    if source_type == "semantic":
        reason = f"Semantic similarity match"
        if score is not None:
            reason += f" (score: {score:.2f})"
    elif source_type == "memory":
        reason = "Repository memory — architectural overview"
    elif source_type == "timeline":
        reason = "Historical timeline context"
    elif source_type == "graph":
        reason = "Dependency graph context"
    else:
        reason = f"{source_type} context"

    # Extract filename from path reference
    filename = os.path.basename(reference) if "/" in reference or "\\" in reference else reference

    lines = []
    lines.append(f"FILE: {reference}")
    if filename != reference:
        lines.append(f"FILENAME: {filename}")
    if symbol:
        lines.append(f"SYMBOL: {symbol}")
    lines.append(f"REASON: {reason}")
    lines.append("CODE:")
    lines.append(content)
    lines.append("")  # blank line separator between chunks

    return "\n".join(lines)


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

        # 1. Query Analysis — derives intent for memory/graph routing
        analysis = self.query_analyzer.analyze(query)
        intent = analysis["intent"]

        # 2. Context Selection — intent-driven, not hardcoded
        raw_items: list = []

        # 2a. Broad structural memory (architecture/tech-stack intents only)
        raw_items.extend(self.context_selector.select_memory_context(repository_id, intent))

        # 2b. Structured memory injections — separate from RAG, feed into Context Builder together
        # Workflow memory: step-by-step traces for workflow/tracing intents
        raw_items.extend(self.context_selector.select_workflow_context(repository_id, intent, query))

        # Symbol memory: class/function lookup for file-lookup/code-explanation intents
        raw_items.extend(self.context_selector.select_symbol_context(repository_id, intent, query))

        # API memory: endpoint records for workflow/API intents
        raw_items.extend(self.context_selector.select_api_context(repository_id, intent, query))

        # 2c. Semantic vector search — always uses the current query
        raw_items.extend(self.context_selector.select_semantic_context(repository_id, query))

        # 2d. Graph context for dependency / coupling queries
        if intent in ("dependency_analysis", "coupling_analysis"):
            raw_items.extend(self.context_selector.select_graph_context(repository_id, analysis["entities"]))

        # 2e. Timeline context only when explicitly about history / evolution
        if intent == "timeline_analysis":
            raw_items.extend(self.context_selector.select_timeline_context(repository_id, query))

        # 3. Context Optimization
        optimized_items = self.context_optimizer.optimize(raw_items, max_tokens)

        # 4. Citation and Stats Generation
        citations = self.citation_builder.build(optimized_items)
        stats = self.retrieval_statistics.generate(len(raw_items), optimized_items)

        # 5. Structured LLM Context Construction (Phase 1 improvement)
        # Each item is formatted as a clearly-attributed block with
        # FILE / SYMBOL / REASON / CODE — not a raw concatenated blob.
        if optimized_items:
            chunk_blocks = [_format_context_item(item) for item in optimized_items]
            llm_context = "---\n".join(chunk_blocks)
        else:
            llm_context = ""

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
