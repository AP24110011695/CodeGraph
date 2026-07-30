"""Dashboard builder for executive engineering dashboard.

Builds complete dashboard from repository data.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class DashboardBuilder:
    """Builds complete dashboard.

    Aggregates all widgets and sections into a cohesive dashboard.
    """

    def __init__(self):
        """Initialize the dashboard builder."""
        pass

    def build_dashboard(
        self,
        workspace_data: dict[str, Any],
        team_analytics: dict[str, Any],
        repository_summaries: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build complete dashboard.

        Args:
            workspace_data: Workspace data.
            team_analytics: Team analytics data.
            repository_summaries: List of repository summaries.

        Returns:
            Dictionary with dashboard data.
        """
        # Build repository cards
        repository_cards = self._build_repository_cards(repository_summaries)

        # Build top risks widget
        top_risks = self._build_top_risks(team_analytics)

        # Build top improvements widget
        top_improvements = self._build_top_improvements(team_analytics)

        # Build technology stack widget
        technology_stack = self._build_technology_stack(team_analytics)

        # Build engineering KPIs widget
        engineering_kpis = self._build_engineering_kpis(team_analytics)

        # Build repository rankings widget
        repository_rankings = self._build_repository_rankings(team_analytics)

        return {
            "repository_cards": repository_cards,
            "top_risks": top_risks,
            "top_improvements": top_improvements,
            "technology_stack": technology_stack,
            "engineering_kpis": engineering_kpis,
            "repository_rankings": repository_rankings,
        }

    def _build_repository_cards(
        self,
        repository_summaries: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Build repository cards.

        Args:
            repository_summaries: List of repository summaries.

        Returns:
            List of repository card widgets.
        """
        from app.dashboard.widget_builder import widget_builder

        cards = []

        for repo in repository_summaries:
            card = widget_builder.build_repository_card(
                repository_name=repo.get("repository_name", "Unknown"),
                architecture_score=repo.get("architecture_score", 0),
                health_score=repo.get("health_score", 0),
                quality_score=repo.get("quality_score", 0),
                security_score=repo.get("security_score", 0),
                risk_score=repo.get("risk_score", 0),
            )
            cards.append(card)

        return cards

    def _build_top_risks(
        self,
        team_analytics: dict[str, Any],
    ) -> dict[str, Any]:
        """Build top risks widget.

        Args:
            team_analytics: Team analytics data.

        Returns:
            Top risks widget.
        """
        from app.dashboard.widget_builder import widget_builder

        risks = []

        risk_metrics = team_analytics.get("risk_metrics", {})
        high_risk_count = risk_metrics.get("high_risk_count", 0)

        if high_risk_count > 0:
            risks.append(f"{high_risk_count} high-risk repositories")

        quality_metrics = team_analytics.get("quality_metrics", {})
        overall_quality = quality_metrics.get("overall_quality", 0)
        if overall_quality < 60:
            risks.append("Low code quality detected")

        security_metrics = team_analytics.get("security_metrics", {})
        vulnerability_count = security_metrics.get("vulnerability_count", 0)
        if vulnerability_count > 0:
            risks.append(f"{vulnerability_count} security vulnerabilities")

        cicd_health = team_analytics.get("cicd_health", {})
        pipeline_health = cicd_health.get("overall_ci_health", 0)
        if pipeline_health < 60:
            risks.append("CI/CD pipeline health issues")

        if not risks:
            risks.append("No critical risks identified")

        return widget_builder.build_list_widget("Top Risks", risks)

    def _build_top_improvements(
        self,
        team_analytics: dict[str, Any],
    ) -> dict[str, Any]:
        """Build top improvements widget.

        Args:
            team_analytics: Team analytics data.

        Returns:
            Top improvements widget.
        """
        from app.dashboard.widget_builder import widget_builder

        improvements = team_analytics.get("top_improvements", [])

        if not improvements:
            improvements = ["Continue monitoring engineering metrics"]

        return widget_builder.build_list_widget("Top Improvements", improvements)

    def _build_technology_stack(
        self,
        team_analytics: dict[str, Any],
    ) -> dict[str, Any]:
        """Build technology stack widget.

        Args:
            team_analytics: Team analytics data.

        Returns:
            Technology stack widget.
        """
        from app.dashboard.widget_builder import widget_builder

        technology_distribution = team_analytics.get("technology_distribution", {})
        languages = technology_distribution.get("languages", {})
        frameworks = technology_distribution.get("frameworks", {})

        tech_items = []

        for lang, count in languages.items():
            tech_items.append(f"{lang}: {count} repositories")

        for framework, count in frameworks.items():
            tech_items.append(f"{framework}: {count} repositories")

        if not tech_items:
            tech_items = ["No technology data available"]

        return widget_builder.build_list_widget("Technology Stack", tech_items)

    def _build_engineering_kpis(
        self,
        team_analytics: dict[str, Any],
    ) -> dict[str, Any]:
        """Build engineering KPIs widget.

        Args:
            team_analytics: Team analytics data.

        Returns:
            Engineering KPIs widget.
        """
        from app.dashboard.widget_builder import widget_builder

        quality_metrics = team_analytics.get("quality_metrics", {})
        risk_metrics = team_analytics.get("risk_metrics", {})
        security_metrics = team_analytics.get("security_metrics", {})
        cicd_health = team_analytics.get("cicd_health", {})

        metrics = {
            "Overall Quality": quality_metrics.get("overall_quality", 0),
            "Overall Risk": risk_metrics.get("overall_risk", 0),
            "Overall Security": security_metrics.get("overall_security", 0),
            "CI/CD Health": cicd_health.get("overall_ci_health", 0),
        }

        return widget_builder.build_kpi_widget("Engineering KPIs", metrics)

    def _build_repository_rankings(
        self,
        team_analytics: dict[str, Any],
    ) -> dict[str, Any]:
        """Build repository rankings widget.

        Args:
            team_analytics: Team analytics data.

        Returns:
            Repository rankings widget.
        """
        from app.dashboard.widget_builder import widget_builder

        rankings = team_analytics.get("repository_rankings", [])

        ranking_items = []
        for ranking in rankings[:5]:
            repo_name = ranking.get("repository", "Unknown")
            score = ranking.get("engineering_score", 0)
            level = ranking.get("level", "unknown")
            ranking_items.append(f"{repo_name}: {score} ({level})")

        if not ranking_items:
            ranking_items = ["No repository rankings available"]

        return widget_builder.build_list_widget("Repository Rankings", ranking_items)


dashboard_builder = DashboardBuilder()
