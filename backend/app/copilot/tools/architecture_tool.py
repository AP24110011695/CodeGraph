"""Architecture Tool."""

from typing import Any, Dict

from app.copilot.models.tool_models import ToolDefinition, ToolResult
from app.copilot.tool_registry import tool_registry

architecture_tool_def = ToolDefinition(
    name="architecture_tool",
    description="Analyzes the architecture, major components, layers, and relationships of the codebase.",
    capabilities=["architecture"],
)


def architecture_tool_handler(repository_id: str, query: str, context: Dict[str, Any]) -> ToolResult:
    """Execute the architecture tool."""
    # Reuse existing analyzers
    from app.analyzers.architecture_builder import architecture_builder
    from app.services.dependency_graph import graph_builder
    from app.services.framework_detector import detector_service
    from app.services.scanner_service import scanner_service
    from app.parsers.parser_engine import ParserEngine
    from storage.repository_store import repository_store

    path = repository_store.resolve_path(repository_id)
    if not path or not path.is_dir():
        return ToolResult(
            tool="architecture_tool",
            summary="Repository path not found.",
            confidence=0.0
        )

    # Note: in a real implementation we would reuse the cache if possible
    # We call scanner, detector, graph, parsers, then architecture builder
    scan = scanner_service.scan(path)
    detection = detector_service.detect(path, scan)
    graph = graph_builder.build(path, scan)
    parsing = ParserEngine.parse_project(path, scan)
    architecture = architecture_builder.build(scan, detection, graph, parsing)

    layers = list(getattr(architecture, "layers", None) or [])
    modules = list(getattr(architecture, "modules", None) or [])
    stats = getattr(architecture, "statistics", None) or {}
    
    summary = (
        f"Architecture analysis complete. Found {len(layers)} architectural layers "
        f"and {len(modules)} major modules."
    )
    
    related = []
    for mod in modules[:12]:
        name = getattr(mod, "name", None) or (mod.get("name") if isinstance(mod, dict) else None)
        if name:
            related.append(str(name))
            
    evidence = [
        {"layers": [getattr(layer, "name", str(layer)) for layer in layers]},
        {"module_count": len(modules)},
        {"statistics": stats},
    ]

    return ToolResult(
        tool="architecture_tool",
        summary=summary,
        evidence=evidence,
        related_files=related,
        confidence=0.9,
        metadata={"node_count": len(getattr(graph, "nodes", []) or [])}
    )

tool_registry.register_tool(architecture_tool_def, architecture_tool_handler)
