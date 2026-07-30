"""Analytics engine for team analytics engine.

Orchestrates team analytics operations using all existing modules.
"""

import logging
from typing import Any

from app.team_analytics.metrics_aggregator import MetricsAggregator, metrics_aggregator
from app.team_analytics.engineering_score import EngineeringScore, engineering_score
from app.team_analytics.trend_builder import TrendBuilder, trend_builder
from app.workspace.workspace_manager import WorkspaceManager, workspace_manager
from app.workspace.repository_registry import RepositoryRegistry, repository_registry

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Performs comprehensive team analytics operations.

    Reuses all existing CodeGraph modules:
    - Workspace Engine (via workspace_manager)
    - Repository Registry (via repository_registry)
    - Quality Analyzer (via aggregated metrics)
    - Risk Engine (via aggregated metrics)
    - Security Analyzer (via aggregated metrics)
    """

    def __init__(
        self,
        metrics_aggregator: MetricsAggregator | None = None,
        engineering_score: EngineeringScore | None = None,
        trend_builder: TrendBuilder | None = None,
        workspace_manager: WorkspaceManager | None = None,
        repository_registry: RepositoryRegistry | None = None,
    ):
        """Initialize the analytics engine.

        Args:
            metrics_aggregator: Optional MetricsAggregator instance.
            engineering_score: Optional EngineeringScore instance.
            trend_builder: Optional TrendBuilder instance.
            workspace_manager: Optional WorkspaceManager instance.
            repository_registry: Optional RepositoryRegistry instance.
        """
        self.metrics_aggregator = metrics_aggregator or MetricsAggregator()
        self.engineering_score = engineering_score or EngineeringScore()
        self.trend_builder = trend_builder or TrendBuilder()
        self.workspace_manager = workspace_manager or WorkspaceManager()
        self.repository_registry = repository_registry or RepositoryRegistry()

    def generate_workspace_analytics(
        self,
        workspace_id: str,
    ) -> dict[str, Any]:
        """Generate comprehensive analytics for a workspace.

        Args:
            workspace_id: Workspace ID.

        Returns:
            Dictionary with workspace analytics.
        """
        # Get workspace
        workspace = self.workspace_manager.get_workspace(workspace_id)

        if not workspace:
            return {
                "error": f"Workspace not found: {workspace_id}",
                "workspace_id": workspace_id,
            }

        # Get repository information
        repositories = list(workspace.repositories.values())

        if not repositories:
            return {
                "workspace_id": workspace_id,
                "workspace_name": workspace.name,
                "engineering_score": 0,
                "workspace_health": 0,
                "summary": {
                    "repositories": 0,
                    "overall_quality": 0,
                    "overall_security": 0,
                    "overall_risk": 0,
                },
                "repository_rankings": [],
                "top_improvements": [
                    "Add repositories to workspace to generate analytics",
                ],
            }

        # Generate repository-level analytics
        repository_analytics = []
        for repo_info in repositories:
            repo_analytics = self._generate_repository_analytics(repo_info)
            repository_analytics.append(repo_analytics)

        # Calculate team-level metrics
        quality_metrics = self.metrics_aggregator.aggregate_quality_metrics(repository_analytics)
        risk_metrics = self.metrics_aggregator.aggregate_risk_metrics(repository_analytics)
        security_metrics = self.metrics_aggregator.aggregate_security_metrics(repository_analytics)
        technology_distribution = self.metrics_aggregator.aggregate_technology_distribution(repository_analytics)
        cicd_health = self.metrics_aggregator.aggregate_ci_cd_health(repository_analytics)

        # Calculate engineering scores
        repository_scores = [
            self.engineering_score.calculate_engineering_score(
                repo.get("architecture_score"),
                repo.get("health_score"),
                repo.get("quality_score"),
                repo.get("risk_score"),
                repo.get("security_score"),
            )
            for repo in repository_analytics
        ]

        team_score = self.engineering_score.calculate_team_score(repository_scores)

        # Calculate workspace health
        workspace_health = self._calculate_workspace_health(repository_analytics)

        # Build trends
        quality_trend = self.trend_builder.build_quality_trend(repository_analytics)
        risk_trend = self.trend_builder.build_risk_trend(repository_analytics)
        security_trend = self.trend_builder.build_security_trend(repository_analytics)
        engineering_trend = self.trend_builder.build_engineering_trend(repository_analytics)

        # Generate repository rankings
        repository_rankings = self._generate_repository_rankings(repository_analytics, repository_scores)

        # Generate top improvements
        top_improvements = self._generate_top_improvements(
            repository_analytics,
            quality_metrics,
            risk_metrics,
            security_metrics,
            cicd_health,
        )

        return {
            "workspace_id": workspace_id,
            "workspace_name": workspace.name,
            "engineering_score": team_score["team_score"],
            "workspace_health": workspace_health,
            "summary": {
                "repositories": len(repositories),
                "overall_quality": quality_metrics.get("overall_quality", 0),
                "overall_security": security_metrics.get("overall_security", 0),
                "overall_risk": risk_metrics.get("overall_risk", 0),
            },
            "quality_metrics": quality_metrics,
            "risk_metrics": risk_metrics,
            "security_metrics": security_metrics,
            "technology_distribution": technology_distribution,
            "cicd_health": cicd_health,
            "quality_trend": quality_trend,
            "risk_trend": risk_trend,
            "security_trend": security_trend,
            "engineering_trend": engineering_trend,
            "repository_rankings": repository_rankings,
            "top_improvements": top_improvements,
            "repository_summaries": repository_analytics,
        }

    def _generate_repository_analytics(
        self,
        repo_info: Any,
    ) -> dict[str, Any]:
        """Generate analytics for a single repository.

        Args:
            repo_info: Repository information from registry.

        Returns:
            Dictionary with repository analytics.
        """
        # Mock scores based on repository info
        # In production, these would come from actual analysis results
        architecture_score = repo_info.architecture_score if repo_info.architecture_score else 50
        health_score = repo_info.health_score if repo_info.health_score else 50
        quality_score = architecture_score  # Simplified
        risk_score = 100 - health_score  # Simplified inverse relationship
        security_score = 70  # Mock security score

        return {
            "repository_name": repo_info.repository_name,
            "upload_id": repo_info.upload_id,
            "architecture_score": architecture_score,
            "health_score": health_score,
            "quality_score": quality_score,
            "risk_score": risk_score,
            "security_score": security_score,
            "languages": repo_info.languages if repo_info.languages else [],
            "frameworks": repo_info.frameworks if repo_info.frameworks else [],
            "has_pipeline": True,  # Mock
            "has_test": True,  # Mock
            "pipeline_health": 75,  # Mock
            "vulnerability_count": 0,  # Mock
        }

    def _calculate_workspace_health(
        self,
        repository_analytics: list[dict[str, Any]],
    ) -> int:
        """Calculate overall workspace health score.

        Args:
            repository_analytics: List of repository analytics.

        Returns:
            Workspace health score (0-100).
        """
        if not repository_analytics:
            return 0

        health_scores = [repo.get("health_score", 50) for repo in repository_analytics]
        return int(sum(health_scores) / len(health_scores))

    def _generate_repository_rankings(
        self,
        repository_analytics: list[dict[str, Any]],
        repository_scores: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Generate repository rankings based on engineering score.

        Args:
            repository_analytics: List of repository analytics.
            repository_scores: List of engineering scores.

        Returns:
            List of repository rankings.
        """
        rankings = []

        for repo_analytics, eng_score in zip(repository_analytics, repository_scores):
            rankings.append({
                "repository": repo_analytics["repository_name"],
                "engineering_score": eng_score["engineering_score"],
                "level": eng_score["level"],
                "upload_id": repo_analytics["upload_id"],
            })

        # Sort by engineering score descending
        rankings.sort(key=lambda x: x["engineering_score"], reverse=True)

        return rankings

    def _generate_top_improvements(
        self,
        repository_analytics: list[dict[str, Any]],
        quality_metrics: dict[str, Any],
        risk_metrics: dict[str, Any],
        security_metrics: dict[str, Any],
        cicd_health: dict[str, Any],
    ) -> list[str]:
        """Generate top improvement recommendations.

        Args:
            repository_analytics: List of repository analytics.
            quality_metrics: Aggregated quality metrics.
            risk_metrics: Aggregated risk metrics.
            security_metrics: Aggregated security metrics.
            cicd_health: Aggregated CI/CD health.

        Returns:
            List of improvement recommendations.
        """
        improvements = []

        # Quality-based recommendations
        if quality_metrics.get("overall_quality", 0) < 70:
            improvements.append("Improve overall code quality through refactoring and best practices")

        # Risk-based recommendations
        if risk_metrics.get("overall_risk", 0) > 50:
            improvements.append("Address high-risk repositories to reduce technical debt")

        # Security-based recommendations
        if security_metrics.get("overall_security", 0) < 70:
            improvements.append("Enhance security measures and address vulnerabilities")

        # CI/CD-based recommendations
        if cicd_health.get("overall_ci_health", 0) < 70:
            improvements.append("Improve CI/CD pipeline health and add automated testing")

        # Technology diversity recommendations
        tech_diversity = quality_metrics.get("repository_count", 0)
        if tech_diversity < 3:
            improvements.append("Increase technology diversity and standardize tooling")

        # Repository count recommendations
        repo_count = len(repository_analytics)
        if repo_count == 0:
            improvements.append("Add repositories to workspace to enable analytics")
        elif repo_count > 20:
            improvements.append("Consider splitting large workspace into focused teams")

        # Generic recommendations if no specific issues
        if not improvements:
            improvements.append("Continue monitoring repository health and performance metrics")

        return improvements[:5]  # Limit to top 5


analytics_engine = AnalyticsEngine()
