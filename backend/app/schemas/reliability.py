from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
import uuid

class RetryPolicyType(str, Enum):
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"

class CircuitBreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class DeadLetterJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_job_id: str
    task_type: str
    repository_id: str
    payload: Dict[str, Any]
    failure_reason: str
    failed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    retry_history: List[Dict[str, Any]] = Field(default_factory=list)

class RetryState(BaseModel):
    job_id: str
    attempts: int = 0
    next_retry_at: Optional[datetime] = None
    last_error: Optional[str] = None
    policy_type: RetryPolicyType = RetryPolicyType.EXPONENTIAL

class CircuitBreakerStatus(BaseModel):
    name: str
    state: CircuitBreakerState
    failure_count: int
    last_failure_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
