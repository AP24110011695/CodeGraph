"""Commit history analysis for Repository Timeline Intelligence."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from app.schemas.timeline import CommitRecord, FileChangeStats
from app.timeline.history_provider import HistoryProvider, LocalMetadataHistoryProvider, _module_of


class CommitAnalyzer:
    """Analyzes normalized commit history into file-level change statistics.

    Depends on HistoryProvider so VCS backends can be swapped without
    changing analysis logic.
    """

    def __init__(self, history_provider: Optional[HistoryProvider] = None):
        self.history_provider = history_provider or LocalMetadataHistoryProvider()

    def fetch_commits(self, repository_id: str, limit: int = 100) -> List[CommitRecord]:
        return self.history_provider.get_commits(repository_id, limit=limit)

    def analyze_file_changes(self, commits: List[CommitRecord]) -> Dict[str, FileChangeStats]:
        stats: Dict[str, FileChangeStats] = {}
        for commit in commits:
            for path in commit.files_changed:
                if path not in stats:
                    stats[path] = FileChangeStats(
                        file_path=path,
                        first_seen=commit.timestamp,
                        last_seen=commit.timestamp,
                    )
                entry = stats[path]
                entry.change_count += 1
                entry.insertions += commit.insertions
                entry.deletions += commit.deletions
                if commit.author not in entry.authors:
                    entry.authors.append(commit.author)
                if entry.first_seen is None or commit.timestamp < entry.first_seen:
                    entry.first_seen = commit.timestamp
                if entry.last_seen is None or commit.timestamp > entry.last_seen:
                    entry.last_seen = commit.timestamp

        max_changes = max((s.change_count for s in stats.values()), default=1)
        for entry in stats.values():
            churn = (entry.insertions + entry.deletions) / max(entry.change_count, 1)
            entry.churn_score = round(
                (0.6 * (entry.change_count / max_changes)) + (0.4 * min(churn / 50.0, 1.0)),
                3,
            )
        return stats

    def author_activity(self, commits: List[CommitRecord]) -> Dict[str, int]:
        return dict(Counter(c.author for c in commits))

    def module_activity(self, commits: List[CommitRecord]) -> Dict[str, int]:
        counter: Counter[str] = Counter()
        for commit in commits:
            modules = commit.modules_touched or [_module_of(p) for p in commit.files_changed]
            for module in set(modules):
                counter[module] += 1
        return dict(counter)

    def change_frequency(self, commits: List[CommitRecord]) -> Dict[str, int]:
        """Files ordered by change frequency."""
        counter: Counter[str] = Counter()
        for commit in commits:
            for path in commit.files_changed:
                counter[path] += 1
        return dict(counter.most_common())

    def period(self, commits: List[CommitRecord]) -> tuple[Optional[datetime], Optional[datetime]]:
        if not commits:
            return None, None
        stamps = [c.timestamp for c in commits]
        return min(stamps), max(stamps)

    def commits_by_module_pair(self, commits: List[CommitRecord]) -> Dict[tuple[str, str], int]:
        pairs: Dict[tuple[str, str], int] = defaultdict(int)
        for commit in commits:
            modules = sorted(set(commit.modules_touched or [_module_of(p) for p in commit.files_changed]))
            for i in range(len(modules)):
                for j in range(i + 1, len(modules)):
                    pairs[(modules[i], modules[j])] += 1
        return dict(pairs)
