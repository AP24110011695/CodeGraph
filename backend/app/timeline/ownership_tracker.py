"""Ownership tracking derived from commit authorship."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List

from app.schemas.timeline import CommitRecord, OwnershipRecord
from app.timeline.commit_analyzer import CommitAnalyzer
from app.timeline.history_provider import _module_of


class OwnershipTracker:
    """Infers path-level ownership and bus factor from commit authors."""

    def __init__(self, commit_analyzer: CommitAnalyzer | None = None):
        self.commit_analyzer = commit_analyzer or CommitAnalyzer()

    def track(
        self,
        repository_id: str,
        commits: List[CommitRecord] | None = None,
    ) -> List[OwnershipRecord]:
        commits = commits if commits is not None else self.commit_analyzer.fetch_commits(repository_id)

        path_authors: Dict[str, Counter] = defaultdict(Counter)
        for commit in commits:
            for path in commit.files_changed:
                path_authors[path][commit.author] += 1
            # Also roll up to module level
            modules = commit.modules_touched or [_module_of(p) for p in commit.files_changed]
            for module in set(modules):
                path_authors[f"module:{module}"][commit.author] += 1

        records: List[OwnershipRecord] = []
        for path, counter in path_authors.items():
            total = sum(counter.values()) or 1
            primary, primary_count = counter.most_common(1)[0]
            significant = [a for a, c in counter.items() if (c / total) >= 0.15]
            records.append(
                OwnershipRecord(
                    path=path,
                    primary_owner=primary,
                    ownership_pct=round(100.0 * primary_count / total, 1),
                    contributors=dict(counter),
                    bus_factor=max(1, len(significant)),
                )
            )

        return sorted(records, key=lambda r: r.ownership_pct, reverse=True)
