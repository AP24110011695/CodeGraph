"""Trend analyzer for repository metrics.

Analyzes trends and changes in repository metrics over time.
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TrendAnalysis:
    """Result of trend analysis."""

    metrics: dict[str, Any]
    trends: dict[str, str]  # "increasing", "decreasing", "stable"
    insights: list[str]


class TrendAnalyzer:
    """Analyzes trends in repository metrics."""

    def __init__(self):
        """Initialize the trend analyzer."""
        pass

    def analyze(self, current_metrics: dict[str, Any], historical_metrics: list[dict[str, Any]] | None = None) -> TrendAnalysis:
        """Analyze trends in repository metrics.

        Args:
            current_metrics: Current repository metrics.
            historical_metrics: List of historical metrics for comparison.

        Returns:
            TrendAnalysis with detected trends and insights.
        """
        if not historical_metrics:
            # No historical data, return basic analysis
            return TrendAnalysis(
                metrics=current_metrics,
                trends={},
                insights=["No historical data available for trend analysis"],
            )

        trends = {}
        insights = []

        # Analyze trends for key metrics
        for key in ["total_files", "quality_score", "security_score", "smell_count"]:
            if key in current_metrics and historical_metrics:
                current_value = current_metrics.get(key)
                if current_value is None:
                    continue

                # Get previous values
                previous_values = [h.get(key) for h in historical_metrics if h.get(key) is not None]
                if not previous_values:
                    continue

                avg_previous = sum(previous_values) / len(previous_values)

                # Determine trend
                if current_value > avg_previous * 1.1:
                    trends[key] = "increasing"
                elif current_value < avg_previous * 0.9:
                    trends[key] = "decreasing"
                else:
                    trends[key] = "stable"

                # Generate insights
                if key == "quality_score" and trends[key] == "increasing":
                    insights.append("Code quality is improving over time")
                elif key == "quality_score" and trends[key] == "decreasing":
                    insights.append("Code quality is declining, attention needed")
                elif key == "smell_count" and trends[key] == "increasing":
                    insights.append("Code smells are increasing, consider refactoring")
                elif key == "security_score" and trends[key] == "decreasing":
                    insights.append("Security score is declining, review security issues")

        return TrendAnalysis(
            metrics=current_metrics,
            trends=trends,
            insights=insights if insights else ["No significant trends detected"],
        )


trend_analyzer = TrendAnalyzer()
