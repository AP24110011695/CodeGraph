"""Widget builder for executive engineering dashboard.

Builds dashboard widgets from repository data.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class WidgetBuilder:
    """Builds dashboard widgets.

    Creates various widget types for the executive dashboard.
    """

    def __init__(self):
        """Initialize the widget builder."""
        pass

    def build_score_card(
        self,
        title: str,
        value: Any,
        category: str,
        trend: str | None = None,
    ) -> dict[str, Any]:
        """Build a score card widget.

        Args:
            title: Widget title.
            value: Score value.
            category: Score category.
            trend: Optional trend direction.

        Returns:
            Score card widget dictionary.
        """
        return {
            "type": "score_card",
            "title": title,
            "value": value,
            "category": category,
            "trend": trend,
            "level": self._get_score_level(value),
        }

    def build_list_widget(
        self,
        title: str,
        items: list[str],
        max_items: int = 5,
    ) -> dict[str, Any]:
        """Build a list widget.

        Args:
            title: Widget title.
            items: List of items.
            max_items: Maximum items to display.

        Returns:
            List widget dictionary.
        """
        return {
            "type": "list",
            "title": title,
            "items": items[:max_items],
            "count": len(items),
        }

    def build_repository_card(
        self,
        repository_name: str,
        architecture_score: Any,
        health_score: Any,
        quality_score: Any,
        security_score: Any,
        risk_score: Any,
    ) -> dict[str, Any]:
        """Build a repository card widget.

        Args:
            repository_name: Repository name.
            architecture_score: Architecture score.
            health_score: Health score.
            quality_score: Quality score.
            security_score: Security score.
            risk_score: Risk score.

        Returns:
            Repository card widget dictionary.
        """
        return {
            "type": "repository_card",
            "repository_name": repository_name,
            "architecture_score": architecture_score,
            "health_score": health_score,
            "quality_score": quality_score,
            "security_score": security_score,
            "risk_score": risk_score,
            "overall_score": self._calculate_overall_score(
                architecture_score,
                health_score,
                quality_score,
                security_score,
                risk_score,
            ),
        }

    def build_kpi_widget(
        self,
        title: str,
        metrics: dict[str, int],
    ) -> dict[str, Any]:
        """Build a KPI widget.

        Args:
            title: Widget title.
            metrics: Dictionary of metric names to values.

        Returns:
            KPI widget dictionary.
        """
        return {
            "type": "kpi",
            "title": title,
            "metrics": metrics,
        }

    def build_chart_widget(
        self,
        title: str,
        chart_type: str,
        data: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build a chart widget.

        Args:
            title: Widget title.
            chart_type: Chart type (bar, line, pie, etc.).
            data: Chart data.

        Returns:
            Chart widget dictionary.
        """
        return {
            "type": "chart",
            "title": title,
            "chart_type": chart_type,
            "data": data,
        }

    def _get_score_level(self, score: Any) -> str:
        """Get score level label.

        Args:
            score: Score value.

        Returns:
            Level label.
        """
        if not isinstance(score, (int, float)):
            return "unknown"
            
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "satisfactory"
        elif score >= 40:
            return "needs_improvement"
        else:
            return "critical"

    def _calculate_overall_score(
        self,
        architecture_score: Any,
        health_score: Any,
        quality_score: Any,
        security_score: Any,
        risk_score: Any,
    ) -> Any:
        """Calculate overall repository score.

        Args:
            architecture_score: Architecture score.
            health_score: Health score.
            quality_score: Quality score.
            security_score: Security score.
            risk_score: Risk score (inverted).

        Returns:
            Overall score.
        """
        scores = [architecture_score, health_score, quality_score, security_score, risk_score]
        if any(not isinstance(s, (int, float)) for s in scores):
            return {
                "status": "unavailable",
                "value": None,
                "reason": "Missing component scores"
            }

        # Invert risk score (lower is better)
        inverted_risk = 100 - risk_score

        # Calculate weighted average
        weights = {
            "architecture": 0.25,
            "health": 0.20,
            "quality": 0.25,
            "security": 0.20,
            "risk": 0.10,
        }

        weighted_sum = (
            architecture_score * weights["architecture"] +
            health_score * weights["health"] +
            quality_score * weights["quality"] +
            security_score * weights["security"] +
            inverted_risk * weights["risk"]
        )

        return int(weighted_sum)


widget_builder = WidgetBuilder()
