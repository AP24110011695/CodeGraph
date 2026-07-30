from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.agents import AgentExecutionRequest, AgentExecutionResponse, AgentInfo
from app.agents.agent_manager import agent_manager

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("", response_model=List[AgentInfo])
async def get_agents():
    """Returns a list of all currently registered agents and their capabilities."""
    return agent_manager.list_agents()

@router.post("/execute/{repository_id}", response_model=AgentExecutionResponse)
async def execute_agents(repository_id: str, request: AgentExecutionRequest):
    """Executes a multi-agent collaboration based on the planning engine's strategy."""
    try:
        return agent_manager.execute(repository_id, request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
