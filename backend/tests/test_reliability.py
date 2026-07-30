import pytest
import time
from unittest.mock import MagicMock
from app.reliability.retry_policy import FixedRetryPolicy, ExponentialRetryPolicy
from app.reliability.dead_letter_queue import DeadLetterQueue
from app.reliability.idempotency_manager import IdempotencyManager
from app.reliability.circuit_breaker import CircuitBreaker, CircuitBreakerState
from app.reliability.timeout_manager import TimeoutManager

def test_fixed_retry_policy():
    policy = FixedRetryPolicy(max_attempts=3, delay_seconds=1.0)
    assert policy.get_delay(1) == 1.0
    assert policy.get_delay(2) == 1.0
    assert policy.get_delay(3) is None

def test_exponential_retry_policy():
    policy = ExponentialRetryPolicy(max_attempts=4, initial_delay=2.0, multiplier=2.0)
    assert policy.get_delay(1) == 2.0
    assert policy.get_delay(2) == 4.0
    assert policy.get_delay(3) == 8.0
    assert policy.get_delay(4) is None

def test_dead_letter_queue():
    dlq = DeadLetterQueue()
    job = dlq.add_job("job1", "scan", "repo1", {"data": "test"}, "error")
    assert dlq.get_job(job.id) == job
    assert len(dlq.get_jobs()) == 1
    dlq.remove_job(job.id)
    assert len(dlq.get_jobs()) == 0

def test_idempotency_duplicate_execution():
    manager = IdempotencyManager()
    fp = manager.generate_fingerprint("scan", "repo1", {"context": "test"})
    assert manager.mark_execution_started("job1", fp) is True
    assert manager.mark_execution_started("job2", fp) is False
    manager.remove_fingerprint(fp)
    assert manager.mark_execution_started("job3", fp) is True

def test_circuit_breaker_open_recovery():
    cb = CircuitBreaker("test_cb", failure_threshold=2, recovery_timeout=0.1)
    assert cb.allow_request() is True
    
    cb.record_failure()
    assert cb.state == CircuitBreakerState.CLOSED
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    assert cb.allow_request() is False
    
    time.sleep(0.15)
    assert cb.allow_request() is True
    assert cb.state == CircuitBreakerState.HALF_OPEN
    
    cb.record_success()
    assert cb.state == CircuitBreakerState.CLOSED

def test_timeout_manager():
    tm = TimeoutManager()
    tm.start()
    
    called = []
    def on_timeout(job_id):
        called.append(job_id)
        
    tm.register_timeout("job1", 0.1, on_timeout)
    time.sleep(1.2) # Monitor loop runs every 1 sec
    assert "job1" in called
    tm.stop()
