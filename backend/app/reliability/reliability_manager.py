import logging
import threading
from typing import Dict, Any, Optional

from app.events.event_bus import event_bus, EventBus
from app.events.event_types import EventType
from app.schemas.reliability import RetryPolicyType
from app.reliability.retry_manager import retry_manager
from app.reliability.dead_letter_queue import dead_letter_queue
from app.reliability.idempotency_manager import idempotency_manager
from app.reliability.circuit_breaker import circuit_breaker_manager
from app.reliability.timeout_manager import timeout_manager
import time

logger = logging.getLogger(__name__)

class ReliabilityManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._initialized = False

    def initialize(self):
        with self._lock:
            if self._initialized:
                return
            
            # Subscribe to events for retry handling
            event_bus.subscribe(EventType.JOB_FAILED, self._handle_job_failed)
            event_bus.subscribe(EventType.JOB_COMPLETED, self._handle_job_completed)
            
            # Start timeout manager
            timeout_manager.start()

            self._initialized = True
            logger.info("ReliabilityManager initialized.")

    def _handle_job_failed(self, event):
        job_id = event.correlation_id or event.payload.get("job_id", "")
        if not job_id:
            logger.warning("JOB_FAILED event missing job_id. Cannot apply reliability policies.")
            return

        task_type = event.payload.get("task_type", "unknown")
        repository_id = event.repository_id or "unknown"
        error_msg = event.payload.get("error", "Unknown error")
        context_data = event.payload.get("context", {})

        # Check circuit breaker
        cb = circuit_breaker_manager.get_breaker(task_type)
        cb.record_failure()

        # Check retries
        delay = retry_manager.register_retry(job_id, error_msg, policy_type=RetryPolicyType.EXPONENTIAL)
        
        if delay is not None:
            # We will retry this job
            # Since this is an async system, we can spin up a quick timer to re-route it
            def _retry_task():
                time.sleep(delay)
                logger.info(f"Retrying task {task_type} for {repository_id} (job_id: {job_id})")
                
                # Check circuit breaker before retrying
                if not cb.allow_request():
                    logger.warning(f"Circuit breaker for {task_type} is OPEN. Failing retry immediately.")
                    # Treat as failure, bypassing wait
                    event_bus.publish(
                        EventType.JOB_FAILED,
                        repository_id=repository_id,
                        payload={
                            "task_type": task_type,
                            "error": "Circuit Breaker OPEN",
                            "context": context_data,
                            "job_id": job_id
                        },
                        correlation_id=job_id
                    )
                    return
                
                # Unmark idempotency so it can run again
                fingerprint = idempotency_manager.generate_fingerprint(task_type, repository_id, context_data)
                idempotency_manager.remove_fingerprint(fingerprint)
                
                from app.workers.task_router import task_router
                task_router.route_task(task_type, repository_id, context_data)

            threading.Thread(target=_retry_task, daemon=True).start()
        else:
            # Exhausted retries, move to DLQ
            state = retry_manager.get_retry_state(job_id)
            history = [{"attempt": state.attempts, "last_error": state.last_error}] if state else []
            dead_letter_queue.add_job(
                job_id=job_id,
                task_type=task_type,
                repository_id=repository_id,
                payload=context_data,
                failure_reason=error_msg,
                retry_history=history
            )
            retry_manager.clear_retry(job_id)

    def _handle_job_completed(self, event):
        job_id = event.correlation_id or event.payload.get("job_id", "")
        task_type = event.payload.get("task_type", "unknown")
        
        # Unregister any timeout
        if job_id:
            timeout_manager.unregister_timeout(job_id)
            retry_manager.clear_retry(job_id)

        # Record success for circuit breaker
        cb = circuit_breaker_manager.get_breaker(task_type)
        cb.record_success()

    def replay_dlq_job(self, dlq_id: str) -> bool:
        job = dead_letter_queue.get_job(dlq_id)
        if not job:
            return False

        logger.info(f"Replaying DLQ job {dlq_id} (original_job_id: {job.original_job_id})")
        
        # Clean idempotency for replay
        fingerprint = idempotency_manager.generate_fingerprint(job.task_type, job.repository_id, job.payload)
        idempotency_manager.remove_fingerprint(fingerprint)
        
        from app.workers.task_router import task_router
        task_router.route_task(job.task_type, job.repository_id, job.payload)
        dead_letter_queue.remove_job(dlq_id)
        return True

# Global instance
reliability_manager = ReliabilityManager()
