"""Security Tool — runs security analysis using Risk Engine and Security Analyzer."""

from typing import Any, Dict

from app.copilot.models.tool_models import ToolDefinition, ToolResult
from app.copilot.tool_registry import tool_registry

security_tool_def = ToolDefinition(
    name="security_tool",
    description="Detects security vulnerabilities and risks using the Security Analyzer and Risk Engine.",
    capabilities=["security"],
)


def security_tool_handler(repository_id: str, query: str, context: Dict[str, Any]) -> ToolResult:
    """Execute the security tool."""
    from app.security.security_analyzer import security_analyzer
    from storage.repository_store import repository_store

    path = repository_store.resolve_path(repository_id)
    if not path or not path.is_dir():
        return ToolResult(
            tool="security_tool",
            summary="Repository path not found.",
            confidence=0.0
        )

    analysis = security_analyzer.analyze(path)
    total = int(getattr(analysis, "total_issues", 0) or 0)
    summary_counts = getattr(analysis, "summary", {}) or {}
    issues = list(getattr(analysis, "issues", None) or [])[:25]

    evidence = []
    related = []
    for issue in issues:
        entry = issue.model_dump(mode="json") if hasattr(issue, "model_dump") else (issue if isinstance(issue, dict) else {"issue": str(issue)})
        evidence.append(entry)
        file_path = entry.get("file_path") or entry.get("file", "")
        if file_path:
            related.append(file_path)

    confidence = 0.95 if total > 0 else 0.7
    summary = (
        f"Security analysis found {total} issue(s). "
        + (f"By severity: {summary_counts}" if summary_counts else "")
    ).strip()

    return ToolResult(
        tool="security_tool",
        summary=summary,
        evidence=evidence,
        related_files=list(set(related))[:10],
        confidence=confidence,
        metadata={
            "total_issues": total,
            "summary_by_severity": summary_counts,
        }
    )


tool_registry.register_tool(security_tool_def, security_tool_handler)
