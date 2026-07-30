"""Dashboard engine for executive engineering dashboard.

Orchestrates dashboard generation using all existing modules.
"""

import logging
from typing import Any

from app.dashboard.executive_summary import ExecutiveSummary, executive_summary
from app.dashboard.dashboard_builder import DashboardBuilder, dashboard_builder
from app.dashboard.widget_builder import WidgetBuilder, widget_builder
from app.team_analytics.analytics_engine import AnalyticsEngine, analytics_engine
from app.workspace.workspace_manager import WorkspaceManager, workspace_manager

logger = logging.getLogger(__name__)


class DashboardEngine:
    """Performs comprehensive dashboard generation operations.

    Reuses all existing CodeGraph modules:
    - Workspace Engine (via workspace_manager)
    - Team Analytics Engine (via analytics_engine)
    - All other analysis modules (via team_analytics aggregation)
    """

    def __init__(
        self,
        executive_summary: ExecutiveSummary | None = None,
        dashboard_builder: DashboardBuilder | None = None,
        widget_builder: WidgetBuilder | None = None,
        analytics_engine: AnalyticsEngine | None = None,
        workspace_manager: WorkspaceManager | None = None,
    ):
        """Initialize the dashboard engine.

        Args:
            executive_summary: Optional ExecutiveSummary instance.
            dashboard_builder: Optional DashboardBuilder instance.
            widget_builder: Optional WidgetBuilder instance.
            analytics_engine: Optional AnalyticsEngine instance.
            workspace_manager: Optional WorkspaceManager instance.
        """
        self.executive_summary = executive_summary or ExecutiveSummary()
        self.dashboard_builder = dashboard_builder or DashboardBuilder()
        self.widget_builder = widget_builder or WidgetBuilder()
        
        # Use shared workspace manager if provided, otherwise create new
        if workspace_manager is not None:
            self.workspace_manager = workspace_manager
            # Create analytics engine with shared workspace manager
            self.analytics_engine = analytics_engine or AnalyticsEngine(
                workspace_manager=workspace_manager,
            )
        else:
            self.workspace_manager = workspace_manager or WorkspaceManager()
            self.analytics_engine = analytics_engine or AnalyticsEngine(
                workspace_manager=self.workspace_manager,
            )

    def generate_dashboard(
        self,
        workspace_id: str,
    ) -> dict[str, Any]:
        """Generate executive dashboard for a workspace.

        Args:
            workspace_id: Workspace ID.

        Returns:
            Dictionary with dashboard data.
        """
        # Get workspace
        workspace = self.workspace_manager.get_workspace(workspace_id)

        if not workspace:
            return {
                "error": f"Workspace not found: {workspace_id}",
                "workspace_id": workspace_id,
            }

        # Generate team analytics
        team_analytics = self.analytics_engine.generate_workspace_analytics(workspace_id)

        if "error" in team_analytics:
            return {
                "error": team_analytics.get("error"),
                "workspace_id": workspace_id,
            }

        # Extract repository summaries
        repository_summaries = team_analytics.get("repository_summaries", [])

        # Generate executive summary
        executive_summary_data = self.executive_summary.generate_executive_summary(
            {"workspace_id": workspace_id, "workspace_name": workspace.name},
            team_analytics,
        )

        # Build dashboard widgets
        dashboard_data = self.dashboard_builder.build_dashboard(
            {"workspace_id": workspace_id, "workspace_name": workspace.name},
            team_analytics,
            repository_summaries,
        )

        # Build score cards
        score_cards = self._build_score_cards(team_analytics)

        # Combine all dashboard components
        return {
            "workspace_id": workspace_id,
            "workspace_name": workspace.name,
            "executive_score": executive_summary_data.get("executive_score", 0),
            "workspace_health": executive_summary_data.get("workspace_health", 0),
            "overall_health": executive_summary_data.get("overall_health"),
            "summary": executive_summary_data.get("summary"),
            "key_insights": executive_summary_data.get("key_insights", []),
            "recommendations": executive_summary_data.get("recommendations", []),
            "score_cards": score_cards,
            "widgets": dashboard_data,
        }

    def _build_score_cards(
        self,
        team_analytics: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Build score cards for dashboard.

        Args:
            team_analytics: Team analytics data.

        Returns:
            List of score card widgets.
        """
        score_cards = []

        # Repository Health
        workspace_health = team_analytics.get("workspace_health", 0)
        score_cards.append(
            self.widget_builder.build_score_card(
                "Repository Health",
                workspace_health,
                "health",
            )
        )

        # Architecture Score
        quality_metrics = team_analytics.get("quality_metrics", {})
        architecture_score = quality_metrics.get("overall_quality", 0)
        score_cards.append(
            self.widget_builder.build_score_card(
                "Architecture Score",
                architecture_score,
                "architecture",
            )
        )

        # Security Score
        security_metrics = team_analytics.get("security_metrics", {})
        security_score = security_metrics.get("overall_security", 0)
        score_cards.append(
            self.widget_builder.build_score_card(
                "Security Score",
                security_score,
                "security",
            )
        )

        # Risk Score (inverted for display)
        risk_metrics = team_analytics.get("risk_metrics", {})
        risk_score = 100 - risk_metrics.get("overall_risk", 0)
        score_cards.append(
            self.widget_builder.build_score_card(
                "Risk Score",
                risk_score,
                "risk",
            )
        )

        # CI/CD Health
        cicd_health = team_analytics.get("cicd_health", {})
        cicd_score = cicd_health.get("overall_ci_health", 0)
        score_cards.append(
            self.widget_builder.build_score_card(
                "CI/CD Health",
                cicd_score,
                "cicd",
            )
        )

        return score_cards


dashboard_engine = DashboardEngine()
