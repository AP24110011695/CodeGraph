"""Hotspot detection — unstable files and high change-frequency areas."""

from __future__ import annotations

from typing import Dict, List

from app.schemas.timeline import CommitRecord, FileChangeStats, Hotspot, HotspotsResponse
from app.timeline.commit_analyzer import CommitAnalyzer


class HotspotDetector:
    """Detects repository hotspots from change frequency and churn.

    Answers:
    - What files are unstable?
    - What parts of the system change frequently?
    """

    def __init__(
        self,
        commit_analyzer: CommitAnalyzer | None = None,
        churn_threshold: float = 0.45,
        min_changes: int = 3,
    ):
        self.commit_analyzer = commit_analyzer or CommitAnalyzer()
        self.churn_threshold = churn_threshold
        self.min_changes = min_changes

    def detect(
        self,
        repository_id: str,
        commits: List[CommitRecord] | None = None,
        file_stats: Dict[str, FileChangeStats] | None = None,
    ) -> HotspotsResponse:
        commits = commits if commits is not None else self.commit_analyzer.fetch_commits(repository_id)
        file_stats = file_stats or self.commit_analyzer.analyze_file_changes(commits)

        hotspots: List[Hotspot] = []
        for path, stats in file_stats.items():
            if stats.change_count < self.min_changes and stats.churn_score < self.churn_threshold:
                continue
            if stats.churn_score < self.churn_threshold and stats.change_count < self.min_changes + 2:
                continue

            risk = self._risk(stats)
            hotspots.append(
                Hotspot(
                    path=path,
                    hotspot_type="file",
                    change_frequency=stats.change_count,
                    churn_score=stats.churn_score,
                    authors=list(stats.authors),
                    risk_level=risk,
                    reason=(
                        f"Changed {stats.change_count} times with churn score "
                        f"{stats.churn_score}; marked {risk} risk."
                    ),
                )
            )

        # Module-level hotspots from frequent modules
        module_activity = self.commit_analyzer.module_activity(commits)
        if module_activity:
            max_mod = max(module_activity.values())
            for module, count in module_activity.items():
                score = round(count / max_mod, 3) if max_mod else 0.0
                if count >= self.min_changes and score >= self.churn_threshold:
                    hotspots.append(
                        Hotspot(
                            path=module,
                            hotspot_type="module",
                            change_frequency=count,
                            churn_score=score,
                            authors=[],
                            risk_level="high" if score >= 0.8 else "medium",
                            reason=f"Module changed in {count} commits (relative frequency {score}).",
                        )
                    )

        hotspots.sort(key=lambda h: (h.churn_score, h.change_frequency), reverse=True)

        unstable = [h.path for h in hotspots if h.hotspot_type == "file" and h.risk_level in ("high", "medium")]
        frequent = [h.path for h in hotspots[:10]]

        summary = (
            f"Detected {len(hotspots)} hotspots. "
            f"Unstable files: {', '.join(unstable[:5]) or 'none'}."
        )

        return HotspotsResponse(
            repository_id=repository_id,
            hotspots=hotspots,
            unstable_files=unstable,
            frequently_changing_parts=frequent,
            summary=summary,
        )

    def _risk(self, stats: FileChangeStats) -> str:
        if stats.churn_score >= 0.75 or stats.change_count >= 10:
            return "high"
        if stats.churn_score >= 0.45 or stats.change_count >= 5:
            return "medium"
        return "low"
