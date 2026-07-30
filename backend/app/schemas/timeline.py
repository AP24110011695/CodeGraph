"""Pydantic schemas for Repository Timeline Intelligence (CG-067)."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CommitRecord(BaseModel):
    """Normalized commit record independent of history provider."""

    sha: str = Field(description="Commit identifier / SHA")
    message: str = Field(description="Commit message summary")
    author: str = Field(description="Author display name")
    email: str = Field(default="", description="Author email")
    timestamp: datetime = Field(description="Commit timestamp (UTC)")
    files_changed: List[str] = Field(default_factory=list, description="Paths touched by the commit")
    insertions: int = Field(default=0, description="Lines added")
    deletions: int = Field(default=0, description="Lines removed")
    modules_touched: List[str] = Field(default_factory=list, description="Top-level modules touched")


class FileChangeStats(BaseModel):
    """Aggregate change statistics for a single file."""

    file_path: str
    change_count: int = 0
    authors: List[str] = Field(default_factory=list)
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    insertions: int = 0
    deletions: int = 0
    churn_score: float = Field(default=0.0, description="Normalized churn / instability score")


class ModuleEvolution(BaseModel):
    """Evolution summary for a module / package."""

    module_name: str
    change_count: int = 0
    file_count: int = 0
    authors: List[str] = Field(default_factory=list)
    related_modules: List[str] = Field(default_factory=list, description="Modules that often change together")
    stability: str = Field(default="stable", description="stable | moderate | unstable")
    summary: str = ""


class FileEvolution(BaseModel):
    """Evolution summary for a single file."""

    file_path: str
    change_count: int = 0
    authors: List[str] = Field(default_factory=list)
    stability: str = Field(default="stable")
    summary: str = ""


class CoEvolutionPair(BaseModel):
    """Pair of modules that frequently evolve together."""

    module_a: str
    module_b: str
    co_change_count: int = 0
    coupling_score: float = Field(default=0.0, description="0.0–1.0 relative coupling strength")


class Hotspot(BaseModel):
    """A frequently changing / unstable area of the repository."""

    path: str
    hotspot_type: str = Field(default="file", description="file | module")
    change_frequency: int = 0
    churn_score: float = 0.0
    authors: List[str] = Field(default_factory=list)
    risk_level: str = Field(default="medium", description="low | medium | high")
    reason: str = ""


class OwnershipRecord(BaseModel):
    """Ownership / contribution profile for a path."""

    path: str
    primary_owner: str
    ownership_pct: float = Field(default=0.0, description="Share of commits by primary owner (0–100)")
    contributors: Dict[str, int] = Field(default_factory=dict, description="Author -> commit count")
    bus_factor: int = Field(default=1, description="Number of significant contributors")


class ArchitectureDriftEvent(BaseModel):
    """Historical architecture drift signal derived from timeline commits."""

    event_id: str
    timestamp: datetime
    description: str
    severity: str = Field(default="info", description="info | warning | critical")
    modules_affected: List[str] = Field(default_factory=list)
    coupling_delta: float = Field(default=0.0, description="Change in coupling pressure")
    category: str = Field(
        default="structural",
        description="structural | dependency | ownership | hotspot",
    )


class HistoricalSummary(BaseModel):
    """Human-readable historical summary answering timeline questions."""

    repository_id: str
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    what_changed_most: List[str] = Field(default_factory=list)
    unstable_files: List[str] = Field(default_factory=list)
    modules_evolving_together: List[str] = Field(default_factory=list)
    architecture_evolution: str = ""
    tightly_coupled_components: List[str] = Field(default_factory=list)
    narrative: str = ""


class TimelineStatisticsModel(BaseModel):
    """Aggregate timeline statistics."""

    total_commits: int = 0
    total_authors: int = 0
    total_files_touched: int = 0
    total_modules_touched: int = 0
    hotspot_count: int = 0
    drift_event_count: int = 0
    average_files_per_commit: float = 0.0
    most_active_author: Optional[str] = None
    most_changed_module: Optional[str] = None
    most_changed_file: Optional[str] = None
    change_frequency_by_module: Dict[str, int] = Field(default_factory=dict)


class RepositoryTimelineResponse(BaseModel):
    """Full repository timeline intelligence payload."""

    repository_id: str
    provider: str = Field(default="local_metadata", description="History provider used")
    commits: List[CommitRecord] = Field(default_factory=list)
    statistics: TimelineStatisticsModel = Field(default_factory=TimelineStatisticsModel)
    historical_summary: HistoricalSummary
    hotspots: List[Hotspot] = Field(default_factory=list)
    ownership: List[OwnershipRecord] = Field(default_factory=list)
    architecture_drift_events: List[ArchitectureDriftEvent] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class EvolutionResponse(BaseModel):
    """Repository evolution tracking response."""

    repository_id: str
    modules: List[ModuleEvolution] = Field(default_factory=list)
    files: List[FileEvolution] = Field(default_factory=list)
    co_evolution: List[CoEvolutionPair] = Field(default_factory=list)
    what_changed_most: List[str] = Field(default_factory=list)
    modules_evolving_together: List[str] = Field(default_factory=list)
    summary: str = ""


class HotspotsResponse(BaseModel):
    """Hotspot detection response."""

    repository_id: str
    hotspots: List[Hotspot] = Field(default_factory=list)
    unstable_files: List[str] = Field(default_factory=list)
    frequently_changing_parts: List[str] = Field(default_factory=list)
    summary: str = ""
