"""Execution statistics for Copilot orchestration runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ExecutionRecord:
    repository_id: str
    intent: str
    tools_used: List[str]
    execution_time_ms: int
    confidence: float
    provider: str


@dataclass
class ExecutionStatistics:
    """Tracks Copilot orchestration metrics."""

    total_runs: int = 0
    total_time_ms: int = 0
    tool_counts: Dict[str, int] = field(default_factory=dict)
    intent_counts: Dict[str, int] = field(default_factory=dict)
    recent: List[ExecutionRecord] = field(default_factory=list)

    def record(
        self,
        repository_id: str,
        intent: str,
        tools_used: List[str],
        execution_time_ms: int,
        confidence: float,
        provider: str,
    ) -> None:
        self.total_runs += 1
        self.total_time_ms += execution_time_ms
        self.intent_counts[intent] = self.intent_counts.get(intent, 0) + 1
        for tool in tools_used:
            self.tool_counts[tool] = self.tool_counts.get(tool, 0) + 1
        self.recent.append(
            ExecutionRecord(
                repository_id=repository_id,
                intent=intent,
                tools_used=list(tools_used),
                execution_time_ms=execution_time_ms,
                confidence=confidence,
                provider=provider,
            )
        )
        if len(self.recent) > 100:
            self.recent = self.recent[-100:]

    def snapshot(self) -> Dict[str, Any]:
        avg = (self.total_time_ms / self.total_runs) if self.total_runs else 0.0
        return {
            "total_runs": self.total_runs,
            "total_time_ms": self.total_time_ms,
            "average_time_ms": round(avg, 2),
            "tool_counts": dict(self.tool_counts),
            "intent_counts": dict(self.intent_counts),
        }


execution_statistics = ExecutionStatistics()
