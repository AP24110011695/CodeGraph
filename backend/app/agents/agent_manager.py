from .collaboration_engine import CollaborationEngine
from .agent_registry import agent_registry
from app.schemas.agents import AgentExecutionResponse, AgentInfo
from typing import List

class AgentManager:
    """Manages the lifecycle and orchestration of engineering agents."""
    def __init__(self):
        self.collaboration = CollaborationEngine()
        
    def execute(self, repository_id: str, query: str) -> AgentExecutionResponse:
        return self.collaboration.execute_collaboration(repository_id, query)
        
    def list_agents(self) -> List[AgentInfo]:
        agents = agent_registry.list_agents()
        return [
            AgentInfo(
                name=a.name,
                description=a.description,
                capabilities=a.capabilities
            )
            for a in agents
        ]

agent_manager = AgentManager()

# Initialize builtins
from .builtin.architecture_agent import ArchitectureAgent
from .builtin.security_agent import SecurityAgent
from .builtin.documentation_agent import DocumentationAgent
from .builtin.refactoring_agent import RefactoringAgent
from .builtin.dependency_agent import DependencyAgent

agent_registry.register(ArchitectureAgent())
agent_registry.register(SecurityAgent())
agent_registry.register(DocumentationAgent())
agent_registry.register(RefactoringAgent())
agent_registry.register(DependencyAgent())
