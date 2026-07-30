from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid

class EventType(str, Enum):
    # Repository Events
    REPOSITORY_UPLOADED = "RepositoryUploaded"
    REPOSITORY_QUEUED = "RepositoryQueued"
    REPOSITORY_SCANNING = "RepositoryScanning"
    REPOSITORY_INDEXED = "RepositoryIndexed"
    REPOSITORY_READY = "RepositoryReady"
    REPOSITORY_FAILED = "RepositoryFailed"

    # Job Events
    JOB_QUEUED = "JobQueued"
    JOB_STARTED = "JobStarted"
    JOB_PROGRESS_UPDATED = "JobProgressUpdated"
    JOB_COMPLETED = "JobCompleted"
    JOB_FAILED = "JobFailed"

    # Analysis Events
    ARCHITECTURE_GENERATED = "ArchitectureGenerated"
    KNOWLEDGE_GRAPH_BUILT = "KnowledgeGraphBuilt"
    METRICS_GENERATED = "MetricsGenerated"
    SECURITY_COMPLETED = "SecurityCompleted"
    QUALITY_COMPLETED = "QualityCompleted"
    RISK_COMPLETED = "RiskCompleted"
    REPORT_GENERATED = "ReportGenerated"
    COPILOT_COMPLETED = "CopilotCompleted"

    # Workspace Events
    WORKSPACE_CREATED = "WorkspaceCreated"
    REPOSITORY_ADDED = "RepositoryAdded"
    REPOSITORY_REMOVED = "RepositoryRemoved"

    # Workflow Events
    WORKFLOW_STARTED = "WorkflowStarted"
    WORKFLOW_STEP_STARTED = "WorkflowStepStarted"
    WORKFLOW_STEP_COMPLETED = "WorkflowStepCompleted"
    WORKFLOW_COMPLETED = "WorkflowCompleted"
    WORKFLOW_FAILED = "WorkflowFailed"
    WORKFLOW_PAUSED = "WorkflowPaused"
    WORKFLOW_CANCELLED = "WorkflowCancelled"

class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    repository_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None
