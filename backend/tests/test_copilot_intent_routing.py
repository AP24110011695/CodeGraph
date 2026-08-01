"""Intent routing integration for Copilot chat orchestration."""

from __future__ import annotations

from app.copilot.intent_router import IntentRouter
from app.copilot.tool_executor import ToolExecutor


def test_intent_router_required_query_routing() -> None:
    router = IntentRouter()

    cases = [
        (
            "What programming languages are used?",
            "language_analysis",
            ["Metrics Engine", "Language Analyzer"],
        ),
        (
            "How many files are in the repository?",
            "repository_overview",
            ["Repository Overview", "Metrics Engine"],
        ),
        (
            "Summarize architecture",
            "architecture_health",
            ["Architecture Analyzer", "Dependency Graph"],
        ),
        (
            "What security risks exist?",
            "security_analysis",
            ["Security Analyzer"],
        ),
        (
            "Explain how authenticate_user works in auth.py",
            "general_query",
            ["RAG Engine"],
        ),
    ]

    for query, intent, modules in cases:
        plan = router.build_execution_plan(query, repository_id="demo")
        assert plan["intent"] == intent, query
        assert plan["required_modules"] == modules, query


def test_tool_executor_aliases_cover_intent_modules() -> None:
    executor = ToolExecutor()
    router = IntentRouter()
    for query in (
        "What programming languages are used?",
        "How many files are in the repository?",
        "Summarize architecture",
        "What security risks exist?",
        "Explain this helper function",
    ):
        plan = router.build_execution_plan(query)
        for module in plan["required_modules"]:
            tool_id = executor.MODULE_ALIASES.get(module, module)
            assert tool_id in executor.list_tools(), f"missing tool for {module}"
