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
    from app.repository_memory.memory_engine import memory_engine

    memory = memory_engine.get_memory(repository_id)
    if not memory:
        return ToolResult(
            tool="symbol_tool",
            summary="No repository memory available. Build index first.",
            confidence=0.0
        )

    symbols = getattr(memory, "symbols", None) or []
    q = query.lower()

    evidence = []
    related = []

    for sym in symbols:
        entry = sym.model_dump(mode="json") if hasattr(sym, "model_dump") else (sym if isinstance(sym, dict) else {})
        name = entry.get("name", "")
        kind = entry.get("kind", "")
        file_path = entry.get("file_path", "")

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

    return ToolResult(
        tool="symbol_tool",
        summary=summary,
        evidence=evidence[:20],
        related_files=list(set(related))[:10],
        confidence=0.95 if evidence else 0.3,
        metadata={"total_symbols": len(symbols)}
    )


tool_registry.register_tool(symbol_tool_def, symbol_tool_handler)
