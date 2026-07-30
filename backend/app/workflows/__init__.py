from app.workflows.workflow_step import WorkflowStep
from app.workflows.workflow_definition import WorkflowDefinition
from app.workflows.workflow_context import WorkflowContext, WorkflowStatus, StepStatus
from app.workflows.workflow_registry import workflow_registry
from app.workflows.workflow_executor import workflow_executor
from app.workflows.workflow_engine import workflow_engine

# Define the standard repository processing workflow
default_repo_workflow = WorkflowDefinition(
    name="repository_processing",
    steps=[
        WorkflowStep(name="upload", task_type="upload"),
        WorkflowStep(name="scan", task_type="scan", dependencies=["upload"]),
        WorkflowStep(name="parse", task_type="parse", dependencies=["scan"]),
        WorkflowStep(name="knowledge_graph", task_type="knowledge_graph", dependencies=["parse"]),
        WorkflowStep(name="dependency_graph", task_type="dependency_graph", dependencies=["parse"]),
        WorkflowStep(name="architecture", task_type="architecture", dependencies=["knowledge_graph", "dependency_graph"]),
        WorkflowStep(name="quality", task_type="quality", dependencies=["parse"]),
        WorkflowStep(name="security", task_type="security", dependencies=["parse"]),
        WorkflowStep(name="risk", task_type="risk", dependencies=["architecture", "quality", "security"]),
        WorkflowStep(name="metrics", task_type="metrics", dependencies=["parse"]),
        WorkflowStep(name="report", task_type="report", dependencies=["risk", "metrics"]),
        WorkflowStep(name="copilot", task_type="copilot", dependencies=["knowledge_graph", "report"]),
        WorkflowStep(name="ready", task_type="ready", dependencies=["copilot"]),
    ]
)

# Register the default workflow
workflow_registry.register(default_repo_workflow)

__all__ = [
    "WorkflowStep",
    "WorkflowDefinition",
    "WorkflowContext",
    "WorkflowStatus",
    "StepStatus",
    "workflow_registry",
    "workflow_executor",
    "workflow_engine"
]
