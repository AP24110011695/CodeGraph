"""Technical debt estimator for CodeGraph.

Estimates technical debt based on detected code smells.
Uses deterministic scoring based on severity and count.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class DebtEstimate:
    """Technical debt estimation result."""

    level: Literal["low", "medium", "high", "critical"]
    estimated_effort: str
    affected_files: int
    refactoring_priority: Literal["low", "medium", "high", "critical"]


class DebtEstimator:
    """Estimates technical debt from code smells."""

    def __init__(self):
        """Initialize the debt estimator."""
        # Severity weights for debt calculation
        self.severity_weights = {
            "critical": 10,
            "major": 5,
            "minor": 1,
        }

    def estimate(self, smells: list[dict]) -> DebtEstimate:
        """Estimate technical debt from detected smells.

        Args:
            smells: List of detected code smells with severity.

        Returns:
            DebtEstimate with level, effort, and priority.
        """
        if not smells:
            return DebtEstimate(
                level="low",
                estimated_effort="< 1 day",
                affected_files=0,
                refactoring_priority="low",
            )

        # Calculate debt score
        debt_score = 0
        critical_count = 0
        major_count = 0
        minor_count = 0
        affected_files_set = set()

        for smell in smells:
            severity = smell.get("severity", "minor")
            debt_score += self.severity_weights.get(severity, 1)

            if severity == "critical":
                critical_count += 1
            elif severity == "major":
                major_count += 1
            elif severity == "minor":
                minor_count += 1

            if "file" in smell:
                affected_files_set.add(smell["file"])

        affected_files = len(affected_files_set)

        # Determine debt level
        if debt_score >= 50 or critical_count >= 3:
            level = "critical"
        elif debt_score >= 30 or critical_count >= 1:
            level = "high"
        elif debt_score >= 15 or major_count >= 5:
            level = "medium"
        else:
            level = "low"

        # Estimate effort based on debt score and affected files
        estimated_effort = self._estimate_effort(debt_score, affected_files)

        # Determine refactoring priority
        refactoring_priority = self._determine_priority(level, critical_count, major_count)

        return DebtEstimate(
            level=level,
            estimated_effort=estimated_effort,
            affected_files=affected_files,
            refactoring_priority=refactoring_priority,
        )

    def _estimate_effort(self, debt_score: int, affected_files: int) -> str:
        """Estimate refactoring effort based on debt score and affected files.

        Args:
            debt_score: Calculated debt score.
            affected_files: Number of files affected by smells.

        Returns:
            Human-readable effort estimate.
        """
        if debt_score >= 50:
            base = "2-4 weeks"
        elif debt_score >= 30:
            base = "1-2 weeks"
        elif debt_score >= 15:
            base = "3-5 days"
        else:
            base = "1-2 days"

        # Adjust for affected files
        if affected_files > 20:
            if "weeks" in base:
                return f"3-4 weeks"
            else:
                return "1-2 weeks"
        elif affected_files > 10:
            if "weeks" in base:
                return base
            else:
                return "1 week"

        return base

    def _determine_priority(
        self,
        level: str,
        critical_count: int,
        major_count: int,
    ) -> Literal["low", "medium", "high", "critical"]:
        """Determine refactoring priority based on debt level and smell counts.

        Args:
            level: Calculated debt level.
            critical_count: Number of critical smells.
            major_count: Number of major smells.

        Returns:
            Refactoring priority level.
        """
        if level == "critical" or critical_count >= 2:
            return "critical"
        elif level == "high" or critical_count >= 1:
            return "high"
        elif level == "medium" or major_count >= 5:
            return "medium"
        else:
            return "low"


debt_estimator = DebtEstimator()
