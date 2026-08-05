"""Runtime Integration Test - Verifies tool registration and execution.

Tests the specific queries mentioned in the bug report to ensure tools are correctly
resolved and executed.
"""

import pytest


class TestRuntimeIntegration:
    """Test that the Query Planner tool names match the Tool Registry."""

    def setup_method(self):
        """Ensure tools are registered."""
        import app.copilot.tools  # noqa: F401 - triggers self-registration
        from app.copilot.tool_registry import tool_registry
        from app.copilot.query_planner import QueryPlanner
        
        self.registry = tool_registry
        self.planner = QueryPlanner()

    def test_all_phase4_tools_registered(self):
        """Verify all Phase 4 tools are registered in the registry."""
        registered_tools = {t.name for t in self.registry.list_tools()}
        
        expected_tools = {
            "architecture_tool",
            "workflow_tool", 
            "api_tool",
            "symbol_tool",
            "quality_tool",
            "security_tool",
        }
        
        assert expected_tools.issubset(registered_tools), (
            f"Missing tools: {expected_tools - registered_tools}. "
            f"Registered: {registered_tools}"
        )

    def test_query_where_is_authentication_uses_symbol_tool(self):
        """'Where is authentication implemented?' should resolve to symbol_tool."""
        plan = self.planner.plan_query(
            query="Where is authentication implemented?",
            intent="file_lookup",
        )
        
        assert "symbol_tool" in plan.required_tools
        assert self.registry.get_tool("symbol_tool") is not None, (
            "symbol_tool must be registered in the registry"
        )

    def test_query_explain_upload_workflow_uses_workflow_tool(self):
        """'Explain upload workflow' should resolve to workflow_tool."""
        plan = self.planner.plan_query(
            query="Explain upload workflow",
            intent="workflow",
        )
        
        assert "workflow_tool" in plan.required_tools
        assert self.registry.get_tool("workflow_tool") is not None, (
            "workflow_tool must be registered in the registry"
        )

    def test_query_explain_architecture_uses_architecture_tool(self):
        """'Explain architecture' should resolve to architecture_tool."""
        plan = self.planner.plan_query(
            query="Explain architecture",
            intent="architecture",
        )
        
        assert "architecture_tool" in plan.required_tools
        assert self.registry.get_tool("architecture_tool") is not None, (
            "architecture_tool must be registered in the registry"
        )

    def test_query_find_security_issues_uses_security_tool(self):
        """'Find security issues' should resolve to security_tool."""
        plan = self.planner.plan_query(
            query="Find security issues",
            intent="security_analysis",
        )
        
        assert "security_tool" in plan.required_tools
        assert self.registry.get_tool("security_tool") is not None, (
            "security_tool must be registered in the registry"
        )

    def test_tool_executor_can_resolve_planned_tools(self):
        """ToolExecutor should be able to resolve all tools from the query plan."""
        from app.copilot.tool_executor import ToolExecutor
        
        # Test each intent
        test_cases = [
            ("Where is authentication implemented?", "file_lookup", "symbol_tool"),
            ("Explain upload workflow", "workflow", "workflow_tool"),
            ("Explain architecture", "architecture", "architecture_tool"),
            ("Find security issues", "security_analysis", "security_tool"),
        ]
        
        executor = ToolExecutor()
        
        for query, intent, expected_tool in test_cases:
            plan = self.planner.plan_query(query=query, intent=intent)
            assert expected_tool in plan.required_tools, (
                f"Expected {expected_tool} in plan for query: {query}"
            )
            
            # Verify tool is in registry
            tool_def = self.registry.get_tool_definition(expected_tool)
            assert tool_def is not None, (
                f"Tool {expected_tool} not found in registry. "
                f"Available tools: {[t.name for t in self.registry.list_tools()]}"
            )
            
            # Verify handler is available
            handler = self.registry.get_tool(expected_tool)
            assert handler is not None, (
                f"Handler for {expected_tool} not found in registry"
            )

    def test_tool_names_are_snake_case(self):
        """Verify all tool names use snake_case convention."""
        registered_tools = {t.name for t in self.registry.list_tools()}
        
        for tool_name in registered_tools:
            # Tool names should be snake_case
            assert tool_name == tool_name.lower(), (
                f"Tool name '{tool_name}' should be snake_case (lowercase with underscores)"
            )
            assert " " not in tool_name, (
                f"Tool name '{tool_name}' should not contain spaces"
            )
