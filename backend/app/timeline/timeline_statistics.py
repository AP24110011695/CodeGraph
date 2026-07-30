"""Timeline statistics and historical summary generation."""

from __future__ import annotations

from typing import List

from app.schemas.timeline import (
    ArchitectureDriftEvent,
    CommitRecord,
    EvolutionResponse,
    HistoricalSummary,
    HotspotsResponse,
    OwnershipRecord,
    TimelineStatisticsModel,
)
from app.timeline.commit_analyzer import CommitAnalyzer


class TimelineStatistics:
    """Aggregates timeline metrics and builds historical summaries.

    Does not duplicate release-notes / memory historical text — produces
    timeline-specific summaries that enrich those systems.
    """

    def __init__(self, commit_analyzer: CommitAnalyzer | None = None):
        self.commit_analyzer = commit_analyzer or CommitAnalyzer()

    def compute(
        self,
        commits: List[CommitRecord],
        hotspots: HotspotsResponse | None = None,
        drift_events: List[ArchitectureDriftEvent] | None = None,
        ownership: List[OwnershipRecord] | None = None,
    ) -> TimelineStatisticsModel:
        authors = self.commit_analyzer.author_activity(commits)
        modules = self.commit_analyzer.module_activity(commits)
        files = self.commit_analyzer.change_frequency(commits)

        avg_files = 0.0
        if commits:
            avg_files = round(
                sum(len(c.files_changed) for c in commits) / len(commits),
                2,
            )

        most_author = max(authors, key=authors.get) if authors else None
        most_module = max(modules, key=modules.get) if modules else None
        most_file = next(iter(files.keys()), None) if files else None

        return TimelineStatisticsModel(
            total_commits=len(commits),
            total_authors=len(authors),
            total_files_touched=len(files),
            total_modules_touched=len(modules),
            hotspot_count=len(hotspots.hotspots) if hotspots else 0,
            drift_event_count=len(drift_events or []),
            average_files_per_commit=avg_files,
            most_active_author=most_author,
            most_changed_module=most_module,
            most_changed_file=most_file,
            change_frequency_by_module=modules,
        )

    def build_historical_summary(
        self,
        repository_id: str,
        commits: List[CommitRecord],
        evolution: EvolutionResponse,
        hotspots: HotspotsResponse,
        drift_events: List[ArchitectureDriftEvent],
        architecture_narrative: str,
    ) -> HistoricalSummary:
        start, end = self.commit_analyzer.period(commits)
        tightly = [
            f"{p.module_a} ↔ {p.module_b}"
            for p in evolution.co_evolution[:5]
            if p.coupling_score >= 0.4
        ]

        narrative = (
            f"Repository '{repository_id}' timeline covers {len(commits)} commits. "
            f"{hotspots.summary} "
            f"{architecture_narrative}"
        )

        return HistoricalSummary(
            repository_id=repository_id,
            period_start=start,
            period_end=end,
            what_changed_most=evolution.what_changed_most,
            unstable_files=hotspots.unstable_files[:10],
            modules_evolving_together=evolution.modules_evolving_together,
            architecture_evolution=architecture_narrative,
            tightly_coupled_components=tightly,
            narrative=narrative,
        )
