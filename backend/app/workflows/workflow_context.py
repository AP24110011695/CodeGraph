from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid


class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class StepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class WorkflowContext(BaseModel):
    """Context for a running workflow — holds all state including checkpoints."""

    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_name: str = "repository_processing"
    repository_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: Optional[str] = None
    progress: int = Field(default=0, ge=0, le=100)
    step_results: Dict[str, Any] = Field(default_factory=dict)
    step_statuses: Dict[str, StepStatus] = Field(default_factory=dict)
    # Arbitrary state data for future extensibility / persistence
    state_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error_message: Optional[str] = None
    correlation_id: Optional[str] = None

    # ------------------------------------------------------------------ #
    # Progress                                                              #
    # ------------------------------------------------------------------ #

    def compute_progress(self, total_steps: int) -> int:
        """Compute overall workflow progress as integer percentage."""
        if total_steps == 0:
            return 100
        completed = sum(
            1 for s in self.step_statuses.values() if s == StepStatus.COMPLETED
        )
        return min(100, int(completed * 100 / total_steps))

    # ------------------------------------------------------------------ #
    # Checkpoint                                                            #
    # ------------------------------------------------------------------ #

    def get_checkpoint(self) -> Dict[str, Any]:
        """Serialise full context for storage."""
        return self.model_dump(mode="json")

    @classmethod
    def from_checkpoint(cls, data: Dict[str, Any]) -> "WorkflowContext":
        """Restore context from a stored checkpoint dict."""
        return cls(**data)

    # ------------------------------------------------------------------ #
    # Helpers                                                               #
    # ------------------------------------------------------------------ #

    def touch(self) -> None:
        """Stamp updated_at to now."""
        self.updated_at = datetime.now(timezone.utc)
