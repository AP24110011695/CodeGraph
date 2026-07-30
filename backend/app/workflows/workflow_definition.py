from typing import List, Dict
from pydantic import BaseModel
from app.workflows.workflow_step import WorkflowStep

class WorkflowDefinition(BaseModel):
    """Defines a workflow and its steps."""
    name: str
    steps: List[WorkflowStep]
    
    def get_step(self, step_name: str) -> WorkflowStep | None:
        """Get a step by name."""
        for step in self.steps:
            if step.name == step_name:
                return step
        return None
        
    def get_executable_steps(self, context) -> List[WorkflowStep]:
        """Get steps that can be executed now."""
        from app.workflows.workflow_context import StepStatus
        
        executable = []
        for step in self.steps:
            status = context.step_statuses.get(step.name, StepStatus.PENDING)
            if status == StepStatus.PENDING and step.can_run(context):
                executable.append(step)
        return executable
