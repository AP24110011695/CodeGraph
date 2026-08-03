"""Schemas for Unified Intelligence Orchestrator / Copilot (CG-070)."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CopilotRequest(BaseModel):
    """Legacy request for POST /copilot/{upload_id}."""

    query: str = Field(..., description="User query about the repository")


class CopilotResponse(BaseModel):
    """Legacy copilot response."""

    upload_id: str = Field(..., description="Repository upload ID")
    query: str = Field(..., description="User query")
    intent: str = Field(..., description="Detected intent")
    module: str = Field(..., description="Module used to answer")
    confidence: int = Field(..., description="Confidence score (0-100)")
    answer: str = Field(..., description="Answer to the query")
    sources: list[str] = Field(default_factory=list, description="Sources of the answer")
    evidence: list[str] = Field(default_factory=list, description="Evidence supporting the answer")
    related_modules: list[str] = Field(default_factory=list, description="Related modules")
    error: str | None = Field(None, description="Error message if failed")


class CopilotChatRequest(BaseModel):
    """Conversational orchestration request."""

    repository_id: str = Field(..., description="Repository identifier")
    query: str = Field(..., description="Engineering question")
    conversation_id: Optional[str] = Field(
        default=None,
        description="Existing conversation id for follow-ups",
    )
    provider: Optional[str] = Field(
        default=None,
        description="LLM provider key (openai|claude|gemini|groq|ollama|azure|local)",
    )


class CopilotExecuteRequest(BaseModel):
    """Explicit execute request with optional tool allow-list."""

    repository_id: str
    query: str
    conversation_id: Optional[str] = None
    provider: Optional[str] = None
    tools: List[str] = Field(
        default_factory=list,
        description="Optional tool ids to force (e.g. timeline, impact_analysis, engineering_reports)",
    )
    impact_target: Optional[str] = Field(
        default=None,
        description="Optional impact analysis target",
    )


class CopilotPlanSummary(BaseModel):
    intent: Optional[str] = None
    required_modules: List[str] = Field(default_factory=list)
    execution_order: List[str] = Field(default_factory=list)
    confidence_score: Optional[float] = None
    estimated_cost: Optional[str] = None


class CopilotChatResponse(BaseModel):
    """Structured engineering response from the orchestrator."""

    conversation_id: str
    repository_id: str
    query: str
    answer: str
    confidence: float = Field(description="0.0–1.0 confidence")
    repository_context: Dict[str, Any] = Field(default_factory=dict)
    modules_used: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    reasoning_summary: str = ""
    related_components: List[str] = Field(default_factory=list)
    related_files: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    execution_time_ms: int = 0
    provider: Optional[str] = None
    intent: Optional[str] = None
    plan_confidence: float = 0.0
    mode: str = "chat"
    plan: Optional[CopilotPlanSummary] = None


class CopilotHistoryResponse(BaseModel):
    conversation_id: Optional[str] = None
    repository_id: Optional[str] = None
    count: int = 0
    history: List[Dict[str, Any]] = Field(default_factory=list)


class CopilotClearHistoryResponse(BaseModel):
    cleared_sessions: int = 0
    conversation_id: Optional[str] = None
    repository_id: Optional[str] = None
