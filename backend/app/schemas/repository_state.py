from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RepositoryStateEnum(str, Enum):
    UPLOADED = "UPLOADED"
    QUEUED = "QUEUED"
    SCANNING = "SCANNING"
    PARSING = "PARSING"
    INDEXING = "INDEXING"
    EMBEDDING = "EMBEDDING"
    ANALYZING = "ANALYZING"
    READY = "READY"
    STALE = "STALE"
    REINDEXING = "REINDEXING"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class RepositoryState(BaseModel):
    repository: str
    state: RepositoryStateEnum
    previous_state: Optional[RepositoryStateEnum] = None
    state_timestamp: datetime
    job_id: Optional[str] = None
    failure_reason: Optional[str] = None
    progress: int = Field(default=0, ge=0, le=100)
    current_stage: Optional[str] = None
