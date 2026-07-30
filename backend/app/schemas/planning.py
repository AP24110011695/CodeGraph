from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class PlanningTraceStep(BaseModel):
    step: str = Field(description="Name of the planning step")
    description: str = Field(description="Details of the decision made during this step")

class AIPlanRequest(BaseModel):
    query: str = Field(description="The incoming repository question or task")

class AIPlanResponse(BaseModel):
    query: str = Field(description="The original user query")
    intent: str = Field(description="The classified query intent")
    required_modules: List[str] = Field(default_factory=list, description="Modules needed to fulfill the request")
    execution_order: List[str] = Field(default_factory=list, description="Order of execution for required modules")
    retrieval_strategy: str = Field(description="The chosen retrieval strategy")
    reasoning_strategy: str = Field(description="The chosen reasoning strategy")
    confidence_score: float = Field(description="Confidence from 0.0 to 1.0 in the generated plan")
    estimated_cost: str = Field(description="Estimated relative computational cost, e.g. 'Low', 'Medium', 'High'")
    planning_trace: List[PlanningTraceStep] = Field(default_factory=list, description="Steps taken by the planner")
