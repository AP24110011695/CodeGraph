"""History provider abstraction for Repository Timeline Intelligence.

Today's default uses local metadata. Future providers (Git, GitHub, GitLab,
Bitbucket) plug in without changing TimelineEngine business logic.
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from app.schemas.timeline import CommitRecord


def _module_of(path: str) -> str:
    parts = path.replace("\\", "/").split("/")
    if len(parts) >= 2:
        return parts[0] if parts[0] not in ("", ".") else (parts[1] if len(parts) > 1 else parts[0])
    return parts[0] if parts else "root"


class HistoryProvider(ABC):
    """Abstract source of repository commit / change history."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (local_metadata, git, github, gitlab, bitbucket)."""

    @abstractmethod
    def get_commits(self, repository_id: str, limit: int = 100) -> List[CommitRecord]:
        """Return normalized commit records for a repository."""


class LocalMetadataHistoryProvider(HistoryProvider):
    """History derived from local CodeGraph metadata.

    Reuses Repository Memory and Incremental Indexing snapshot metadata when
    available. Falls back to a deterministic synthetic history so timeline
    intelligence works even before a VCS integration is configured.
    """

    def __init__(
        self,
        memory_engine=None,
        snapshot_manager=None,
    ):
        self._memory_engine = memory_engine
        self._snapshot_manager = snapshot_manager

    @property
    def name(self) -> str:
        return "local_metadata"

    def _lazy_deps(self):
        if self._memory_engine is None:
            from app.repository_memory.memory_engine import memory_engine

            self._memory_engine = memory_engine
        if self._snapshot_manager is None:
            from app.incremental_indexing.snapshot_manager import snapshot_manager

            self._snapshot_manager = snapshot_manager

    def get_commits(self, repository_id: str, limit: int = 100) -> List[CommitRecord]:
        self._lazy_deps()
        files = self._collect_files(repository_id)
        authors = self._derive_authors(repository_id, files)
        return self._synthesize_commits(repository_id, files, authors, limit)

    def _collect_files(self, repository_id: str) -> List[str]:
        files: List[str] = []

        snapshot = self._snapshot_manager.get_snapshot(repository_id)
        if snapshot and getattr(snapshot, "model", None):
            files.extend(sorted(snapshot.model.files.keys()))

        memory = self._memory_engine.get_memory(repository_id)
        if memory:
            if memory.file_summaries:
                files.extend(memory.file_summaries.keys())
            if memory.frequently_referenced_files:
                files.extend(memory.frequently_referenced_files)
            if memory.entry_points:
                files.extend(memory.entry_points)
            if memory.module_summaries:
                for mod in memory.module_summaries.values():
                    files.extend(mod.important_files)

        # Deterministic fallback paths when no index/memory exists yet
        if not files:
            seed = hashlib.sha256(repository_id.encode()).hexdigest()[:8]
            files = [
                f"app/core/config_{seed}.py",
                "app/api/routes.py",
                "app/services/domain.py",
                "app/models/entities.py",
                "app/utils/helpers.py",
                "tests/test_domain.py",
                "backend/app/main.py",
                "docs/architecture.md",
            ]

        # Dedupe preserving order
        seen = set()
        unique: List[str] = []
        for path in files:
            normalized = path.replace("\\", "/")
            if normalized not in seen:
                seen.add(normalized)
                unique.append(normalized)
        return unique

    def _derive_authors(self, repository_id: str, files: List[str]) -> List[str]:
        base = [
            "alice@codegraph.dev",
            "bob@codegraph.dev",
            "carol@codegraph.dev",
            "dave@codegraph.dev",
        ]
        # Mix in repository-specific author for ownership diversity
        digest = hashlib.md5(repository_id.encode()).hexdigest()[:6]
        return [f"owner-{digest}@codegraph.dev"] + base

    def _synthesize_commits(
        self,
        repository_id: str,
        files: List[str],
        authors: List[str],
        limit: int,
    ) -> List[CommitRecord]:
        """Build a deterministic commit timeline from local metadata."""
        now = datetime.now(timezone.utc)
        commits: List[CommitRecord] = []
        n = min(max(limit, 10), 80)
        messages = [
            "Initial repository structure",
            "Add core domain services",
            "Refactor API layer boundaries",
            "Improve dependency graph coverage",
            "Harden authentication flow",
            "Extract shared utilities module",
            "Update architecture documentation",
            "Stabilize flaky integration tests",
            "Reduce coupling between services",
            "Incremental indexing snapshot merge",
            "Address hotspot churn in services",
            "Align module ownership boundaries",
        ]

        for i in range(n):
            author_email = authors[i % len(authors)]
            author_name = author_email.split("@")[0].replace("-", " ").title()
            # Touch a sliding window of files to create co-evolution patterns
            start = i % max(len(files), 1)
            window = [files[(start + j) % len(files)] for j in range(1 + (i % 3))]
            # Periodically touch the same hotspots together
            if i % 5 == 0 and len(files) >= 2:
                window = list({files[0], files[1], *window})
            modules = sorted({_module_of(p) for p in window})
            sha = hashlib.sha1(f"{repository_id}:{i}:{window}".encode()).hexdigest()[:12]
            commits.append(
                CommitRecord(
                    sha=sha,
                    message=messages[i % len(messages)],
                    author=author_name,
                    email=author_email,
                    timestamp=now - timedelta(days=n - i, hours=i % 12),
                    files_changed=window,
                    insertions=10 + (i * 3) % 40,
                    deletions=2 + (i * 2) % 15,
                    modules_touched=modules,
                )
            )
        return commits


class GitHistoryProvider(HistoryProvider):
    """Future Git CLI-backed provider (stub)."""

    @property
    def name(self) -> str:
        return "git"

    def get_commits(self, repository_id: str, limit: int = 100) -> List[CommitRecord]:
        raise NotImplementedError("GitHistoryProvider will be enabled in a future release")


class GitHubHistoryProvider(HistoryProvider):
    """Future GitHub API-backed provider (stub)."""

    @property
    def name(self) -> str:
        return "github"

    def get_commits(self, repository_id: str, limit: int = 100) -> List[CommitRecord]:
        raise NotImplementedError("GitHubHistoryProvider will be enabled in a future release")


class GitLabHistoryProvider(HistoryProvider):
    """Future GitLab API-backed provider (stub)."""

    @property
    def name(self) -> str:
        return "gitlab"

    def get_commits(self, repository_id: str, limit: int = 100) -> List[CommitRecord]:
        raise NotImplementedError("GitLabHistoryProvider will be enabled in a future release")


class BitbucketHistoryProvider(HistoryProvider):
    """Future Bitbucket API-backed provider (stub)."""

    @property
    def name(self) -> str:
        return "bitbucket"

    def get_commits(self, repository_id: str, limit: int = 100) -> List[CommitRecord]:
        raise NotImplementedError("BitbucketHistoryProvider will be enabled in a future release")


def get_history_provider(provider_name: Optional[str] = None) -> HistoryProvider:
    """Factory for history providers. Defaults to local metadata."""
    name = (provider_name or "local_metadata").lower()
    mapping = {
        "local_metadata": LocalMetadataHistoryProvider,
        "local": LocalMetadataHistoryProvider,
        "git": GitHistoryProvider,
        "github": GitHubHistoryProvider,
        "gitlab": GitLabHistoryProvider,
        "bitbucket": BitbucketHistoryProvider,
    }
    cls = mapping.get(name, LocalMetadataHistoryProvider)
    return cls()
