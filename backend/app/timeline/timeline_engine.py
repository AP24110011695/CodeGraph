"""Repository Timeline Intelligence Engine facade (CG-067)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from app.cache.cache_interface import CacheInterface
from app.cache.cache_keys import CacheKeys
from app.cache.cache_manager import cache_manager
from app.schemas.timeline import (
    EvolutionResponse,
    HotspotsResponse,
    RepositoryTimelineResponse,
)
from app.telemetry.telemetry_manager import telemetry_manager
from app.timeline.architecture_drift import ArchitectureDrift
from app.timeline.commit_analyzer import CommitAnalyzer
from app.timeline.evolution_tracker import EvolutionTracker
from app.timeline.history_provider import HistoryProvider, get_history_provider
from app.timeline.hotspot_detector import HotspotDetector
from app.timeline.ownership_tracker import OwnershipTracker
from app.timeline.timeline_statistics import TimelineStatistics

logger = logging.getLogger(__name__)


class TimelineEngine:
    """Coordinates timeline intelligence across specialized analyzers.

    Reuses Repository Memory, Incremental Indexing snapshots (via history
    provider), Distributed Cache, and Telemetry. Does not re-index repositories
    or re-run dependency analysis.
    """

    def __init__(
        self,
        history_provider: Optional[HistoryProvider] = None,
        commit_analyzer: Optional[CommitAnalyzer] = None,
        evolution_tracker: Optional[EvolutionTracker] = None,
        hotspot_detector: Optional[HotspotDetector] = None,
        ownership_tracker: Optional[OwnershipTracker] = None,
        architecture_drift: Optional[ArchitectureDrift] = None,
        statistics: Optional[TimelineStatistics] = None,
        cache: Optional[CacheInterface] = None,
        memory_engine=None,
    ):
        self.history_provider = history_provider or get_history_provider("local_metadata")
        self.commit_analyzer = commit_analyzer or CommitAnalyzer(self.history_provider)
        self.evolution_tracker = evolution_tracker or EvolutionTracker(self.commit_analyzer)
        self.hotspot_detector = hotspot_detector or HotspotDetector(self.commit_analyzer)
        self.ownership_tracker = ownership_tracker or OwnershipTracker(self.commit_analyzer)
        self.architecture_drift = architecture_drift or ArchitectureDrift(
            self.commit_analyzer,
            self.evolution_tracker,
            self.hotspot_detector,
        )
        self.statistics = statistics or TimelineStatistics(self.commit_analyzer)
        self._cache = cache or cache_manager
        self._memory_engine = memory_engine

    def _memory(self):
        if self._memory_engine is None:
            from app.repository_memory.memory_engine import memory_engine

            self._memory_engine = memory_engine
        return self._memory_engine

    def get_timeline(self, repository_id: str, limit: int = 100) -> RepositoryTimelineResponse:
        cache_key = CacheKeys.timeline(repository_id)
        cached = self._cache.get(cache_key)
        if cached is not None:
            if isinstance(cached, RepositoryTimelineResponse):
                return cached
            return RepositoryTimelineResponse.model_validate(cached)

        with telemetry_manager.track("timeline.generate", component="timeline"):
            telemetry_manager.increment("timeline.generate")
            logger.info("TimelineEngine: generating timeline for %s", repository_id)

            commits = self.commit_analyzer.fetch_commits(repository_id, limit=limit)
            evolution = self.evolution_tracker.track(repository_id, commits)
            hotspots = self.hotspot_detector.detect(repository_id, commits)
            ownership = self.ownership_tracker.track(repository_id, commits)
            drift_events = self.architecture_drift.detect(
                repository_id,
                commits,
                co_evolution=evolution.co_evolution,
                hotspots=hotspots.hotspots,
            )
            tightly = [
                f"{p.module_a} ↔ {p.module_b}"
                for p in evolution.co_evolution[:5]
                if p.coupling_score >= 0.4
            ]
            narrative = self.architecture_drift.evolution_narrative(
                repository_id, drift_events, tightly
            )
            stats = self.statistics.compute(commits, hotspots, drift_events, ownership)
            summary = self.statistics.build_historical_summary(
                repository_id,
                commits,
                evolution,
                hotspots,
                drift_events,
                narrative,
            )

            # Enrich repository memory with a timeline note (non-destructive)
            self._enrich_memory(repository_id, summary.narrative)

            response = RepositoryTimelineResponse(
                repository_id=repository_id,
                provider=self.history_provider.name,
                commits=commits,
                statistics=stats,
                historical_summary=summary,
                hotspots=hotspots.hotspots,
                ownership=ownership,
                architecture_drift_events=drift_events,
                generated_at=datetime.now(timezone.utc),
            )
            self._cache.set(cache_key, response.model_dump(mode="json"), ttl_seconds=300)
            return response

    def get_evolution(self, repository_id: str) -> EvolutionResponse:
        cache_key = CacheKeys.timeline_evolution(repository_id)
        cached = self._cache.get(cache_key)
        if cached is not None:
            if isinstance(cached, EvolutionResponse):
                return cached
            return EvolutionResponse.model_validate(cached)

        with telemetry_manager.track("timeline.evolution", component="timeline"):
            telemetry_manager.increment("timeline.evolution")
            result = self.evolution_tracker.track(repository_id)
            self._cache.set(cache_key, result.model_dump(mode="json"), ttl_seconds=300)
            return result

    def get_hotspots(self, repository_id: str) -> HotspotsResponse:
        cache_key = CacheKeys.timeline_hotspots(repository_id)
        cached = self._cache.get(cache_key)
        if cached is not None:
            if isinstance(cached, HotspotsResponse):
                return cached
            return HotspotsResponse.model_validate(cached)

        with telemetry_manager.track("timeline.hotspots", component="timeline"):
            telemetry_manager.increment("timeline.hotspots")
            result = self.hotspot_detector.detect(repository_id)
            self._cache.set(cache_key, result.model_dump(mode="json"), ttl_seconds=300)
            return result

    def answer(self, repository_id: str, question: str) -> str:
        """Lightweight Q&A over timeline intelligence for agents / planning."""
        q = question.lower()
        timeline = self.get_timeline(repository_id)
        summary = timeline.historical_summary

        if "changed the most" in q or "what changed" in q:
            return (
                "Most changed: " + ", ".join(summary.what_changed_most)
                if summary.what_changed_most
                else "No dominant changes."
            )
        if "evolve together" in q or "evolving together" in q:
            return (
                "Modules evolving together: " + "; ".join(summary.modules_evolving_together)
                if summary.modules_evolving_together
                else "No co-evolving modules detected."
            )
        if "unstable" in q:
            return (
                "Unstable files: " + ", ".join(summary.unstable_files)
                if summary.unstable_files
                else "No unstable files detected."
            )
        if "frequently" in q or "change frequently" in q:
            parts = [h.path for h in timeline.hotspots[:8]]
            return (
                "Frequently changing parts: " + ", ".join(parts)
                if parts
                else "No frequently changing parts detected."
            )
        if "architecture" in q and ("evolv" in q or "drift" in q or "how has" in q):
            return summary.architecture_evolution
        if "tightly coupled" in q or "coupling" in q:
            return (
                "Tightly coupled: " + ", ".join(summary.tightly_coupled_components)
                if summary.tightly_coupled_components
                else "No tightly coupled components detected."
            )
        if "timeline" in q or "history" in q:
            return summary.narrative
        return summary.narrative

    def _enrich_memory(self, repository_id: str, narrative: str) -> None:
        """Attach a timeline note into existing repository memory when present."""
        try:
            memory = self._memory().get_memory(repository_id)
            if not memory:
                return
            note = f"[Timeline] {narrative[:240]}"
            if note not in memory.technical_debt_notes:
                # Keep list bounded
                memory.technical_debt_notes = (memory.technical_debt_notes + [note])[-20:]
                self._memory()._store.set(repository_id, memory)
        except Exception as exc:  # noqa: BLE001 — enrichment must not break timeline
            logger.debug("Timeline memory enrichment skipped: %s", exc)


timeline_engine = TimelineEngine()
