"""Repository Timeline Intelligence Engine module (CG-067)."""

from .architecture_drift import ArchitectureDrift
from .commit_analyzer import CommitAnalyzer
from .evolution_tracker import EvolutionTracker
from .history_provider import (
    BitbucketHistoryProvider,
    GitHistoryProvider,
    GitHubHistoryProvider,
    GitLabHistoryProvider,
    HistoryProvider,
    LocalMetadataHistoryProvider,
    get_history_provider,
)
from .hotspot_detector import HotspotDetector
from .ownership_tracker import OwnershipTracker
from .timeline_engine import TimelineEngine, timeline_engine
from .timeline_statistics import TimelineStatistics

__all__ = [
    "ArchitectureDrift",
    "BitbucketHistoryProvider",
    "CommitAnalyzer",
    "EvolutionTracker",
    "GitHistoryProvider",
    "GitHubHistoryProvider",
    "GitLabHistoryProvider",
    "HistoryProvider",
    "HotspotDetector",
    "LocalMetadataHistoryProvider",
    "OwnershipTracker",
    "TimelineEngine",
    "TimelineStatistics",
    "get_history_provider",
    "timeline_engine",
]
