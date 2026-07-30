import time
import logging
import threading
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.schemas.reliability import CircuitBreakerState, CircuitBreakerStatus

logger = logging.getLogger(__name__)

class CircuitBreaker:
    def __init__(self, name: str, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_at: Optional[datetime] = None
        self.last_success_at: Optional[datetime] = None
        self._lock = threading.Lock()

    def record_success(self):
        with self._lock:
            self.last_success_at = datetime.now(timezone.utc)
            if self.state == CircuitBreakerState.HALF_OPEN or self.state == CircuitBreakerState.OPEN:
                logger.info(f"Circuit Breaker '{self.name}' recovered. Transitioning to CLOSED.")
                self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0

    def record_failure(self):
        with self._lock:
            self.last_failure_at = datetime.now(timezone.utc)
            self.failure_count += 1
            if self.state == CircuitBreakerState.CLOSED and self.failure_count >= self.failure_threshold:
                logger.warning(f"Circuit Breaker '{self.name}' threshold reached ({self.failure_count}). Transitioning to OPEN.")
                self.state = CircuitBreakerState.OPEN

    def allow_request(self) -> bool:
        with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            
            if self.state == CircuitBreakerState.OPEN:
                if self.last_failure_at:
                    elapsed = (datetime.now(timezone.utc) - self.last_failure_at).total_seconds()
                    if elapsed >= self.recovery_timeout:
                        logger.info(f"Circuit Breaker '{self.name}' recovery timeout passed. Transitioning to HALF_OPEN.")
                        self.state = CircuitBreakerState.HALF_OPEN
                        return True
                return False
                
            if self.state == CircuitBreakerState.HALF_OPEN:
                # In half-open, we allow one request through to test
                return True

            return False

    def get_status(self) -> CircuitBreakerStatus:
        with self._lock:
            return CircuitBreakerStatus(
                name=self.name,
                state=self.state,
                failure_count=self.failure_count,
                last_failure_at=self.last_failure_at,
                last_success_at=self.last_success_at
            )

class CircuitBreakerManager:
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()

    def get_breaker(self, name: str, failure_threshold: int = 5, recovery_timeout: float = 60.0) -> CircuitBreaker:
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name, failure_threshold, recovery_timeout)
            return self._breakers[name]
            
    def get_all_statuses(self) -> list[CircuitBreakerStatus]:
        with self._lock:
            return [b.get_status() for b in self._breakers.values()]

# Global instance
circuit_breaker_manager = CircuitBreakerManager()
