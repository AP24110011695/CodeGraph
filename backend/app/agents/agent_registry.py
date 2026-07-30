from typing import Dict, List
from .base_agent import BaseAgent

class AgentRegistry:
    """Central registry for discovering available agents."""
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent

    def get_agent(self, name: str) -> BaseAgent:
        return self._agents.get(name)
        
    def list_agents(self) -> List[BaseAgent]:
        return list(self._agents.values())

agent_registry = AgentRegistry()
