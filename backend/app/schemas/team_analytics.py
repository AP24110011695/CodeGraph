"""Schemas for team analytics API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class RepositorySummary(BaseModel):
    """Repository summary for team analytics."""

    repository_name: str = Field(..., description="Repository name")
    upload_id: str = Field(..., description="Upload ID")
    architecture_score: Any = Field(..., description="Architecture score")
    health_score: Any = Field(..., description="Health score")
    quality_score: Any = Field(..., description="Quality score")
    risk_score: Any = Field(..., description="Risk score")
    security_score: Any = Field(..., description="Security score")
    engineering_score: Any | None = Field(None, description="Engineering score")


class RepositoryRanking(BaseModel):
    """Repository ranking based on engineering score."""

    repository: str = Field(..., description="Repository name")
    engineering_score: int = Field(..., description="Engineering score")
    level: str = Field(..., description="Performance level")
    upload_id: str = Field(..., description="Upload ID")


class MetricsSummary(BaseModel):
    """Summary of aggregated metrics."""

    repositories: int = Field(..., description="Number of repositories")
    overall_quality: int = Field(..., description="Overall quality score")
    overall_security: int = Field(..., description="Overall security score")
    overall_risk: int = Field(..., description="Overall risk score")


class QualityMetrics(BaseModel):
    """Aggregated quality metrics."""

    overall_quality: int = Field(..., description="Overall quality score")
    average_quality: float = Field(..., description="Average quality score")
    quality_trend: str = Field(..., description="Quality trend")
    repository_count: int = Field(..., description="Repository count")


class RiskMetrics(BaseModel):
    """Aggregated risk metrics."""

    overall_risk: int = Field(..., description="Overall risk score")
    average_risk: float = Field(..., description="Average risk score")
    risk_trend: str = Field(..., description="Risk trend")
    high_risk_count: int = Field(..., description="High risk repository count")
    repository_count: int = Field(..., description="Repository count")


class SecurityMetrics(BaseModel):
    """Aggregated security metrics."""

    overall_security: int = Field(..., description="Overall security score")
    average_security: float = Field(..., description="Average security score")
    security_trend: str = Field(..., description="Security trend")
    vulnerability_count: int = Field(..., description="Total vulnerability count")
    repository_count: int = Field(..., description="Repository count")


class TechnologyDistribution(BaseModel):
    """Technology distribution across repositories."""

    languages: dict[str, int] = Field(default_factory=dict, description="Language distribution")
    frameworks: dict[str, int] = Field(default_factory=dict, description="Framework distribution")
    dominant_language: str | None = Field(None, description="Dominant language")
    technology_diversity: int = Field(..., description="Technology diversity score")


class CICDHealth(BaseModel):
    """Aggregated CI/CD health metrics."""

    overall_ci_health: int = Field(..., description="Overall CI/CD health score")
    average_ci_health: float = Field(..., description="Average CI/CD health score")
    pipelines_configured: int = Field(..., description="Number of pipelines configured")
    automated_tests: int = Field(..., description="Number of automated tests")
    repository_count: int = Field(..., description="Repository count")


class TrendAnalysis(BaseModel):
    """Trend analysis results."""

    trend: str = Field(..., description="Overall trend")
    improvement_rate: float = Field(..., description="Improvement rate percentage")
    declining_repos: int = Field(..., description="Number of declining repositories")
    improving_repos: int = Field(..., description="Number of improving repositories")
    stable_repos: int = Field(..., description="Number of stable repositories")


class TeamAnalyticsResponse(BaseModel):
    """Complete team analytics response."""

    workspace_id: str = Field(..., description="Workspace ID")
    workspace_name: str = Field(..., description="Workspace name")
    engineering_score: int = Field(..., description="Team engineering score")
    workspace_health: int = Field(..., description="Workspace health score")
    summary: MetricsSummary = Field(..., description="Summary metrics")
    quality_metrics: QualityMetrics | None = Field(None, description="Quality metrics")
    risk_metrics: RiskMetrics | None = Field(None, description="Risk metrics")
    security_metrics: SecurityMetrics | None = Field(None, description="Security metrics")
    technology_distribution: TechnologyDistribution | None = Field(None, description="Technology distribution")
    cicd_health: CICDHealth | None = Field(None, description="CI/CD health")
    quality_trend: dict[str, Any] | None = Field(None, description="Quality trend")
    risk_trend: dict[str, Any] | None = Field(None, description="Risk trend")
    security_trend: dict[str, Any] | None = Field(None, description="Security trend")
    engineering_trend: dict[str, Any] | None = Field(None, description="Engineering trend")
    repository_rankings: list[RepositoryRanking] = Field(default_factory=list, description="Repository rankings")
    top_improvements: list[str] = Field(default_factory=list, description="Top improvement recommendations")
    repository_summaries: list[RepositorySummary] = Field(default_factory=list, description="Repository summaries")
    error: str | None = Field(None, description="Error message if failed")
