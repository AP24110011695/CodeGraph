import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.schemas.repository_state import RepositoryStateEnum
from app.repository_state.state_machine import RepositoryStateMachine
from app.repository_state.state_manager import state_manager
from app.repository_state.transition_validator import TransitionValidator
from app.jobs.job_manager import job_manager
from app.jobs.job_status import Job, JobStatus

client = TestClient(app)

def setup_module():
    # Clear the state manager before tests
    state_manager._states.clear()

def teardown_function():
    # Clear after each test
    state_manager._states.clear()

def test_initial_state():
    sm = RepositoryStateMachine("repo-1")
    assert sm.current_state.state == RepositoryStateEnum.UPLOADED

def test_valid_transitions():
    sm = RepositoryStateMachine("repo-2")
    
    # UPLOADED -> QUEUED
    state = sm.transition_to(RepositoryStateEnum.QUEUED)
    assert state.state == RepositoryStateEnum.QUEUED
    
    # QUEUED -> SCANNING
    state = sm.transition_to(RepositoryStateEnum.SCANNING)
    assert state.state == RepositoryStateEnum.SCANNING
    
    # SCANNING -> PARSING
    state = sm.transition_to(RepositoryStateEnum.PARSING)
    assert state.state == RepositoryStateEnum.PARSING
    
    # PARSING -> INDEXING
    state = sm.transition_to(RepositoryStateEnum.INDEXING)
    assert state.state == RepositoryStateEnum.INDEXING
    
    # INDEXING -> EMBEDDING
    state = sm.transition_to(RepositoryStateEnum.EMBEDDING)
    assert state.state == RepositoryStateEnum.EMBEDDING
    
    # EMBEDDING -> ANALYZING
    state = sm.transition_to(RepositoryStateEnum.ANALYZING)
    assert state.state == RepositoryStateEnum.ANALYZING
    
    # ANALYZING -> READY
    state = sm.transition_to(RepositoryStateEnum.READY)
    assert state.state == RepositoryStateEnum.READY
    assert sm.is_ready()

def test_invalid_transition():
    sm = RepositoryStateMachine("repo-3")
    
    with pytest.raises(ValueError, match="Invalid state transition"):
        # UPLOADED -> READY is invalid
        sm.transition_to(RepositoryStateEnum.READY)

def test_failed_job_transition():
    sm = RepositoryStateMachine("repo-4")
    sm.transition_to(RepositoryStateEnum.QUEUED)
    sm.transition_to(RepositoryStateEnum.SCANNING)
    
    state = sm.transition_to(RepositoryStateEnum.FAILED, failure_reason="Test failure")
    assert state.state == RepositoryStateEnum.FAILED
    assert state.failure_reason == "Test failure"
    
    # FAILED -> QUEUED (retry)
    state = sm.transition_to(RepositoryStateEnum.QUEUED)
    assert state.state == RepositoryStateEnum.QUEUED

def test_cancelled_job_transition():
    sm = RepositoryStateMachine("repo-5")
    sm.transition_to(RepositoryStateEnum.QUEUED)
    sm.transition_to(RepositoryStateEnum.SCANNING)
    
    state = sm.transition_to(RepositoryStateEnum.CANCELLED)
    assert state.state == RepositoryStateEnum.CANCELLED

def test_api_endpoint():
    sm = RepositoryStateMachine("CodeGraphTest")
    sm.transition_to(RepositoryStateEnum.QUEUED)
    sm.transition_to(RepositoryStateEnum.SCANNING, progress=25, current_stage="Initial scan")
    
    response = client.get("/repository-state/CodeGraphTest")
    assert response.status_code == 200
    data = response.json()
    assert data["repository"] == "CodeGraphTest"
    assert data["state"] == "SCANNING"
    assert data["progress"] == 25
    assert data["current_stage"] == "Initial scan"

def test_api_not_found():
    response = client.get("/repository-state/UnknownRepo")
    assert response.status_code == 404

def test_job_queue_integration():
    repo_id = "repo-queue-test"
    # Ensure in-memory + any stale DB workflow hydrate does not leak prior runs.
    state_manager._states.pop(repo_id, None)

    # Create job (should set to QUEUED). Use a private manager with no workers
    # so the global worker pool cannot race past QUEUED before assertions.
    manager = job_manager.__class__(max_queue_size=10, num_workers=0)
    try:
        with patch.object(manager, '_validate_repository'):
            job = manager.create_job(repo_id, "indexing")

            sm = RepositoryStateMachine(repo_id)
            assert sm.current_state.state == RepositoryStateEnum.QUEUED
            assert sm.current_state.job_id == job.job_id

            manager.cancel_job(job.job_id)
            assert sm.current_state.state == RepositoryStateEnum.CANCELLED
    finally:
        manager.shutdown()
        state_manager._states.pop(repo_id, None)
