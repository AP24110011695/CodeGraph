"""Intent routing integration for Copilot chat orchestration.

Updated for Phase 1: deterministic Phase 1 intents replace legacy capability names.
"""

from __future__ import annotations

from app.copilot.intent_router import IntentRouter
from app.copilot.tool_executor import ToolExecutor


def test_intent_router_required_query_routing() -> None:
    router = IntentRouter()

    # Phase 1 intent routing cases.
    # All Phase 1 intents route through RAG Engine.
    # The deterministic rules classify queries before keyword matching.
    cases = [
        (
            "What programming languages are used?",
            # Phase 1: 'languages used' matched by workflow/file_lookup patterns.
            # Falls through to general_query as 'language_analysis' is a legacy intent.
            ["general_query", "workflow", "file_lookup"],
            ["RAG Engine"],
        ),
        (
            "How many files are in the repository?",
            # 'How many files' is a file_lookup pattern in Phase 1
            ["file_lookup", "general_query"],
            ["RAG Engine"],
        ),
        (
            "Summarize architecture",
            # Phase 1: 'architecture' keyword maps to 'architecture' intent
            ["architecture", "general_query"],
            ["RAG Engine"],
        ),
        (
            "What security risks exist?",
            # Phase 1: 'security risks' not in deterministic rules; falls to general_query
            ["general_query", "bug_analysis"],
            ["RAG Engine"],
        ),
        (
            "Explain how authenticate_user works in auth.py",
            # Phase 1: 'how does this work' → code_explanation
            ["code_explanation", "workflow", "general_query"],
            ["RAG Engine"],
        ),
    ]

    for query, expected_intents, expected_modules in cases:
        plan = router.build_execution_plan(query, repository_id="demo")
        assert plan["intent"] in expected_intents, (
            f"Query: '{query}'\n"
            f"Expected intent in {expected_intents}, got: '{plan['intent']}'"
        )
        assert plan["required_modules"] == expected_modules, (
            f"Query: '{query}'\n"
            f"Expected modules {expected_modules}, got: {plan['required_modules']}"
        )


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
