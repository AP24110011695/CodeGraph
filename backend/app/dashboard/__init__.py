"""Executive engineering dashboard for CodeGraph."""

from app.dashboard.dashboard_engine import DashboardEngine, dashboard_engine
from app.dashboard.executive_summary import ExecutiveSummary, executive_summary
from app.dashboard.dashboard_builder import DashboardBuilder, dashboard_builder
from app.dashboard.widget_builder import WidgetBuilder, widget_builder

__all__ = [
    "dashboard_engine",
    "executive_summary",
    "dashboard_builder",
    "widget_builder",
    "DashboardEngine",
    "ExecutiveSummary",
    "DashboardBuilder",
    "WidgetBuilder",
]
