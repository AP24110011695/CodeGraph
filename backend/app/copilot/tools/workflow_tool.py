"""Workflow Tool."""

from typing import Any, Dict

from app.copilot.models.tool_models import ToolDefinition, ToolResult
from app.copilot.tool_registry import tool_registry

workflow_tool_def = ToolDefinition(
    name="workflow_tool",
    description="Analyzes workflow structures, execution paths, and major system flows.",
    capabilities=["workflow"],
)


def workflow_tool_handler(repository_id: str, query: str, context: Dict[str, Any]) -> ToolResult:
    """Execute the workflow tool."""
    from app.repository_memory.memory_engine import memory_engine

    memory = memory_engine.get_memory(repository_id)
    if not memory:
        return ToolResult(
            tool="workflow_tool",
            summary="No repository memory available.",
            confidence=0.0
        )
        
    workflows = getattr(memory, "workflows", None) or []
    
    # Simple semantic filter based on query string if possible, or just return all
    # A real implementation might use an embedding match on workflows
    evidence = []
    related = []
    summary_msg = f"Found {len(workflows)} workflows in repository memory."
    
    for wf in workflows:
        name = getattr(wf, "name", str(wf))
        if isinstance(wf, dict):
            name = wf.get("name", "")
        evidence.append(wf.model_dump(mode="json") if hasattr(wf, "model_dump") else wf)
        related.append(name)

    return ToolResult(
        tool="workflow_tool",
        summary=summary_msg,
        evidence=evidence,
        related_files=related[:10],
        confidence=0.85,
        metadata={"total_workflows": len(workflows)}
    )

tool_registry.register_tool(workflow_tool_def, workflow_tool_handler)
