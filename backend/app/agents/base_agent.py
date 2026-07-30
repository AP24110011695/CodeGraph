from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAgent(ABC):
    """Abstract base class for all engineering agents."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The unique identifier of the agent."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """A brief description of the agent's purpose."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """A list of specific capabilities this agent provides."""
        pass

    @abstractmethod
    def execute(self, repository_id: str, query: str, context: Dict[str, Any]) -> str:
        """
        Execute the agent's logic.
        Agents should NOT call one another directly. They should rely on the planner's context.
        """
        pass
