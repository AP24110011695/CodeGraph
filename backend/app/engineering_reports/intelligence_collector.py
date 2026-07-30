"""Collects intelligence from existing CodeGraph engines without re-analysis."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CollectedIntelligence:
    """Bundle of optional intelligence payloads from existing facades."""

    memory: Any = None
    memory_summary: Any = None
    architecture_summary: str = ""
    timeline: Any = None
    evolution: Any = None
    hotspots: Any = None
    impact_summary: Any = None
    impact_sample: Any = None
    sources: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


class IntelligenceCollector:
    """Composes existing engine outputs. Never re-indexes or re-traverses graphs."""

    def __init__(
        self,
        memory_engine=None,
        timeline_engine=None,
        impact_engine=None,
        reasoning_engine=None,
    ):
        self._memory_engine = memory_engine
        self._timeline_engine = timeline_engine
        self._impact_engine = impact_engine
        self._reasoning_engine = reasoning_engine

    def _memory(self):
        if self._memory_engine is None:
            from app.repository_memory.memory_engine import memory_engine

            self._memory_engine = memory_engine
        return self._memory_engine

    def _timeline(self):
        if self._timeline_engine is None:
            from app.timeline.timeline_engine import timeline_engine

            self._timeline_engine = timeline_engine
        return self._timeline_engine

    def _impact(self):
        if self._impact_engine is None:
            from app.impact_analysis.impact_engine import impact_engine

            self._impact_engine = impact_engine
        return self._impact_engine

    def _reasoning(self):
        if self._reasoning_engine is None:
            from app.architecture_reasoning.reasoning_engine import reasoning_engine

            self._reasoning_engine = reasoning_engine
        return self._reasoning_engine

    def collect(
        self,
        repository_id: str,
        impact_target: Optional[str] = None,
    ) -> CollectedIntelligence:
        bundle = CollectedIntelligence()

        try:
            mem = self._memory().get_memory(repository_id)
            if not mem:
                mem = self._memory().build_memory(repository_id)
            bundle.memory = mem
            bundle.memory_summary = self._memory().get_memory_summary(repository_id)
            bundle.sources.append("Repository Memory")
        except Exception as exc:  # noqa: BLE001
            logger.debug("Memory collection skipped: %s", exc)
            bundle.notes.append("Repository Memory unavailable")

        try:
            arch = self._reasoning().summary(repository_id)
            bundle.architecture_summary = getattr(arch, "overall_architecture", "") or ""
            bundle.sources.append("Architecture Reasoning")
        except Exception as exc:  # noqa: BLE001
            logger.debug("Reasoning collection skipped: %s", exc)
            if bundle.memory and bundle.memory.architecture_summary:
                bundle.architecture_summary = bundle.memory.architecture_summary
                bundle.sources.append("Repository Memory (architecture)")

        try:
            bundle.timeline = self._timeline().get_timeline(repository_id, limit=40)
            bundle.evolution = self._timeline().get_evolution(repository_id)
            bundle.hotspots = self._timeline().get_hotspots(repository_id)
            bundle.sources.append("Timeline Intelligence")
        except Exception as exc:  # noqa: BLE001
            logger.debug("Timeline collection skipped: %s", exc)
            bundle.notes.append("Timeline Intelligence unavailable")

        try:
            bundle.impact_summary = self._impact().get_summary(repository_id)
            from app.schemas.impact_analysis import ImpactAnalyzeRequest

            target = impact_target or self._default_impact_target(bundle)
            bundle.impact_sample = self._impact().analyze(
                repository_id,
                ImpactAnalyzeRequest(target=target, max_depth=3),
            )
            bundle.sources.append("Impact Analysis")
        except Exception as exc:  # noqa: BLE001
            logger.debug("Impact collection skipped: %s", exc)
            bundle.notes.append("Impact Analysis unavailable")

        return bundle

    def _default_impact_target(self, bundle: CollectedIntelligence) -> str:
        if bundle.memory:
            if bundle.memory.entry_points:
                return bundle.memory.entry_points[0]
            if bundle.memory.module_summaries:
                return next(iter(bundle.memory.module_summaries.keys()))
        if bundle.hotspots and bundle.hotspots.unstable_files:
            return bundle.hotspots.unstable_files[0]
        return "app"
