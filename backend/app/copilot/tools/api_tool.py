"""API Tool — queries API Memory for endpoint and handler information."""

from typing import Any, Dict

from app.copilot.models.tool_models import ToolDefinition, ToolResult
from app.copilot.tool_registry import tool_registry

api_tool_def = ToolDefinition(
    name="api_tool",
    description="Finds API endpoints, handlers, request flows, and API documentation from API Memory.",
    capabilities=["api"],
)


def api_tool_handler(repository_id: str, query: str, context: Dict[str, Any]) -> ToolResult:
    """Execute the API tool."""
    from app.repository_memory.memory_engine import memory_engine

    memory = memory_engine.get_memory(repository_id)
    if not memory:
        return ToolResult(
            tool="api_tool",
            summary="No repository memory available. Build index first.",
            confidence=0.0
        )

    apis = getattr(memory, "apis", None) or []

    evidence = []
    related = []
    q = query.lower()

    for api in apis:
        entry = api.model_dump(mode="json") if hasattr(api, "model_dump") else (api if isinstance(api, dict) else {})
        endpoint = entry.get("endpoint", "")
        method = entry.get("method", "")
        file_path = entry.get("file_path", "")
        handler = entry.get("handler", "")

        # Include all if query is generic, else filter by keyword
        if not q or any(kw in endpoint.lower() or kw in handler.lower() for kw in q.split()):
            evidence.append(entry)
            if file_path:
                related.append(file_path)

    if not evidence and apis:
        # fallback: return all when no filter matches
        evidence = [
            (api.model_dump(mode="json") if hasattr(api, "model_dump") else api)
            for api in apis[:20]
        ]

    summary = f"Found {len(apis)} API endpoint(s) in repository memory. Matched {len(evidence)} to query."

    return ToolResult(
        tool="api_tool",
        summary=summary,
        evidence=evidence[:20],
        related_files=list(set(related))[:10],
        confidence=0.9 if evidence else 0.4,
        metadata={"total_apis": len(apis)}
    )


tool_registry.register_tool(api_tool_def, api_tool_handler)
