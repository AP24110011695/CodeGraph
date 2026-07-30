import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from app.workflows.workflow_context import WorkflowContext
from app.workflows.workflow_definition import WorkflowDefinition
from app.workflows.workflow_registry import workflow_registry
from app.workflows.workflow_executor import workflow_executor

logger = logging.getLogger(__name__)

_CHECKPOINT_DIR = Path("storage/workflow_checkpoints")


class WorkflowEngine:
    """High-level facade — orchestrates workflow start, lifecycle, and checkpoint persistence.

    Delegates execution to WorkflowExecutor.
    Delegates step definitions to WorkflowRegistry.
    Never contains business logic.
    """

    def __init__(self) -> None:
        self._registry = workflow_registry
        self._executor = workflow_executor
        _CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Start                                                                 #
    # ------------------------------------------------------------------ #

    def start_workflow(
        self,
        workflow_name: str,
        repository_id: str,
        *,
        correlation_id: Optional[str] = None,
    ) -> WorkflowContext:
        """Create a brand-new workflow context and start execution."""
        definition = self._get_definition(workflow_name)
        context = WorkflowContext(
            workflow_name=workflow_name,
            repository_id=repository_id,
            correlation_id=correlation_id or repository_id,
        )
        self._executor.start_workflow(definition, context)
        return context

    # ------------------------------------------------------------------ #
    # Query                                                                 #
    # ------------------------------------------------------------------ #

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowContext]:
        return self._executor.get_context(workflow_id)

    def list_workflows(self) -> List[WorkflowContext]:
        return self._executor.list_workflows()

    # ------------------------------------------------------------------ #
    # Control                                                               #
    # ------------------------------------------------------------------ #

    def pause_workflow(self, workflow_id: str) -> bool:
        return self._executor.pause_workflow(workflow_id)

    def resume_workflow(self, workflow_id: str) -> bool:
        return self._executor.resume_workflow(workflow_id)

    def cancel_workflow(self, workflow_id: str) -> bool:
        return self._executor.cancel_workflow(workflow_id)

    # ------------------------------------------------------------------ #
    # Checkpoint                                                            #
    # ------------------------------------------------------------------ #

    def save_checkpoint(self, workflow_id: str) -> Optional[Path]:
        """Persist workflow context to disk as JSON."""
        ctx = self._executor.get_context(workflow_id)
        if not ctx:
            return None
        path = _CHECKPOINT_DIR / f"{workflow_id}.json"
        path.write_text(json.dumps(ctx.get_checkpoint(), default=str), encoding="utf-8")
        logger.info(f"[Checkpoint] Saved {workflow_id} → {path}")
        return path

    def restore_checkpoint(
        self, workflow_name: str, checkpoint_data: Optional[Dict] = None, workflow_id: Optional[str] = None
    ) -> WorkflowContext:
        """Restore a workflow from a checkpoint dict OR from disk by workflow_id."""
        if checkpoint_data is None and workflow_id is not None:
            path = _CHECKPOINT_DIR / f"{workflow_id}.json"
            if not path.exists():
                raise FileNotFoundError(f"No checkpoint found for workflow {workflow_id}")
            checkpoint_data = json.loads(path.read_text(encoding="utf-8"))

        if checkpoint_data is None:
            raise ValueError("checkpoint_data or workflow_id required")

        definition = self._get_definition(workflow_name)
        context = WorkflowContext.from_checkpoint(checkpoint_data)
        context.workflow_name = workflow_name
        self._executor.start_workflow(definition, context)
        logger.info(f"[Checkpoint] Restored workflow {context.workflow_id}")
        return context

    # ------------------------------------------------------------------ #
    # Internal                                                              #
    # ------------------------------------------------------------------ #

    def _get_definition(self, workflow_name: str) -> WorkflowDefinition:
        definition = self._registry.get_workflow(workflow_name)
        if not definition:
            raise ValueError(f"Workflow '{workflow_name}' not found in registry")
        return definition


# Global singleton
workflow_engine = WorkflowEngine()
