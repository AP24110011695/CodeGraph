"""Risk classifier for repository risk analysis.

Classifies risks into levels based on scores and evidence.
"""

import logging
from dataclasses import dataclass, field
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass
class RiskLevel:
    """Risk level classification."""

    level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    score_range: tuple[int, int]
    color: str


class RiskClassifier:
    """Classifies risks into levels based on scores."""

    # Risk level definitions
    LEVELS = {
        "CRITICAL": RiskLevel("CRITICAL", (80, 100), "red"),
        "HIGH": RiskLevel("HIGH", (60, 79), "orange"),
        "MEDIUM": RiskLevel("MEDIUM", (40, 59), "yellow"),
        "LOW": RiskLevel("LOW", (0, 39), "green"),
    }

    def classify(self, score: int) -> str:
        """Classify a risk score into a risk level.

        Args:
            score: Risk score (0-100).

        Returns:
            Risk level string (LOW, MEDIUM, HIGH, CRITICAL).
        """
        for level_name, level_def in self.LEVELS.items():
            if level_def.score_range[0] <= score <= level_def.score_range[1]:
                return level_name
        return "LOW"

    def classify_by_severity(self, severity: str) -> str:
        """Classify based on severity string from analyzers.

        Args:
            severity: Severity string (critical, high, medium, low, minor, major).

        Returns:
            Risk level string (LOW, MEDIUM, HIGH, CRITICAL).
        """
        severity_map = {
            "critical": "CRITICAL",
            "major": "HIGH",
            "high": "HIGH",
            "medium": "MEDIUM",
            "minor": "LOW",
            "low": "LOW",
        }
        return severity_map.get(severity.lower(), "MEDIUM")

    def get_level_color(self, level: str) -> str:
        """Get the color for a risk level.

        Args:
            level: Risk level string.

        Returns:
            Color string.
        """
        return self.LEVELS.get(level, RiskLevel("LOW", (0, 39), "green")).color


risk_classifier = RiskClassifier()
