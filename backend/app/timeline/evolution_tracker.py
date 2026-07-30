"""Repository evolution tracking — modules, files, and co-evolution."""

from __future__ import annotations

from typing import Dict, List

from app.schemas.timeline import (
    CoEvolutionPair,
    CommitRecord,
    EvolutionResponse,
    FileChangeStats,
    FileEvolution,
    ModuleEvolution,
)
from app.timeline.commit_analyzer import CommitAnalyzer
from app.timeline.history_provider import _module_of


def _stability(change_count: int, threshold_high: int = 8, threshold_mid: int = 3) -> str:
    if change_count >= threshold_high:
        return "unstable"
    if change_count >= threshold_mid:
        return "moderate"
    return "stable"


class EvolutionTracker:
    """Tracks how modules and files evolve and which ones change together.

    Enriches answers to:
    - What changed the most?
    - Which modules evolve together?
    """

    def __init__(self, commit_analyzer: CommitAnalyzer | None = None):
        self.commit_analyzer = commit_analyzer or CommitAnalyzer()

    def track(self, repository_id: str, commits: List[CommitRecord] | None = None) -> EvolutionResponse:
        commits = commits if commits is not None else self.commit_analyzer.fetch_commits(repository_id)
        file_stats = self.commit_analyzer.analyze_file_changes(commits)
        module_activity = self.commit_analyzer.module_activity(commits)
        pair_counts = self.commit_analyzer.commits_by_module_pair(commits)

        modules = self._build_modules(file_stats, module_activity, pair_counts)
        files = self._build_files(file_stats)
        co_evolution = self._build_co_evolution(pair_counts)

        what_changed_most = [
            m.module_name for m in sorted(modules, key=lambda m: m.change_count, reverse=True)[:5]
        ]
        together = [
            f"{p.module_a} ↔ {p.module_b} ({p.co_change_count})"
            for p in co_evolution[:5]
        ]

        summary = (
            f"Tracked {len(modules)} modules and {len(files)} files across {len(commits)} commits. "
            f"Most changed: {', '.join(what_changed_most[:3]) or 'n/a'}."
        )

        return EvolutionResponse(
            repository_id=repository_id,
            modules=modules,
            files=files,
            co_evolution=co_evolution,
            what_changed_most=what_changed_most,
            modules_evolving_together=together,
            summary=summary,
        )

    def _build_modules(
        self,
        file_stats: Dict[str, FileChangeStats],
        module_activity: Dict[str, int],
        pair_counts: Dict[tuple[str, str], int],
    ) -> List[ModuleEvolution]:
        module_files: Dict[str, List[str]] = {}
        module_authors: Dict[str, set] = {}
        for path, stats in file_stats.items():
            module = _module_of(path)
            module_files.setdefault(module, []).append(path)
            module_authors.setdefault(module, set()).update(stats.authors)

        related: Dict[str, set] = {m: set() for m in module_activity}
        for (a, b), count in pair_counts.items():
            if count >= 2:
                related.setdefault(a, set()).add(b)
                related.setdefault(b, set()).add(a)

        results: List[ModuleEvolution] = []
        for module, count in sorted(module_activity.items(), key=lambda x: x[1], reverse=True):
            results.append(
                ModuleEvolution(
                    module_name=module,
                    change_count=count,
                    file_count=len(module_files.get(module, [])),
                    authors=sorted(module_authors.get(module, set())),
                    related_modules=sorted(related.get(module, set())),
                    stability=_stability(count),
                    summary=(
                        f"Module '{module}' changed in {count} commits "
                        f"({_stability(count)})."
                    ),
                )
            )
        return results

    def _build_files(self, file_stats: Dict[str, FileChangeStats]) -> List[FileEvolution]:
        results: List[FileEvolution] = []
        for path, stats in sorted(file_stats.items(), key=lambda x: x[1].change_count, reverse=True):
            results.append(
                FileEvolution(
                    file_path=path,
                    change_count=stats.change_count,
                    authors=list(stats.authors),
                    stability=_stability(stats.change_count),
                    summary=(
                        f"File '{path}' changed {stats.change_count} times "
                        f"(churn={stats.churn_score})."
                    ),
                )
            )
        return results

    def _build_co_evolution(
        self,
        pair_counts: Dict[tuple[str, str], int],
    ) -> List[CoEvolutionPair]:
        if not pair_counts:
            return []
        max_count = max(pair_counts.values())
        pairs = [
            CoEvolutionPair(
                module_a=a,
                module_b=b,
                co_change_count=count,
                coupling_score=round(count / max_count, 3),
            )
            for (a, b), count in pair_counts.items()
        ]
        return sorted(pairs, key=lambda p: p.co_change_count, reverse=True)
