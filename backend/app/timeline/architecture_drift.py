"""Architecture drift signals derived from repository timeline evolution.

Reuses Knowledge Graph / existing architecture intelligence conceptually and
does NOT reimplement the snapshot Architecture Drift Engine at
``app.architecture_drift``. This module produces *historical* drift events
from commit co-evolution and hotspot pressure.
"""

from __future__ import annotations

import hashlib
from typing import List

from app.schemas.timeline import (
    ArchitectureDriftEvent,
    CoEvolutionPair,
    CommitRecord,
    Hotspot,
)
from app.timeline.commit_analyzer import CommitAnalyzer
from app.timeline.evolution_tracker import EvolutionTracker
from app.timeline.hotspot_detector import HotspotDetector


class ArchitectureDrift:
    """Detects architecture evolution / coupling drift over time.

    Answers:
    - How has the architecture evolved?
    - What components became tightly coupled?
    """

    def __init__(
        self,
        commit_analyzer: CommitAnalyzer | None = None,
        evolution_tracker: EvolutionTracker | None = None,
        hotspot_detector: HotspotDetector | None = None,
        memory_engine=None,
    ):
        self.commit_analyzer = commit_analyzer or CommitAnalyzer()
        self.evolution_tracker = evolution_tracker or EvolutionTracker(self.commit_analyzer)
        self.hotspot_detector = hotspot_detector or HotspotDetector(self.commit_analyzer)
        self._memory_engine = memory_engine

    def _memory(self):
        if self._memory_engine is None:
            from app.repository_memory.memory_engine import memory_engine

            self._memory_engine = memory_engine
        return self._memory_engine

    def detect(
        self,
        repository_id: str,
        commits: List[CommitRecord] | None = None,
        co_evolution: List[CoEvolutionPair] | None = None,
        hotspots: List[Hotspot] | None = None,
    ) -> List[ArchitectureDriftEvent]:
        commits = commits if commits is not None else self.commit_analyzer.fetch_commits(repository_id)
        if co_evolution is None:
            evolution = self.evolution_tracker.track(repository_id, commits)
            co_evolution = evolution.co_evolution
        if hotspots is None:
            hotspots = self.hotspot_detector.detect(repository_id, commits).hotspots

        from datetime import datetime, timezone

        events: List[ArchitectureDriftEvent] = []
        anchor = commits[-1].timestamp if commits else datetime.now(timezone.utc)

        # Tight coupling from co-evolution
        for pair in co_evolution[:8]:
            if pair.coupling_score < 0.4:
                continue
            severity = "critical" if pair.coupling_score >= 0.8 else "warning"
            events.append(
                ArchitectureDriftEvent(
                    event_id=self._event_id(repository_id, pair.module_a, pair.module_b),
                    timestamp=anchor,
                    description=(
                        f"Modules '{pair.module_a}' and '{pair.module_b}' became tightly coupled "
                        f"(co-changed {pair.co_change_count} times, score={pair.coupling_score})."
                    ),
                    severity=severity,
                    modules_affected=[pair.module_a, pair.module_b],
                    coupling_delta=pair.coupling_score,
                    category="dependency",
                )
            )

        # Hotspot structural pressure
        for hotspot in [h for h in hotspots if h.risk_level == "high"][:5]:
            events.append(
                ArchitectureDriftEvent(
                    event_id=self._event_id(repository_id, "hotspot", hotspot.path),
                    timestamp=anchor,
                    description=(
                        f"High-churn hotspot at '{hotspot.path}' indicates architectural instability."
                    ),
                    severity="warning",
                    modules_affected=[hotspot.path],
                    coupling_delta=hotspot.churn_score,
                    category="hotspot",
                )
            )

        # Enrich with repository memory architecture notes when available
        memory = self._memory().get_memory(repository_id)
        if memory and memory.architecture_summary and commits:
            events.append(
                ArchitectureDriftEvent(
                    event_id=self._event_id(repository_id, "memory", "architecture"),
                    timestamp=anchor,
                    description=(
                        "Architecture memory baseline considered for drift narrative: "
                        f"{memory.architecture_summary[:180]}"
                    ),
                    severity="info",
                    modules_affected=list(memory.module_summaries.keys())[:5],
                    coupling_delta=0.0,
                    category="structural",
                )
            )

        return events

    def evolution_narrative(
        self,
        repository_id: str,
        events: List[ArchitectureDriftEvent],
        tightly_coupled: List[str],
    ) -> str:
        if not events:
            return (
                f"Architecture for '{repository_id}' appears stable over the observed timeline "
                "with no significant coupling drift detected."
            )
        critical = sum(1 for e in events if e.severity == "critical")
        warnings = sum(1 for e in events if e.severity == "warning")
        coupled = ", ".join(tightly_coupled[:4]) or "none highlighted"
        return (
            f"Architecture evolved with {len(events)} drift signals "
            f"({critical} critical, {warnings} warnings). "
            f"Tightly coupled components: {coupled}."
        )

    def _event_id(self, repository_id: str, *parts: str) -> str:
        raw = ":".join([repository_id, *parts])
        return hashlib.sha1(raw.encode()).hexdigest()[:12]
