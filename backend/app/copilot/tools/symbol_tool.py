"""Symbol Tool — queries Symbol Table for function/class/method lookups."""

from typing import Any, Dict

from app.copilot.models.tool_models import ToolDefinition, ToolResult
from app.copilot.tool_registry import tool_registry

symbol_tool_def = ToolDefinition(
    name="symbol_tool",
    description="Locates functions, classes, and methods from the Symbol Table in repository memory.",
    capabilities=["symbol"],
)


def symbol_tool_handler(repository_id: str, query: str, context: Dict[str, Any]) -> ToolResult:
    """Execute the symbol tool."""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("SYMBOL_TOOL: symbol_tool_handler called")
    logger.info("=" * 80)
    logger.info("Repository ID: %s", repository_id)
    logger.info("Query: %s", query)
    
    from app.repository_memory.memory_engine import memory_engine

    logger.info("SYMBOL_TOOL: MemoryEngine instance ID: %s", id(memory_engine))
    logger.info("SYMBOL_TOOL: MemoryStore instance ID: %s", id(memory_engine._store))
    logger.info("SYMBOL_TOOL: MemoryStore.contains(%s): %s", repository_id, memory_engine._store.contains(repository_id))

    # Try to get memory directly from memory_engine
    memory = memory_engine.get_memory(repository_id)
    
    # If memory not available, check if we can build it
    if not memory:
        logger.warning("SYMBOL_TOOL: Memory not available, checking if we can build...")
        from app.indexing.index_manager import get_shared_index_manager
        index_manager = get_shared_index_manager()
        index = index_manager.get_index(repository_id)
        if index and index.status.value == "READY":
            try:
                logger.info("SYMBOL_TOOL: Building memory...")
                memory = memory_engine.build_memory(repository_id)
                logger.info("SYMBOL_TOOL: Memory built successfully")
            except Exception as e:
                logger.error("SYMBOL_TOOL: Failed to build memory: %s", e)
                return ToolResult(
                    tool="symbol_tool",
                    summary=f"Failed to build repository memory: {str(e)}",
                    confidence=0.0
                )
        else:
            logger.warning("SYMBOL_TOOL: Repository not indexed")
            return ToolResult(
                tool="symbol_tool",
                summary="Repository not indexed. Please index the repository first.",
                confidence=0.0
            )
    
    logger.info("SYMBOL_TOOL: Memory available")
    logger.info("  Has symbol_summaries attribute: %s", hasattr(memory, "symbol_summaries"))
    logger.info("  Has symbols attribute: %s", hasattr(memory, "symbols"))
    
    if hasattr(memory, "symbol_summaries"):
        logger.info("  symbol_summaries type: %s", type(memory.symbol_summaries))
        logger.info("  symbol_summaries count: %d", len(memory.symbol_summaries))
        symbols = list(memory.symbol_summaries.values())
    else:
        symbols = getattr(memory, "symbols", None) or []
        logger.info("  symbols type: %s", type(symbols))
        logger.info("  symbols count: %d", len(symbols))
    
    logger.info("SYMBOL_TOOL: Total symbols to process: %d", len(symbols))
    
    q = query.lower()

    evidence = []
    related = []

    for sym in symbols:
        entry = sym.model_dump(mode="json") if hasattr(sym, "model_dump") else (sym if isinstance(sym, dict) else {})
        name = entry.get("name", "")
        kind = entry.get("kind", "")
        file_path = entry.get("file_path", "")
        
        # Extract file path from symbol name if not directly available
        if not file_path and "::" in name:
            file_path = name.split("::")[0]

        # Match if any query token is part of the symbol name
        if any(tok in name.lower() for tok in q.split() if len(tok) > 2):
            evidence.append(entry)
            if file_path:
                related.append(file_path)

    # If no match, return top symbols (fallback)
    if not evidence and symbols:
        evidence = [
            (s.model_dump(mode="json") if hasattr(s, "model_dump") else s)
            for s in symbols[:20]
        ]

    summary = (
        f"Symbol table contains {len(symbols)} symbol(s). "
        f"Found {len(evidence)} matching symbol(s) for query."
    )
    
    logger.info("SYMBOL_TOOL: Evidence found: %d", len(evidence))
    logger.info("SYMBOL_TOOL: Related files: %d", len(related))
    logger.info("=" * 80)

    return ToolResult(
        tool="symbol_tool",
        summary=summary,
        evidence=evidence[:20],
        related_files=list(set(related))[:10],
        confidence=0.95 if evidence else 0.3,
        metadata={"total_symbols": len(symbols)}
    )


tool_registry.register_tool(symbol_tool_def, symbol_tool_handler)
