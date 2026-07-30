"""Schemas for dashboard API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class ScoreCard(BaseModel):
    """Score card widget."""

    type: str = Field(..., description="Widget type")
    title: str = Field(..., description="Widget title")
    value: int = Field(..., description="Score value")
    category: str = Field(..., description="Score category")
    trend: str | None = Field(None, description="Trend direction")
    level: str = Field(..., description="Score level")


class ListWidget(BaseModel):
    """List widget."""

    type: str = Field(..., description="Widget type")
    title: str = Field(..., description="Widget title")
    items: list[str] = Field(default_factory=list, description="List items")
    count: int = Field(..., description="Item count")


class KPIWidget(BaseModel):
    """KPI widget."""

    type: str = Field(..., description="Widget type")
    title: str = Field(..., description="Widget title")
    metrics: dict[str, int] = Field(default_factory=dict, description="KPI metrics")


class RepositoryCard(BaseModel):
    """Repository card widget."""

    type: str = Field(..., description="Widget type")
    repository_name: str = Field(..., description="Repository name")
    architecture_score: int = Field(..., description="Architecture score")
    health_score: int = Field(..., description="Health score")
    quality_score: int = Field(..., description="Quality score")
    security_score: int = Field(..., description="Security score")
    risk_score: int = Field(..., description="Risk score")
    overall_score: int = Field(..., description="Overall score")


class DashboardWidgets(BaseModel):
    """Dashboard widgets collection."""

    repository_cards: list[RepositoryCard] = Field(default_factory=list, description="Repository cards")
    top_risks: ListWidget = Field(..., description="Top risks widget")
    top_improvements: ListWidget = Field(..., description="Top improvements widget")
    technology_stack: ListWidget = Field(..., description="Technology stack widget")
    engineering_kpis: KPIWidget = Field(..., description="Engineering KPIs widget")
    repository_rankings: ListWidget = Field(..., description="Repository rankings widget")


class DashboardResponse(BaseModel):
    """Complete dashboard response."""

    workspace_id: str = Field(..., description="Workspace ID")
    workspace_name: str = Field(..., description="Workspace name")
    executive_score: int = Field(..., description="Executive score")
    workspace_health: int = Field(..., description="Workspace health")
    overall_health: str = Field(..., description="Overall health level")
    summary: str = Field(..., description="Executive summary")
    key_insights: list[str] = Field(default_factory=list, description="Key insights")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations")
    score_cards: list[ScoreCard] = Field(default_factory=list, description="Score cards")
    widgets: DashboardWidgets = Field(..., description="Dashboard widgets")
    error: str | None = Field(None, description="Error message if failed")
