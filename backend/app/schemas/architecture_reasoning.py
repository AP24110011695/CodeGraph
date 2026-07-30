from pydantic import BaseModel, Field
from typing import List

class ReasoningTraceStep(BaseModel):
    step: str = Field(description="Name of the reasoning step")
    description: str = Field(description="Details of the reasoning step")

class ArchitectureExplanationRequest(BaseModel):
    query: str = Field(description="The architectural question to explain")

class ArchitectureExplanationResponse(BaseModel):
    summary: str = Field(description="High-level summary of the explanation")
    evidence: List[str] = Field(default_factory=list, description="Evidence gathered from existing context")
    referenced_modules: List[str] = Field(default_factory=list, description="List of module names involved")
    confidence_score: float = Field(description="Confidence from 0.0 to 1.0")
    reasoning_trace: List[ReasoningTraceStep] = Field(default_factory=list, description="Steps taken to reach conclusion")

class ArchitectureSummaryResponse(BaseModel):
    repository_id: str
    overall_architecture: str
