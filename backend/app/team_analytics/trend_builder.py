"""Trend builder for team analytics engine.

Builds trend analysis from repository metrics.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class TrendBuilder:
    """Builds trend analysis from repository metrics.

    Analyzes trends in quality, risk, security, and other metrics.
    """

    def __init__(self):
        """Initialize the trend builder."""
        pass

    def build_quality_trend(
        self,
        repository_metrics: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build quality trend analysis.

        Args:
            repository_metrics: List of repository quality metrics.

        Returns:
            Dictionary with quality trend analysis.
        """
        if not repository_metrics:
            return {
                "trend": "unknown",
                "improvement_rate": 0,
                "declining_repos": 0,
                "improving_repos": 0,
                "stable_repos": 0,
            }

        # Simplified trend analysis (would need historical data for real trends)
        quality_scores = [
            repo.get("quality_score", 50)
            for repo in repository_metrics
        ]

        average_quality = sum(quality_scores) / len(quality_scores)

        # Classify repositories based on quality
        declining_repos = sum(1 for score in quality_scores if score < 50)
        improving_repos = sum(1 for score in quality_scores if score > 70)
        stable_repos = len(quality_scores) - declining_repos - improving_repos

        # Determine overall trend
        if improving_repos > declining_repos:
            trend = "improving"
            improvement_rate = (improving_repos / len(quality_scores)) * 100
        elif declining_repos > improving_repos:
            trend = "declining"
            improvement_rate = -(declining_repos / len(quality_scores)) * 100
        else:
            trend = "stable"
            improvement_rate = 0

        return {
            "trend": trend,
            "improvement_rate": improvement_rate,
            "declining_repos": declining_repos,
            "improving_repos": improving_repos,
            "stable_repos": stable_repos,
        }

    def build_risk_trend(
        self,
        repository_metrics: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build risk trend analysis.

        Args:
            repository_metrics: List of repository risk metrics.

        Returns:
            Dictionary with risk trend analysis.
        """
        if not repository_metrics:
            return {
                "trend": "unknown",
                "risk_increase_rate": 0,
                "high_risk_repos": 0,
                "low_risk_repos": 0,
                "stable_rpos": 0,
            }

        risk_scores = [
            repo.get("risk_score", 50)
            for repo in repository_metrics
        ]

        average_risk = sum(risk_scores) / len(risk_scores)

        # Classify repositories based on risk
        high_risk_repos = sum(1 for score in risk_scores if score > 70)
        low_risk_repos = sum(1 for score in risk_scores if score < 30)
        stable_repos = len(risk_scores) - high_risk_repos - low_risk_repos

        # Determine overall trend
        if high_risk_repos > low_risk_repos:
            trend = "increasing"
            risk_increase_rate = (high_risk_repos / len(risk_scores)) * 100
        elif low_risk_repos > high_risk_repos:
            trend = "decreasing"
            risk_increase_rate = -(low_risk_repos / len(risk_scores)) * 100
        else:
            trend = "stable"
            risk_increase_rate = 0

        return {
            "trend": trend,
            "risk_increase_rate": risk_increase_rate,
            "high_risk_repos": high_risk_repos,
            "low_risk_repos": low_risk_repos,
            "stable_repos": stable_repos,
        }

    def build_security_trend(
        self,
        repository_metrics: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build security trend analysis.

        Args:
            repository_metrics: List of repository security metrics.

        Returns:
            Dictionary with security trend analysis.
        """
        if not repository_metrics:
            return {
                "trend": "unknown",
                "security_improvement_rate": 0,
                "vulnerable_repos": 0,
                "secure_repos": 0,
                "stable_repos": 0,
            }

        security_scores = [
            repo.get("security_score", 50)
            for repo in repository_metrics
        ]

        average_security = sum(security_scores) / len(security_scores)

        # Classify repositories based on security
        vulnerable_repos = sum(1 for score in security_scores if score < 50)
        secure_repos = sum(1 for score in security_scores if score > 80)
        stable_repos = len(security_scores) - vulnerable_repos - secure_repos

        # Determine overall trend
        if secure_repos > vulnerable_repos:
            trend = "improving"
            security_improvement_rate = (secure_repos / len(security_scores)) * 100
        elif vulnerable_repos > secure_repos:
            trend = "declining"
            security_improvement_rate = -(vulnerable_repos / len(security_scores)) * 100
        else:
            trend = "stable"
            security_improvement_rate = 0

        return {
            "trend": trend,
            "security_improvement_rate": security_improvement_rate,
            "vulnerable_repos": vulnerable_repos,
            "secure_repos": secure_repos,
            "stable_repos": stable_repos,
        }

    def build_engineering_trend(
        self,
        repository_metrics: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build overall engineering trend.

        Args:
            repository_metrics: List of repository engineering metrics.

        Returns:
            Dictionary with overall engineering trend.
        """
        if not repository_metrics:
            return {
                "trend": "unknown",
                "overall_direction": 0,
                "improving_count": 0,
                "declining_count": 0,
            }

        engineering_scores = [
            repo.get("engineering_score", 50)
            for repo in repository_metrics
        ]

        average_score = sum(engineering_scores) / len(engineering_scores)

        # Classify repositories
        improving_count = sum(1 for score in engineering_scores if score > 70)
        declining_count = sum(1 for score in engineering_scores if score < 50)

        # Determine overall direction
        if improving_count > declining_count:
            trend = "improving"
            overall_direction = 1
        elif declining_count > improving_count:
            trend = "declining"
            overall_direction = -1
        else:
            trend = "stable"
            overall_direction = 0

        return {
            "trend": trend,
            "overall_direction": overall_direction,
            "improving_count": improving_count,
            "declining_count": declining_count,
        }


trend_builder = TrendBuilder()
