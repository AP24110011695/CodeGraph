"""Quality Tool — runs code quality analysis using QualityAnalyzer."""

from typing import Any, Dict

from app.copilot.models.tool_models import ToolDefinition, ToolResult
from app.copilot.tool_registry import tool_registry

quality_tool_def = ToolDefinition(
    name="quality_tool",
    description="Analyzes code quality, maintainability scores, and detects code smells.",
    capabilities=["quality"],
)


def quality_tool_handler(repository_id: str, query: str, context: Dict[str, Any]) -> ToolResult:
    """Execute the quality tool."""
    from app.quality.quality_analyzer import quality_analyzer
    from storage.repository_store import repository_store

    path = repository_store.resolve_path(repository_id)
    if not path or not path.is_dir():
        return ToolResult(
            tool="quality_tool",
            summary="Repository path not found.",
            confidence=0.0
        )

    result = quality_analyzer.analyze(path)
    scores = result.scores
    recs = result.recommendations

    # Extract score values safely
    overall = getattr(scores, "overall", None)
    maintainability = getattr(scores, "maintainability", None)
    complexity = getattr(scores, "complexity", None)
    test_coverage = getattr(scores, "test_coverage", None)
    documentation = getattr(scores, "documentation", None)

    summary = (
        f"Quality analysis complete. Overall score: {overall:.1f}/100. "
        f"Maintainability: {maintainability:.1f}/100."
        if overall and maintainability
        else "Quality analysis complete."
    )

    evidence = [
        {
            "overall_score": overall,
            "maintainability": maintainability,
            "complexity": complexity,
            "test_coverage": test_coverage,
            "documentation": documentation,
        }
    ]

    all_recs = []
    for attr in ("critical", "high", "medium", "low"):
        for rec in (getattr(recs, attr, None) or []):
            all_recs.append(
                rec.message if hasattr(rec, "message") else str(rec)
            )

    return ToolResult(
        tool="quality_tool",
        summary=summary,
        evidence=evidence,
        related_files=[],
        confidence=0.9,
        metadata={
            "recommendations": all_recs[:15],
            "project_name": result.project_name,
            "metadata": result.metadata,
        }
    )


tool_registry.register_tool(quality_tool_def, quality_tool_handler)
