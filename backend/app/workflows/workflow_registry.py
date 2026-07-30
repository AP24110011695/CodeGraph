from typing import Dict, Any, Callable
from app.workflows.workflow_definition import WorkflowDefinition
import logging

logger = logging.getLogger(__name__)

class WorkflowRegistry:
    """Registry for workflow definitions."""
    
    def __init__(self):
        self._workflows: Dict[str, WorkflowDefinition] = {}
        
    def register(self, definition: WorkflowDefinition) -> None:
        """Register a workflow definition."""
        self._workflows[definition.name] = definition
        logger.info(f"Registered workflow: {definition.name}")
        
    def get_workflow(self, name: str) -> WorkflowDefinition | None:
        """Get a workflow definition by name."""
        return self._workflows.get(name)

# Global registry
workflow_registry = WorkflowRegistry()
