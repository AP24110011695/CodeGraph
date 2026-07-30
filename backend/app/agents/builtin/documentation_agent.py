from ..base_agent import BaseAgent
from app.repository_memory.memory_engine import memory_engine
from typing import Dict, Any

class DocumentationAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "DocumentationAgent"
        
    @property
    def description(self) -> str:
        return "Generates documentation and repository summaries."
        
    @property
    def capabilities(self) -> list[str]:
        return ["generate documentation", "explain modules", "produce repository summaries"]
        
    def execute(self, repository_id: str, query: str, context: Dict[str, Any]) -> str:
        summary = memory_engine.get_memory_summary(repository_id)
        if summary and summary.architecture_summary:
            return f"Documentation generation based on memory: {summary.architecture_summary}"
        return "Generated standard documentation for the requested components."
