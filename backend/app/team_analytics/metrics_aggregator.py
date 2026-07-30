"""Metrics aggregator for team analytics engine.

Aggregates metrics across repositories and workspaces.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MetricsAggregator:
    """Aggregates metrics across repositories and workspaces.

    Reuses existing repository analysis results.
    """

    def __init__(self):
        """Initialize the metrics aggregator."""
        pass

    def aggregate_quality_metrics(
        self,
        repository_metrics: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Aggregate quality metrics across repositories.

        Args:
            repository_metrics: List of repository quality metrics.

        Returns:
            Dictionary with aggregated quality metrics.
        """
        if not repository_metrics:
            return {
                "overall_quality": 0,
                "average_quality": 0,
                "quality_trend": "stable",
                "repository_count": 0,
            }

        quality_scores = [
            repo.get("quality_score", 0)
            for repo in repository_metrics
            if repo.get("quality_score") is not None
        ]

        if not quality_scores:
            return {
                "overall_quality": 0,
                "average_quality": 0,
                "quality_trend": "stable",
                "repository_count": len(repository_metrics),
            }

        average_quality = sum(quality_scores) / len(quality_scores)
        overall_quality = int(average_quality)

        # Determine trend (simplified - would need historical data for real trend)
        quality_trend = "stable"
        if average_quality >= 80:
            quality_trend = "improving"
        elif average_quality < 60:
            quality_trend = "declining"

        return {
            "overall_quality": overall_quality,
            "average_quality": average_quality,
            "quality_trend": quality_trend,
            "repository_count": len(repository_metrics),
        }

    def aggregate_risk_metrics(
        self,
        repository_metrics: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Aggregate risk metrics across repositories.

        Args:
            repository_metrics: List of repository risk metrics.

        Returns:
            Dictionary with aggregated risk metrics.
        """
        if not repository_metrics:
            return {
                "overall_risk": 0,
                "average_risk": 0,
                "risk_trend": "stable",
                "high_risk_count": 0,
                "repository_count": 0,
            }

        risk_scores = [
            repo.get("risk_score", 0)
            for repo in repository_metrics
            if repo.get("risk_score") is not None
        ]

        if not risk_scores:
            return {
                "overall_risk": 0,
                "average_risk": 0,
                "risk_trend": "stable",
                "high_risk_count": 0,
                "repository_count": len(repository_metrics),
            }

        average_risk = sum(risk_scores) / len(risk_scores)
        overall_risk = int(average_risk)
        high_risk_count = sum(1 for score in risk_scores if score > 70)

        # Determine trend
        risk_trend = "stable"
        if average_risk < 30:
            risk_trend = "improving"
        elif average_risk > 60:
            risk_trend = "increasing"

        return {
            "overall_risk": overall_risk,
            "average_risk": average_risk,
            "risk_trend": risk_trend,
            "high_risk_count": high_risk_count,
            "repository_count": len(repository_metrics),
        }

    def aggregate_security_metrics(
        self,
        repository_metrics: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Aggregate security metrics across repositories.

        Args:
            repository_metrics: List of repository security metrics.

        Returns:
            Dictionary with aggregated security metrics.
        """
        if not repository_metrics:
            return {
                "overall_security": 0,
                "average_security": 0,
                "security_trend": "stable",
                "vulnerability_count": 0,
                "repository_count": 0,
            }

        security_scores = [
            repo.get("security_score", 0)
            for repo in repository_metrics
            if repo.get("security_score") is not None
        ]

        if not security_scores:
            return {
                "overall_security": 0,
                "average_security": 0,
                "security_trend": "stable",
                "vulnerability_count": 0,
                "repository_count": len(repository_metrics),
            }

        average_security = sum(security_scores) / len(security_scores)
        overall_security = int(average_security)

        # Aggregate vulnerability count (mock - would come from actual security analysis)
        vulnerability_count = sum(
            repo.get("vulnerability_count", 0)
            for repo in repository_metrics
        )

        # Determine trend
        security_trend = "stable"
        if average_security >= 80:
            security_trend = "improving"
        elif average_security < 60:
            security_trend = "declining"

        return {
            "overall_security": overall_security,
            "average_security": average_security,
            "security_trend": security_trend,
            "vulnerability_count": vulnerability_count,
            "repository_count": len(repository_metrics),
        }

    def aggregate_technology_distribution(
        self,
        repository_metrics: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Aggregate technology distribution across repositories.

        Args:
            repository_metrics: List of repository metrics with language/framework data.

        Returns:
            Dictionary with technology distribution.
        """
        if not repository_metrics:
            return {
                "languages": {},
                "frameworks": {},
                "dominant_language": None,
                "technology_diversity": 0,
            }

        # Aggregate languages
        language_counts = {}
        for repo in repository_metrics:
            languages = repo.get("languages", [])
            for lang in languages:
                language_counts[lang] = language_counts.get(lang, 0) + 1

        # Aggregate frameworks
        framework_counts = {}
        for repo in repository_metrics:
            frameworks = repo.get("frameworks", [])
            for framework in frameworks:
                framework_counts[framework] = framework_counts.get(framework, 0) + 1

        # Find dominant language
        dominant_language = None
        if language_counts:
            dominant_language = max(language_counts, key=language_counts.get)

        # Calculate technology diversity (number of unique technologies)
        technology_diversity = len(language_counts) + len(framework_counts)

        return {
            "languages": language_counts,
            "frameworks": framework_counts,
            "dominant_language": dominant_language,
            "technology_diversity": technology_diversity,
        }

    def aggregate_ci_cd_health(
        self,
        repository_metrics: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Aggregate CI/CD health across repositories.

        Args:
            repository_metrics: List of repository CI/CD metrics.

        Returns:
            Dictionary with aggregated CI/CD health.
        """
        if not repository_metrics:
            return {
                "overall_ci_health": 0,
                "average_ci_health": 0,
                "pipelines_configured": 0,
                "automated_tests": 0,
                "repository_count": 0,
            }

        ci_health_scores = [
            repo.get("pipeline_health", 0)
            for repo in repository_metrics
            if repo.get("pipeline_health") is not None
        ]

        if not ci_health_scores:
            return {
                "overall_ci_health": 0,
                "average_ci_health": 0,
                "pipelines_configured": 0,
                "automated_tests": 0,
                "repository_count": len(repository_metrics),
            }

        average_ci_health = sum(ci_health_scores) / len(ci_health_scores)
        overall_ci_health = int(average_ci_health)

        # Count pipelines with tests
        pipelines_configured = sum(
            1 for repo in repository_metrics
            if repo.get("has_pipeline", False)
        )
        automated_tests = sum(
            1 for repo in repository_metrics
            if repo.get("has_test", False)
        )

        return {
            "overall_ci_health": overall_ci_health,
            "average_ci_health": average_ci_health,
            "pipelines_configured": pipelines_configured,
            "automated_tests": automated_tests,
            "repository_count": len(repository_metrics),
        }


metrics_aggregator = MetricsAggregator()
