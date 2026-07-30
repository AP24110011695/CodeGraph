from .agent_registry import agent_registry
from app.schemas.agents import AgentResponse
from typing import List, Dict, Any

class TaskDispatcher:
    """Dispatches execution instructions to specific agents."""
    def dispatch(self, repository_id: str, query: str, required_agents: List[str], shared_context: Dict[str, Any]) -> List[AgentResponse]:
        results = []
        for agent_name in required_agents:
            agent = agent_registry.get_agent(agent_name)
            if agent:
                res = agent.execute(repository_id, query, shared_context)
                results.append(AgentResponse(
                    agent_name=agent_name,
                    result=res,
                    confidence=0.9
                ))
            else:
                results.append(AgentResponse(
                    agent_name=agent_name,
                    result="Agent not found in registry.",
                    confidence=0.0
                ))
        return results
