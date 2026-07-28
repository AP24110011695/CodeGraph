"""Architecture comparator for architecture drift detection.

Compares detected architecture with inferred patterns to identify drift.
"""

import logging
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass
class ArchitectureHealthGrade:
    """Architecture health grade classification."""

    grade: Literal["A", "B", "C", "D", "F"]
    score_range: tuple[int, int]
    description: str


class ArchitectureComparator:
    """Compares detected architecture with inferred patterns to identify drift.

    Reuses outputs from:
    - Architecture Builder
    - Dependency Graph
    - Metrics Engine
    """

    # Health grade definitions
    GRADES = {
        "A": ArchitectureHealthGrade("A", (90, 100), "Excellent - Architecture is well-structured and stable"),
        "B": ArchitectureHealthGrade("B", (80, 89), "Good - Minor architectural issues present"),
        "C": ArchitectureHealthGrade("C", (70, 79), "Fair - Some architectural drift detected"),
        "D": ArchitectureHealthGrade("D", (60, 69), "Poor - Significant architectural issues"),
        "F": ArchitectureHealthGrade("F", (0, 59), "Critical - Major architectural problems"),
    }

    def __init__(self):
        """Initialize the architecture comparator."""
        pass

    def calculate_health_score(
        self,
        violations: int,
        layer_violations: int,
        cross_layer_dependencies: int,
        circular_dependencies: int,
        high_coupling: int,
        god_modules: int,
    ) -> int:
        """Calculate overall architecture health score.

        Args:
            violations: Total number of violations.
            layer_violations: Number of layer violations.
            cross_layer_dependencies: Number of cross-layer dependencies.
            circular_dependencies: Number of circular dependencies.
            high_coupling: Number of high coupling issues.
            god_modules: Number of god modules.

        Returns:
            Overall health score (0-100).
        """
        score = 100

        # Deduct for violations
        score -= violations * 5

        # Deduct for layer violations
        score -= layer_violations * 10

        # Deduct for cross-layer dependencies
        score -= cross_layer_dependencies * 15

        # Deduct for circular dependencies
        score -= circular_dependencies * 20

        # Deduct for high coupling
        score -= high_coupling * 10

        # Deduct for god modules
        score -= god_modules * 15

        return max(0, min(100, round(score)))

    def calculate_drift_score(self, health_score: int) -> int:
        """Calculate drift score (inverse of health score).

        Args:
            health_score: Architecture health score (0-100).

        Returns:
            Drift score (0-100).
        """
        return 100 - health_score

    def calculate_grade(self, health_score: int) -> str:
        """Calculate health grade from score.

        Args:
            health_score: Health score (0-100).

        Returns:
            Health grade string (A, B, C, D, F).
        """
        for grade_name, grade_def in self.GRADES.items():
            if grade_def.score_range[0] <= health_score <= grade_def.score_range[1]:
                return grade_name
        return "F"

    def get_stability_score(
        self,
        violations: int,
        circular_dependencies: int,
        high_coupling: int,
    ) -> int:
        """Calculate architecture stability score.

        Args:
            violations: Total number of violations.
            circular_dependencies: Number of circular dependencies.
            high_coupling: Number of high coupling issues.

        Returns:
            Stability score (0-100).
        """
        score = 100

        # Circular dependencies significantly impact stability
        score -= circular_dependencies * 25

        # High coupling impacts stability
        score -= high_coupling * 10

        # General violations impact stability
        score -= violations * 5

        return max(0, min(100, round(score)))


architecture_comparator = ArchitectureComparator()
