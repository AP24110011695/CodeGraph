from typing import Callable, Any, List, Optional
from pydantic import BaseModel
from app.workflows.workflow_context import WorkflowContext

class WorkflowStep(BaseModel):
    """A step in a workflow."""
    name: str
    task_type: str
    dependencies: List[str] = []
    retry_count: int = 3
    timeout_seconds: Optional[int] = None
    
    def can_run(self, context: WorkflowContext) -> bool:
        """Check if all dependencies are completed."""
        from app.workflows.workflow_context import StepStatus
        for dep in self.dependencies:
            if context.step_statuses.get(dep) != StepStatus.COMPLETED:
                return False
        return True
