"""Shared filesystem path helpers for repository upload roots.

CodeGraph historically used both ``storage/extracted`` and ``uploads``.
Resolvers check known roots so APIs behave consistently without duplicating
path logic in every router.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable
from app.core.config import settings

# Preferred order: extract pipeline root first, then uploads-based analyzers.
def get_repository_roots() -> tuple[Path, ...]:
    """Get repository roots from settings."""
    return (
        Path(settings.STORAGE_DIR) / "extracted",
        Path(settings.UPLOAD_DIR),
    )

REPOSITORY_ROOTS = get_repository_roots()


def get_upload_dir() -> Path:
    """Get the upload directory from settings."""
    return Path(settings.UPLOAD_DIR)


def get_storage_dir() -> Path:
    """Get the storage directory from settings."""
    return Path(settings.STORAGE_DIR)


def get_extracted_dir() -> Path:
    """Get the extracted directory from settings."""
    return Path(settings.STORAGE_DIR) / "extracted"


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


def get_project_path(upload_id: str) -> Path:
    """Get project path from upload directory for API endpoints."""
    return get_upload_dir() / upload_id
