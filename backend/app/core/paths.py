"""Shared filesystem path helpers for repository upload roots.

CodeGraph historically used both ``storage/extracted`` and ``uploads``.
Resolvers check known roots so APIs behave consistently without duplicating
path logic in every router.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

# Preferred order: extract pipeline root first, then uploads-based analyzers.
REPOSITORY_ROOTS: tuple[Path, ...] = (
    Path("storage/extracted"),
    Path("uploads"),
)


def iter_repository_roots() -> Iterable[Path]:
    return REPOSITORY_ROOTS


def resolve_repository_path(repository_id: str) -> Path | None:
    """Return the first existing directory for ``repository_id``, else None."""
    for root in REPOSITORY_ROOTS:
        candidate = root / repository_id
        if candidate.is_dir():
            return candidate
    return None


def expected_repository_path(repository_id: str) -> Path:
    """Canonical path used in 404 messages when no directory exists yet."""
    return REPOSITORY_ROOTS[0] / repository_id
