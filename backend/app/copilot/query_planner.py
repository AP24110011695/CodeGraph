"""Query Planner — deterministic reasoning and planning layer.

Converts classified intent + query into a structured execution plan specifying
required tools, memory, retrieval strategy, and reasoning steps.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.copilot.models.query_plan_models import QueryPlan, QueryStep

logger = logging.getLogger(__name__)


# Intent → Tool mappings (deterministic rules)
# Note: Tool names must match the registered names in tool_registry (snake_case)
_INTENT_TOOLS: Dict[str, List[str]] = {
    "file_lookup": ["symbol_tool"],
    "code_explanation": ["symbol_tool"],
    "workflow": ["workflow_tool"],
    "architecture": ["architecture_tool"],
    "api_flow": ["api_tool"],
    "quality_analysis": ["quality_tool"],
    "security_analysis": ["security_tool"],
    "bug_analysis": ["security_tool", "symbol_tool"],
    "general_query": [],  # No tools, rely on RAG
}

# Intent → Memory mappings (deterministic rules)
_INTENT_MEMORY: Dict[str, List[str]] = {
    "file_lookup": ["symbol_table"],
    "code_explanation": ["symbol_table", "module_memory"],
    "workflow": ["workflow_memory", "route_memory"],
    "architecture": ["architecture_memory", "module_memory", "dependency_memory"],
    "api_flow": ["api_memory", "route_memory"],
    "quality_analysis": ["module_memory", "file_memory"],
    "security_analysis": ["symbol_table", "module_memory"],
    "bug_analysis": ["symbol_table", "module_memory"],
    "general_query": ["module_memory", "file_memory"],  # Broad memory for general queries
}

# Intent → Retrieval strategy mappings
_INTENT_RETRIEVAL_STRATEGY: Dict[str, str] = {
    "file_lookup": "symbol_table_lookup",
    "code_explanation": "hybrid_semantic",
    "workflow": "graph_traversal",
    "architecture": "hybrid_semantic",
    "api_flow": "graph_traversal",
    "quality_analysis": "hybrid_semantic",
    "security_analysis": "hybrid_semantic",
    "bug_analysis": "hybrid_semantic",
    "general_query": "hybrid_semantic",
}

# Intent → Expected output type
_INTENT_OUTPUT_TYPE: Dict[str, str] = {
    "file_lookup": "direct_match_list",
    "code_explanation": "explanation",
    "workflow": "trace",
    "architecture": "analysis",
    "api_flow": "trace",
    "quality_analysis": "analysis",
    "security_analysis": "analysis",
    "bug_analysis": "analysis",
    "general_query": "general",
}


class QueryPlanner:
    """Deterministic query planner that creates structured execution plans.
    
    The planner:
    1. Takes classified intent and entities from Intent Router
    2. Applies deterministic rules to select tools, memory, and retrieval strategy
    3. Detects multi-step questions and decomposes them
    4. Produces a QueryPlan for Tool Router and Context Builder
    """

    def __init__(self):
        self._trace: List[Dict[str, Any]] = []

    def plan_query(
        self,
        query: str,
        intent: str,
        entities: Optional[List[Dict[str, str]]] = None,
        repository_id: Optional[str] = None,
    ) -> QueryPlan:
        """Create a structured execution plan for the query.
        
        Args:
            query: Original user query
            intent: Classified intent from Intent Router
            entities: Extracted entities (name, type)
            repository_id: Repository identifier
            
        Returns:
            QueryPlan with tools, memory, retrieval strategy, and reasoning steps
        """
        self._trace = []
        query_lower = query.lower()
        
        # Normalize intent
        normalized_intent = self._normalize_intent(intent)
        self._trace.append({
            "step": "Intent Normalization",
            "original_intent": intent,
            "normalized_intent": normalized_intent,
        })
        
        # Select tools
        tools = self._select_tools(normalized_intent, query_lower)
        self._trace.append({
            "step": "Tool Selection",
            "intent": normalized_intent,
            "selected_tools": tools,
        })
        
        # Select memory
        memory = self._select_memory(normalized_intent, query_lower)
        self._trace.append({
            "step": "Memory Selection",
            "intent": normalized_intent,
            "selected_memory": memory,
        })
        
        # Determine retrieval strategy
        retrieval_strategy = self._select_retrieval_strategy(normalized_intent, query_lower)
        retrieval_required = retrieval_strategy != "none"
        self._trace.append({
            "step": "Retrieval Strategy",
            "strategy": retrieval_strategy,
            "retrieval_required": retrieval_required,
        })
        
        # Detect multi-step questions
        reasoning_steps = self._detect_multi_step(query_lower, normalized_intent)
        self._trace.append({
            "step": "Multi-Step Detection",
            "is_multi_step": len(reasoning_steps) > 1,
            "reasoning_steps": reasoning_steps,
        })
        
        # Determine expected output type
        output_type = _INTENT_OUTPUT_TYPE.get(normalized_intent, "general")
        
        # Calculate confidence
        confidence = self._calculate_confidence(normalized_intent, query_lower, tools)
        
        # Handle fallback if confidence is low
        fallback_triggered = False
        if confidence < 0.5:
            self._trace.append({
                "step": "Fallback Triggered",
                "reason": f"Low confidence {confidence:.2f}",
            })
            tools = []
            memory = ["module_memory", "file_memory"]
            retrieval_strategy = "hybrid_semantic"
            retrieval_required = True
            reasoning_steps = []
            output_type = "general"
            fallback_triggered = True
        
        plan = QueryPlan(
            original_query=query,
            intent=normalized_intent,
            required_tools=tools,
            required_memory=memory,
            retrieval_required=retrieval_required,
            retrieval_strategy=retrieval_strategy,
            reasoning_steps=reasoning_steps,
            expected_output_type=output_type,
            entities=entities or [],
            confidence=confidence,
            fallback_triggered=fallback_triggered,
            planning_trace=self._trace,
        )
        
        logger.info(
            "QueryPlan created: intent=%s, tools=%s, memory=%s, retrieval=%s, confidence=%.2f",
            normalized_intent,
            tools,
            memory,
            retrieval_strategy,
            confidence,
        )
        
        return plan

    def _normalize_intent(self, intent: str) -> str:
        """Normalize intent to canonical form."""
        # Map legacy intents to Phase 1 equivalents
        intent_mapping = {
            "architecture_health": "architecture",
            "architecture_recommendation": "architecture",
            "architecture_drift": "architecture",
            "bug_localization": "bug_analysis",
            "security_analysis": "security_analysis",
            "risk_analysis": "security_analysis",
            "api_documentation": "api_flow",
            "dependency_graph": "architecture",
            "dependency_health": "quality_analysis",
            "code_smells": "quality_analysis",
        }
        return intent_mapping.get(intent, intent)

    def _select_tools(self, intent: str, query_lower: str) -> List[str]:
        """Select required tools based on intent and query keywords."""
        tools = list(_INTENT_TOOLS.get(intent, []))
        
        # Multi-tool overrides based on query keywords
        if "architecture" in query_lower and "workflow" in query_lower:
            if "workflow_tool" not in tools:
                tools.append("workflow_tool")
            if "architecture_tool" not in tools:
                tools.append("architecture_tool")
        
        if "architecture" in query_lower and "upload" in query_lower:
            if "workflow_tool" not in tools:
                tools.append("workflow_tool")
            if "api_tool" not in tools:
                tools.append("api_tool")
            if "architecture_tool" not in tools:
                tools.append("architecture_tool")
        
        # Add symbol_tool for security vulnerability analysis
        if intent == "security_analysis" and ("vulnerability" in query_lower or "vulnerabilities" in query_lower):
            if "symbol_tool" not in tools:
                tools.append("symbol_tool")
        
        return tools

    def _select_memory(self, intent: str, query_lower: str) -> List[str]:
        """Select required memory types based on intent and query keywords."""
        memory = list(_INTENT_MEMORY.get(intent, []))
        
        # Add memory for specific keywords
        if "api" in query_lower and "api_memory" not in memory:
            memory.append("api_memory")
        
        if "config" in query_lower and "configuration_memory" not in memory:
            memory.append("configuration_memory")
        
        if "database" in query_lower or "schema" in query_lower:
            if "database_schema_memory" not in memory:
                memory.append("database_schema_memory")
        
        return memory

    def _select_retrieval_strategy(self, intent: str, query_lower: str) -> str:
        """Select retrieval strategy based on intent."""
        strategy = _INTENT_RETRIEVAL_STRATEGY.get(intent, "hybrid_semantic")
        
        # Override for specific patterns
        if "where is" in query_lower or "find" in query_lower:
            if "symbol" in query_lower or "function" in query_lower or "class" in query_lower:
                return "symbol_table_lookup"
        
        if "workflow" in query_lower or "trace" in query_lower or "flow" in query_lower:
            return "graph_traversal"
        
        return strategy

    def _detect_multi_step(self, query_lower: str, intent: str) -> List[str]:
        """Detect multi-step questions and decompose into reasoning steps."""
        steps = []
        
        # Pattern: "Explain X and identify Y"
        if " and " in query_lower and ("identify" in query_lower or "find" in query_lower):
            parts = query_lower.split(" and ")
            if len(parts) == 2:
                steps.append(f"Understand and analyze: {parts[0]}")
                steps.append(f"Identify and locate: {parts[1]}")
                steps.append("Combine findings into comprehensive answer")
                return steps
        
        # Pattern: "Explain X and find issues"
        if "explain" in query_lower and ("issue" in query_lower or "problem" in query_lower or "vulnerability" in query_lower):
            steps.append("Understand the component or workflow")
            steps.append("Analyze for issues or vulnerabilities")
            steps.append("Document findings with evidence")
            return steps
        
        # Pattern: Security analysis
        if intent == "security_analysis" or intent == "bug_analysis":
            steps.append("Identify relevant components and symbols")
            steps.append("Analyze code for security issues or bugs")
            steps.append("Trace data flow and dependencies")
            steps.append("Compile findings with evidence")
            return steps
        
        # Pattern: Architecture explanation
        if intent == "architecture":
            steps.append("Identify relevant modules and components")
            steps.append("Analyze architectural structure")
            steps.append("Trace dependencies and relationships")
            steps.append("Document architecture with evidence")
            return steps
        
        # Pattern: Workflow tracing
        if intent == "workflow" or intent == "api_flow":
            steps.append("Identify entry point")
            steps.append("Trace execution path")
            steps.append("Document workflow steps")
            return steps
        
        # Default: single step
        steps.append(f"Execute {intent} analysis")
        return steps

    def _calculate_confidence(self, intent: str, query_lower: str, tools: List[str]) -> float:
        """Calculate confidence in the plan based on intent clarity and tool availability."""
        base_confidence = 0.5  # Start lower for unknown intents
        
        # Boost confidence if we have specific tools
        if tools:
            base_confidence += 0.3
        
        # Boost confidence for known intents
        if intent in _INTENT_TOOLS:
            base_confidence += 0.1
        
        # Boost confidence for clear intent keywords
        intent_keywords = {
            "file_lookup": ["where", "find", "locate"],
            "code_explanation": ["explain", "how", "what"],
            "workflow": ["workflow", "flow", "trace", "how does"],
            "architecture": ["architecture", "structure", "design"],
            "api_flow": ["api", "endpoint", "route"],
            "security_analysis": ["security", "vulnerability", "issue"],
            "bug_analysis": ["bug", "error", "problem"],
        }
        
        keywords = intent_keywords.get(intent, [])
        if any(kw in query_lower for kw in keywords):
            base_confidence += 0.1
        
        # Penalize unknown intents
        if intent not in _INTENT_TOOLS and intent != "general_query":
            base_confidence -= 0.2
        
        # Cap at 1.0, floor at 0.0
        return max(0.0, min(base_confidence, 1.0))


query_planner = QueryPlanner()
