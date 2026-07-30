"""Engineering score calculator for team analytics engine.

Calculates composite engineering scores from repository metrics.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class EngineeringScore:
    """Calculates composite engineering scores.

    Combines architecture, health, quality, risk, and security scores
    into a single engineering score.
    """

    def __init__(self):
        """Initialize the engineering score calculator."""
        pass

    def calculate_engineering_score(
        self,
        architecture_score: int | None = None,
        health_score: int | None = None,
        quality_score: int | None = None,
        risk_score: int | None = None,
        security_score: int | None = None,
    ) -> dict[str, Any]:
        """Calculate composite engineering score.

        Args:
            architecture_score: Architecture score (0-100).
            health_score: Health score (0-100).
            quality_score: Quality score (0-100).
            risk_score: Risk score (0-100, lower is better).
            security_score: Security score (0-100).

        Returns:
            Dictionary with engineering score and breakdown.
        """
        # Collect available scores
        scores = []
        if architecture_score is not None:
            scores.append(("architecture", architecture_score))
        if health_score is not None:
            scores.append(("health", health_score))
        if quality_score is not None:
            scores.append(("quality", quality_score))
        if security_score is not None:
            scores.append(("security", security_score))
        
        # Risk score is inverted (lower is better)
        if risk_score is not None:
            inverted_risk = 100 - risk_score
            scores.append(("risk", inverted_risk))

        if not scores:
            return {
                "engineering_score": 0,
                "breakdown": {},
                "score_count": 0,
                "level": "unknown",
            }

        # Calculate weighted average
        weights = {
            "architecture": 0.25,
            "health": 0.20,
            "quality": 0.25,
            "security": 0.20,
            "risk": 0.10,
        }

        weighted_sum = 0
        total_weight = 0

        breakdown = {}
        for score_name, score_value in scores:
            weight = weights.get(score_name, 0.20)
            weighted_sum += score_value * weight
            total_weight += weight
            breakdown[score_name] = score_value

        # Normalize by total weight
        if total_weight > 0:
            engineering_score = int(weighted_sum / total_weight)
        else:
            engineering_score = 0

        # Determine level
        if engineering_score >= 90:
            level = "excellent"
        elif engineering_score >= 75:
            level = "good"
        elif engineering_score >= 60:
            level = "satisfactory"
        elif engineering_score >= 40:
            level = "needs_improvement"
        else:
            level = "critical"

        return {
            "engineering_score": engineering_score,
            "breakdown": breakdown,
            "score_count": len(scores),
            "level": level,
        }

    def calculate_team_score(
        self,
        repository_scores: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Calculate team-level engineering score.

        Args:
            repository_scores: List of repository engineering scores.

        Returns:
            Dictionary with team score and statistics.
        """
        if not repository_scores:
            return {
                "team_score": 0,
                "average_score": 0,
                "median_score": 0,
                "highest_score": 0,
                "lowest_score": 0,
                "repository_count": 0,
                "level": "unknown",
            }

        scores = [repo.get("engineering_score", 0) for repo in repository_scores]

        average_score = sum(scores) / len(scores)
        sorted_scores = sorted(scores)
        median_score = sorted_scores[len(sorted_scores) // 2]
        highest_score = max(scores)
        lowest_score = min(scores)

        # Determine level
        if average_score >= 90:
            level = "excellent"
        elif average_score >= 75:
            level = "good"
        elif average_score >= 60:
            level = "satisfactory"
        elif average_score >= 40:
            level = "needs_improvement"
        else:
            level = "critical"

        return {
            "team_score": int(average_score),
            "average_score": average_score,
            "median_score": median_score,
            "highest_score": highest_score,
            "lowest_score": lowest_score,
            "repository_count": len(scores),
            "level": level,
        }


engineering_score = EngineeringScore()
