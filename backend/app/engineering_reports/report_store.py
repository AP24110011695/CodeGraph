"""In-memory report store for generated engineering reports."""

from __future__ import annotations

import threading
from typing import Dict, List, Optional

from app.schemas.engineering_reports import EngineeringReport


class ReportStore:
    """Stores latest reports per repository. Swap later for persistent storage."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._by_repo: Dict[str, List[EngineeringReport]] = {}

    def add(self, report: EngineeringReport) -> None:
        with self._lock:
            bucket = self._by_repo.setdefault(report.repository_id, [])
            bucket.append(report)
            # Keep newest last; bound history
            self._by_repo[report.repository_id] = bucket[-20:]

    def list(self, repository_id: str) -> List[EngineeringReport]:
        with self._lock:
            return list(self._by_repo.get(repository_id, []))

    def latest(self, repository_id: str) -> Optional[EngineeringReport]:
        reports = self.list(repository_id)
        return reports[-1] if reports else None

    def get(self, repository_id: str, report_id: str) -> Optional[EngineeringReport]:
        for report in self.list(repository_id):
            if report.report_id == report_id:
                return report
        return None


report_store = ReportStore()
