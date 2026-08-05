"""Phase 4 Tool Calling Tests.

Tests verify:
- Tool Registry registration
- ToolRouter intent-to-capability-to-tool mapping
- All 6 specialized tools are reachable via router
- Multi-tool resolution for complex queries
- Fallback to empty list when no tool applies (RAG fallback)
- ToolResult standardized schema enforcement
- ContextBuilder merges tool_results
- PromptBuilder includes tool evidence sections
"""

import pytest
from typing import Any, Dict, List


# --- Tool Registry Tests ---

class TestToolRegistry:
    def test_all_tools_registered(self):
        """All 6 Phase 4 tools must be registered."""
        import app.copilot.tools  # noqa — triggers self-registration
        from app.copilot.tool_registry import tool_registry

        names = {d.name for d in tool_registry.list_tools()}
        for expected in [
            "architecture_tool",
            "workflow_tool",
            "api_tool",
            "symbol_tool",
            "quality_tool",
            "security_tool",
        ]:
            assert expected in names, f"Missing tool: {expected}"

    def test_find_tools_by_single_capability(self):
        import app.copilot.tools  # noqa
        from app.copilot.tool_registry import tool_registry

        tools = tool_registry.find_tools_by_capabilities(["security"])
        assert any(t.name == "security_tool" for t in tools)

    def test_find_tools_by_multiple_capabilities(self):
        import app.copilot.tools  # noqa
        from app.copilot.tool_registry import tool_registry

        tools = tool_registry.find_tools_by_capabilities(["architecture", "workflow"])
        names = {t.name for t in tools}
        assert "architecture_tool" in names
        assert "workflow_tool" in names


# --- Tool Router Tests ---

class TestToolRouter:
    def setup_method(self):
        import app.copilot.tools  # noqa — ensure tools registered
        from app.copilot.tool_router import ToolRouter
        from app.copilot.tool_registry import tool_registry
        self.router = ToolRouter(registry=tool_registry)

    def test_architecture_intent(self):
        tools = self.router.resolve_tools("architecture", "Explain CodeGraph architecture")
        names = [t.name for t in tools]
        assert "architecture_tool" in names

    def test_workflow_intent(self):
        tools = self.router.resolve_tools("workflow", "Explain upload flow")
        names = [t.name for t in tools]
        assert "workflow_tool" in names

    def test_api_intent(self):
        tools = self.router.resolve_tools("api_flow", "Where is POST /upload implemented?")
        names = [t.name for t in tools]
        assert "api_tool" in names

    def test_symbol_intent(self):
        tools = self.router.resolve_tools("file_lookup", "Where is authenticate_user()?")
        names = [t.name for t in tools]
        assert "symbol_tool" in names

    def test_quality_intent(self):
        tools = self.router.resolve_tools("quality_analysis", "Analyze code quality")
        names = [t.name for t in tools]
        assert "quality_tool" in names

    def test_security_intent(self):
        tools = self.router.resolve_tools("security_analysis", "Find security issues")
        names = [t.name for t in tools]
        assert "security_tool" in names

    def test_multi_tool_complex_query(self):
        """'Explain upload architecture' should invoke architecture + workflow + api."""
        tools = self.router.resolve_tools("architecture", "Explain upload architecture")
        names = {t.name for t in tools}
        # All three must be present
        assert "architecture_tool" in names, f"Missing architecture_tool in {names}"
        assert "workflow_tool" in names, f"Missing workflow_tool in {names}"
        assert "api_tool" in names, f"Missing api_tool in {names}"

    def test_fallback_general_query(self):
        """general_query intent should return no tools (fall back to RAG)."""
        tools = self.router.resolve_tools("general_query", "What is the capital of France?")
        assert tools == [], f"Expected empty list for general_query, got {[t.name for t in tools]}"

    def test_fallback_unknown_intent(self):
        """Unknown intent should return no tools."""
        tools = self.router.resolve_tools("unknown_intent_xyz", "some query")
        assert tools == []


# --- ToolResult Schema Tests ---

class TestToolResultSchema:
    def test_tool_result_schema_enforced(self):
        """ToolResult must enforce required fields and confidence range."""
        from app.copilot.models.tool_models import ToolResult

        result = ToolResult(
            tool="test_tool",
            summary="Test summary",
            evidence=[{"key": "value"}],
            related_files=["src/foo.py"],
            confidence=0.85,
            metadata={"extra": 1}
        )
        assert result.tool == "test_tool"
        assert 0.0 <= result.confidence <= 1.0
        assert isinstance(result.evidence, list)
        assert isinstance(result.related_files, list)
        assert isinstance(result.metadata, dict)

    def test_confidence_clamp(self):
        """Confidence must be in [0, 1]."""
        from app.copilot.models.tool_models import ToolResult
        import pydantic

        with pytest.raises((pydantic.ValidationError, ValueError)):
            ToolResult(tool="x", summary="s", confidence=1.5)


# --- ToolExecutor Integration Tests ---

class TestToolExecutorPhase4:
    def setup_method(self):
        import app.copilot.tools  # noqa

    def test_execute_specialized_tools_security(self):
        """execute_specialized_tools returns list (may be empty if no repo path)."""
        from app.copilot.tool_executor import ToolExecutor

        executor = ToolExecutor()
        results = executor.execute_specialized_tools(
            repository_id="nonexistent_repo",
            query="Find security issues",
            intent="security_analysis",
        )
        # Should return a list (possibly with an error status if repo not found)
        assert isinstance(results, list)
        # If it returned something, must have standardized keys
        for r in results:
            assert "tool" in r
            assert "summary" in r
            assert "confidence" in r
            assert "status" in r

    def test_execute_specialized_tools_general_returns_empty(self):
        """general_query must return empty list so RAG fallback kicks in."""
        from app.copilot.tool_executor import ToolExecutor

        executor = ToolExecutor()
        results = executor.execute_specialized_tools(
            repository_id="any_repo",
            query="What does this codebase do?",
            intent="general_query",
        )
        assert results == []


# --- ContextBuilder Integration Tests ---

class TestContextBuilderToolIntegration:
    def test_tool_results_merged_into_context(self):
        """ContextBuilder.build() must include formatted tool_results in output."""
        from app.copilot.context_builder import ContextBuilder
        from unittest.mock import MagicMock

        mock_memory = MagicMock()
        mock_memory.get_memory_summary.return_value = None
        mock_rag = MagicMock()
        mock_rag.generate_context.return_value = MagicMock(llm_context=None, citations=[])

        builder = ContextBuilder(memory_engine=mock_memory, rag_engine=mock_rag)

        tool_results = [
            {
                "tool": "security_tool",
                "summary": "Found 3 issues.",
                "evidence": [{"file": "src/auth.py", "issue": "SQL injection"}],
                "related_files": ["src/auth.py"],
                "confidence": 0.9,
                "metadata": {},
                "latency_ms": 50,
                "status": "ok",
            }
        ]

        context = builder.build(
            repository_id="test",
            query="Find security issues",
            tool_results=tool_results,
        )

        assert "tool_results" in context
        assert len(context["tool_results"]) == 1
        assert context["tool_results"][0]["tool"] == "security_tool"
        assert "security_tool" in context["modules_touched"]

    def test_failed_tool_results_excluded(self):
        """Tool results with status='error' must NOT appear in formatted output."""
        from app.copilot.context_builder import ContextBuilder
        from unittest.mock import MagicMock

        builder = ContextBuilder(
            memory_engine=MagicMock(get_memory_summary=MagicMock(return_value=None)),
            rag_engine=MagicMock(generate_context=MagicMock(return_value=MagicMock(llm_context=None, citations=[])))
        )

        tool_results = [
            {"tool": "quality_tool", "summary": "Error occurred.", "evidence": [], "related_files": [],
             "confidence": 0.0, "metadata": {}, "latency_ms": 0, "status": "error"},
        ]

        context = builder.build(repository_id="test", query="q", tool_results=tool_results)
        assert context["tool_results"] == []
