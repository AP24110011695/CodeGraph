import logging
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timezone, timedelta
from app.schemas.reliability import RetryState, RetryPolicyType
from app.reliability.retry_policy import FixedRetryPolicy, LinearRetryPolicy, ExponentialRetryPolicy, RetryPolicy

logger = logging.getLogger(__name__)

class RetryManager:
    def __init__(self):
        self._retry_states: Dict[str, RetryState] = {}
        self._lock = threading.Lock()
        
        self.default_policies = {
            RetryPolicyType.FIXED: FixedRetryPolicy(max_attempts=3, delay_seconds=5.0),
            RetryPolicyType.LINEAR: LinearRetryPolicy(max_attempts=4, base_delay=5.0),
            RetryPolicyType.EXPONENTIAL: ExponentialRetryPolicy(max_attempts=5, initial_delay=2.0)
        }

    def register_retry(self, job_id: str, error: str, policy_type: RetryPolicyType = RetryPolicyType.EXPONENTIAL) -> Optional[float]:
        """
        Record a failure and return the delay until next retry.
        Returns None if retries are exhausted.
        """
        with self._lock:
            state = self._retry_states.get(job_id)
            if not state:
                state = RetryState(job_id=job_id, policy_type=policy_type)
                self._retry_states[job_id] = state

            state.attempts += 1
            state.last_error = error
            
            policy = self.default_policies.get(policy_type, self.default_policies[RetryPolicyType.EXPONENTIAL])
            delay = policy.get_delay(state.attempts)
            
            if delay is not None:
                state.next_retry_at = datetime.now(timezone.utc) + timedelta(seconds=delay)
                logger.info(f"Job {job_id} failed. Retrying in {delay} seconds (Attempt {state.attempts}). Error: {error}")
            else:
                state.next_retry_at = None
                logger.warning(f"Job {job_id} failed and exhausted all {state.attempts} retries. Error: {error}")
            
            return delay

    def get_retry_state(self, job_id: str) -> Optional[RetryState]:
        with self._lock:
            return self._retry_states.get(job_id)

    def clear_retry(self, job_id: str) -> None:
        with self._lock:
            if job_id in self._retry_states:
                del self._retry_states[job_id]

# Global instance
retry_manager = RetryManager()
