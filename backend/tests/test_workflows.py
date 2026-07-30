"""
Tests for CG-054 (Workflow Orchestration Engine) and CG-055 (Distributed Task Execution Layer).
"""

import time
import threading
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.main import app
from app.workflows.workflow_context import WorkflowContext, WorkflowStatus, StepStatus
from app.workflows.workflow_step import WorkflowStep
from app.workflows.workflow_definition import WorkflowDefinition
from app.workflows.workflow_registry import WorkflowRegistry
from app.workflows.workflow_executor import WorkflowExecutor
from app.workflows.workflow_engine import WorkflowEngine
from app.workers.worker_manager import WorkerManager, WorkerStatus, WorkerHealth
from app.workers.task_executor import TaskExecutor
from app.workers.task_router import TaskRouter
from app.workers.worker_pool import WorkerPool
from app.events.event_bus import EventBus
from app.events.event_types import EventType

client = TestClient(app)


# ============================================================
# WorkflowContext
# ============================================================

class TestWorkflowContext:
    def test_creation_defaults(self):
        ctx = WorkflowContext(repository_id="repo-1")
        assert ctx.workflow_id
        assert ctx.status == WorkflowStatus.PENDING
        assert ctx.progress == 0
        assert ctx.step_statuses == {}

    def test_compute_progress(self):
        ctx = WorkflowContext(repository_id="repo-1")
        ctx.step_statuses = {
            "scan": StepStatus.COMPLETED,
            "parse": StepStatus.COMPLETED,
            "ready": StepStatus.PENDING,
        }
        assert ctx.compute_progress(3) == 66

    def test_compute_progress_all_done(self):
        ctx = WorkflowContext(repository_id="r")
        ctx.step_statuses = {"a": StepStatus.COMPLETED, "b": StepStatus.COMPLETED}
        assert ctx.compute_progress(2) == 100

    def test_checkpoint_roundtrip(self):
        ctx = WorkflowContext(repository_id="repo-cp")
        ctx.status = WorkflowStatus.RUNNING
        ctx.step_statuses = {"scan": StepStatus.COMPLETED}
        data = ctx.get_checkpoint()
        restored = WorkflowContext.from_checkpoint(data)
        assert restored.workflow_id == ctx.workflow_id
        assert restored.status == WorkflowStatus.RUNNING
        assert restored.step_statuses["scan"] == StepStatus.COMPLETED


# ============================================================
# WorkflowStep & WorkflowDefinition
# ============================================================

class TestWorkflowDefinition:
    def _make_definition(self):
        return WorkflowDefinition(
            name="test_wf",
            steps=[
                WorkflowStep(name="a", task_type="upload"),
                WorkflowStep(name="b", task_type="scan", dependencies=["a"]),
                WorkflowStep(name="c", task_type="parse", dependencies=["b"]),
            ],
        )

    def test_get_step(self):
        defn = self._make_definition()
        step = defn.get_step("b")
        assert step is not None
        assert step.task_type == "scan"

    def test_executable_steps_initial(self):
        defn = self._make_definition()
        ctx = WorkflowContext(repository_id="r")
        runnable = defn.get_executable_steps(ctx)
        assert len(runnable) == 1
        assert runnable[0].name == "a"

    def test_executable_steps_after_a(self):
        defn = self._make_definition()
        ctx = WorkflowContext(repository_id="r")
        ctx.step_statuses["a"] = StepStatus.COMPLETED
        runnable = defn.get_executable_steps(ctx)
        assert runnable[0].name == "b"

    def test_can_run_respects_dependencies(self):
        step = WorkflowStep(name="b", task_type="scan", dependencies=["a"])
        ctx = WorkflowContext(repository_id="r")
        assert not step.can_run(ctx)
        ctx.step_statuses["a"] = StepStatus.COMPLETED
        assert step.can_run(ctx)


# ============================================================
# WorkflowRegistry
# ============================================================

class TestWorkflowRegistry:
    def test_register_and_get(self):
        reg = WorkflowRegistry()
        defn = WorkflowDefinition(name="my_wf", steps=[])
        reg.register(defn)
        assert reg.get_workflow("my_wf") is defn

    def test_get_missing(self):
        reg = WorkflowRegistry()
        assert reg.get_workflow("not_there") is None


# ============================================================
# WorkflowExecutor (isolated with mocked router)
# ============================================================

def _make_instant_executor():
    """Return a WorkflowExecutor whose task router resolves steps immediately."""
    bus = EventBus()
    router = TaskRouter()

    executor = WorkflowExecutor.__new__(WorkflowExecutor)
    executor._contexts = {}
    executor._definitions = {}
    executor._lock = threading.Lock()
    bus.subscribe(EventType.JOB_COMPLETED, executor._handle_job_completed)
    bus.subscribe(EventType.JOB_FAILED, executor._handle_job_failed)
    executor._bus = bus
    executor._router = router

    # Override route_task to immediately publish JOB_COMPLETED via bus
    def fake_route(task_type, repository_id, context_data):
        bus.publish(
            EventType.JOB_COMPLETED,
            repository_id=repository_id,
            payload={"task_type": task_type, "result": {}, "context": context_data},
        )

    router.route_task = fake_route

    # Wire executor to use fake router
    import app.workers.task_router as tr_module
    original_router = tr_module.task_router
    tr_module.task_router = router

    return executor, bus, router, original_router


class TestWorkflowExecutor:
    def test_single_step_workflow_completes(self):
        import sys
        import app.workflows.workflow_executor
        eb_module = sys.modules['app.workflows.workflow_executor']
        import app.repository_state.state_machine as sm_module
        tr_module = sys.modules['app.workflows.workflow_executor']
        from app.events.event_bus import EventBus

        bus = EventBus()
        executor = WorkflowExecutor.__new__(WorkflowExecutor)
        executor._contexts = {}
        executor._definitions = {}
        executor._lock = threading.Lock()
        bus.subscribe(EventType.JOB_COMPLETED, executor._handle_job_completed)
        bus.subscribe(EventType.JOB_FAILED, executor._handle_job_failed)

        fired = []
        bus.subscribe(EventType.WORKFLOW_COMPLETED, lambda e: fired.append(e))

        orig_bus = eb_module.event_bus
        orig_sm = sm_module.RepositoryStateMachine
        orig_router = tr_module.task_router

        def fake_route(task_type, repository_id, context_data):
            bus.publish(
                EventType.JOB_COMPLETED,
                repository_id=repository_id,
                payload={"task_type": task_type, "result": {}, "context": context_data},
            )

        fake_router = TaskRouter()
        fake_router.route_task = fake_route
        tr_module.task_router = fake_router
        eb_module.event_bus = bus
        sm_module.RepositoryStateMachine = MagicMock()

        try:
            defn = WorkflowDefinition(
                name="mini",
                steps=[WorkflowStep(name="upload", task_type="upload")],
            )
            ctx = WorkflowContext(repository_id="repo-x")
            executor.start_workflow(defn, ctx)
            time.sleep(0.3)
            assert ctx.status == WorkflowStatus.COMPLETED
            assert ctx.progress == 100
        finally:
            tr_module.task_router = orig_router
            eb_module.event_bus = orig_bus
            sm_module.RepositoryStateMachine = orig_sm

    def test_pause_resume(self):
        import sys
        import app.workflows.workflow_executor
        eb_module = sys.modules['app.workflows.workflow_executor']
        import app.repository_state.state_machine as sm_module
        tr_module = sys.modules['app.workflows.workflow_executor']
        from app.events.event_bus import EventBus

        bus = EventBus()
        executor = WorkflowExecutor.__new__(WorkflowExecutor)
        executor._contexts = {}
        executor._definitions = {}
        executor._lock = threading.Lock()
        bus.subscribe(EventType.JOB_COMPLETED, executor._handle_job_completed)
        bus.subscribe(EventType.JOB_FAILED, executor._handle_job_failed)

        orig_bus = eb_module.event_bus
        orig_sm = sm_module.RepositoryStateMachine
        orig_router = tr_module.task_router
        eb_module.event_bus = bus
        sm_module.RepositoryStateMachine = MagicMock()
        # Non-completing router
        tr_module.task_router = TaskRouter()

        try:
            defn = WorkflowDefinition(
                name="wf",
                steps=[WorkflowStep(name="scan", task_type="scan")],
            )
            ctx = WorkflowContext(repository_id="repo-pause")
            executor.start_workflow(defn, ctx)

            ok = executor.pause_workflow(ctx.workflow_id)
            assert ok
            assert ctx.status == WorkflowStatus.PAUSED

            ok = executor.resume_workflow(ctx.workflow_id)
            assert ok
            assert ctx.status == WorkflowStatus.RUNNING
        finally:
            eb_module.event_bus = orig_bus
            sm_module.RepositoryStateMachine = orig_sm
            tr_module.task_router = orig_router

    def test_cancel(self):
        import sys
        import app.workflows.workflow_executor
        eb_module = sys.modules['app.workflows.workflow_executor']
        import app.repository_state.state_machine as sm_module
        tr_module = sys.modules['app.workflows.workflow_executor']
        from app.events.event_bus import EventBus

        bus = EventBus()
        executor = WorkflowExecutor.__new__(WorkflowExecutor)
        executor._contexts = {}
        executor._definitions = {}
        executor._lock = threading.Lock()
        bus.subscribe(EventType.JOB_COMPLETED, executor._handle_job_completed)
        bus.subscribe(EventType.JOB_FAILED, executor._handle_job_failed)

        orig_bus = eb_module.event_bus
        orig_sm = sm_module.RepositoryStateMachine
        orig_router = tr_module.task_router
        eb_module.event_bus = bus
        sm_module.RepositoryStateMachine = MagicMock()
        tr_module.task_router = TaskRouter()  # non-completing

        try:
            defn = WorkflowDefinition(
                name="wf",
                steps=[WorkflowStep(name="scan", task_type="scan")],
            )
            ctx = WorkflowContext(repository_id="repo-cancel")
            executor.start_workflow(defn, ctx)
            ok = executor.cancel_workflow(ctx.workflow_id)
            assert ok
            assert ctx.status == WorkflowStatus.CANCELLED
        finally:
            eb_module.event_bus = orig_bus
            sm_module.RepositoryStateMachine = orig_sm
            tr_module.task_router = orig_router

    def test_step_failure_marks_workflow_failed(self):
        import sys
        import app.workflows.workflow_executor
        eb_module = sys.modules['app.workflows.workflow_executor']
        import app.repository_state.state_machine as sm_module
        tr_module = sys.modules['app.workflows.workflow_executor']
        from app.events.event_bus import EventBus

        bus = EventBus()
        executor = WorkflowExecutor.__new__(WorkflowExecutor)
        executor._contexts = {}
        executor._definitions = {}
        executor._lock = threading.Lock()
        bus.subscribe(EventType.JOB_COMPLETED, executor._handle_job_completed)
        bus.subscribe(EventType.JOB_FAILED, executor._handle_job_failed)

        orig_bus = eb_module.event_bus
        orig_sm = sm_module.RepositoryStateMachine
        orig_router = tr_module.task_router
        eb_module.event_bus = bus
        sm_module.RepositoryStateMachine = MagicMock()

        def fail_route(task_type, repository_id, context_data):
            bus.publish(
                EventType.JOB_FAILED,
                repository_id=repository_id,
                payload={"task_type": task_type, "error": "boom", "context": context_data},
            )

        fail_router = TaskRouter()
        fail_router.route_task = fail_route
        tr_module.task_router = fail_router

        try:
            defn = WorkflowDefinition(
                name="wf",
                steps=[WorkflowStep(name="scan", task_type="scan")],
            )
            ctx = WorkflowContext(repository_id="repo-fail")
            executor.start_workflow(defn, ctx)
            time.sleep(0.3)
            assert ctx.status == WorkflowStatus.FAILED
            assert "scan" in ctx.error_message
        finally:
            eb_module.event_bus = orig_bus
            sm_module.RepositoryStateMachine = orig_sm
            tr_module.task_router = orig_router


# ============================================================
# WorkerManager
# ============================================================

class TestWorkerManager:
    def test_register_and_list(self):
        mgr = WorkerManager()
        info = mgr.register_worker("w1", ["all"])
        assert info.worker_id == "w1"
        assert len(mgr.get_workers()) == 1

    def test_heartbeat_updates_status(self):
        mgr = WorkerManager()
        mgr.register_worker("w2", [])
        mgr.heartbeat("w2", WorkerStatus.BUSY, current_task="scan")
        w = mgr.get_worker("w2")
        assert w.status == WorkerStatus.BUSY
        assert w.current_task == "scan"
        assert w.health == WorkerHealth.HEALTHY

    def test_check_health_stale_worker(self):
        import datetime
        mgr = WorkerManager()
        mgr.register_worker("w3", [])
        # Backdate heartbeat
        with mgr._lock:
            mgr._workers["w3"].last_heartbeat = (
                datetime.datetime.now(datetime.timezone.utc)
                - datetime.timedelta(seconds=200)
            )
        mgr.check_health()
        w = mgr.get_worker("w3")
        assert w.status == WorkerStatus.OFFLINE
        assert w.health == WorkerHealth.UNHEALTHY

    def test_get_idle_workers_filters(self):
        mgr = WorkerManager()
        mgr.register_worker("w4", ["all"])
        mgr.heartbeat("w4", WorkerStatus.IDLE)
        mgr.register_worker("w5", ["all"])
        mgr.heartbeat("w5", WorkerStatus.BUSY)
        idle = mgr.get_idle_workers()
        assert any(w.worker_id == "w4" for w in idle)
        assert all(w.worker_id != "w5" for w in idle)

    def test_deregister(self):
        mgr = WorkerManager()
        mgr.register_worker("w6", [])
        mgr.deregister_worker("w6")
        assert mgr.get_worker("w6") is None


# ============================================================
# TaskExecutor
# ============================================================

class TestTaskExecutor:
    def test_register_and_execute_custom_handler(self):
        ex = TaskExecutor.__new__(TaskExecutor)
        ex._handlers = {}
        ex.register_handler("noop", lambda repo_id, **_: {"ok": True})
        result = ex.execute("noop", "repo-1")
        assert result == {"ok": True}

    def test_missing_handler_raises(self):
        ex = TaskExecutor.__new__(TaskExecutor)
        ex._handlers = {}
        with pytest.raises(ValueError, match="No handler"):
            ex.execute("unknown", "repo-1")

    def test_default_handlers_registered(self):
        ex = TaskExecutor()
        types = ex.list_task_types()
        for expected in ["upload", "scan", "parse", "architecture", "quality",
                         "security", "risk", "metrics", "report", "copilot", "ready"]:
            assert expected in types


# ============================================================
# TaskRouter
# ============================================================

class TestTaskRouter:
    def test_route_and_consume(self):
        router = TaskRouter()
        router.route_task("scan", "repo-1", {"key": "val"})
        task = router.get_next_task(timeout=1.0)
        assert task is not None
        assert task["task_type"] == "scan"
        assert task["repository_id"] == "repo-1"

    def test_empty_queue_returns_none(self):
        router = TaskRouter()
        task = router.get_next_task(timeout=0.1)
        assert task is None


# ============================================================
# WorkerPool
# ============================================================

class TestWorkerPool:
    def test_start_stop(self):
        pool = WorkerPool(num_workers=2)
        pool.start()
        time.sleep(0.2)
        assert pool.active_count() == 2
        pool.stop()
        time.sleep(0.2)
        assert pool.active_count() == 0

    def test_idempotent_start(self):
        pool = WorkerPool(num_workers=1)
        pool.start()
        pool.start()  # Should not double-spawn
        time.sleep(0.1)
        assert pool.active_count() == 1
        pool.stop()


# ============================================================
# Concurrent workflows
# ============================================================

class TestConcurrentWorkflows:
    def test_multiple_concurrent_workflows(self):
        """Multiple workflows can run simultaneously without interference."""
        import sys
        import app.workflows.workflow_executor
        eb_module = sys.modules['app.workflows.workflow_executor']
        import app.repository_state.state_machine as sm_module
        tr_module = sys.modules['app.workflows.workflow_executor']

        from app.events.event_bus import EventBus as _EventBus
        bus = _EventBus()
        orig_bus = eb_module.event_bus
        orig_sm = sm_module.RepositoryStateMachine
        orig_router = tr_module.task_router

        eb_module.event_bus = bus
        sm_module.RepositoryStateMachine = MagicMock()

        executor = WorkflowExecutor.__new__(WorkflowExecutor)
        executor._contexts = {}
        executor._definitions = {}
        executor._lock = threading.Lock()
        bus.subscribe(EventType.JOB_COMPLETED, executor._handle_job_completed)
        bus.subscribe(EventType.JOB_FAILED, executor._handle_job_failed)

        def instant_route(task_type, repository_id, context_data):
            bus.publish(
                EventType.JOB_COMPLETED,
                repository_id=repository_id,
                payload={"task_type": task_type, "result": {}, "context": context_data},
            )

        fast_router = TaskRouter()
        fast_router.route_task = instant_route
        tr_module.task_router = fast_router

        try:
            defn = WorkflowDefinition(
                name="concurrent_wf",
                steps=[
                    WorkflowStep(name="upload", task_type="upload"),
                    WorkflowStep(name="scan", task_type="scan", dependencies=["upload"]),
                ],
            )
            contexts = []
            for i in range(3):
                ctx = WorkflowContext(repository_id=f"repo-concurrent-{i}")
                executor.start_workflow(defn, ctx)
                contexts.append(ctx)

            time.sleep(0.5)
            for ctx in contexts:
                assert ctx.status == WorkflowStatus.COMPLETED, (
                    f"Workflow {ctx.workflow_id} not completed: {ctx.status}"
                )
        finally:
            eb_module.event_bus = orig_bus
            sm_module.RepositoryStateMachine = orig_sm
            tr_module.task_router = orig_router


# ============================================================
# API Endpoints
# ============================================================

class TestWorkflowAPI:
    def test_start_unknown_workflow(self):
        response = client.post("/workflows/start/my-repo?workflow_name=nonexistent_wf")
        assert response.status_code == 404

    def test_list_workflows(self):
        response = client.get("/workflows")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_nonexistent_workflow(self):
        response = client.get("/workflows/does-not-exist")
        assert response.status_code == 404

    def test_pause_nonexistent_workflow(self):
        response = client.post("/workflows/does-not-exist/pause")
        assert response.status_code == 400

    def test_cancel_nonexistent_workflow(self):
        response = client.post("/workflows/does-not-exist/cancel")
        assert response.status_code == 400

    def test_restore_missing_checkpoint(self):
        response = client.post(
            "/workflows/restore",
            json={"workflow_name": "repository_processing", "workflow_id": "missing-id"},
        )
        assert response.status_code == 404


class TestWorkersAPI:
    def test_list_workers(self):
        response = client.get("/workers")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_idle_workers(self):
        response = client.get("/workers/idle")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# ============================================================
# Regression — previous modules still work
# ============================================================

class TestRegression:
    def test_upload_api_still_works(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_events_api_still_works(self):
        response = client.get("/events")
        assert response.status_code == 200

    def test_jobs_api_still_works(self):
        response = client.get("/jobs")
        assert response.status_code == 200

    def test_repository_state_api_still_works(self):
        response = client.get("/repository-state/does-not-exist")
        # 404 is fine — proves the router is wired
        assert response.status_code in (200, 404)
