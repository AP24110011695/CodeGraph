"""Composite repository health scoring from collected intelligence signals."""

from __future__ import annotations

from app.engineering_reports.intelligence_collector import CollectedIntelligence
from app.schemas.engineering_reports import HealthScoreBreakdown


class HealthScorer:
    """Derives a 0–100 health score without re-running analyzers."""

    def score(self, data: CollectedIntelligence, quality_metrics: dict) -> HealthScoreBreakdown:
        architecture = 55.0
        if data.architecture_summary and len(data.architecture_summary) > 40:
            architecture = 75.0
        if data.memory and data.memory.architecture_summary:
            architecture = min(90.0, architecture + 10.0)

        memory_coverage = 40.0
        if data.memory:
            modules = len(data.memory.module_summaries or {})
            files = len(data.memory.file_summaries or {})
            memory_coverage = min(95.0, 40.0 + modules * 5 + min(files, 10) * 2)

        timeline_stability = 70.0
        hotspot_count = int(quality_metrics.get("hotspot_count") or 0)
        if data.hotspots:
            timeline_stability = max(25.0, 85.0 - hotspot_count * 4)
        elif data.timeline:
            timeline_stability = 65.0

        impact_inverse = 70.0
        if data.impact_sample:
            risk = data.impact_sample.risk.risk_score
            impact_inverse = max(10.0, 100.0 - risk)
        elif data.impact_summary:
            impact_inverse = max(20.0, 90.0 - data.impact_summary.average_blast_radius * 5)

        debt_inverse = 75.0
        debt_notes = int(quality_metrics.get("debt_note_count") or 0)
        sec_notes = int(quality_metrics.get("security_note_count") or 0)
        debt_inverse = max(15.0, 90.0 - debt_notes * 4 - sec_notes * 5)

        overall = round(
            0.25 * architecture
            + 0.15 * memory_coverage
            + 0.20 * timeline_stability
            + 0.25 * impact_inverse
            + 0.15 * debt_inverse,
            1,
        )
        return HealthScoreBreakdown(
            overall=overall,
            architecture=round(architecture, 1),
            memory_coverage=round(memory_coverage, 1),
            timeline_stability=round(timeline_stability, 1),
            impact_risk_inverse=round(impact_inverse, 1),
            debt_pressure_inverse=round(debt_inverse, 1),
            grade=self._grade(overall),
        )

    def _grade(self, score: float) -> str:
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"

    def confidence(self, sources: list[str]) -> float:
        base = 0.35 + 0.12 * len(set(sources))
        return round(min(0.95, base), 3)
