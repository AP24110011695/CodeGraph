import logging
import threading
from typing import Dict, Optional, List

from app.workflows.workflow_context import WorkflowContext, WorkflowStatus, StepStatus
from app.workflows.workflow_definition import WorkflowDefinition
from app.workers.task_router import task_router
from app.events.event_bus import event_bus
from app.events.event_types import EventType
from app.repository_state.state_machine import RepositoryStateMachine
from app.schemas.repository_state import RepositoryStateEnum

logger = logging.getLogger(__name__)

# Mapping workflow step task_type → repository state to transition into
_STEP_TO_REPO_STATE: Dict[str, RepositoryStateEnum] = {
    "scan": RepositoryStateEnum.SCANNING,
    "parse": RepositoryStateEnum.PARSING,
    "knowledge_graph": RepositoryStateEnum.INDEXING,
    "dependency_graph": RepositoryStateEnum.INDEXING,
    "architecture": RepositoryStateEnum.ANALYZING,
    "quality": RepositoryStateEnum.ANALYZING,
    "security": RepositoryStateEnum.ANALYZING,
    "risk": RepositoryStateEnum.ANALYZING,
    "metrics": RepositoryStateEnum.ANALYZING,
    "report": RepositoryStateEnum.ANALYZING,
    "copilot": RepositoryStateEnum.ANALYZING,
    "ready": RepositoryStateEnum.READY,
}

# Mapping workflow step task_type → EventType to publish when completed
_STEP_COMPLETION_EVENT: Dict[str, EventType] = {
    "knowledge_graph": EventType.KNOWLEDGE_GRAPH_BUILT,
    "architecture": EventType.ARCHITECTURE_GENERATED,
    "quality": EventType.QUALITY_COMPLETED,
    "security": EventType.SECURITY_COMPLETED,
    "risk": EventType.RISK_COMPLETED,
    "metrics": EventType.METRICS_GENERATED,
    "report": EventType.REPORT_GENERATED,
    "copilot": EventType.COPILOT_COMPLETED,
    "ready": EventType.REPOSITORY_READY,
}


class WorkflowExecutor:
    """Executes workflows — orchestrates step routing, state transitions, and event publishing.

    Rules
    -----
    * Workflow engine *orchestrates only* — no business logic lives here.
    * Business logic stays inside existing modules (architecture_builder, etc.).
    * Workers *execute only* — they call TaskExecutor handlers.
    * State Machine and Event Bus are called here as integration points.
    """

    def __init__(self) -> None:
        self._contexts: Dict[str, WorkflowContext] = {}
        self._definitions: Dict[str, WorkflowDefinition] = {}
        self._lock = threading.Lock()

        # Subscribe to worker completion/failure events
        event_bus.subscribe(EventType.JOB_COMPLETED, self._handle_job_completed)
        event_bus.subscribe(EventType.JOB_FAILED, self._handle_job_failed)

    # ------------------------------------------------------------------ #
    # Lifecycle                                                             #
    # ------------------------------------------------------------------ #

    def start_workflow(self, definition: WorkflowDefinition, context: WorkflowContext) -> None:
        """Register and start a workflow."""
        with self._lock:
            context.workflow_name = definition.name
            self._contexts[context.workflow_id] = context
            self._definitions[context.workflow_id] = definition
            context.status = WorkflowStatus.RUNNING
            context.touch()
            logger.info(f"[Workflow {context.workflow_id}] Started for repo {context.repository_id}")

        event_bus.publish(
            event_type=EventType.WORKFLOW_STARTED,
            repository_id=context.repository_id,
            payload={"workflow_id": context.workflow_id, "workflow_name": context.workflow_name},
            correlation_id=context.workflow_id,
        )
        self._advance(context.workflow_id)

    def pause_workflow(self, workflow_id: str) -> bool:
        with self._lock:
            ctx = self._contexts.get(workflow_id)
            if ctx and ctx.status == WorkflowStatus.RUNNING:
                ctx.status = WorkflowStatus.PAUSED
                ctx.touch()
                logger.info(f"[Workflow {workflow_id}] Paused")
                event_bus.publish(
                    EventType.WORKFLOW_PAUSED,
                    repository_id=ctx.repository_id,
                    payload={"workflow_id": workflow_id},
                )
                return True
        return False

    def resume_workflow(self, workflow_id: str) -> bool:
        with self._lock:
            ctx = self._contexts.get(workflow_id)
            if ctx and ctx.status == WorkflowStatus.PAUSED:
                ctx.status = WorkflowStatus.RUNNING
                ctx.touch()
                logger.info(f"[Workflow {workflow_id}] Resumed")
            else:
                return False
        self._advance(workflow_id)
        return True

    def cancel_workflow(self, workflow_id: str) -> bool:
        with self._lock:
            ctx = self._contexts.get(workflow_id)
            if ctx and ctx.status in (
                WorkflowStatus.PENDING,
                WorkflowStatus.RUNNING,
                WorkflowStatus.PAUSED,
            ):
                ctx.status = WorkflowStatus.CANCELLED
                ctx.touch()
                logger.info(f"[Workflow {workflow_id}] Cancelled")
                self._try_repo_state(ctx.repository_id, RepositoryStateEnum.CANCELLED)
                event_bus.publish(
                    EventType.WORKFLOW_CANCELLED,
                    repository_id=ctx.repository_id,
                    payload={"workflow_id": workflow_id},
                )
                return True
        return False

    def get_context(self, workflow_id: str) -> Optional[WorkflowContext]:
        with self._lock:
            return self._contexts.get(workflow_id)

    def list_workflows(self) -> List[WorkflowContext]:
        with self._lock:
            return list(self._contexts.values())

    # ------------------------------------------------------------------ #
    # Internal advance logic                                                #
    # ------------------------------------------------------------------ #

    def _advance(self, workflow_id: str) -> None:
        """Determine next runnable steps and push them to the task router."""
        with self._lock:
            ctx = self._contexts.get(workflow_id)
            defn = self._definitions.get(workflow_id)
            if not ctx or not defn:
                return
            if ctx.status != WorkflowStatus.RUNNING:
                return

            runnable = defn.get_executable_steps(ctx)

            if not runnable:
                # Check for completion
                all_done = all(
                    ctx.step_statuses.get(s.name) == StepStatus.COMPLETED
                    for s in defn.steps
                )
                if all_done:
                    ctx.status = WorkflowStatus.COMPLETED
                    ctx.progress = 100
                    ctx.touch()
                    logger.info(f"[Workflow {workflow_id}] COMPLETED")
                    event_bus.publish(
                        EventType.WORKFLOW_COMPLETED,
                        repository_id=ctx.repository_id,
                        payload={"workflow_id": workflow_id},
                    )
                return

            for step in runnable:
                ctx.step_statuses[step.name] = StepStatus.RUNNING
                ctx.current_step = step.name
                ctx.touch()

                # Transition repository state if applicable
                repo_state = _STEP_TO_REPO_STATE.get(step.task_type)
                if repo_state:
                    self._try_repo_state(
                        ctx.repository_id,
                        repo_state,
                        current_stage=step.name,
                    )

                # Route task to workers
                task_router.route_task(
                    task_type=step.task_type,
                    repository_id=ctx.repository_id,
                    context_data={
                        "workflow_id": workflow_id,
                        "step_name": step.name,
                        "correlation_id": ctx.correlation_id,
                    },
                )
                logger.info(f"[Workflow {workflow_id}] Queued step '{step.name}'")

    # ------------------------------------------------------------------ #
    # Event handlers                                                        #
    # ------------------------------------------------------------------ #

    def _handle_job_completed(self, event) -> None:
        """Handle step completion published by workers via Event Bus."""
        ctx_data = event.payload.get("context")
        if not ctx_data or "workflow_id" not in ctx_data:
            return  # Not a workflow-managed job

        workflow_id: str = ctx_data["workflow_id"]
        step_name: str = ctx_data["step_name"]

        with self._lock:
            ctx = self._contexts.get(workflow_id)
            defn = self._definitions.get(workflow_id)
            if not ctx:
                return

            ctx.step_statuses[step_name] = StepStatus.COMPLETED
            ctx.step_results[step_name] = event.payload.get("result")
            if defn:
                ctx.progress = ctx.compute_progress(len(defn.steps))
            ctx.touch()
            logger.info(f"[Workflow {workflow_id}] Step '{step_name}' completed")

        # Publish domain-level completion event if applicable
        step = None
        with self._lock:
            defn = self._definitions.get(workflow_id)
            if defn:
                step = defn.get_step(step_name)

        if step:
            domain_event = _STEP_COMPLETION_EVENT.get(step.task_type)
            if domain_event:
                with self._lock:
                    ctx = self._contexts.get(workflow_id)
                event_bus.publish(
                    event_type=domain_event,
                    repository_id=ctx.repository_id if ctx else None,
                    payload={"workflow_id": workflow_id, "step": step_name},
                    correlation_id=workflow_id,
                )

        self._advance(workflow_id)

    def _handle_job_failed(self, event) -> None:
        """Handle step failure published by workers via Event Bus."""
        ctx_data = event.payload.get("context")
        if not ctx_data or "workflow_id" not in ctx_data:
            return

        workflow_id: str = ctx_data["workflow_id"]
        step_name: str = ctx_data["step_name"]
        error: str = event.payload.get("error", "Unknown error")

        with self._lock:
            ctx = self._contexts.get(workflow_id)
            if not ctx:
                return
            ctx.step_statuses[step_name] = StepStatus.FAILED
            ctx.status = WorkflowStatus.FAILED
            ctx.error_message = f"Step '{step_name}' failed: {error}"
            ctx.touch()
            logger.error(f"[Workflow {workflow_id}] Step '{step_name}' failed: {error}")
            self._try_repo_state(ctx.repository_id, RepositoryStateEnum.FAILED, failure_reason=error)
            event_bus.publish(
                EventType.WORKFLOW_FAILED,
                repository_id=ctx.repository_id,
                payload={"workflow_id": workflow_id, "step": step_name, "error": error},
            )

    # ------------------------------------------------------------------ #
    # Helpers                                                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _try_repo_state(
        repository_id: str,
        new_state: RepositoryStateEnum,
        *,
        current_stage: Optional[str] = None,
        failure_reason: Optional[str] = None,
    ) -> None:
        """Best-effort repository state transition — never raises."""
        try:
            sm = RepositoryStateMachine(repository_id)
            sm.transition_to(
                new_state,
                current_stage=current_stage,
                failure_reason=failure_reason,
            )
        except Exception as exc:
            logger.warning(f"[StateMachine] Could not transition {repository_id} → {new_state}: {exc}")


# Global singleton
workflow_executor = WorkflowExecutor()
