"""Repository snapshot comparison result."""

from app.schemas.incremental_indexing import ChangeSet


class SnapshotDiff(ChangeSet):
    """Named evolution diff; kept compatible with the existing ChangeSet API."""

    pass
