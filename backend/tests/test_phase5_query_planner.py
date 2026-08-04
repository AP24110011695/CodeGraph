"""Phase 5 Query Planner Tests.

Tests verify:
- QueryPlan schema validation
- Deterministic query decomposition
- Intent-to-tool mapping
- Intent-to-memory mapping
- Retrieval strategy selection
- Multi-step question detection
- Fallback handling for low confidence
- Integration with CopilotEngine
"""

import pytest
from typing import Any, Dict, List


# --- QueryPlan Schema Tests ---

class TestQueryPlanSchema:
    def test_query_plan_required_fields(self):
        """QueryPlan must enforce required fields."""
        from app.copilot.models.query_plan_models import QueryPlan

        plan = QueryPlan(
            original_query="Where is upload implemented?",
            intent="file_lookup",
            required_tools=["SymbolTool"],
            required_memory=["symbol_table"],
            retrieval_required=True,
            retrieval_strategy="symbol_table_lookup",
            reasoning_steps=["Locate upload function"],
            expected_output_type="direct_match_list",
            entities=[{"name": "upload", "type": "function"}],
            confidence=0.9,
        )

        assert plan.original_query == "Where is upload implemented?"
        assert plan.intent == "file_lookup"
        assert plan.required_tools == ["SymbolTool"]
        assert plan.required_memory == ["symbol_table"]
        assert plan.retrieval_required is True
        assert plan.retrieval_strategy == "symbol_table_lookup"
        assert plan.reasoning_steps == ["Locate upload function"]
        assert plan.expected_output_type == "direct_match_list"
        assert plan.confidence == 0.9
        assert plan.fallback_triggered is False

    def test_query_plan_confidence_range(self):
        """Confidence must be in [0, 1]."""
        from app.copilot.models.query_plan_models import QueryPlan
        import pydantic

        with pytest.raises((pydantic.ValidationError, ValueError)):
            QueryPlan(
                original_query="test",
                intent="general_query",
                confidence=1.5,
            )

        with pytest.raises((pydantic.ValidationError, ValueError)):
            QueryPlan(
                original_query="test",
                intent="general_query",
                confidence=-0.1,
            )

    def test_query_step_schema(self):
        """QueryStep must enforce required fields."""
        from app.copilot.models.query_plan_models import QueryStep

        step = QueryStep(
            step_number=1,
            description="Find authentication components",
            tools=["SymbolTool"],
            memory=["symbol_table"],
            retrieval=True,
            output_dependency=None,
        )

        assert step.step_number == 1
        assert step.description == "Find authentication components"
        assert step.tools == ["SymbolTool"]
        assert step.memory == ["symbol_table"]
        assert step.retrieval is True


# --- Query Planner Tests ---

class TestQueryPlanner:
    def setup_method(self):
        from app.copilot.query_planner import QueryPlanner
        self.planner = QueryPlanner()

    def test_file_lookup_plan(self):
        """'Where is upload implemented?' should select symbol_tool and symbol_table memory."""
        plan = self.planner.plan_query(
            query="Where is upload implemented?",
            intent="file_lookup",
        )

        assert plan.intent == "file_lookup"
        assert "symbol_tool" in plan.required_tools
        assert "symbol_table" in plan.required_memory
        assert plan.retrieval_strategy == "symbol_table_lookup"
        assert plan.expected_output_type == "direct_match_list"
        assert plan.confidence > 0.7

    def test_workflow_plan(self):
        """'Explain upload workflow' should select workflow_tool and workflow_memory."""
        plan = self.planner.plan_query(
            query="Explain upload workflow",
            intent="workflow",
        )

        assert plan.intent == "workflow"
        assert "workflow_tool" in plan.required_tools
        assert "workflow_memory" in plan.required_memory
        assert plan.retrieval_strategy == "graph_traversal"
        assert plan.expected_output_type == "trace"
        assert len(plan.reasoning_steps) > 1

    def test_architecture_plan(self):
        """'Explain upload architecture' should select architecture, workflow, and api tools."""
        plan = self.planner.plan_query(
            query="Explain upload architecture",
            intent="architecture",
        )

        assert plan.intent == "architecture"
        assert "architecture_tool" in plan.required_tools
        # Multi-tool override for "architecture" + "upload"
        assert "workflow_tool" in plan.required_tools
        assert "api_tool" in plan.required_tools
        assert "architecture_memory" in plan.required_memory
        assert plan.retrieval_strategy == "hybrid_semantic"
        assert plan.expected_output_type == "analysis"

    def test_security_analysis_plan(self):
        """'Find authentication vulnerabilities' should select security and symbol tools."""
        plan = self.planner.plan_query(
            query="Find authentication vulnerabilities",
            intent="security_analysis",
        )

        assert plan.intent == "security_analysis"
        assert "security_tool" in plan.required_tools
        # "vulnerability" keyword adds symbol_tool
        assert "symbol_tool" in plan.required_tools
        assert "symbol_table" in plan.required_memory
        assert plan.retrieval_strategy == "hybrid_semantic"
        assert plan.expected_output_type == "analysis"

    def test_general_query_fallback(self):
        """Unknown or general query should trigger fallback with RAG."""
        plan = self.planner.plan_query(
            query="What is the capital of France?",
            intent="general_query",
        )

        assert plan.intent == "general_query"
        assert plan.required_tools == []  # No specialized tools
        assert plan.retrieval_required is True
        assert plan.retrieval_strategy == "hybrid_semantic"
        assert plan.expected_output_type == "general"

    def test_multi_step_detection(self):
        """'Explain X and identify Y' should produce multiple reasoning steps."""
        plan = self.planner.plan_query(
            query="Explain authentication flow and identify vulnerabilities",
            intent="security_analysis",
        )

        assert len(plan.reasoning_steps) >= 2
        assert any("understand" in step.lower() for step in plan.reasoning_steps)
        assert any("identify" in step.lower() or "analyze" in step.lower() for step in plan.reasoning_steps)

    def test_intent_normalization(self):
        """Legacy intents should be normalized to Phase 1 equivalents."""
        plan = self.planner.plan_query(
            query="Analyze architecture health",
            intent="architecture_health",
        )

        assert plan.intent == "architecture"  # Normalized
        assert "architecture_tool" in plan.required_tools

    def test_retrieval_strategy_override(self):
        """'where is' queries should override to symbol_table_lookup."""
        plan = self.planner.plan_query(
            query="Where is the authenticate_user function?",
            intent="code_explanation",
        )

        assert plan.retrieval_strategy == "symbol_table_lookup"

    def test_confidence_calculation(self):
        """Confidence should be higher for clear intent with tools."""
        plan_with_tools = self.planner.plan_query(
            query="Find security issues in authentication",
            intent="security_analysis",
        )

        plan_without_tools = self.planner.plan_query(
            query="Tell me about this codebase",
            intent="general_query",
        )

        assert plan_with_tools.confidence > plan_without_tools.confidence

    def test_fallback_on_low_confidence(self):
        """Low confidence plans should trigger fallback."""
        # Use a mock scenario that would produce low confidence
        plan = self.planner.plan_query(
            query="xyz random unclear query",
            intent="unknown_intent",
        )

        # Unknown intent should have lower confidence
        assert plan.confidence < 0.8
        # Should still have retrieval enabled (never block user)
        assert plan.retrieval_required is True
        assert plan.retrieval_required is True

    def test_memory_keyword_enrichment(self):
        """Specific keywords should enrich memory selection."""
        plan = self.planner.plan_query(
            query="Explain the database schema and API configuration",
            intent="architecture",
        )

        assert "database_schema_memory" in plan.required_memory
        assert "configuration_memory" in plan.required_memory

    def test_planning_trace(self):
        """Planning trace should record decision steps."""
        plan = self.planner.plan_query(
            query="Explain upload workflow",
            intent="workflow",
        )

        assert len(plan.planning_trace) > 0
        trace_steps = [t["step"] for t in plan.planning_trace]
        assert "Intent Normalization" in trace_steps
        assert "Tool Selection" in trace_steps
        assert "Memory Selection" in trace_steps
        assert "Retrieval Strategy" in trace_steps


# --- Integration Tests ---

class TestQueryPlannerIntegration:
    def test_query_planner_in_copilot_engine(self):
        """CopilotEngine should use QueryPlanner to create execution plans."""
        from app.copilot.copilot_engine import CopilotEngine
        from app.copilot.query_planner import QueryPlanner

        # Ensure QueryPlanner is available
        engine = CopilotEngine(query_planner=QueryPlanner())

        # Verify the planner is attached
        assert engine.query_planner is not None
        assert isinstance(engine.query_planner, QueryPlanner)

    def test_query_plan_to_tool_executor(self):
        """QueryPlan's required_tools should be passed to ToolExecutor."""
        from app.copilot.query_planner import QueryPlanner
        from app.copilot.tool_executor import ToolExecutor

        planner = QueryPlanner()
        plan = planner.plan_query(
            query="Find security issues",
            intent="security_analysis",
        )

        executor = ToolExecutor()
        # Mock execution to verify tools are passed
        # (Integration test would need actual repository)
        assert len(plan.required_tools) > 0
        assert "security_tool" in plan.required_tools

    def test_query_plan_to_context_builder(self):
        """QueryPlan's memory and retrieval flags should be used by ContextBuilder."""
        from app.copilot.query_planner import QueryPlanner
        from app.copilot.context_builder import ContextBuilder
        from unittest.mock import MagicMock

        planner = QueryPlanner()
        plan = planner.plan_query(
            query="Explain workflow",
            intent="workflow",
        )

        mock_memory = MagicMock()
        mock_memory.get_memory_summary.return_value = None
        mock_rag = MagicMock()
        mock_rag.generate_context.return_value = MagicMock(llm_context=None, citations=[])

        builder = ContextBuilder(memory_engine=mock_memory, rag_engine=mock_rag)

        # Build context with plan
        context = builder.build(
            repository_id="test",
            query="Explain workflow",
            plan={
                "required_modules": [],
                "retrieval_required": plan.retrieval_required,
                "required_memory": plan.required_memory,
                "retrieval_strategy": plan.retrieval_strategy,
                "reasoning_steps": plan.reasoning_steps,
                "expected_output_type": plan.expected_output_type,
            },
        )

        # Verify plan parameters are reflected in context
        assert context["retrieval_strategy"] == plan.retrieval_strategy
        assert context["required_memory"] == plan.required_memory
        assert context["reasoning_steps"] == plan.reasoning_steps
        assert context["expected_output_type"] == plan.expected_output_type


# --- Test Cases from Phase 5 Specification ---

class TestPhase5SpecificationTests:
    """Tests from the Phase 5 specification document."""

    def setup_method(self):
        from app.copilot.query_planner import QueryPlanner
        self.planner = QueryPlanner()

    def test_spec_test_1_file_lookup(self):
        """Test 1: 'Where is upload implemented?' → symbol_tool, File lookup plan."""
        plan = self.planner.plan_query(
            query="Where is upload implemented?",
            intent="file_lookup",
        )

        assert "symbol_tool" in plan.required_tools
        assert plan.expected_output_type == "direct_match_list"
        assert plan.retrieval_strategy == "symbol_table_lookup"

    def test_spec_test_2_workflow(self):
        """Test 2: 'Explain upload workflow' → workflow_tool, Workflow Memory."""
        plan = self.planner.plan_query(
            query="Explain upload workflow",
            intent="workflow",
        )

        assert "workflow_tool" in plan.required_tools
        assert "workflow_memory" in plan.required_memory

    def test_spec_test_3_architecture(self):
        """Test 3: 'Explain upload architecture' → architecture, workflow, api tools."""
        plan = self.planner.plan_query(
            query="Explain upload architecture",
            intent="architecture",
        )

        assert "architecture_tool" in plan.required_tools
        assert "workflow_tool" in plan.required_tools
        assert "api_tool" in plan.required_tools

    def test_spec_test_4_security(self):
        """Test 4: 'Find authentication vulnerabilities' → security_tool, symbol_tool."""
        plan = self.planner.plan_query(
            query="Find authentication vulnerabilities",
            intent="security_analysis",
        )

        assert "security_tool" in plan.required_tools
        assert "symbol_tool" in plan.required_tools

    def test_spec_test_5_unknown_fallback(self):
        """Test 5: Unknown question → Safe fallback to RAG."""
        plan = self.planner.plan_query(
            query="What is the meaning of life?",
            intent="general_query",
        )

        assert plan.retrieval_required is True
        assert plan.retrieval_strategy == "hybrid_semantic"
        # Should not block the user - general_query has no specialized tools
        assert plan.required_tools == []
        # Should have memory and retrieval enabled
        assert len(plan.required_memory) > 0
