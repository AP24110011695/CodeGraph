from ..base_agent import BaseAgent
from app.architecture_reasoning.reasoning_engine import reasoning_engine
from typing import Dict, Any

class ArchitectureAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "ArchitectureAgent"
        
    @property
    def description(self) -> str:
        return "Specializes in explaining architecture, modules, and request flows."
        
    @property
    def capabilities(self) -> list[str]:
        return ["explain architecture", "analyze module relationships", "explain request flow"]
        
    def execute(self, repository_id: str, query: str, context: Dict[str, Any]) -> str:
        # Reuses the Architecture Reasoning module
        explanation = reasoning_engine.explain(repository_id, query)
        return explanation.summary
