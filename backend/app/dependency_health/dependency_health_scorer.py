"""Dependency health scorer for dependency health dashboard.

Scores dependency health based on various metrics.
"""

import logging
from dataclasses import dataclass, field
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass
class HealthGrade:
    """Health grade classification."""

    grade: Literal["A", "B", "C", "D", "F"]
    score_range: tuple[int, int]
    description: str


class DependencyHealthScorer:
    """Scores dependency health based on metrics."""

    # Health grade definitions
    GRADES = {
        "A": HealthGrade("A", (90, 100), "Excellent - Dependencies are healthy and well-maintained"),
        "B": HealthGrade("B", (80, 89), "Good - Minor issues present but overall healthy"),
        "C": HealthGrade("C", (70, 79), "Fair - Some issues that should be addressed"),
        "D": HealthGrade("D", (60, 69), "Poor - Significant issues requiring attention"),
        "F": HealthGrade("F", (0, 59), "Critical - Major issues requiring immediate action"),
    }

    def calculate_grade(self, score: int) -> str:
        """Calculate health grade from score.

        Args:
            score: Health score (0-100).

        Returns:
            Health grade string (A, B, C, D, F).
        """
        for grade_name, grade_def in self.GRADES.items():
            if grade_def.score_range[0] <= score <= grade_def.score_range[1]:
                return grade_name
        return "F"

    def calculate_overall_score(
        self,
        cycle_count: int,
        coupling_density: float,
        isolated_count: int,
        fan_out_max: int,
        fan_in_max: int,
        external_count: int,
    ) -> int:
        """Calculate overall dependency health score.

        Args:
            cycle_count: Number of dependency cycles.
            coupling_density: Dependency coupling density.
            isolated_count: Number of isolated modules.
            fan_out_max: Maximum fan-out (outgoing dependencies).
            fan_in_max: Maximum fan-in (incoming dependencies).
            external_count: Number of external dependencies.

        Returns:
            Overall health score (0-100).
        """
        score = 100

        # Deduct for cycles
        score -= cycle_count * 15

        # Deduct for high coupling density
        if coupling_density > 3:
            score -= min(20, (coupling_density - 3) * 5)

        # Deduct for isolated modules
        score -= min(10, isolated_count * 2)

        # Deduct for high fan-out
        if fan_out_max > 10:
            score -= min(15, (fan_out_max - 10) * 2)

        # Deduct for high fan-in
        if fan_in_max > 10:
            score -= min(10, (fan_in_max - 10) * 2)

        # Deduct for excessive external dependencies
        if external_count > 50:
            score -= min(10, (external_count - 50) * 0.2)

        return max(0, min(100, round(score)))


dependency_health_scorer = DependencyHealthScorer()
