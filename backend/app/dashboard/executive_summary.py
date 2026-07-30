"""Executive summary for executive engineering dashboard.

Generates executive-level summaries from engineering data.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ExecutiveSummary:
    """Generates executive summaries.

    Creates high-level summaries for executive consumption.
    """

    def __init__(self):
        """Initialize the executive summary generator."""
        pass

    def generate_executive_summary(
        self,
        workspace_data: dict[str, Any],
        team_analytics: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate executive summary.

        Args:
            workspace_data: Workspace data.
            team_analytics: Team analytics data.

        Returns:
            Dictionary with executive summary.
        """
        engineering_score = team_analytics.get("engineering_score", 0)
        workspace_health = team_analytics.get("workspace_health", 0)
        repository_count = team_analytics.get("summary", {}).get("repositories", 0)

        # Determine overall health
        overall_health = self._determine_overall_health(
            engineering_score,
            workspace_health,
        )

        # Generate summary text
        summary_text = self._generate_summary_text(
            overall_health,
            repository_count,
            engineering_score,
            team_analytics,
        )

        # Generate key insights
        key_insights = self._generate_key_insights(team_analytics)

        # Generate recommendations
        recommendations = self._generate_executive_recommendations(team_analytics)

        return {
            "executive_score": engineering_score,
            "workspace_health": workspace_health,
            "overall_health": overall_health,
            "summary": summary_text,
            "key_insights": key_insights,
            "recommendations": recommendations,
        }

    def _determine_overall_health(
        self,
        engineering_score: int,
        workspace_health: int,
    ) -> str:
        """Determine overall health level.

        Args:
            engineering_score: Engineering score.
            workspace_health: Workspace health score.

        Returns:
            Health level string.
        """
        average_score = (engineering_score + workspace_health) / 2

        if average_score >= 90:
            return "excellent"
        elif average_score >= 75:
            return "good"
        elif average_score >= 60:
            return "satisfactory"
        elif average_score >= 40:
            return "needs_improvement"
        else:
            return "critical"

    def _generate_summary_text(
        self,
        overall_health: str,
        repository_count: int,
        engineering_score: int,
        team_analytics: dict[str, Any],
    ) -> str:
        """Generate summary text.

        Args:
            overall_health: Overall health level.
            repository_count: Number of repositories.
            engineering_score: Engineering score.
            team_analytics: Team analytics data.

        Returns:
            Summary text string.
        """
        summary_parts = []

        if overall_health == "excellent":
            summary_parts.append(f"Overall engineering health is excellent across {repository_count} repositories.")
        elif overall_health == "good":
            summary_parts.append(f"Overall engineering health is strong across {repository_count} repositories.")
        elif overall_health == "satisfactory":
            summary_parts.append(f"Overall engineering health is satisfactory across {repository_count} repositories.")
        elif overall_health == "needs_improvement":
            summary_parts.append(f"Overall engineering health needs improvement across {repository_count} repositories.")
        else:
            summary_parts.append(f"Overall engineering health is critical across {repository_count} repositories.")

        # Add specific insights
        quality_metrics = team_analytics.get("quality_metrics", {})
        risk_metrics = team_analytics.get("risk_metrics", {})
        security_metrics = team_analytics.get("security_metrics", {})

        if quality_metrics.get("overall_quality", 0) < 70:
            summary_parts.append(" Quality improvements are recommended.")
        if risk_metrics.get("overall_risk", 0) > 50:
            summary_parts.append(" Risk management requires attention.")
        if security_metrics.get("overall_security", 0) < 70:
            summary_parts.append(" Security enhancements are needed.")

        return "".join(summary_parts)

    def _generate_key_insights(
        self,
        team_analytics: dict[str, Any],
    ) -> list[str]:
        """Generate key insights.

        Args:
            team_analytics: Team analytics data.

        Returns:
            List of key insights.
        """
        insights = []

        repository_count = team_analytics.get("summary", {}).get("repositories", 0)
        insights.append(f"Monitoring {repository_count} repositories")

        quality_metrics = team_analytics.get("quality_metrics", {})
        overall_quality = quality_metrics.get("overall_quality", 0)
        if overall_quality >= 80:
            insights.append("High overall code quality")
        elif overall_quality < 60:
            insights.append("Code quality requires attention")

        risk_metrics = team_analytics.get("risk_metrics", {})
        overall_risk = risk_metrics.get("overall_risk", 0)
        if overall_risk < 30:
            insights.append("Low risk profile")
        elif overall_risk > 60:
            insights.append("High risk profile detected")

        security_metrics = team_analytics.get("security_metrics", {})
        overall_security = security_metrics.get("overall_security", 0)
        if overall_security >= 80:
            insights.append("Strong security posture")
        elif overall_security < 60:
            insights.append("Security posture needs improvement")

        return insights[:5]

    def _generate_executive_recommendations(
        self,
        team_analytics: dict[str, Any],
    ) -> list[str]:
        """Generate executive-level recommendations.

        Args:
            team_analytics: Team analytics data.

        Returns:
            List of recommendations.
        """
        recommendations = []

        quality_metrics = team_analytics.get("quality_metrics", {})
        risk_metrics = team_analytics.get("risk_metrics", {})
        security_metrics = team_analytics.get("security_metrics", {})
        cicd_health = team_analytics.get("cicd_health", {})

        if quality_metrics.get("overall_quality", 0) < 70:
            recommendations.append("Invest in code quality improvement initiatives")

        if risk_metrics.get("overall_risk", 0) > 50:
            recommendations.append("Prioritize technical debt reduction")

        if security_metrics.get("overall_security", 0) < 70:
            recommendations.append("Enhance security measures and vulnerability management")

        if cicd_health.get("overall_ci_health", 0) < 70:
            recommendations.append("Improve CI/CD pipeline health and automation")

        # Add general recommendation if none specific
        if not recommendations:
            recommendations.append("Continue monitoring engineering metrics and best practices")

        return recommendations[:3]


executive_summary = ExecutiveSummary()
