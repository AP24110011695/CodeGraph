"""Query Plan models for the Copilot reasoning and planning layer."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class QueryPlan(BaseModel):
    """Structured execution plan for a user query.
    
    The Query Planner creates this from the classified intent and raw query.
    It specifies exactly what tools, memory, and retrieval are needed.
    """
    
    original_query: str = Field(..., description="The original user query")
    intent: str = Field(..., description="Classified intent from Intent Router")
    
    # Tool selection
    required_tools: List[str] = Field(
        default_factory=list,
        description="Tool names that should be executed (e.g., 'ArchitectureTool', 'WorkflowTool')"
    )
    
    # Memory selection
    required_memory: List[str] = Field(
        default_factory=list,
        description="Memory types to retrieve (e.g., 'module_memory', 'workflow_memory', 'symbol_table')"
    )
    
    # Retrieval strategy
    retrieval_required: bool = Field(
        default=True,
        description="Whether hybrid semantic retrieval should run"
    )
    retrieval_strategy: str = Field(
        default="hybrid_semantic",
        description="Retrieval strategy: symbol_table_lookup, hybrid_semantic, graph_traversal, schema_lookup"
    )
    
    # Reasoning steps for multi-step questions
    reasoning_steps: List[str] = Field(
        default_factory=list,
        description="Ordered reasoning steps for multi-step questions"
    )
    
    # Expected output
    expected_output_type: str = Field(
        default="general",
        description="Expected output structure: direct_match_list, explanation, analysis, trace, general"
    )
    
    # Metadata
    entities: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Entities extracted from the query (name, type)"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Planner confidence in this plan"
    )
    fallback_triggered: bool = Field(
        default=False,
        description="Whether this is a fallback plan due to uncertain classification"
    )
    
    # Planning trace (internal, not exposed to users)
    planning_trace: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Internal trace of planning decisions"
    )


class QueryStep(BaseModel):
    """A single step in a multi-step query execution plan."""
    
    step_number: int = Field(..., description="Order of this step")
    description: str = Field(..., description="Human-readable description of this step")
    tools: List[str] = Field(default_factory=list, description="Tools to execute in this step")
    memory: List[str] = Field(default_factory=list, description="Memory to retrieve in this step")
    retrieval: bool = Field(default=False, description="Whether retrieval is needed in this step")
    output_dependency: Optional[str] = Field(
        default=None,
        description="If this step depends on output from a previous step"
    )
