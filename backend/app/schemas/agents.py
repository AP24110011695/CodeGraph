from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.schemas.planning import AIPlanResponse

class AgentResponse(BaseModel):
    agent_name: str = Field(description="Name of the agent that executed")
    result: str = Field(description="The outcome or finding produced by the agent")
    confidence: float = Field(description="Confidence of the agent in its result")

class AgentExecutionRequest(BaseModel):
    query: str = Field(description="The problem or task for the agents to solve collaboratively")

class AgentExecutionResponse(BaseModel):
    query: str = Field(description="Original request")
    plan: AIPlanResponse = Field(description="The execution plan drafted by the Planning Engine")
    agent_results: List[AgentResponse] = Field(description="Individual results from each engaged agent")
    final_summary: str = Field(description="Synthesized summary of all agent findings")
    execution_time_ms: int = Field(description="Total time spent collaborating in ms")

class AgentInfo(BaseModel):
    name: str = Field(description="Agent identifier")
    description: str = Field(description="What the agent specializes in")
    capabilities: List[str] = Field(description="List of capabilities")
